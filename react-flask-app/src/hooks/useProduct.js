import { useState, useEffect } from 'react';
import axios from '../components/axiosConfig'; // Ensure this path is correct based on your project structure

export const useProduct = () => {
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

  const fetchProducts = async () => {
    try {
      const response = await axios.get('/main/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const handleAddProduct = async () => {
    try {
      const response = await axios.post('/main/product', newProduct);
      setProducts([...products, response.data]);
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

  const handleUpdateProduct = async () => {
    try {
      if (editProduct) {
        const response = await axios.put(`/main/product/${editProduct.product_id}`, editProduct);
        setProducts(products.map((product) => (product.product_id === editProduct.product_id ? response.data : product)));
        setEditProduct(null);
      }
    } catch (error) {
      console.error('Error updating product:', error);
    }
  };

  const handleDeleteProduct = async (product_id) => {
    try {
      await axios.delete(`/main/product/${product_id}`);
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