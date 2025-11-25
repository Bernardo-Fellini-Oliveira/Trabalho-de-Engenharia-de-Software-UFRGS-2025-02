import React, { use } from 'react';
import './HomePage.css';
import { useNavigate } from 'react-router';
import LogoutButton from '../../components/LogoutButton';
import { useAuth } from '../../context/auth_context';

// === Ícones SVG Inline para ilustrar os botões ===
const IconCheck = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
);

const IconPlus = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
        <line x1="12" y1="8" x2="12" y2="16"></line>
        <line x1="8" y1="12" x2="16" y2="12"></line>
    </svg>
);

const IconSearch = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
    </svg>
);

const IconEdit = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
    </svg>
);

const IconBell = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
    </svg>
);

const IconHistory = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"></circle>
        <polyline points="12 6 12 12 16 14"></polyline>
    </svg>
);

const IconLogin = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
        <polyline points="10 17 15 12 10 7"></polyline>
        <line x1="15" y1="12" x2="3" y2="12"></line>
    </svg>
);

const IconSignUp = () => (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
        <circle cx="8.5" cy="7" r="4"></circle>
        <line x1="20" y1="8" x2="20" y2="14"></line>
        <line x1="23" y1="11" x2="17" y2="11"></line>
    </svg>
);

function HomePage() {
    const navigate = useNavigate();

    const handleNavigation = (pageName: string) => {
        
        // Exemplo de como seria a navegação real:
        navigate(pageName);
    };

    const {isAuthenticated, user} = useAuth(); 

    return (
        <div className="home-page-wrapper">
            <h1 className="home-title">Gestão de Mandatos e Órgãos</h1>
            <p className="home-subtitle">Selecione uma opção para começar</p>

            <div className="menu-grid">
                
                <div className="menu-card" onClick={() => handleNavigation("/check")}>
                    <div className="card-icon"><IconCheck /></div>
                    <div className="card-text">Verificar Elegibilidade</div>
                </div>

                <div className="menu-card" onClick={() => handleNavigation("/search")}>
                                    <div className="card-icon"><IconSearch /></div>
                                    <div className="card-text">Consultar Dados</div>
                </div>

                <div className="menu-card" onClick={() => handleNavigation("/login")}>
                    <div className="card-icon"><IconLogin /></div>
                    <div className="card-text">Login</div>
                </div>
            { isAuthenticated && user && 
                <>
                <div className="menu-card" onClick={() => handleNavigation("/insert")}>
                    <div className="card-icon"><IconPlus /></div>
                    <div className="card-text">Inserir Dados</div>
                </div>
        
                
       
                <div className="menu-card" onClick={() => handleNavigation("/edit")}>
                    <div className="card-icon"><IconEdit /></div>
                    <div className="card-text">Editar Dados</div>
                </div>
        
                <div className="menu-card" onClick={() => handleNavigation("/tickets")}>
                    <div className="card-icon"><IconBell /></div>
                    <div className="card-text">Notificações</div>
                </div>

                
       
                <div className="menu-card" onClick={() => handleNavigation("/log")}>
                    <div className="card-icon"><IconHistory /></div>
                    <div className="card-text">Histórico de Modificações</div>
                </div>
                </>
            }
            { isAuthenticated && user && user.role == 'superadmin' &&
                <div className="menu-card" onClick={() => handleNavigation("/")}>
                    <div className="card-icon"><IconSignUp/></div>
                    <div className="card-text">Sign Up</div>
                </div>
            }    
            </div>
            { isAuthenticated && user &&
            <LogoutButton logoutText="Sair" />
            }
        </div>
    );
}

export default HomePage;