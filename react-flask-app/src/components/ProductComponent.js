import React from 'react';
import { useProduct } from '../hooks/useProduct';

const ProductComponent = () => {
  const {
    products,
    newProduct,
    setNewProduct,
    editProduct,
    setEditProduct,
    handleAddProduct,
    handleUpdateProduct,
    handleDeleteProduct
  } = useProduct();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setNewProduct((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditProduct((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (editProduct) {
      handleUpdateProduct();
    } else {
      handleAddProduct();
    }
  };

  return (
    <div className="product-management">
      <h2>Manage Products</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          name="category_id"
          placeholder="Category ID"
          value={editProduct ? editProduct.category_id : newProduct.category_id}
          onChange={editProduct ? handleEditChange : handleChange}
        />
        <input
          type="number"
          name="image_id"
          placeholder="Image ID"
          value={editProduct ? editProduct.image_id : newProduct.image_id}
          onChange={editProduct ? handleEditChange : handleChange}
        />
        <textarea
          name="product_description"
          placeholder="Description"
          value={editProduct ? editProduct.product_description : newProduct.product_description}
          onChange={editProduct ? handleEditChange : handleChange}
        />
        <input
          type="number"
          name="product_price"
          placeholder="Price"
          min="0"
          step="0.01"
          value={editProduct ? editProduct.product_price : newProduct.product_price}
          onChange={editProduct ? handleEditChange : handleChange}
        />
        <input
          type="number"
          name="stock"
          placeholder="Stock"
          min="0"
          value={editProduct ? editProduct.stock : newProduct.stock}
          onChange={editProduct ? handleEditChange : handleChange}
        />
        <input
          type="text"
          name="image_path"
          placeholder="Image Path"
          value={editProduct ? editProduct.image_path : newProduct.image_path}
          onChange={editProduct ? handleEditChange : handleChange}
        />
        <button type="submit">{editProduct ? 'Update Product' : 'Add Product'}</button>
      </form>
      <ul>
        {products.map((product) => (
          <li key={product.product_id}>
            {product.product_description} - ${product.product_price}
            <p>{product.stock} in stock</p>
            <p>{product.image_path}</p>
            <button onClick={() => setEditProduct(product)}>Edit</button>
            <button onClick={() => handleDeleteProduct(product.product_id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProductComponent;