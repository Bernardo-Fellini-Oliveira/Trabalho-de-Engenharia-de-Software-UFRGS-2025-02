import React, { useEffect, useState } from 'react';
import api from '../../services/api'; 
import './LogPage.css';

// === Interfaces ===
interface HistoricoEntry {
    id: number;
    created_at: string;
    tipo_operacao: string;
    entidade_alvo: string;
    operation: string;
}

interface HistoricoResponse {
    limite: number;
    deslocamento: number;
    total_itens: number;
    historico: HistoricoEntry[];
}

const LogPage: React.FC = () => {
    const [logs, setLogs] = useState<HistoricoEntry[]>([]);
    const [loading, setLoading] = useState<boolean>(false);

    // Carregar histórico
    const fetchHistorico = async () => {
        setLoading(true);
        try {
            // Solicitamos 50 itens para preencher bem a tabela
            const response = await api.get<HistoricoResponse>('/historico/?limite=50');
            setLogs(response.data.historico);
        } catch (error: any) {
            console.error('Erro ao buscar histórico:', error);
            alert('Erro ao carregar log: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistorico();
    }, []);

    // Formatação de data
    const formatDateTime = (isoString: string) => {
        if (!isoString) return '-';
        const date = new Date(isoString);
        return date.toLocaleString('pt-BR');
    };

    // Helper simples para cor da badge (opcional, baseado no texto)
    const getBadgeClass = (tipo: string) => {
        const t = tipo?.toLowerCase() || '';
        if (t.includes('associacao') || t.includes('associação')) return 'op-associacao';
        if (t.includes('create') || t.includes('criação')) return 'op-criacao';
        if (t.includes('delete') || t.includes('remoção')) return 'op-delecao';
        if (t.includes('update') || t.includes('atualização')) return 'op-atualizacao';
        return '';
    };

    return (
        <div className="log-page-wrapper">
            <div className="search-container">
                <h1 className="page-title">Histórico de Operações</h1>
                <span className="page-description">Registro de atividades e auditoria do sistema</span>

                <div className="table-container">
                    {loading ? (
                        <p style={{ textAlign: 'center', padding: '20px' }}>Carregando histórico...</p>
                    ) : logs.length === 0 ? (
                        <p style={{ textAlign: 'center', padding: '20px' }}>Nenhum registro encontrado.</p>
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th style={{width: '50px'}}>ID</th>
                                    <th style={{width: '180px'}}>Data/Hora</th>
                                    <th style={{width: '150px'}}>Tipo</th>
                                    <th style={{width: '150px'}}>Entidade</th>
                                    <th>Detalhes da Operação</th>
                                </tr>
                            </thead>
                            <tbody>
                                {logs.map((log) => (
                                    <tr key={log.id}>
                                        <td>{log.id}</td>
                                        <td>{formatDateTime(log.created_at)}</td>
                                        <td>
                                            <span className={`log-badge ${getBadgeClass(log.tipo_operacao)}`}>
                                                {log.tipo_operacao}
                                            </span>
                                        </td>
                                        <td><strong>{log.entidade_alvo}</strong></td>
                                        <td>{log.operation}</td>
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

export default LogPage;