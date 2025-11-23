import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import './EditPage.css';

// === Ícones SVG Inline ===
const IconEdit = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>;
const IconSave = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>;
const IconCancel = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>;
const IconTrash = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>;
const IconFinish = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17.5 19c0-1.7-1.3-3-3-3h-5c-1.7 0-3 1.3-3 3"/><circle cx="12" cy="5" r="3"/><path d="M12 8v8"/></svg>;

// === Interfaces ===
type Tab = 'pessoa' | 'orgao' | 'cargo' | 'ocupacao';

interface Pessoa { id_pessoa: number; nome: string; ativo: number | boolean; }
interface Orgao { id_orgao: number; nome: string; ativo: number | boolean; }

// CORREÇÃO 1: Adicionado 'exclusivo' à interface Cargo
interface Cargo { 
    id_cargo: number; 
    nome: string; 
    id_orgao: number; 
    ativo: number | boolean; 
    exclusivo: number | boolean; 
}

interface Ocupacao {
    id_ocupacao: number;
    id_pessoa: number;
    id_cargo: number;
    data_inicio: string;
    data_fim: string | null;
    mandato: number;
    // Campos auxiliares para exibição
    nome_pessoa?: string;
    nome_cargo?: string;
    nome_orgao?: string;
    id_orgao?: number;
}

