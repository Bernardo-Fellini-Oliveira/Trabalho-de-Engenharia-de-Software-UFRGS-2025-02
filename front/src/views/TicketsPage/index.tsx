import React, { useEffect, useState } from 'react';
import api from '../../services/api'; // Ajuste o caminho conforme sua estrutura
import '../../../styles.css'
import './TicketsPage.css';

// === Ícones SVG ===
const IconCheck = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="20 6 9 17 4 12"></polyline>
    </svg>
);

const IconX = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
);

// === Interfaces ===
interface Notificacao {
    id: number;
    data_solicitacao: string;
    operation: string;
    status_aprovacao: string;
    data_aprovacao: string | null;
    tipo_operacao: string;
    entidade_alvo: string;
    // dados_payload existe no backend mas não precisamos exibir na tabela principal
}

const NotificationsPage: React.FC = () => {
    const [notificacoes, setNotificacoes] = useState<Notificacao[]>([]);
    const [loading, setLoading] = useState<boolean>(false);

    // Carregar notificações ao montar o componente
    const fetchNotificacoes = async () => {
        setLoading(true);
        try {
            const response = await api.get('/notificacoes/');
            // Ordenar: Pendentes primeiro, depois por data mais recente
            const sorted = response.data.sort((a: Notificacao, b: Notificacao) => {
                if (a.status_aprovacao === 'Pendente' && b.status_aprovacao !== 'Pendente') return -1;
                if (a.status_aprovacao !== 'Pendente' && b.status_aprovacao === 'Pendente') return 1;
                return new Date(b.data_solicitacao).getTime() - new Date(a.data_solicitacao).getTime();
            });
            setNotificacoes(sorted);
        } catch (error: any) {
            console.error('Erro ao buscar notificações:', error);
            alert('Erro ao carregar notificações: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNotificacoes();
    }, []);

    // Função para formatar data e hora
    const formatDateTime = (isoString: string | null) => {
        if (!isoString) return '-';
        const date = new Date(isoString);
        return date.toLocaleString('pt-BR');
    };

    // Handler para Aprovar
    const handleApprove = async (id: number) => {
        if (!confirm('Deseja realmente APROVAR esta solicitação? Isso criará os dados no banco.')) return;

        try {
            // Chama o endpoint POST definido em notificacoes.py
            await api.post(`/notificacoes/aprovar/${id}?approve=true`);
            alert('Solicitação aprovada com sucesso!');
            fetchNotificacoes(); // Recarrega a lista
        } catch (error: any) {
            console.error('Erro ao aprovar:', error);
            alert('Erro ao aprovar: ' + (error.response?.data?.detail || error.message));
        }
    };

    // Handler para Deletar (Excluir do banco)
    const handleDelete = async (id: number) => {
        if (!confirm('Deseja realmente EXCLUIR esta notificação do banco de dados?')) return;

        // VERIFICAÇÃO: O backend fornecido NÃO possui um endpoint DELETE.
        // Conforme solicitado, emitimos um alerta.
        alert(`Funcionalidade de exclusão não implementada no backend (Endpoint DELETE /api/notificacoes/${id} não encontrado).`);
        
        /* // CÓDIGO FUTURO (Quando o backend tiver o endpoint):
        try {
            await api.delete(`/notificacoes/${id}`);
            alert('Notificação removida!');
            fetchNotificacoes();
        } catch (error) { ... }
        */
    };

    const getStatusClass = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'aprovado': return 'status-aprovado';
            case 'recusado': return 'status-recusado';
            default: return 'status-pendente';
        }
    };

    return (
        <div className="notifications-page-wrapper">
            <header>
                <div id="header-container">
                    <nav>
                        <ul>
                            <li><a href="/">MENU PRINCIPAL</a></li>
                            <li><a href="/check">VERIFICAR ELEGIBILIDADE</a></li>
                            <li><a href="/search">CONSULTAR</a></li>
                            <li><a href="/insert">INSERIR</a></li>
                            <li><a href="/edit">EDITAR</a></li>
                            <li><a href="/log">HISTÓRICO</a></li>
                            <li><a href="/tickets">NOTIFICAÇÕES</a></li>
                        </ul>
                    </nav>
                </div>
                <div id="header-line"></div>
            </header>
            <div className="search-container">
                <div className='topo'>
                    <h1>Central de Notificações</h1>
                    <p>Gerenciamento de solicitações e tickets pendentes</p>
                </div>

                <div className="table-container">
                    {loading ? (
                        <p style={{ textAlign: 'center', padding: '20px' }}>Carregando notificações...</p>
                    ) : notificacoes.length === 0 ? (
                        <p style={{ textAlign: 'center', padding: '20px' }}>Nenhuma notificação encontrada.</p>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th style={{width: '50px'}}>ID</th>
                                    <th>Data Solicitação</th>
                                    <th>Operação</th>
                                    <th>Status</th>
                                    <th>Data Aprovação</th>
                                    <th style={{width: '100px', textAlign: 'center'}}>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {notificacoes.map((notif) => (
                                    <tr key={notif.id}>
                                        <td>{notif.id}</td>
                                        <td>{formatDateTime(notif.data_solicitacao)}</td>
                                        <td>{notif.operation}</td>
                                        <td>
                                            <span className={`status-badge ${getStatusClass(notif.status_aprovacao)}`}>
                                                {notif.status_aprovacao}
                                            </span>
                                        </td>
                                        <td>{formatDateTime(notif.data_aprovacao)}</td>
                                        <td style={{ textAlign: 'center' }}>
                                            {/* Só exibe botões se estiver Pendente (ou conforme regra de negócio) */}
                                            {notif.status_aprovacao === 'Pendente' ? (
                                                <>
                                                    <button 
                                                        className="action-btn btn-approve" 
                                                        onClick={() => handleApprove(notif.id)} 
                                                        title="Aprovar Solicitação"
                                                    >
                                                        <IconCheck />
                                                    </button>
                                                    <button 
                                                        className="action-btn btn-delete" 
                                                        onClick={() => handleDelete(notif.id)} 
                                                        title="Excluir Notificação"
                                                    >
                                                        <IconX />
                                                    </button>
                                                </>
                                            ) : (
                                                <span style={{color: '#999', fontSize: '12px'}}>Processado</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
};

export default NotificationsPage;