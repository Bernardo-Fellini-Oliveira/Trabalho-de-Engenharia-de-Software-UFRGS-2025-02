import React, { useState } from 'react';
import './TeladeRegistro.css'; // Importa os estilos específicos para esta tela

const RegisterScreen = () => {
  const [usuario, setUsuario] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmaSenha, setConfirmaSenha] = useState('');

  const handleRegister = (e: { preventDefault: () => void; }) => {
    e.preventDefault(); // Impede o recarregamento da página

    if (senha !== confirmaSenha) {
      alert("Erro: As senhas não conferem!");
      return;
    }

    alert(`Tentativa de Registro:\nUsuário: ${usuario}\nSenha: ${senha}`);
    // Aqui você colocaria a lógica real de registro (fetch, validação, etc.)
  };

  return (
    <div className="register-page-container">
      <div className="register-box">
        {/* Título principal no topo */}
        <h1 className="register-title">
          Controle de Mandatos
        </h1>
        
        <form className="register-form" onSubmit={handleRegister}>
          
          {/* Campo Usuário */}
          <label htmlFor="usuario">Usuário</label>
          <input
            type="text"
            id="usuario"
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
            required
          />

          {/* Campo Senha */}
          <label htmlFor="senha">Senha</label>
          <input
            type="password"
            id="senha"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            required
          />

          {/* Novo Campo: Confirme a sua senha */}
          <label htmlFor="confirma-senha">Confirme a sua senha</label>
          <input
            type="password"
            id="confirma-senha"
            value={confirmaSenha}
            onChange={(e) => setConfirmaSenha(e.target.value)}
            required
          />

          {/* Botão de Registrar */}
          <button type="submit" className="register-button">
            Registrar
          </button>
        </form>
      </div>
    </div>
  );
};

export default RegisterScreen;
