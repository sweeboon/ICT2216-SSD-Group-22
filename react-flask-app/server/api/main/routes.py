import base64, logging, uuid, re
from datetime import datetime
from flask import request, jsonify, abort, current_app, session
from flask_login import login_required, current_user
from flask_principal import RoleNeed, Permission
from werkzeug.security import generate_password_hash, check_password_hash
from api.models import Product, Cart, Payment, Order, Sessions,Account
from api import db, csrf
from api.main import bp


# Password validation function
def validate_password(password):
    min_length = 8
    has_number = re.compile(r'[0-9]')
    has_special_char = re.compile(r'[@#$%^&+=]')

    if len(password) < min_length:
        return False, "Password must be at least 8 characters long."
    if not has_number.search(password):
        return False, "Password must contain at least one number."
    if not has_special_char.search(password):
        return False, "Password must contain at least one special character."
    return True, ""

# Register new user
@bp.route('/auth/register', methods=['POST'])
@csrf.exempt
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')
    date_of_birth = data.get('date_of_birth')
    address = data.get('address')

    if not email or not password or not username:
        return jsonify({'error': 'Missing required fields'}), 400

    valid, message = validate_password(password)
    if not valid:
        return jsonify({'error': message}), 400

    hashed_password = generate_password_hash(password)
    new_account = Account(
        email=email,
        password=hashed_password,
        name=username,
        date_of_birth=date_of_birth,
        address=address
    )
    db.session.add(new_account)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# Check if the cart has items
@bp.route('/cart/check', methods=['GET'])
@login_required
def check_cart():
    account_id = current_user.account_id
    cart_items = Cart.query.filter_by(account_id=account_id).all()
    
    if not cart_items:
        return jsonify({'message': 'Your cart is empty. Add items to your cart before proceeding to checkout.'}), 400
    
    return jsonify({'message': 'You have items in your cart. You can proceed to checkout.'}), 200

# Create Payment and Process Order
@bp.route('/payment', methods=['POST'])
@login_required
@csrf.exempt
def create_payment():
    try:
        data = request.get_json()
        payment_method = data.get('payment_method')
        total_amount = data.get('total_amount')
        
        if not payment_method or not total_amount:
            return jsonify({'message': 'Payment method and total amount are required'}), 400

        account_id = current_user.get_id()
        cart_items = Cart.query.filter_by(account_id=account_id).all()
        
        if not cart_items:
            return jsonify({'message': 'Your cart is empty. Add items to your cart before proceeding to checkout.'}), 400

        # Create Payment
        new_payment = Payment(
            account_id=account_id,
            total_amount=total_amount,
            payment_method=payment_method,
            payment_status='Pending',  # Set initial status to pending
            payment_date=datetime.now()
        )
        db.session.add(new_payment)
        db.session.commit()

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

        return jsonify({'message': 'Payment successful and order placed', 'payment_id': new_payment.payment_id}), 201

    except Exception as e:
        logging.error(f"Error processing payment: {str(e)}")
        db.session.rollback()
        return jsonify({'message': 'Failed to process payment', 'error': str(e)}), 500

# Read All Products
@bp.route('/products', methods=['GET'])
@csrf.exempt
def get_products():
    products = Product.query.all()
    product_list = [{'product_id': p.product_id, 'category_id': p.category_id, 'product_description': p.product_description, 
                     'product_price': p.product_price, 'stock': p.stock, 'image_path': p.image_path} for p in products]
    return jsonify(product_list), 200


# Read a Single Product
@bp.route('/products/<int:product_id>', methods=['GET'])
@csrf.exempt
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'product_id': product.product_id, 'category_id': product.category_id, 'product_description': product.product_description, 
                    'product_price': product.product_price, 'stock': product.stock, 'image_path': product.image_path}), 200


@bp.route('/cart', methods=['GET'])
def get_cart_items():
    account_id = current_user.get_id() if current_user.is_authenticated else None
    session_id = request.args.get('session_id')

    if account_id:
        cart_items = Cart.query.filter_by(account_id=account_id).all()
    elif session_id:
        cart_items = Cart.query.filter_by(session_id=session_id).all()
    else:
        return jsonify({'error': 'account_id or session_id must be provided'}), 400

    cart_list = [
        {
            'cart_id': item.cart_id,
            'product_id': item.product_id,
            'product_description': item.product.product_description,
            'image_path': item.product.image_path,
            'account_id': item.account_id,
            'session_id': item.session_id,
            'quantity': item.quantity,
            'cart_item_price': item.cart_item_price,
        } for item in cart_items
    ]
    return jsonify(cart_list), 200

@bp.route('/cart', methods=['POST'])
@csrf.exempt
def add_to_cart():
    data = request.json
    if current_user.is_authenticated:
        account_id = current_user.get_id()
        session_id = None
    else:
        account_id = None
        session_id = data.get('session_id')

    cart_item = Cart.query.filter_by(account_id=account_id, session_id=session_id, product_id=data['product_id']).first()

    if cart_item:
        # If item exists, update the quantity
        cart_item.quantity += data['quantity']
        cart_item.cart_item_price += data['cart_item_price'] * data['quantity']
    else:
        # If item does not exist, create a new one
        new_item = Cart(
            product_id=data['product_id'],
            account_id=account_id,
            session_id=session_id,
            quantity=data['quantity'],
            cart_item_price=data['cart_item_price']
        )
        db.session.add(new_item)
    
    db.session.commit()
    return jsonify({'message': 'Item added to cart'}), 201

@bp.route('/cart/transfer', methods=['POST'])
@login_required
def transfer_cart():
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400
    
    session_cart_items = Cart.query.filter_by(session_id=session_id).all()
    for item in session_cart_items:
        existing_item = Cart.query.filter_by(account_id=current_user.account_id, product_id=item.product_id).first()
        if existing_item:
            existing_item.quantity += item.quantity
            existing_item.cart_item_price += item.cart_item_price
        else:
            item.account_id = current_user.account_id
            item.session_id = None
        db.session.commit()

    return jsonify({'message': 'Cart items transferred to your account'}), 200

@bp.route('/cart/<int:cart_id>', methods=['DELETE'])
@csrf.exempt
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200

@bp.route('/orders', methods=['GET'])
@login_required
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
