import base64, logging, uuid, re, html, mimetypes
from datetime import datetime
from flask import request, jsonify, abort, current_app, session
from flask_login import login_required, current_user
from flask_principal import RoleNeed, Permission
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from api.models import Product, Cart, Payment, Order, Account
from api import db, csrf, limiter
from api.main import bp
from .encryption import encrypt_data, decrypt_data, generate_key
import logging
import os
from defusedxml.ElementTree import parse as safe_parse, ParseError,  EntitiesForbidden
import requests
from config import Config
from concurrent.futures import ThreadPoolExecutor

encryption_key = generate_key()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
UPLOAD_FOLDER = 'public/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2mb max
VIRUSTOTAL_API_KEY = '348f1df07a7b57c0e39b5990c700ce57de4a1bb178bb5a97d6293dac4e0f9b91'
executor = ThreadPoolExecutor(max_workers=4)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def scan_file_with_virustotal(api_key, file_path):
    url = 'https://www.virustotal.com/vtapi/v2/file/scan'
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file)}
        params = {'apikey': api_key}
        response = requests.post(url, files=files, params=params)
        return response.json()

def get_scan_report(api_key, resource):
    url = 'https://www.virustotal.com/vtapi/v2/file/report'
    params = {'apikey': api_key, 'resource': resource}
    response = requests.get(url, params=params)
    return response.json()

def sanitize_input(input):
    if input is None:
        return None
    return html.escape(input)

def validate_numeric(value):
    return value.isdigit()

# Check if the cart has items
@bp.route('/cart/check', methods=['GET'])
@login_required
@limiter.limit("10 per minute") # Apply rate limiting
def check_cart():
    account_id = current_user.account_id
    cart_items = Cart.query.filter_by(account_id=account_id).all()
    
    if not cart_items:
        return jsonify({'message': 'Your cart is empty. Add items to your cart before proceeding to checkout.'}), 400
    
    return jsonify({'message': 'You have items in your cart. You can proceed to checkout.'}), 200

