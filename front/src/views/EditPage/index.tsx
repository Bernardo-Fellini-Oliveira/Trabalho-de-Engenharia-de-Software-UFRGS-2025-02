import React, { use, useEffect, useState } from 'react';
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
    orgao: string;
    substituto_para?: number;
}

interface Ocupacao {
    id_ocupacao: number;
    id_pessoa: number;
    id_cargo: number;
    data_inicio: string;
    data_fim: string | null;
    mandato: number;
    // Campos auxiliares para exibição
    pessoa?: string;
    cargo?: string;
    orgao?: string;
    id_orgao?: number;
}

function EditPage() {
    // Estados Principais
    const [activeTab, setActiveTab] = useState<Tab>('pessoa');
    const [filtroBusca, setFiltroBusca] = useState("");
    
    const [filtroBuscaComplexa, setFiltroBuscaComplexa] = useState("");

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
    const [deleting, setDeleting] = useState(false);

    // Modal de Finalização
    const [showModal, setShowModal] = useState(false);
    const [finishData, setFinishData] = useState({nome_substituto: '', id_ocupacao: 0, data_fim: '', data_inicio_sub: '', data_fim_sub: '', definitiva: true})//pessoa_substituta: '', cargo_substituto: '',  });



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
                        pessoa: auxPessoas.find(p => p.id_pessoa === o.id_pessoa)?.nome || `ID ${o.id_pessoa}`,
                        cargo: cargo?.nome || `ID ${o.id_cargo}`,
                        orgao: auxOrgaos.find(org => org.id_orgao === cargo?.id_orgao)?.nome,
                        id_orgao: cargo?.id_orgao
                    };
                });
                setData(enriched);

                console.log("Ocupações carregadas:", enriched);
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
    useEffect(() => { fetchData(); }, [activeTab, auxPessoas, auxOrgaos, auxCargos]);

    console.log("Data:", data);
    const filteredData = data.filter(item => {
        console.log("Filtering item:", item);
        if (!filtroBusca) return true;
        const term = filtroBusca.toLowerCase();
        
        if (activeTab === 'pessoa' || activeTab === 'orgao' || activeTab === 'cargo') {
            return item.nome?.toLowerCase().includes(term);
        }
        if (activeTab === 'ocupacao') {
            return (item.pessoa?.toLowerCase().includes(term) ||
                    item.cargo?.toLowerCase().includes(term));
        }
        return true;
    });

    // === HANDLERS ===
    const handleClickRow = (id: number) => {
        console.log("Clicou na linha:", id, "Deletando?", deleting);
        if (deleting) {
            toggleSelect(id);
        }
    };


    const toggleSelect = (id: number) => {
        setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
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
            fetchAux();
            //fetchData();
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
            fetchAux();
        } catch (err: any) {
            alert("Erro ao excluir: " + (err.response?.data?.detail || err.message));
        }
    };

    const openFinishModal = async (idOcupacao: number) => {
        setFinishData({ 
            id_ocupacao: idOcupacao,
            definitiva: true,
            data_fim: "",
            data_inicio_sub: "",
            data_fim_sub: "",
            nome_substituto: ""
        });

        setShowModal(true);

        try {
            const resp = await api.get(`/ocupacao/substituto_proximo/${idOcupacao}`);
            console.log("Substituto próximo:", resp.data);
            
            if (resp.data) {
                setFinishData(prev => ({
                    ...prev,
                    data_inicio_sub: resp.data.data_inicio_sugerida || "",
                    data_fim_sub: resp.data.data_fim_sugerida || "",
                    nome_substituto: resp.data.nome_substituto || ""
                }));
            }
        } catch (err) {
            console.warn("Sem substituto próximo.");
        }
    };


    const confirmFinish = async () => {

        if(!finishData.data_fim) {
            alert("Por favor, preencha a data de fim da ocupação.");
            return;
        }

        if(!finishData.definitiva && !finishData.data_inicio_sub) {
            alert("Por favor, preencha a data de início do substituto ou marque como finalização definitiva.");
            return;
        }
        
        try {
            const payload = {
                definitiva: finishData.definitiva,
                data_fim: finishData.data_fim,
                data_inicio_substitutos: finishData.data_inicio_sub || null,
                data_fim_substitutos: finishData.data_fim_sub || null
            };

            await api.put(
                `/ocupacao/finalizar/${finishData.id_ocupacao}`,
                payload
            );

            alert("Finalizado com sucesso!");
            setShowModal(false);
            fetchAux();

        } catch (err: any) {
            alert("Erro ao finalizar: " + (err.response?.data?.detail || err.message));
        }
    };


    const fetchFilteredOcupacoes = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/busca?tipo=flat&busca=${filtroBuscaComplexa}`);
            setData(res.data);
            console.log(res.data);
        } catch (err) {
            console.error(err);
            alert("Erro ao carregar dados.");
        } finally {
            setLoading(false);
        }
    };

    console.log("Filtered Data:", filteredData);


    // === RENDER TABLE ===
    const renderTable = () => {
        if (loading) return <p style={{textAlign:'center', padding: 20}}>Carregando...</p>;
        if (!filteredData.length) return <p style={{textAlign:'center', padding: 20}}>Sem dados.</p>;

        return (
            <table className="data-table">
                <thead>
                    <tr>

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
                            <tr key={id} onClick={() => handleClickRow(id)} style={{backgroundColor: selectedIds.includes(id) ? "#FFEEF0" : "transparent"}}>

                                {/* === PESSOA === */}
                                {activeTab === 'pessoa' && (
                                    <>
                                        <td>{row.id_pessoa}</td>
                                        <td>
                                            {isEditing ?
                                                <input className="edit-input" value={editForm.nome} onChange={e => setEditForm({...editForm, nome: e.target.value})} onClick={(e) => e.stopPropagation()} />
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
                                                : row.pessoa}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <select className="edit-input" value={editForm.id_cargo} onChange={e => setEditForm({...editForm, id_cargo: Number(e.target.value)})}>
                                                    {auxCargos.map(c => <option key={c.id_cargo} value={c.id_cargo}>{`${c.nome} (${c.orgao})`}</option>)}
                                                </select>
                                                : `${row.cargo} (${row.orgao})`}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <input type="date" className="edit-input" value={editForm.data_inicio} onChange={e => {
                                                    const value = e.target.value;
                                                    if(value === '' || value === "''")
                                                        setEditForm({...editForm, data_inicio: null});
                                                    else
                                                        setEditForm({...editForm, data_inicio: e.target.value})}} />
                                                : row.data_inicio}
                                        </td>
                                        <td>
                                            {isEditing ?
                                                <input type="date" className="edit-input" value={editForm.data_fim || ''} onChange={e => {
                                                    const value = e.target.value;
                                                    if(value === '' || value === "''")
                                                        setEditForm({...editForm, data_fim: null});
                                                    else
                                                    setEditForm({...editForm, data_fim: e.target.value})}} />
                                                : (row.data_fim || '-')}
                                        </td>
                                    </>
                                )}

                                <td className="action-cell">
                                    {isEditing ? (
                                        <>
                                            <button className="icon-btn save" onClick={(e) => {e.stopPropagation(); saveEdit()}} title="Salvar"><IconSave/></button>
                                            <button className="icon-btn cancel" onClick={(e) => {e.stopPropagation(); setEditingId(null)}} title="Cancelar"><IconCancel/></button>
                                        </>
                                    ) : (
                                        <>
                                            <button className="icon-btn edit" onClick={(e) => {e.stopPropagation(); startEdit(row)}} title="Editar"><IconEdit/></button>
                                            {activeTab === 'ocupacao' && !row.data_fim && (
                                                <button className="icon-btn finish" onClick={(e) => {e.stopPropagation(); openFinishModal(row.id_ocupacao)}} title="Finalizar/Substituir">
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

                        {!deleting && (
                            <div className="button-group">
                                <button className="btn btn-danger" onClick={() => setDeleting(true)} disabled={deleting}>
                                    <IconTrash/> Excluir Itens
                                </button>
                            </div>
                        )}


                        {deleting && (
                            <>

                            <div className="button-group">
                                <button className="btn btn-secondary" onClick={() => {setDeleting(false); setSelectedIds([])}}>Cancelar Exclusão</button>
                            </div>
                            

                            <div className="button-group">

                            {
                                selectedIds.length == filteredData.length ? (
                                        <button className="btn btn-secondary" onClick={() => setSelectedIds([])}>
                                            Desmarcar Todos ( {filteredData.length} )
                                        </button>
                                    ) : 
                                    
                                (
                                <button className="btn btn-danger" onClick={() => setSelectedIds(filteredData.map(item => {
                                    const idKey = activeTab === 'ocupacao' ? 'id_ocupacao' : `id_${activeTab}`;
                                    return item[idKey];
                                }))}>
                                    Selecionar Todos ( {filteredData.length} )
                                </button>
                                )
                            }

                            </div>

                            <div className="button-group">
                                <button className="btn btn-danger" onClick={deleteBatch} disabled={selectedIds.length === 0}>
                                    <IconTrash/> Excluir Selecionados ({selectedIds.length})
                                </button>
                            </div>



                            </>
                        )}


                    </div>

                    {
                    activeTab == 'ocupacao' && (
                    <div className="filter-row">
                        <div className="filter-group" style={{flex: 2, marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '15px'}}>
                            <label>Busca Complexa</label>
                            <input
                                className="filter-input"
                                type="text"
                                placeholder={`Buscar em ${activeTab}...`}
                                value={filtroBuscaComplexa}
                                onChange={e => setFiltroBuscaComplexa(e.target.value)}
                            />
                        </div>

                        <div className="button-group">
                            <button className="btn btn-secondary" onClick={() => {
                                setFiltroBuscaComplexa("");
                                fetchAux();
                            }}>
                                Limpar
                            </button>
                            <button className="btn btn-primary" onClick={() => fetchFilteredOcupacoes()}>
                                Filtrar
                            </button>

                        </div>


                    </div>
  
                )}
                </div>


                <div className="table-container">
                    {renderTable()}
                </div>

            {showModal && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <div className="modal-header">Finalizar Mandato</div>

                        {/* DATA FIM */}
                        <div className="filter-group" style={{ marginBottom: 15 }}>
                            <label>Fim do Mandato Atual</label>
                            <input
                                type="date"
                                className="edit-input"
                                value={finishData.data_fim}
                                onChange={e =>
                                    setFinishData({ ...finishData, data_fim: e.target.value })
                                }
                            />
                        </div>

                        {/* OPÇÕES DE FINALIZAÇÃO */}
                        <div style={{
                            display: "flex",
                            gap: "15px",
                            marginBottom: "20px"
                        }}>
                            {/* CARD - SAÍDA DEFINITIVA */}
                            <div
                                className={`option-card ${finishData.definitiva ? "selected" : ""}`}
                                onClick={() => setFinishData({ ...finishData, definitiva: true })}
                            >
                                <h4>Saída Definitiva</h4>
                                <p style={{ fontSize: 13 }}>
                                    Encerra o mandato sem indicar substituto.
                                </p>
                                <input
                                    type="radio"
                                    checked={finishData.definitiva}
                                    onChange={() => setFinishData({ ...finishData, definitiva: true })}
                                />
                            </div>

                            {finishData.nome_substituto && (

                            <div
                                className={`option-card ${!finishData.definitiva ? "selected" : ""}`}
                                onClick={() => setFinishData({ ...finishData, definitiva: false })}
                            >
                                <h4>Substituto</h4>
                                <p style={{ fontSize: 13 }}>
                                    Indica um substituto imediato para assumir o cargo.
                                </p>
                                <input
                                    type="radio"
                                    checked={!finishData.definitiva}
                                    onChange={() => setFinishData({ ...finishData, definitiva: false })}
                                />
                            </div>
                            )}

                        </div>

                        {/* CAMPOS DO SUBSTITUTO */}
                        {!finishData.definitiva && finishData.nome_substituto && (
                            <div style={{
                                background: "#f1f3f5",
                                padding: 12,
                                borderRadius: 6,
                                border: "1px solid #dcdcdc"
                                }}>
                                <p style={{ fontSize: 13, fontWeight: "bold", marginBottom: 10 }}>
                                    Dados do Substituto
                                </p>
                                <p><strong>Nome:</strong> {finishData.nome_substituto}</p>

                                <div className="filter-group" style={{ marginBottom: 10 }}>
                                    <label>Início Substituto</label>
                                    <input
                                        type="date"
                                        className="edit-input"
                                        value={finishData.data_inicio_sub}
                                        onChange={e =>
                                            setFinishData({
                                                ...finishData,
                                                data_inicio_sub: e.target.value
                                            })
                                        }
                                    />
                                </div>

                                <div className="filter-group">
                                    <label>Fim Substituto (Opcional)</label>
                                    <input
                                        type="date"
                                        className="edit-input"
                                        value={finishData.data_fim_sub}
                                        onChange={e =>
                                            setFinishData({
                                                ...finishData,
                                                data_fim_sub: e.target.value
                                            })
                                        }
                                    />
                                </div>
                            </div>
                        )}

                        {
                            !finishData.definitiva && !finishData.nome_substituto && (
                                <p style={{marginBottom: 10 }}>
                                    Nenhum substituto imediato disponível para esta ocupação.
                                </p>
                            )
                        }

                        <div className="modal-actions">
                            <button className="btn btn-secondary" onClick={() => setShowModal(false)}>
                                Cancelar
                            </button>
                            <button className="btn btn-primary" onClick={confirmFinish}>
                                Confirmar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            </div>
        </div>
    );
}

export default EditPage;