// src/components/Login.js
import React, { useState } from 'react';
import axios from 'axios';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/api/token/', {
                username,
                password
            });
            const { access, refresh } = response.data;

            // Сохраняем токены
            localStorage.setItem('access', access);
            localStorage.setItem('refresh', refresh);

            alert('Успешный вход!');
            window.location.href = '/products';  // или куда нужно
        } catch (err) {
            setError('Неверный логин или пароль');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>Вход</h2>
            {error && <p style={{color: 'red'}}>{error}</p>}
            <input
                type="text"
                placeholder="Логин"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
            />
            <input
                type="password"
                placeholder="Пароль"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
            />
            <button type="submit">Войти</button>
        </form>
    );
};

export default Login;