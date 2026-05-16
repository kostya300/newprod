// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import OrderForm from './components/OrderForm';

const rootElement = document.getElementById('order-form-root');
if (rootElement) {
  ReactDOM.createRoot(rootElement).render(<OrderForm />);
}