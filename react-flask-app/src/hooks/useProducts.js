import { useState, useEffect } from 'react';

export const useProducts = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    setProducts([
      { id: 1, name: 'Whiskey', price: '$50', image: 'whiskey.jpg' },
      { id: 2, name: 'Wine', price: '$20', image: 'wine.jpg' },
      { id: 3, name: 'Beer', price: '$10', image: 'beer.jpg' },
    ]);
  }, []);

  return products;
};
