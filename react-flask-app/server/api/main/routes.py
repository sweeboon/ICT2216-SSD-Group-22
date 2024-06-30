import base64
from flask import request, jsonify, abort, current_app
from api.models import Product
from api import db, csrf
from api.main import bp

# CRUD operations for the Product model

# Read All Products
@bp.route('/products', methods=['GET'])
@csrf.exempt
def get_products():
    products = Product.query.all()
    product_list = [{'product_id': p.product_id, 'category_id': p.category_id, 'image_id': p.image_id, 'product_description': p.product_description, 
                     'product_price': p.product_price, 'stock': p.stock, 'image_path': p.image_path} for p in products]
    return jsonify(product_list), 200

# Create a New Product
@bp.route('/products', methods=['POST'])
@csrf.exempt
def create_product():
    if not request.json or not all(key in request.json for key in ['category_id', 'image_id', 'product_description', 'product_price', 'stock', 'image_path']):
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
        image_id=request.json['image_id'],
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
    return jsonify({'product_id': product.product_id, 'category_id': product.category_id, 'image_id': product.image_id, 'product_description': product.product_description, 
                    'product_price': product.product_price, 'stock': product.stock, 'image_path': product.image_path}), 200

# Update a Product
@bp.route('/products/<int:product_id>', methods=['PUT'])
@csrf.exempt
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if not request.json:
        abort(400)
    
    product.category_id = request.json.get('category_id', product.category_id)
    product.image_id = request.json.get('image_id', product.image_id)
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
