import React, { useState } from 'react';
import './TeladeRegistro.css';
import { signUpRequest } from "../../services/auth"; // Importe a função de serviço

// Se você precisar redirecionar para uma página de login após o sucesso,
// Mantenha o useNavigate (opcional)
import { useNavigate } from 'react-router-dom'; 


const RegisterScreen = () => {
  const [usuario, setUsuario] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmaSenha, setConfirmaSenha] = useState('');
  const [loading, setLoading] = useState(false); // Mantido para UX
  
  const navigate = useNavigate(); // 💡 Mantido para redirecionar após o cadastro

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); 

    if (senha !== confirmaSenha) {
      alert("Erro: As senhas não conferem!");
      return;
    }
    
    if (!usuario || !senha || !confirmaSenha) {
        alert("Por favor, preencha todos os campos.");
        return;
    }

    setLoading(true); // Inicia o carregamento

    try {
      // 🚨 ÚNICA REQUISIÇÃO: Apenas registra o usuário.
      // Espera uma resposta de sucesso do backend (status 200/201).
      await signUpRequest(usuario, senha); 
      
      alert(`Usuário "${usuario}" criado com sucesso! Agora você pode fazer login.`);
      
      // 💡 Ação Pós-Cadastro: Redirecionar para a tela de Login
      navigate("/login"); 
      
      // OU: Limpar o formulário para adicionar outro usuário
      // setUsuario('');
      // setSenha('');
      // setConfirmaSenha('');

    } catch (error) {
      // O erro é capturado aqui (ex: nome de usuário já existe)
      console.error("Falha no registro:", error);
      alert("Erro ao criar usuário. Tente novamente ou verifique se o nome de usuário já está em uso.");
    } finally {
      setLoading(false); // Finaliza o carregamento
    }
  };

  return (
    <div className="register-page-container">
      <div className="register-box">
        <h1 className="register-title">Controle de Mandatos</h1>
        
        <form className="register-form" onSubmit={handleRegister}>
          
          <label htmlFor="usuario">Usuário</label>
          <input
            type="text"
            id="usuario"
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
            required
            disabled={loading}
          />

          <label htmlFor="senha">Senha</label>
          <input
            type="password"
            id="senha"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
            disabled={loading}
          />

          <label htmlFor="confirma-senha">Confirme a sua senha</label>
          <input
            type="password"
            id="confirma-senha"
            value={confirmaSenha}
            onChange={(e) => setConfirmaSenha(e.target.value)}
            required
            disabled={loading}
          />

          <button 
            type="submit" 
            className="register-button"
            disabled={loading} 
          >
            {loading ? 'Criando usuário...' : 'Criar Conta'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default RegisterScreen;