import React, { useEffect, useState } from 'react';
import { useProduct } from '../hooks/useProduct';
import { useAuth } from '../hooks/useAuth';
import axios from '../components/axiosConfig'; // Ensure this path is correct based on your project structure
import ImageUpload from '../components/ImageUpload'; // Import the ImageUpload component
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
  const [uploadSuccess, setUploadSuccess] = useState(''); // State for the image upload success message

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
    console.log('Image uploaded with URL:', uploadedUrl); // Debugging
    if (editProduct) {
      setEditProduct((prevState) => ({
        ...prevState,
        image_path: uploadedUrl,
      }));
    } else {
      setNewProduct((prevState) => ({
        ...prevState,
        image_path: uploadedUrl,
      }));
      console.log('newProduct after image upload:', { ...newProduct, image_path: uploadedUrl }); // Debugging
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Submitting newProduct:', { ...newProduct }); // Debugging
    try {
      if (editProduct) {
        await handleUpdateProduct();
        setUploadSuccess('Product saved successfully!');
      } else {
        await handleAddProduct();
        setUploadSuccess('Product saved successfully!');
      }
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
            placeholder="Product Name"
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
          <ImageUpload onUpload={handleImageUpload} /> {/* Use the ImageUpload component */}
          {uploadSuccess && <p style={{ color: 'green' }}>{uploadSuccess}</p>}
          <button type="submit">{editProduct ? 'Update Product' : 'Add Product'}</button>
        </form>
      )}
      <ul>
        {products.map((product) => (
          <li key={product.product_id}>
            {product.product_description} - ${product.product_price}
            <p>{product.stock} in stock</p>
            <img src={product.image_path} alt={product.product_description} style={{ width: '100px', height: '100px' }} />
            {isLoggedIn && isAdmin && (
              <div className='product-management-buttons'>
    

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