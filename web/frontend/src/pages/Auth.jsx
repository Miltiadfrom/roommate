import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../api';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = isLogin 
        ? await authAPI.login(phone, password)
        : await authAPI.register(phone, password);
      
      localStorage.setItem('userId', response.data.user_id.toString());
      navigate('/profile');
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isLogin ? 'Вход' : 'Регистрация'}</h2>
        
        {error && (
          <div style={{ color: 'red', marginBottom: '1rem', textAlign: 'center' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Телефон или логин</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
              placeholder="+7..."
            />
          </div>

          <div className="form-group">
            <label>Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />
          </div>

          <button type="submit" className="btn btn-block">
            {isLogin ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="auth-switch">
          {isLogin ? (
            <>
              Нет аккаунта?{' '}
              <button onClick={() => setIsLogin(false)}>
                Зарегистрироваться
              </button>
            </>
          ) : (
            <>
              Уже есть аккаунт?{' '}
              <button onClick={() => setIsLogin(true)}>
                Войти
              </button>
            </>
          )}
        </div>

        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <button 
            onClick={() => {
              localStorage.removeItem('userId');
              navigate('/');
            }}
            style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', textDecoration: 'underline' }}
          >
            Выйти из профиля
          </button>
        </div>
      </div>
    </div>
  );
}
