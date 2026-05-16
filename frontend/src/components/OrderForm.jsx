import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../css/order.css';

const OrderForm = () => {
    const [cartItems, setCartItems] = useState([]);
    const [cartTotal, setCartTotal] = useState(0);
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        phone: '',
        email: '',
        delivery_type: 'pickup',
        city: '',
        address: '',
        postal_code: '',
        payment_method: '',
        card_number: '',
        card_expiry: '',
        card_cvv: '',
        comment: '',
        agree: false,
    });

    // Загрузка корзины при старте
    useEffect(() => {
        axios.get('http://localhost:8000/api/cart/')
            .then(res => {
                setCartItems(res.data);
                const total = res.data.reduce((sum, item) => sum + item.total_price, 0);
                setCartTotal(total);
            })
            .catch(err => console.error(err));
    }, []);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!formData.agree) return alert("Нужно согласиться с правилами");

        axios.post('http://localhost:8000/api/order/', formData)
            .then(res => {
                alert('✅ Заказ оформлен!');
                // Перейти на страницу успеха
            })
            .catch(err => {
                alert('❌ Ошибка при оформлении');
            });
    };

    return (
        <div className="order-page">
            <section className="hero">
                <h1><span className="gradient-text">ОФОРМЛЕНИЕ ЗАКАЗА</span></h1>
            </section>

            <div className="order-container">
                {/* Отображение корзины */}
                <div className="cart-preview">
                    <h3>Ваш заказ:</h3>
                    {cartItems.length === 0 ? (
                        <p>Корзина пуста</p>
                    ) : (
                        <ul>
                            {cartItems.map(item => (
                                <li key={item.id}>
                                    {item.product.name} × {item.quantity} = {item.total_price} ₽
                                </li>
                            ))}
                            <li><strong>Итого: {cartTotal} ₽</strong></li>
                        </ul>
                    )}
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Имя</label>
                        <input
                            type="text"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Фамилия</label>
                        <input
                            type="text"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Телефон</label>
                        <input
                            type="tel"
                            name="phone"
                            value={formData.phone}
                            onChange={handleChange}
                            placeholder="+7 (999) 123-45-67"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Способ получения</label>
                        <div className="radio-group">
                            <label className="radio-option">
                                <input
                                    type="radio"
                                    name="delivery_type"
                                    value="pickup"
                                    checked={formData.delivery_type === 'pickup'}
                                    onChange={handleChange}
                                />
                                Самовывоз
                            </label>
                            <label className="radio-option">
                                <input
                                    type="radio"
                                    name="delivery_type"
                                    value="courier"
                                    onChange={handleChange}
                                />
                                Доставка курьером
                            </label>
                        </div>
                    </div>

                    {formData.delivery_type === 'courier' && (
                        <div className="delivery-fields">
                            <div className="form-group">
                                <label>Город</label>
                                <input
                                    type="text"
                                    name="city"
                                    value={formData.city}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label>Адрес</label>
                                <input
                                    type="text"
                                    name="address"
                                    value={formData.address}
                                    onChange={handleChange}
                                />
                            </div>
                        </div>
                    )}

                    <div className="form-group">
                        <label>Способ оплаты</label>
                        <select
                            name="payment_method"
                            value={formData.payment_method}
                            onChange={handleChange}
                            required
                        >
                            <option value="">Выберите способ</option>
                            <option value="cash">Наличными при получении</option>
                            <option value="card">Онлайн-оплата картой</option>
                        </select>
                    </div>

                    {formData.payment_method === 'card' && (
                        <div className="card-fields">
                            <div className="form-group">
                                <label>Номер карты</label>
                                <input
                                    type="text"
                                    name="card_number"
                                    placeholder="1234 5678 9012 3456"
                                    value={formData.card_number}
                                    onChange={handleChange}
                                    maxLength="19"
                                />
                            </div>
                            <div className="form-group">
                                <label>Срок</label>
                                <input
                                    type="text"
                                    name="card_expiry"
                                    placeholder="ММ/ГГ"
                                    value={formData.card_expiry}
                                    onChange={handleChange}
                                    maxLength="5"
                                />
                            </div>
                            <div className="form-group">
                                <label>CVV</label>
                                <input
                                    type="text"
                                    name="card_cvv"
                                    placeholder="123"
                                    value={formData.card_cvv}
                                    onChange={handleChange}
                                    maxLength="3"
                                />
                            </div>
                        </div>
                    )}

                    <div className="form-group">
                        <label>Комментарий</label>
                        <textarea
                            name="comment"
                            value={formData.comment}
                            onChange={handleChange}
                            rows="3"
                        />
                    </div>

                    <div className="agree-box">
                        <label>
                            <input
                                type="checkbox"
                                name="agree"
                                checked={formData.agree}
                                onChange={handleChange}
                            />
                            Я согласен с <a href="/rules" target="_blank">правилами</a>
                        </label>
                    </div>

                    <button type="submit" className="checkout-btn">
                        Подтвердить заказ
                    </button>
                </form>
            </div>
        </div>
    );
};

export default OrderForm;