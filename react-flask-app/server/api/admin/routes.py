from flask_login import current_user, login_required
from flask import request, jsonify, abort, current_app
from flask_principal import RoleNeed, Permission
from api.admin import bp
from api.models import Account, Role, Order, Payment, Product, Category
from api import db, csrf, limiter
import base64
from passlib.hash import pbkdf2_sha256

admin_permission = Permission(RoleNeed('Admin'))

@bp.route('/users', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def get_users():
    users = Account.query.filter(~Account.roles.any(Role.name == 'Admin'), Account.account_id != current_user.account_id).all()
    users_data = []
    for user in users:
        user_roles = [role.name for role in user.roles]
        users_data.append({
            'account_id': user.account_id,
            'email': user.email,
            'name': user.name,
            'address': user.address,
            'roles': user_roles
        })
    return jsonify(users_data), 200

@bp.route('/users/<int:account_id>', methods=['PUT'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def update_user(account_id):
    data = request.get_json()
    user = Account.query.get(account_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if any(role.name == 'Admin' for role in user.roles):
        return jsonify({'message': 'Cannot modify admin users'}), 403

    user.email = data.get('email', user.email)
    user.name = data.get('name', user.name)
    user.address = data.get('address', user.address)
    
    new_password = data.get('password')
    if new_password:
        user.password = pbkdf2_sha256.hash(new_password)
    
    db.session.commit()
    
    return jsonify({'message': 'User updated successfully'}), 200

@bp.route('/users/<int:account_id>', methods=['DELETE'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def delete_user(account_id):
    user = Account.query.get(account_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if any(role.name == 'Admin' for role in user.roles):
        return jsonify({'message': 'Cannot delete admin users'}), 403

    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200


@bp.route('/assign-role', methods=['POST'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def assign_role():
    data = request.get_json()
    account_id = data.get('account_id')
    role_name = data.get('role_name')

    if not account_id or not role_name:
        return jsonify({'message': 'Account ID and Role Name are required'}), 400

    account = Account.query.get(account_id)
    if not account:
        return jsonify({'message': 'Account not found'}), 404

    if any(role.name == 'Admin' for role in account.roles):
        return jsonify({'message': 'You cannot change the roles of another admin user'}), 403

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({'message': 'Role not found'}), 404

    account.roles = [role]
    db.session.commit()

    return jsonify({'message': f'Role {role_name} assigned to account {account.email} successfully'}), 200

@bp.route('/roles', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def get_roles():
    roles = Role.query.all()
    roles_data = [{'id': role.id, 'name': role.name} for role in roles]
    return jsonify(roles_data), 200

@bp.route('/orders', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def get_all_orders():
    orders = Order.query.all()
    orders_data = [{
        'order_id': order.order_id,
        'account_id': order.account_id,
        'account_email': Account.query.get(order.account_id).email,
        'product_id': order.product_id,
        'order_status': order.order_status,
        'order_price': order.order_price,
        'order_date': order.order_date,
        'quantity': order.quantity,
        'payment_id': order.payment_id,
        'payment_method': Payment.query.get(order.payment_id).payment_method,
        'total_amount': Payment.query.get(order.payment_id).total_amount
    } for order in orders]
    return jsonify(orders_data), 200

@bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.json.get('status')

    if not new_status:
        return jsonify({'message': 'New status is required'}), 400

    if new_status not in ['Pending', 'Completed']:
        return jsonify({'message': 'Invalid status value'}), 400

    order.order_status = new_status
    db.session.commit()
    return jsonify({'message': 'Order status updated successfully'}), 200

# Create a New Product
@bp.route('/products', methods=['POST'])
@csrf.exempt
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
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

# Update a Product
@bp.route('/products/<int:product_id>', methods=['PUT'])
@csrf.exempt
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
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
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    
    return '', 204

@bp.route('/categories', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def get_categories():
    categories = Category.query.all()
    categories_data = [{'category_id': category.category_id, 'category_name': category.category_name} for category in categories]
    return jsonify(categories_data), 200
