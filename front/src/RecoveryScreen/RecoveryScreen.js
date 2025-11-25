import React, { useState } from 'react';
import './RecoveryScreen.css'; // Importa os estilos específicos para esta tela

const RecoveryScreen = () => {
  const [usuario, setUsuario] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault(); // Impede o recarregamento da página
    alert(`Solicitação de recuperação para:\nUsuário: ${usuario}\nEmail: ${email}`);
    // Aqui você integraria com uma API para enviar o email de recuperação
    // ou redirecionaria para a próxima etapa da recuperação.
  };

  return (
    <div className="recovery-page-container">
      <div className="recovery-box">
        {/* Título principal no topo */}
        <h1 className="recovery-title">
          Controle de Mandatos
        </h1>
        
        <form className="recovery-form" onSubmit={handleSubmit}>
          
          {/* Campo Usuário */}
          <label htmlFor="usuario">Usuário</label>
          <input
            type="text"
            id="usuario"
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
            required
          />

          {/* Campo Email de recuperação */}
          <label htmlFor="email">Email de recuperação</label>
          <input
            type="email" // Tipo "email" para validação básica do navegador
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          {/* Botão de Confirmar envio */}
          <button type="submit" className="recovery-button">
            Confirmar envio
          </button>
        </form>
      </div>
    </div>
  );
};

export default RecoveryScreen;
