import React from 'react';
import './Header.css';

interface HeaderProps {
    role?: string;
}

const Header = ({ role }: HeaderProps) => {
  return (
    <header>
        <div id="header-container">
            <nav>
                <ul>
                    <li><a href="/">MENU PRINCIPAL</a></li>
                    <li><a href="/check">VERIFICAR ELEGIBILIDADE</a></li>
                    <li><a href="/search">CONSULTAR</a></li>

                    {role &&
                    <>
                    <li><a href="/insert">INSERIR</a></li>
                    <li><a href="/edit">EDITAR</a></li>
                    <li><a href="/log">HISTÓRICO</a></li>
                    </>
                    }

                    {role === 'admin' &&
                    <li><a href="/tickets">NOTIFICAÇÕES</a></li>
                    }
                </ul>
            </nav>
        </div>
        <div id="header-line"></div>
    </header>
  );
};

export default Header;