import React, { use, useState } from 'react';
import '../../../styles.css'
import './HomePage.css';
import { useNavigate } from 'react-router';
import LogoutButton from '../../components/LogoutButton';
import { useAuth } from '../../context/auth_context';
import api from '../../services/api';



function HomePage() {
    const navigate = useNavigate();

    const handleNavigation = (pageName: string) => {
        
        // Exemplo de como seria a navegação real:
        navigate(pageName);
    };

    const {isAuthenticated, user} = useAuth(); 

    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [deletePassword, setDeletePassword] = useState("");
    const [deleteLoading, setDeleteLoading] = useState(false);

    const deleteAccount = async () => {
        try {
            setDeleteLoading(true);

            const resp = await api.delete("/auth/delete_account", {
                data: { password: deletePassword }
            });

            alert("Conta excluída com sucesso!");

            localStorage.removeItem("access_token");

            window.location.href = "/login";

        } catch (err: any) {
            alert(err.response?.data?.detail || "Erro ao excluir conta");
            console.log(err);
        } finally {
            setDeleteLoading(false);
        }
    };


    const renderDeleteModal = () => {
        return (
            <div className="modal-overlay">
                <div className="modal-content">
                    
                    <div className="modal-header">
                        Excluir Conta
                    </div>

                    <p className="modal-text">
                        Tem certeza de que deseja prosseguir com a exclusão da sua conta?<br />
                        <strong className="modal-strong">
                            Esta ação é permanente e não poderá ser desfeita.
                        </strong>
                    </p>

                    {/* Campo de confirmação */}
                    <div className="filter-group">
                        <label style={{ fontWeight: 600, display: "block", marginBottom: 6 }}>
                            Confirme sua senha
                        </label>
                        <input
                            type="password"
                            className="edit-input"
                            placeholder="Digite sua senha"
                            value={deletePassword}
                            onChange={e => setDeletePassword(e.target.value)}
                            style={{ width: "100%" }}
                        />
                    </div>

                    <div className="modal-actions">
                        <button
                            className="btn btn-secondary"
                            onClick={() => {
                                setDeletePassword("");
                                setShowDeleteModal(false);
                            }}
                            style={{ padding: "8px 16px" }}
                        >
                            Cancelar
                        </button>

                        <button
                            className="btn btn-danger"
                            onClick={deleteAccount}
                            disabled={deleteLoading || deletePassword.length === 0}
                            style={{ padding: "8px 20px" }}
                        >
                            {deleteLoading ? "Excluindo..." : "Excluir Conta"}
                        </button>
                    </div>

                </div>
            </div>
        );
    };


    return (
        <div className="home-page">
            { showDeleteModal && renderDeleteModal() }
            <div className='topo'>
                <h1>Gestão de Mandatos e Órgãos</h1>
                <p>Selecione uma opção para começar</p>
            </div>

            <div className="menu-grid">
                
                <div className="menu-card" onClick={() => handleNavigation("/check")}>
                    <div className="card-text">Verificar Elegibilidade</div>
                </div>

                <div className="menu-card" onClick={() => handleNavigation("/search")}>
                    <div className="card-text">Consultar Dados</div>
                </div>

            { !isAuthenticated &&
                <div className="menu-card" onClick={() => handleNavigation("/login")}>
                    <div className="card-text">Login</div>
                </div>
            }
            { isAuthenticated && user && 
                <>
                <div className="menu-card" onClick={() => handleNavigation("/insert")}>
                    <div className="card-text">Inserir Dados</div>
                </div>
        
                
       
                <div className="menu-card" onClick={() => handleNavigation("/edit")}>
                    <div className="card-text">Editar Dados</div>
                </div>
        


            
                <div className="menu-card" onClick={() => handleNavigation("/log")}>
                    <div className="card-text">Histórico de Modificações</div>
                </div>
                </>
            }
            { isAuthenticated && user && user.role == 'admin' &&

                <>
                <div className="menu-card" onClick={() => handleNavigation("/signup")}>
                    <div className="card-text">Sign Up</div>
                </div>

                <div className="menu-card" onClick={() => handleNavigation("/tickets")}>
                    <div className="card-text">Notificações</div>
                </div>
                </>
            }    
            </div>
            { isAuthenticated && user &&
                <LogoutButton logoutText="Sair" />
            }

            { isAuthenticated && user && user.role !== 'admin' &&
                <button className="btn btn-danger" onClick={() => setShowDeleteModal(true)} style={{backgroundColor: "rgb(154, 0, 0)", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px", cursor: "pointer", marginTop: "20px", width: "200px"}}>
                    Excluir minha conta
                </button>
            }
            
        </div>
    );
}

export default HomePage;