@bp.route('/payment', methods=['POST'])
@login_required
@csrf.exempt
@limiter.limit("10 per minute") # Apply rate limiting
def create_payment():
    try:
        data = request.get_json()
        payment_method = data.get('payment_method')
        total_amount = data.get('total_amount')
        credit_card_number = data.get('credit_card_number')
        expiry_date = data.get('expiry_date')
        cvv = data.get('cvv')

        logging.info(f"Received payment data: {data}")

        if not payment_method or not total_amount:
            return jsonify({'message': 'Payment method and total amount are required'}), 400

        account_id = current_user.get_id()
        cart_items = Cart.query.filter_by(account_id=account_id).all()

        if not cart_items:
            return jsonify({'message': 'Your cart is empty. Add items to your cart before proceeding to checkout.'}), 400

        # Encrypt sensitive information
        encrypted_credit_card_number = encrypt_data(credit_card_number, encryption_key)
        encrypted_expiry_date = encrypt_data(expiry_date, encryption_key)
        encrypted_cvv = encrypt_data(cvv, encryption_key)

        logging.info("Credit card information encrypted successfully.")

        # Create Payment
        new_payment = Payment(
            account_id=account_id,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status='Pending',  # Set initial status to pending
            payment_date=datetime.now(),
            credit_card_number=encrypted_credit_card_number.encode('utf-8'),
            expiry_date=encrypted_expiry_date.encode('utf-8'),
            cvv=encrypted_cvv.encode('utf-8')
        )
        db.session.add(new_payment)
        db.session.commit()

        logging.info("Payment record created successfully.")

        # Process Orders
        for item in cart_items:
            new_order = Order(
                payment_id=new_payment.payment_id,
                account_id=account_id,
                product_id=item.product_id,
                order_status='Pending',  # Set initial status to pending
                order_price=item.cart_item_price,
                order_date=datetime.now(),
                quantity=item.quantity
            )
            db.session.add(new_order)
            db.session.delete(item)  # Remove item from cart

        db.session.commit()
        new_payment.payment_status = 'Completed'  # Update payment status to completed
        db.session.commit()

        logging.info("Orders processed and payment status updated successfully.")

        return jsonify({'message': 'Payment successful and order placed', 'payment_id': new_payment.payment_id}), 201

    except Exception as e:
        logging.error(f"Error processing payment: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Failed to process payment', 'error': str(e)}), 500

# Read All Products
@bp.route('/products', methods=['GET'])
@login_required
@csrf.exempt
@limiter.limit("10 per minute") # Apply rate limiting
def get_products():
    logger.info("Fetching all products")
    products = Product.query.all()
    if not products:
        logger.warning("No products found")
        return jsonify({'message': 'No products found'}), 404

    product_list = [{'product_id': p.product_id, 'category_id': p.category_id, 'product_description': p.product_description, 
                     'product_price': p.product_price, 'stock': p.stock, 'image_path': p.image_path} for p in products]
    logger.info(f"Found {len(product_list)} products")
    for product in product_list:
        logger.info(f"Product: {product}")
    return jsonify(product_list), 200


# Read a Single Product
@bp.route('/products/<int:product_id>', methods=['GET'])
@csrf.exempt
@limiter.limit("10 per minute") # Apply rate limiting
def get_product(product_id):
    logger.info(f"Fetching product with ID {product_id}")
    product = Product.query.get_or_404(product_id)
    return jsonify({'product_id': product.product_id, 'category_id': product.category_id, 'product_description': product.product_description, 
                    'product_price': product.product_price, 'stock': product.stock, 'image_path': product.image_path}), 200


from defusedxml.ElementTree import parse as safe_parse, ParseError

@bp.route('/upload-image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        current_app.logger.error("No file part in the request")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        current_app.logger.error("No file selected for uploading")
        return jsonify({"error": "No file selected for uploading"}), 400

    if not allowed_file(file.filename):
        current_app.logger.error("Invalid file extension")
        return jsonify({"error": "Invalid file extension"}), 400

    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        # Ensure the upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        if file_length > MAX_CONTENT_LENGTH:
            current_app.logger.error("File size exceeds limit")
            return jsonify({"error": "File size exceeds limit"}), 400

        # Read file content to validate as XML
        file_content = file.read().decode('utf-8', errors='ignore')
        file.seek(0)

        if filename.lower().endswith(('png', 'jpg', 'jpeg')):
            try:
                # Securely parse XML content
                safe_parse(file)
                current_app.logger.error("XML content detected in image file")
                return jsonify({"error": "Invalid image file containing XML content"}), 400
            except EntitiesForbidden:
                current_app.logger.error("XXE attempt detected in the uploaded file")
                return jsonify({"error": "Invalid image file containing XXE payload"}), 400
            except ParseError:
                current_app.logger.info("No XML content detected, proceeding with file upload")
                file.seek(0)  # Reset file pointer after parsing

        # Save the file locally
        with open(file_path, 'wb') as f:
            f.write(file.read())

        # Scan the file using VirusTotal
        scan_result = scan_file_with_virustotal(VIRUSTOTAL_API_KEY, file_path)
        if scan_result.get('response_code') != 1:
            return jsonify({"error": "File scan failed"}), 500

        # Get scan report asynchronously
        resource = scan_result['resource']
        future_report = executor.submit(get_scan_report, VIRUSTOTAL_API_KEY, resource)
        report = future_report.result()

        # Check for malware
        positives = report.get('positives')
        if positives is not None and positives > 0:
            os.remove(file_path)
            return jsonify({'error': 'Malware detected in file'}), 400

        current_app.logger.info(f"Image stored successfully: {file_path}")

        # Return the temporary file path
        return jsonify({"file_path": file_path}), 200

    except Exception as e:
        current_app.logger.error(f"Exception occurred during image upload: {e}")
        return jsonify({"error": str(e)}), 500




@bp.route('/cart', methods=['GET'])
@login_required
@limiter.limit("10 per minute") # Apply rate limiting
def get_cart_items():
    account_id = current_user.get_id() if current_user.is_authenticated else None

    if account_id:
        cart_items = Cart.query.filter_by(account_id=account_id).all()
    else:
        return jsonify({'error': 'account_id must be provided'}), 400

    cart_list = [
        {
            'cart_id': item.cart_id,
            'product_id': item.product_id,
            'product_description': item.product.product_description,
            'image_path': item.product.image_path,
            'account_id': item.account_id,
            'quantity': item.quantity,
            'cart_item_price': item.cart_item_price,
        } for item in cart_items
    ]
    return jsonify(cart_list), 200

@bp.route('/cart', methods=['POST'])
@login_required
@csrf.exempt
@limiter.limit("10 per minute") # Apply rate limiting
def add_to_cart():
    data = request.json
    if current_user.is_authenticated:
        account_id = current_user.get_id()
    else:
        account_id = None

    cart_item = Cart.query.filter_by(account_id=account_id, product_id=data['product_id']).first()

    if cart_item:
        # If item exists, update the quantity
        cart_item.quantity += data['quantity']
        cart_item.cart_item_price += data['cart_item_price'] * data['quantity']
    else:
        # If item does not exist, create a new one
        new_item = Cart(
            product_id=data['product_id'],
            account_id=account_id,
            quantity=data['quantity'],
            cart_item_price=data['cart_item_price']
        )
        db.session.add(new_item)
    
    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 201

@bp.route('/cart/<int:cart_id>', methods=['DELETE'])
@login_required
@csrf.exempt
@limiter.limit("10 per minute") # Apply rate limiting
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200

@bp.route('/cart/total', methods=['GET'])
@login_required
@limiter.limit("10 per minute") # Apply rate limiting
def get_cart_total():
    account_id = current_user.account_id
    cart_items = Cart.query.filter_by(account_id=account_id).all()
    
    if not cart_items:
        return jsonify({'total_amount': 0, 'message': 'Your cart is empty. Add items to your cart before proceeding to checkout.'}), 200

    total_amount = sum(item.cart_item_price for item in cart_items)
    return jsonify({'total_amount': total_amount, 'message': 'You have items in your cart. You can proceed to checkout.'}), 200

@bp.route('/orders', methods=['GET'])
@login_required
@limiter.limit("10 per minute") # Apply rate limiting
def get_orders():
    account_id = current_user.account_id
    orders = Order.query.filter_by(account_id=account_id).all()

    orders_list = [
        {
            'order_id': order.order_id,
            'payment_id': order.payment_id,
            'product_id': order.product_id,
            'order_status': order.order_status,
            'order_price': order.order_price,
            'order_date': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'quantity': order.quantity,
            'product_description': Product.query.get(order.product_id).product_description
        } for order in orders
    ]
    
    return jsonify(orders_list), 200