function EditPage() {
    // Estados Principais
    const [activeTab, setActiveTab] = useState<Tab>('pessoa');
    const [filtroBusca, setFiltroBusca] = useState("");
    
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<any[]>([]);

    // Dados Auxiliares (Combobox)
    const [auxPessoas, setAuxPessoas] = useState<Pessoa[]>([]);
    const [auxOrgaos, setAuxOrgaos] = useState<Orgao[]>([]);
    const [auxCargos, setAuxCargos] = useState<Cargo[]>([]);

    // Controle de Edição e Seleção
    const [editingId, setEditingId] = useState<number | null>(null);
    const [editForm, setEditForm] = useState<any>({});
    const [selectedIds, setSelectedIds] = useState<number[]>([]);

    // Modal de Finalização
    const [showModal, setShowModal] = useState(false);
    const [finishData, setFinishData] = useState({ id_ocupacao: 0, data_fim: '', data_inicio_sub: '', data_fim_sub: '', definitiva: false });

    // === FETCH DATA ===
    const fetchAux = async () => {
        try {
            const [p, o, c] = await Promise.all([
                api.get('/pessoa/'),
                api.get('/orgao/'),
                api.get('/cargo/')
            ]);
            setAuxPessoas(p.data);
            setAuxOrgaos(o.data);
            setAuxCargos(c.data);
        } catch (err) { console.error("Erro ao carregar auxiliares", err); }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            let endpoint = '';
            if (activeTab === 'pessoa') endpoint = '/pessoa/';
            if (activeTab === 'orgao') endpoint = '/orgao/';
            if (activeTab === 'cargo') endpoint = '/cargo/';
            if (activeTab === 'ocupacao') endpoint = '/ocupacao/';

            const res = await api.get(endpoint);
            
            if (activeTab === 'ocupacao') {
                const enriched = res.data.map((o: Ocupacao) => {
                    const cargo = auxCargos.find(c => c.id_cargo === o.id_cargo);
                    return {
                        ...o,
                        nome_pessoa: auxPessoas.find(p => p.id_pessoa === o.id_pessoa)?.nome || `ID ${o.id_pessoa}`,
                        nome_cargo: cargo?.nome || `ID ${o.id_cargo}`,
                        nome_orgao: auxOrgaos.find(org => org.id_orgao === cargo?.id_orgao)?.nome,
                        id_orgao: cargo?.id_orgao
                    };
                });
                setData(enriched);
            } else {
                setData(res.data);
            }
        } catch (err) {
            console.error(err);
            alert("Erro ao carregar dados.");
        } finally {
            setLoading(false);
            setEditingId(null);
            setSelectedIds([]);
        }
    };

    useEffect(() => { fetchAux(); }, []);
    useEffect(() => { if(auxCargos.length > 0 || activeTab !== 'ocupacao') fetchData(); }, [activeTab, auxCargos]);

    const filteredData = data.filter(item => {
        if (!filtroBusca) return true;
        const term = filtroBusca.toLowerCase();
        
        if (activeTab === 'pessoa' || activeTab === 'orgao' || activeTab === 'cargo') {
            return item.nome?.toLowerCase().includes(term);
        }
        if (activeTab === 'ocupacao') {
            return (item.nome_pessoa?.toLowerCase().includes(term) ||
                    item.nome_cargo?.toLowerCase().includes(term));
        }
        return true;
    });

    // === HANDLERS ===

    const toggleSelect = (id: number) => {
        setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
    };

    const toggleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.checked) {
            const idKey = activeTab === 'ocupacao' ? 'id_ocupacao' : `id_${activeTab}`;
            setSelectedIds(filteredData.map(i => i[idKey]));
        } else {
            setSelectedIds([]);
        }
    };

    const startEdit = (row: any) => {
        const idKey = activeTab === 'ocupacao' ? 'id_ocupacao' : `id_${activeTab}`;
        setEditingId(row[idKey]);
        setEditForm({ ...row });
    };

    const saveEdit = async () => {
        try {
            let url = '';
            if (activeTab === 'ocupacao') url = `/ocupacao/alterar/${editingId}`;
            else url = `/${activeTab}/${editingId}`;

            await api.put(url, editForm);
            alert("Atualizado com sucesso!");
            fetchData();
        } catch (err: any) {
            alert("Erro ao salvar: " + (err.response?.data?.detail || err.message));
        }
    };

    const deleteBatch = async () => {
        if (!confirm(`Deseja excluir ${selectedIds.length} itens?`)) return;

        try {
            if (activeTab === 'ocupacao') {
                await api.delete('/ocupacao/delete_list/', { data: selectedIds });
            } else {
                const params = new URLSearchParams();
                const paramName = activeTab === 'pessoa' ? 'ids_pessoas' : (activeTab === 'orgao' ? 'ids_orgaos' : 'ids_cargo');
                selectedIds.forEach(id => params.append(paramName, id.toString()));
                
                let url = activeTab === 'cargo' ? '/cargo/delete/lista/' : `/${activeTab}/delete/lote/`;
                await api.delete(`${url}?${params.toString()}`);
            }
            alert("Itens excluídos!");
            fetchData();
        } catch (err: any) {
            alert("Erro ao excluir: " + (err.response?.data?.detail || err.message));
        }
    };

    const openFinishModal = (row: Ocupacao) => {
        setFinishData({
            id_ocupacao: row.id_ocupacao,
            data_fim: new Date().toISOString().split('T')[0],
            data_inicio_sub: '',
            data_fim_sub: '',
            definitiva: false
        });
        setShowModal(true);
    };

    const confirmFinish = async () => {
        try {
            const payload = {
                definitiva: finishData.definitiva,
                data_fim: finishData.data_fim,
                data_inicio_substitutos: finishData.data_inicio_sub || null,
                data_fim_substitutos: finishData.data_fim_sub || null
            };
            await api.put(`/ocupacao/finalizar/${finishData.id_ocupacao}`, payload);
            alert("Finalizado com sucesso!");
            setShowModal(false);
            fetchData();
        } catch (err: any) {
            alert("Erro ao finalizar: " + (err.response?.data?.detail || err.message));
        }
    };

    // === RENDER TABLE ===
    const renderTable = () => {
        if (loading) return <p style={{textAlign:'center', padding: 20}}>Carregando...</p>;
        if (!filteredData.length) return <p style={{textAlign:'center', padding: 20}}>Sem dados.</p>;

        return (
            <table className="data-table">
                <thead>
                    <tr>
                        <th style={{width: 40}}>
                            <input type="checkbox" onChange={toggleSelectAll} checked={filteredData.length > 0 && selectedIds.length === filteredData.length} />
                        </th>
                        
                        {activeTab === 'pessoa' && <><th>ID</th><th>Nome</th><th>Ativo</th></>}
                        {activeTab === 'orgao' && <><th>ID</th><th>Nome</th><th>Ativo</th></>}
                        {/* CORREÇÃO 3: Adicionada coluna Exclusivo */}
                        {activeTab === 'cargo' && <><th>ID</th><th>Nome</th><th>Órgão</th><th>Ativo</th><th>Exclusivo</th></>}
                        {activeTab === 'ocupacao' && <><th>Pessoa</th><th>Cargo</th><th>Início</th><th>Fim</th></>}
                        
                        <th style={{width: 100}}>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredData.map(row => {
                        const idKey = activeTab === 'ocupacao' ? 'id_ocupacao' : `id_${activeTab}`;
                        const id = row[idKey];
                        const isEditing = editingId === id;

                        return (
                            <tr key={id}>
                                <td>
                                    <input type="checkbox" checked={selectedIds.includes(id)} onChange={() => toggleSelect(id)} />
                                </td>

                                {/* === PESSOA === */}
                                {activeTab === 'pessoa' && (
                                    <>
                                        <td>{row.id_pessoa}</td>
                                        <td>
                                            {isEditing ?
                                                <input className="edit-input" value={editForm.nome} onChange={e => setEditForm({...editForm, nome: e.target.value})} />
                                                : row.nome}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <select className="edit-input" value={editForm.ativo ? 1 : 0} onChange={e => setEditForm({...editForm, ativo: parseInt(e.target.value)})}>
                                                    <option value={1}>Sim</option><option value={0}>Não</option>
                                                </select>
                                                : (row.ativo ? 'Sim' : 'Não')}
                                        </td>
                                    </>
                                )}

                                {/* === ORGAO === */}
                                {activeTab === 'orgao' && (
                                    <>
                                        <td>{row.id_orgao}</td>
                                        <td>
                                            {isEditing ?
                                                <input className="edit-input" value={editForm.nome} onChange={e => setEditForm({...editForm, nome: e.target.value})} />
                                                : row.nome}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <select className="edit-input" value={editForm.ativo ? 1 : 0} onChange={e => setEditForm({...editForm, ativo: parseInt(e.target.value)})}>
                                                    <option value={1}>Sim</option><option value={0}>Não</option>
                                                </select>
                                                : (row.ativo ? 'Sim' : 'Não')}
                                        </td>
                                    </>
                                )}

                                {/* === CARGO === */}
                                {activeTab === 'cargo' && (
                                    <>
                                        <td>{row.id_cargo}</td>
                                        <td>
                                            {isEditing ?
                                                <input className="edit-input" value={editForm.nome} onChange={e => setEditForm({...editForm, nome: e.target.value})} />
                                                : row.nome}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <select className="edit-input" value={editForm.id_orgao} onChange={e => setEditForm({...editForm, id_orgao: Number(e.target.value)})}>
                                                    {auxOrgaos.map(o => <option key={o.id_orgao} value={o.id_orgao}>{o.nome}</option>)}
                                                </select>
                                                : row.orgao || auxOrgaos.find((o:any) => o.id_orgao === row.id_orgao)?.nome}
                                        </td>
                                        {/* CORREÇÃO 2: Conversão explícita para Inteiro (1 ou 0) ao editar Ativo */}
                                        <td>
                                            {isEditing ?
                                                <select className="edit-input" value={editForm.ativo ? 1 : 0} onChange={e => setEditForm({...editForm, ativo: parseInt(e.target.value)})}>
                                                    <option value={1}>Sim</option><option value={0}>Não</option>
                                                </select>
                                                : (row.ativo ? 'Sim' : 'Não')}
                                        </td>
                                        {/* CORREÇÃO 3: Célula para editar/visualizar Exclusivo */}
                                        <td>
                                            {isEditing ?
                                                <select className="edit-input" value={editForm.exclusivo ? 1 : 0} onChange={e => setEditForm({...editForm, exclusivo: parseInt(e.target.value)})}>
                                                    <option value={1}>Sim</option><option value={0}>Não</option>
                                                </select>
                                                : (row.exclusivo ? 'Sim' : 'Não')}
                                        </td>
                                    </>
                                )}

                                {/* === OCUPACAO === */}
                                {activeTab === 'ocupacao' && (
                                    <>
                                        <td>
                                            {isEditing ?
                                                <select className="edit-input" value={editForm.id_pessoa} onChange={e => setEditForm({...editForm, id_pessoa: Number(e.target.value)})}>
                                                    {auxPessoas.map(p => <option key={p.id_pessoa} value={p.id_pessoa}>{p.nome}</option>)}
                                                </select>
                                                : row.nome_pessoa}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <select className="edit-input" value={editForm.id_cargo} onChange={e => setEditForm({...editForm, id_cargo: Number(e.target.value)})}>
                                                    {auxCargos.map(c => <option key={c.id_cargo} value={c.id_cargo}>{c.nome}</option>)}
                                                </select>
                                                : row.nome_cargo}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <input type="date" className="edit-input" value={editForm.data_inicio} onChange={e => setEditForm({...editForm, data_inicio: e.target.value})} />
                                                : row.data_inicio}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <input type="date" className="edit-input" value={editForm.data_fim || ''} onChange={e => setEditForm({...editForm, data_fim: e.target.value})} />
                                                : (row.data_fim || '-')}
                                        </td>
                                    </>
                                )}

                                <td className="action-cell">
                                    {isEditing ? (
                                        <>
                                            <button className="icon-btn save" onClick={saveEdit} title="Salvar"><IconSave/></button>
                                            <button className="icon-btn cancel" onClick={() => setEditingId(null)} title="Cancelar"><IconCancel/></button>
                                        </>
                                    ) : (
                                        <>
                                            <button className="icon-btn edit" onClick={() => startEdit(row)} title="Editar"><IconEdit/></button>
                                            {activeTab === 'ocupacao' && !row.data_fim && (
                                                <button className="icon-btn finish" onClick={() => openFinishModal(row)} title="Finalizar/Substituir">
                                                    <IconFinish/>
                                                </button>
                                            )}
                                        </>
                                    )}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        );
    };

    return (
        <div className="edit-page-wrapper">
            <div className="search-container">
                <h1 className="search-title">Edição de Dados</h1>
                <p className='search-description'>Editando os dados</p>
                <div className="filter-card">
                    <div className="filter-row">
                        <div className="filter-group" style={{flex: 2}}>
                            <label>Busca Textual</label>
                            <input
                                className="filter-input"
                                type="text"
                                placeholder={`Buscar em ${activeTab}...`}
                                value={filtroBusca}
                                onChange={e => setFiltroBusca(e.target.value)}
                            />
                        </div>

                        <div className="filter-group">
                            <label>Tabela (Tipo de Dado)</label>
                            <select className="filter-select" value={activeTab} onChange={(e) => setActiveTab(e.target.value as Tab)}>
                                <option value="pessoa">Pessoas</option>
                                <option value="orgao">Órgãos</option>
                                <option value="cargo">Cargos</option>
                                <option value="ocupacao">Ocupações</option>
                            </select>
                        </div>

                        <div className="button-group">
                            <button className="btn btn-danger" onClick={deleteBatch} disabled={selectedIds.length === 0}>
                                <IconTrash/> Excluir Selecionados ({selectedIds.length})
                            </button>
                        </div>
                    </div>
                </div>

                <div className="table-container">
                    {renderTable()}
                </div>

                {showModal && (
                    <div className="modal-overlay">
                        <div className="modal-content">
                            <div className="modal-header">Finalizar Mandato</div>
                            
                            <div className="filter-group" style={{marginBottom: 15}}>
                                <label>Fim do Mandato Atual</label>
                                <input type="date" className="edit-input" value={finishData.data_fim} onChange={e => setFinishData({...finishData, data_fim: e.target.value})} />
                            </div>

                            <div className="filter-group" style={{marginBottom: 15}}>
                                <label>
                                    <input type="checkbox" checked={finishData.definitiva} onChange={e => setFinishData({...finishData, definitiva: e.target.checked})} />
                                    &nbsp; Saída Definitiva (Sem substitutos)
                                </label>
                            </div>

                            {!finishData.definitiva && (
                                <div style={{background: '#f8f9fa', padding: 10, borderRadius: 4}}>
                                    <p style={{fontSize: 12, fontWeight: 'bold', marginBottom: 10}}>Dados do Substituto</p>
                                    <div className="filter-group" style={{marginBottom: 10}}>
                                        <label>Início Substituto</label>
                                        <input type="date" className="edit-input" value={finishData.data_inicio_sub} onChange={e => setFinishData({...finishData, data_inicio_sub: e.target.value})} />
                                    </div>
                                    <div className="filter-group">
                                        <label>Fim Substituto (Opcional)</label>
                                        <input type="date" className="edit-input" value={finishData.data_fim_sub} onChange={e => setFinishData({...finishData, data_fim_sub: e.target.value})} />
                                    </div>
                                </div>
                            )}

                            <div className="modal-actions">
                                <button className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancelar</button>
                                <button className="btn btn-primary" onClick={confirmFinish}>Confirmar</button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default EditPage;