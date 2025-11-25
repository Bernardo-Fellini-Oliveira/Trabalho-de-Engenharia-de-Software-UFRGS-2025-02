import React, { useEffect, useState } from 'react';
import { loginRequest } from "../../services/auth";
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';

const LoginScreen = () => {
  const [usuario, setUsuario] = useState('');
  const [senha, setSenha] = useState('');

  const { login: authLogin, user, loading } = useAuth();
  const navigate = useNavigate();
    console.log("LoginScreen: user changed:", user);
    console.log("LoginScreen: loading state:", loading);
    
  useEffect(() => {

    if (!loading && user) {
      navigate("/");
    }
  }, [user, loading]);

  async function handleLogin(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      const token = await loginRequest(usuario, senha);
      await authLogin(token);
    } catch {
      alert("Usuário ou senha inválidos");
    }
  }

  if (loading) {
    return <div>Carregando...</div>;
  }

  if (user) {
    return null; // já vai redirecionar no useEffect
  }

  return (
    <div className="register-page-container">
      <div className="register-box">
        <h1 className="register-title">Controle de Mandatos</h1>

        <form className="register-form" onSubmit={handleLogin}>
          <label>Usuário</label>
          <input value={usuario} onChange={(e) => setUsuario(e.target.value)} />

          <label>Senha</label>
          <input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} />

          <button type="submit" className="register-button">Entrar</button>
        </form>
      </div>
    </div>
  );
};

export default LoginScreen;
