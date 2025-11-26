import React, { use } from 'react';
import '../../../styles.css'
import './HomePage.css';
import { useNavigate } from 'react-router';
import LogoutButton from '../../components/LogoutButton';
import { useAuth } from '../../context/auth_context';



function HomePage() {
    const navigate = useNavigate();

    const handleNavigation = (pageName: string) => {
        
        // Exemplo de como seria a navegação real:
        navigate(pageName);
    };

    const {isAuthenticated, user} = useAuth(); 
    return (
        <div className="home-page">
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
        </div>
    );
}

export default HomePage;