from flask import Blueprint, jsonify, request
from api.models import Product
from api import db

bp = Blueprint('main', __name__)

# CRUD operations for the Product model
@bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    product_list = [{'product_id': p.product_id, 'category_id': p.category_id, 'image_id': p.image_id, 'product_description': p.product_description, 
                     'product_price': p.product_price, 'stock': p.stock, 'image_path': p.image_path} for p in products]
    print(product_list)
    return jsonify(product_list), 200

@bp.route('/product', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(
        category_id=data['category_id'],
        image_id=data['image_id'],
        product_description=data['product_description'],
        product_price=data['product_price'],
        stock=data['stock'],
        image_path=data['image_path']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'New product added successfully.', 'product': new_product.product_id}), 201

@bp.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    product = Product.query.get_or_404(product_id)
    product.category_id = data['category_id']
    product.image_id = data['image_id']
    product.product_description = data['product_description']
    product.product_price = data['product_price']
    product.stock = data['stock']
    product.image_path = data['image_path']
    db.session.commit()
    return jsonify({'message': 'Product updated successfully.'}), 200

@bp.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully.'}), 200