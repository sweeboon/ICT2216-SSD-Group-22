import React, { useEffect } from 'react';
import { useProduct } from '../hooks/useProduct';
import '../css/Shop.css'; // Import the CSS file

const Shop = () => {
  const { products, fetchProducts } = useProduct();

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  return (
    <div className="shop">
      <h1>Product Catalog</h1>
      <div className="product-grid">
        {products.map((product) => (
          <div key={product.product_id} className="product-item">
            <h3>{product.product_description}</h3>
            <p>Price: ${product.product_price}</p>
            <img src={product.image_path} alt={product.product_description} 
              style={{ width: '200px', height: '200px' }} />
            <button>Add to Cart</button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Shop;
