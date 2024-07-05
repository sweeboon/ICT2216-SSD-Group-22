import React, { useEffect, useState } from 'react';
import { useProduct } from '../hooks/useProduct';
import { useAuth } from '../hooks/useAuth';
import axios from '../components/axiosConfig'; // Ensure this path is correct based on your project structure

const ProductComponent = () => {
  const { isLoggedIn, roles } = useAuth();
  const {
    products,
    newProduct,
    setNewProduct,
    editProduct,
    setEditProduct,
    handleAddProduct,
    handleUpdateProduct,
    handleDeleteProduct,
  } = useProduct();
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get('/admin/categories');
        setCategories(response.data);
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    fetchCategories();
  }, []);

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

  const isAdmin = roles.includes('Admin');

  return (
    <div className="product-management">
      <h2>Manage Products</h2>
      {isLoggedIn && isAdmin && (
        <form onSubmit={handleSubmit}>
          <select
            name="category_id"
            value={editProduct ? editProduct.category_id : newProduct.category_id}
            onChange={editProduct ? handleEditChange : handleChange}
          >
            <option value="">Select Category</option>
            {categories.map((category) => (
              <option key={category.category_id} value={category.category_id}>
                {category.category_name}
              </option>
            ))}
          </select>
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
      )}
      <ul>
        {products.map((product) => (
          <li key={product.product_id}>
            {product.product_description} - ${product.product_price}
            <p>{product.stock} in stock</p>
            <p>{product.image_path}</p>
            {isLoggedIn && isAdmin && (
              <>
                <button onClick={() => setEditProduct(product)}>Edit</button>
                <button onClick={() => handleDeleteProduct(product.product_id)}>Delete</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProductComponent;
