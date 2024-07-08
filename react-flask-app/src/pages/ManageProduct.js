import React, { useEffect, useState } from 'react';
import { useProduct } from '../hooks/useProduct';
import { useAuth } from '../hooks/useAuth';
import axios from '../components/axiosConfig';
import ImageUpload from '../components/ImageUpload';
import '../css/ManageProduct.css';

const ManageProduct = () => {
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
  const [uploadSuccess, setUploadSuccess] = useState('');

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

  const handleImageUpload = (uploadedUrl) => {
    setNewProduct((prevState) => ({
      ...prevState,
      image_path: uploadedUrl,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editProduct) {
        await handleUpdateProduct();
      } else {
        await handleAddProduct();
      }
      setUploadSuccess('Product saved successfully!');
    } catch (error) {
      alert('An error occurred while saving the product. Please try again.');
      console.error('Error saving product:', error);
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
            value={newProduct.category_id}
            onChange={handleChange}
            className="category_id"
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
            placeholder="Product Description"
            value={newProduct.product_description}
            onChange={handleChange}
          />
          <input
            type="number"
            name="product_price"
            placeholder="Price"
            min="0"
            step="0.01"
            value={newProduct.product_price}
            onChange={handleChange}
          />
          <input
            type="number"
            name="stock"
            placeholder="Stock"
            min="0"
            value={newProduct.stock}
            onChange={handleChange}
          />
          <ImageUpload onUpload={handleImageUpload} />
          {uploadSuccess && <p className="upload-success">{uploadSuccess}</p>}
          <button type="submit">{editProduct ? 'Update Product' : 'Add Product'}</button>
        </form>
      )}
      <ul>
        {products.map((product) => (
          <li key={product.product_id}>
            <div className="product-info">
              <h3>{product.product_description}</h3>
              <p>${product.product_price}</p>
              <p>{product.stock} in stock</p>
            </div>
            <img src={product.image_path} alt={product.product_description} />
            {isLoggedIn && isAdmin && (
              <div className="product-actions">
                <button onClick={() => setEditProduct(product)}>Edit</button>
                <button className="delete-button" onClick={() => handleDeleteProduct(product.product_id)}>Delete</button>
              </div>
            )}
          </li>
        ))}
      </ul>
      <footer className="footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default ManageProduct;
