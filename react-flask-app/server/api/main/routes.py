import base64, logging, uuid
from datetime import datetime
from flask import request, jsonify, abort, current_app
from api.models import Product, Cart, Sessions
from api import db, csrf
from api.main import bp

@bp.route('/sessions', methods=['POST'])
def create_session():
    try:
        ssid = str(uuid.uuid4())
        new_session = Sessions(ssid=ssid, timestamp=datetime.utcnow())
        db.session.add(new_session)
        db.session.commit()
        return jsonify({'ssid': ssid}), 201
    except Exception as e:
        logging.error(f"Error creating session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/sessions/<ssid>', methods=['PUT'])
def update_session(ssid):
    logging.info(f"Received update request for session {ssid} with payload: {request.json}")
    try:
        session = Sessions.query.get_or_404(ssid)
        data = request.json
        if 'timestamp' in data:
            session.timestamp = data['timestamp']
        if 'token' in data:
            session.token = data['token']
        if 'referer' in data:
            session.referer = data['referer']
        
        db.session.commit()
        logging.info(f"Session {ssid} updated successfully")
        return jsonify({'message': 'Session updated'}), 200
    except Exception as e:
        logging.error(f"Error updating session {ssid}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/sessions/<ssid>', methods=['GET'])
def get_session(ssid):
    session = Sessions.query.get(ssid)

    if session is None:
        return jsonify({'error': 'Session not found'}), 404

    session_data = {
        'ssid': session.ssid,
        'timestamp': session.timestamp,
        'token': session.token,
        'referer': session.referer
    }
    return jsonify(session_data), 200

# Read All Products
@bp.route('/products', methods=['GET'])
@csrf.exempt
def get_products():
    products = Product.query.all()
    product_list = [{'product_id': p.product_id, 'category_id': p.category_id, 'product_description': p.product_description, 
                     'product_price': p.product_price, 'stock': p.stock, 'image_path': p.image_path} for p in products]
    return jsonify(product_list), 200

# Create a New Product
@bp.route('/products', methods=['POST'])
@csrf.exempt
def create_product():
    if not request.json or not all(key in request.json for key in ['category_id', 'product_description', 'product_price', 'stock', 'image_path']):
        abort(400)  # Bad request

    supabase = current_app.supabase
    
    image_data = request.json['image_path']  # Assuming image data is base64 encoded
    image_name = f"{request.json['product_description'].replace(' ', '_')}.png"

    response = supabase.storage.from_("your-bucket-name").upload(image_name, base64.b64decode(image_data))

    if response['status'] != 'ok':
        abort(500)  # Handle error

    image_url = supabase.storage.from_("your-bucket-name").get_public_url(image_name)

    new_product = Product(
        category_id=request.json['category_id'],
        product_description=request.json['product_description'],
        product_price=request.json['product_price'],
        stock=request.json['stock'],
        image_path=image_url  # Store the URL of the uploaded image
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({'product_id': new_product.product_id}), 201

# Read a Single Product
@bp.route('/products/<int:product_id>', methods=['GET'])
@csrf.exempt
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'product_id': product.product_id, 'category_id': product.category_id, 'product_description': product.product_description, 
                    'product_price': product.product_price, 'stock': product.stock, 'image_path': product.image_path}), 200

# Update a Product
@bp.route('/products/<int:product_id>', methods=['PUT'])
@csrf.exempt
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if not request.json:
        abort(400)
    
    product.category_id = request.json.get('category_id', product.category_id)
    product.product_description = request.json.get('product_description', product.product_description)
    product.product_price = request.json.get('product_price', product.product_price)
    product.stock = request.json.get('stock', product.stock)
    product.image_path = request.json.get('image_path', product.image_path)
    
    db.session.commit()
    
    return jsonify({'product_id': product.product_id}), 200

# Delete a Product
@bp.route('/products/<int:product_id>', methods=['DELETE'])
@csrf.exempt
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return '', 204

@bp.route('/cart', methods=['GET'])
def get_cart_items():
    account_id = request.args.get('account_id')
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
            'created_at': item.created_at,
            'quantity': item.quantity,
            'cart_item_price': item.cart_item_price,
        } for item in cart_items
    ]
    return jsonify(cart_list), 200

@bp.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.json
    logging.info(f"Received payload: {data}")

    account_id = data.get('account_id')
    session_id = data.get('session_id')

    cart_item = None
    if account_id:
        cart_item = Cart.query.filter_by(account_id=account_id, product_id=data['product_id']).first()
    elif session_id:
        cart_item = Cart.query.filter_by(session_id=session_id, product_id=data['product_id']).first()

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

@bp.route('/cart/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'}), 200