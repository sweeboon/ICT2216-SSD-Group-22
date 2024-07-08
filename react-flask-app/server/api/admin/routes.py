from flask_login import current_user, login_required
from flask import request, jsonify, abort, current_app
from flask_principal import RoleNeed, Permission
from api.admin import bp
from api.models import Account, Role, Order, Payment, Product, Category, AuditLog
from api import db, csrf, limiter
import base64,mimetypes
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from flask import request
import os

admin_permission = Permission(RoleNeed('Admin'))

def get_ip_address():
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.getlist('X-Forwarded-For')[0]
    else:
        ip = request.remote_addr
    return ip

def log_audit_event(user_id, user_name, action, details, ip_address):
    audit_log = AuditLog(
        user_id=user_id,
        user_name=user_name,
        action=action,
        details=details,
        ip_address=ip_address,
        timestamp=datetime.utcnow()
    )
    db.session.add(audit_log)
    db.session.commit()

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
    changes = []
    user.email = data.get('email', user.email)
    user.name = data.get('name', user.name)
    user.address = data.get('address', user.address)
    
    new_password = data.get('password')
    if new_password:
        user.password = pbkdf2_sha256.hash(new_password)
    
    db.session.commit()
    ip_address = get_ip_address()
    log_audit_event(current_user.account_id, current_user.name, 'Update User', f'Updated user {account_id}:{user.name}: {"; ".join(changes)}', ip_address)
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
    ip_address = get_ip_address()
    log_audit_event(current_user.account_id, current_user.name, 'Delete User', f'Deleted user {account_id}:{user.name}', ip_address)
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
    ip_address = get_ip_address()
    log_audit_event(current_user.account_id, current_user.name, 'Assign Role', f'Assigned role {role_name} to user {account_id}:{account.name}',ip_address)
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

    old_status = order.order_status
    order.order_status = new_status
    db.session.commit()
   
    ip_address = get_ip_address()
    log_audit_event(current_user.account_id, current_user.name, 'Update Order Status', f'Updated order {order_id} status from {old_status} to {new_status}',ip_address)
    return jsonify({'message': 'Order status updated successfully'}), 200

# Create a New Product
@bp.route('/products', methods=['POST'])
@csrf.exempt
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute")  # Apply rate limiting
def create_product():
    data = request.get_json()
    
    current_app.logger.info(f'Received data for new product: {data}')
    
    # Check if all required fields are present
    required_fields = ['category_id', 'product_description', 'product_price', 'stock', 'image_path']
    if not data or not all(field in data for field in required_fields):
        missing_fields = [field for field in required_fields if field not in data]
        current_app.logger.error(f'Missing required fields: {missing_fields}')
        return jsonify({'message': f'Missing required fields: {missing_fields}'}), 400

    try:
        image_path = data['image_path']
        
        # Save product to the database
        new_product = Product(
            category_id=data['category_id'],
            product_description=data['product_description'],
            product_price=data['product_price'],
            stock=data['stock'],
            image_path=image_path  # Store the URL of the uploaded image
        )

        db.session.add(new_product)
        db.session.commit()
        ip_address = get_ip_address()

        current_app.logger.info(f'Product created with ID: {new_product.product_id}')
        log_audit_event(current_user.account_id, current_user.name, 'Create Product', f'Created product {new_product.product_id} with description {new_product.product_description}, price {new_product.product_price}, stock {new_product.stock}', ip_address)

        return jsonify({'product_id': new_product.product_id}), 201
    
    except Exception as e:
        current_app.logger.error(f'Error creating product: {str(e)}')
        return jsonify({'message': 'Internal Server Error'}), 500

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
    
    changes = []
    if request.json.get('category_id') and request.json['category_id'] != product.category_id:
        changes.append(f"category_id: {product.category_id} -> {request.json['category_id']}")
        product.category_id = request.json['category_id']
    if request.json.get('product_description') and request.json['product_description'] != product.product_description:
        changes.append(f"description: {product.product_description} -> {request.json['product_description']}")
        product.product_description = request.json['product_description']
    if request.json.get('product_price') and request.json['product_price'] != product.product_price:
        changes.append(f"price: {product.product_price} -> {request.json['product_price']}")
        product.product_price = request.json['product_price']
    if request.json.get('stock') and request.json['stock'] != product.stock:
        changes.append(f"stock: {product.stock} -> {request.json['stock']}")
        product.stock = request.json['stock']
    if request.json.get('image_path') and request.json['image_path'] != product.image_path:
        changes.append(f"image_path: {product.image_path} -> {request.json['image_path']}")
        product.image_path = request.json['image_path']
    
    db.session.commit()
    ip_address = get_ip_address()
    log_audit_event(current_user.account_id, current_user.name, 'Update Product', f'Updated product {product_id} :{product.product_description}: {"; ".join(changes)}', ip_address)
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
    ip_address = get_ip_address()
    log_audit_event(current_user.account_id, current_user.name, 'Delete Product', f'Deleted product {product_id} with description {product.product_description}', ip_address)
    return '', 204

@bp.route('/categories', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
@limiter.limit("10 per minute") # Apply rate limiting
def get_categories():
    categories = Category.query.all()
    categories_data = [{'category_id': category.category_id, 'category_name': category.category_name} for category in categories]
    return jsonify(categories_data), 200
@bp.route('/audit_logs', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def get_audit_logs():
    try:
        print("Fetching audit logs...")
        logs = AuditLog.query.all()
        if not logs:
            print("No audit logs found")
        logs_data = [{
            'id': log.id,
            'user_id': log.user_id,
            'user_name': log.user_name,
            'action': log.action,
            'details': log.details,
            'timestamp': log.timestamp,
            'ip_address': log.ip_address  # Fetching IP address
        } for log in logs]
        print(f"Fetched {len(logs_data)} audit logs")
        return jsonify(logs_data), 200
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        return jsonify({"error": "Error fetching audit logs"}), 500