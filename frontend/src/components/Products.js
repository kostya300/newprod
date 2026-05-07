// src/components/Products.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Products = () => {
    const [products, setProducts] = useState([]);

    useEffect(() => {
        const fetchProducts = async () => {
            try {
                const token = localStorage.getItem('access');
                const response = await axios.get('/api/products/', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                setProducts(response.data);
            } catch (err) {
                console.error(err);
            }
        };
        fetchProducts();
    }, []);

    return (
        <div>
            <h2>Товары</h2>
            {products.map(p => (
                <div key={p.id}>
                    <h3>{p.name}</h3>
                    <p>{p.price} ₽</p>
                </div>
            ))}
        </div>
    );
};

export default Products;