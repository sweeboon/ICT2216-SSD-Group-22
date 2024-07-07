import { useState, useEffect } from 'react';
import axios from '../components/axiosConfig'; // Ensure this path is correct based on your project structure

export const useProduct = () => {
  const [products, setProducts] = useState([]);
  const [newProduct, setNewProduct] = useState({
    category_id: '',
    product_description: '',
    product_price: '',
    stock: '',
    image_path: ''
  });
  const [editProduct, setEditProduct] = useState(null);

  const fetchProducts = async () => {
    try {
      const response = await axios.get('/main/products');
      const productsWithData = response.data.map(product => ({
        ...product,
        image_path: `${product.image_path}`
      }));
      setProducts(productsWithData);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const handleAddProduct = async () => {
    const requiredFields = [
      'category_id',
      'product_description',
      'product_price',
      'stock',
      'image_path'
    ];
    
    for (const field of requiredFields) {
      if (!newProduct[field] || newProduct[field].toString().trim() === '') {
        alert(`Please fill in the ${field.replace('_', ' ')}.`);
        return;
      }
    }
  
    console.log('Sending newProduct:', newProduct);

    try {
      const response = await axios.post('/admin/products', newProduct);
      console.log('Product added:', response.data);
      fetchProducts(); // Refresh the product list
      setNewProduct({
        category_id: '',
        product_description: '',
        product_price: '',
        stock: '',
        image_path: ''
      }); // Reset the new product fields
    } catch (error) {
      console.error('Error adding product:', error);
      throw error;
    }
  };

  const handleUpdateProduct = async () => {
    try {
      const response = await axios.put(`/admin/products/${editProduct.product_id}`, editProduct);
      console.log('Product updated:', response.data);
      fetchProducts(); // Refresh the product list
      setEditProduct(null); // Clear the edit product state after update
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleDeleteProduct = async (product_id) => {
    try {
      await axios.delete(`/admin/products/${product_id}`);
      setProducts(products.filter((product) => product.product_id !== product_id));
    } catch (error) {
      console.error('Error deleting product:', error);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  return {
    products,
    newProduct,
    setNewProduct,
    editProduct,
    setEditProduct,
    fetchProducts,
    handleAddProduct,
    handleUpdateProduct,
    handleDeleteProduct
  };
};