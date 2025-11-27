import React, { useEffect, useState } from 'react';
import api from '../../services/api'; 
import '../../../styles.css';
import '../SearchPage/SearchPage.css';
import './TicketsPage.css';
import Header from '../../components/Header';
import { useAuth } from '../../context/auth_context';

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

interface Notificacao {
    id: number;
    data_solicitacao: string;
    operation: string;
    status_aprovacao: string;
    data_aprovacao: string | null;
    tipo_operacao: string;
    entidade_alvo: string;
}

const NotificationsPage: React.FC = () => {
    const [notificacoes, setNotificacoes] = useState<Notificacao[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const { user } = useAuth();

    const fetchNotificacoes = async () => {
        setLoading(true);
        try {
            const response = await api.get('/notificacoes/');
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

    const formatDateTime = (isoString: string | null) => {
        if (!isoString) return '-';
        const date = new Date(isoString);
        return date.toLocaleString('pt-BR');
    };

    const handleApprove = async (id: number) => {
        if (!confirm('Deseja realmente APROVAR esta solicitação? Isso criará os dados no banco.')) return;

        try {
            await api.post(`/notificacoes/aprovar/${id}?approve=true`);
            alert('Solicitação aprovada com sucesso!');
            fetchNotificacoes(); 
        } catch (error: any) {
            console.error('Erro ao aprovar:', error);
            alert('Erro ao aprovar: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm('Deseja realmente EXCLUIR esta notificação do banco de dados?')) return;
        try {
            await api.post(`/notificacoes/recusar/${id}`);
            alert('Notificação excluída com sucesso!');
            fetchNotificacoes(); 
        } catch (error: any) {
            console.error('Erro ao excluir:', error);
            alert('Erro ao excluir: ' + (error.response?.data?.detail || error.message));
        }
    };

    const getStatusClass = (status: string) => {
        switch (status?.toLowerCase()) {
            case 'aprovado': return 'status-aprovado';
            case 'recusado': return 'status-recusado';
            default: return 'status-pendente';
        }
    };

    return (
        <div className="search-page">
            
            <Header role={user?.role} />

            <div className="search-container">
                <div className='topo'>
                    <h1>Central de Notificações</h1>
                    <p>Gerenciamento de solicitações e tickets pendentes</p>
                </div>

                <div className="tabela-container">
                    {loading ? (
                        <p style={{ textAlign: 'center', padding: '20px' }}>Carregando notificações...</p>
                    ) : notificacoes.length === 0 ? (
                        <p style={{ textAlign: 'center', padding: '20px' }}>Nenhuma notificação encontrada.</p>
                    ) : (
                        <table className="dado-tabela">
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
                                            <span className={`badge-status ${getStatusClass(notif.status_aprovacao)}`}>
                                                {notif.status_aprovacao}
                                            </span>
                                        </td>
                                        <td>{formatDateTime(notif.data_aprovacao)}</td>
                                        <td style={{ textAlign: 'center' }}>
                                            {notif.status_aprovacao === 'Pendente' ? (
                                                <>
                                                    <button 
                                                        className="botao-acao botao-aprovar" 
                                                        onClick={() => handleApprove(notif.id)} 
                                                        title="Aprovar Solicitação"
                                                    >
                                                        <IconCheck />
                                                    </button>
                                                    <button 
                                                        className="botao-acao botao-excluir" 
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