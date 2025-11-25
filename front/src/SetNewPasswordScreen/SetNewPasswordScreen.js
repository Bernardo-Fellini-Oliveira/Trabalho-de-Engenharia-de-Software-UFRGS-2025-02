import React, { useState } from 'react';
import './SetNewPasswordScreen.css'; // Importa os estilos específicos para esta tela

const SetNewPasswordScreen = () => {
  const [novaSenha, setNovaSenha] = useState('');
  const [confirmaNovaSenha, setConfirmaNovaSenha] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault(); // Impede o recarregamento da página

    if (novaSenha !== confirmaNovaSenha) {
      alert("Erro: As senhas não conferem!");
      return;
    }

    if (novaSenha.length < 6) { // Exemplo de validação simples
        alert("A nova senha deve ter pelo menos 6 caracteres.");
        return;
    }

    alert(`Nova senha cadastrada com sucesso: ${novaSenha}`);
    // Aqui você enviaria a nova senha para a API para atualização
    // e, em caso de sucesso, redirecionaria para a tela de login.
  };

  return (
    <div className="set-new-password-page-container">
      <div className="set-new-password-box">
        {/* Título principal no topo */}
        <h1 className="set-new-password-title">
          Controle de Mandatos
        </h1>
        
        <form className="set-new-password-form" onSubmit={handleSubmit}>
          
          {/* Campo Nova senha */}
          <label htmlFor="nova-senha">Nova senha</label>
          <input
            type="password"
            id="nova-senha"
            value={novaSenha}
            onChange={(e) => setNovaSenha(e.target.value)}
            required
          />

          {/* Campo Confirmar nova senha */}
          <label htmlFor="confirma-nova-senha">Confirmar nova senha</label>
          <input
            type="password"
            id="confirma-nova-senha"
            value={confirmaNovaSenha}
            onChange={(e) => setConfirmaNovaSenha(e.target.value)}
            required
          />

          {/* Botão de Cadastrar nova senha */}
          <button type="submit" className="set-new-password-button">
            Cadastrar nova senha
          </button>
        </form>
      </div>
    </div>
  );
};

export default SetNewPasswordScreen;
