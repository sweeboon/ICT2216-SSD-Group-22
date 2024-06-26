import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProductComponent = () => {
  const [products, setProducts] = useState([]);
  const [newProduct, setNewProduct] = useState({
    category_id: '',
    image_id: '',
    product_description: '',
    product_price: '',
    stock: '',
    image_path: ''
  });
  const [editProduct, setEditProduct] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get('/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

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

  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      console.log("Adding product:", newProduct);
      const response = await axios.post('/product', newProduct);
      setProducts([...products, response.data.product]);
      setNewProduct({
        category_id: '',
        image_id: '',
        product_description: '',
        product_price: '',
        stock: '',
        image_path: ''
      });
    } catch (error) {
      console.error('Error adding product:', error);
    }
  };

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put(`/product/${editProduct.product_id}`, editProduct);
      setProducts(products.map((product) => (product.product_id === editProduct.product_id ? response.data : product)));
      setEditProduct(null);
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleEdit = (product) => {
    setEditProduct(product);
  };

  const handleDelete = async (product_id) => {
    try {
      await axios.delete(`/product/${product_id}`);
      setProducts(products.filter((product) => product.product_id !== product_id));
    } catch (error) {
      console.error('Error deleting product:', error);
    }
  };

  return (
    <div className="product-management">
      <h2>Manage Products</h2>
      <form onSubmit={editProduct ? handleUpdateProduct : handleAddProduct}>
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
            <button onClick={() => handleEdit(product)}>Edit</button>
            <button onClick={() => handleDelete(product.product_id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default ProductComponent;