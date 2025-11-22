import React, { useEffect, useState } from 'react';
import api from '../../services/api'; 
import axios from 'axios';
import '../../../styles.css'; 

// === Interfaces de Tipagem ===
interface PessoaDB { id_pessoa: number; nome: string; ativo: boolean; }
interface OrgaoDB { id_orgao: number; nome: string; ativo: boolean; }
interface CargoDB { id_cargo: number; nome: string; ativo: boolean; id_orgao: number; }

interface FormPessoa { id_temp: number; nome: string; }
interface FormOrgao { id_temp: number; nome: string; }
interface FormCargo { id_temp: number; nome: string; orgao_associado: string; exclusivo: boolean; }
interface FormVinculo { id_temp: number; pessoa_v: string; cargo_v: string; inicio_v: string; fim_v: string; }

function InputPage() {
    // === Estados para DATALISTS ===
    const [dbPessoas, setDbPessoas] = useState<PessoaDB[]>([]);
    const [dbOrgaos, setDbOrgaos] = useState<OrgaoDB[]>([]);
    const [dbCargos, setDbCargos] = useState<CargoDB[]>([]);

    // === Estados dos Formulários Dinâmicos ===
    const [listaPessoas, setListaPessoas] = useState<FormPessoa[]>([{ id_temp: Date.now(), nome: '' }]);
    const [listaOrgaos, setListaOrgaos] = useState<FormOrgao[]>([{ id_temp: Date.now(), nome: '' }]);
    const [listaCargos, setListaCargos] = useState<FormCargo[]>([{ id_temp: Date.now(), nome: '', orgao_associado: '', exclusivo: false }]);
    const [listaVinculos, setListaVinculos] = useState<FormVinculo[]>([{ id_temp: Date.now(), pessoa_v: '', cargo_v: '', inicio_v: '', fim_v: '' }]);

    const [loading, setLoading] = useState(false);

    // === 1. Carregar dados ===
    useEffect(() => {
        const loadData = async () => {
            try {
                const [p, o, c] = await Promise.all([
                    api.get<PessoaDB[]>('/pessoa/'),
                    api.get<OrgaoDB[]>('/orgao/'),
                    api.get<CargoDB[]>('/cargo/')
                ]);
                setDbPessoas(p.data);
                setDbOrgaos(o.data);
                setDbCargos(c.data);
            } catch (err) {
                console.error("Erro ao carregar dados base", err);
            }
        };
        loadData();
    }, []);

    // === 2. Funções de Manipulação ===
    const handleAdd = (tipo: string) => {
        const id_temp = Date.now();
        if (tipo === 'pessoa') setListaPessoas([...listaPessoas, { id_temp, nome: '' }]);
        if (tipo === 'orgao') setListaOrgaos([...listaOrgaos, { id_temp, nome: '' }]);
        if (tipo === 'cargo') setListaCargos([...listaCargos, { id_temp, nome: '', orgao_associado: '', exclusivo: false }]);
        if (tipo === 'vinculo') setListaVinculos([...listaVinculos, { id_temp, pessoa_v: '', cargo_v: '', inicio_v: '', fim_v: '' }]);
    };

    const handleRemove = (tipo: string, id_temp: number) => {
        // A verificação de segurança permanece aqui, mas o botão sumirá visualmente
        if (tipo === 'pessoa' && listaPessoas.length > 1) setListaPessoas(listaPessoas.filter(i => i.id_temp !== id_temp));
        if (tipo === 'orgao' && listaOrgaos.length > 1) setListaOrgaos(listaOrgaos.filter(i => i.id_temp !== id_temp));
        if (tipo === 'cargo' && listaCargos.length > 1) setListaCargos(listaCargos.filter(i => i.id_temp !== id_temp));
        if (tipo === 'vinculo' && listaVinculos.length > 1) setListaVinculos(listaVinculos.filter(i => i.id_temp !== id_temp));
    };

    const handleChange = (tipo: string, id_temp: number, field: string, value: any) => {
        if (tipo === 'pessoa') setListaPessoas(listaPessoas.map(i => i.id_temp === id_temp ? { ...i, [field]: value } : i));
        if (tipo === 'orgao') setListaOrgaos(listaOrgaos.map(i => i.id_temp === id_temp ? { ...i, [field]: value } : i));
        if (tipo === 'cargo') setListaCargos(listaCargos.map(i => i.id_temp === id_temp ? { ...i, [field]: value } : i));
        if (tipo === 'vinculo') setListaVinculos(listaVinculos.map(i => i.id_temp === id_temp ? { ...i, [field]: value } : i));
    };

    // === 3. Helpers e Envio ===
    const extractId = (val: string): number | null => {
        if (!val) return null;
        const parts = val.split(' - ');
        const id = parseInt(parts[0]);
        return isNaN(id) ? null : id;
    };

    const enviar = async (tipo: string) => {
        setLoading(true);
        try {
            if (tipo === 'pessoas') {
                const payload = listaPessoas.filter(p => p.nome.trim() !== "").map(p => ({ nome: p.nome }));
                if (payload.length === 0) return alert("Preencha os nomes.");
                await api.post('/pessoa/', payload);
                alert('Pessoas inseridas com sucesso!');
                setListaPessoas([{ id_temp: Date.now(), nome: '' }]);
            }
            if (tipo === 'orgaos') {
                const payload = listaOrgaos.filter(o => o.nome.trim() !== "").map(o => ({ nome: o.nome, ativo: 1 }));
                if (payload.length === 0) return alert("Preencha os órgãos.");
                await api.post('/orgao/', payload);
                alert('Órgãos inseridos com sucesso!');
                setListaOrgaos([{ id_temp: Date.now(), nome: '' }]);
            }
            if (tipo === 'cargos') {
                const payload = [];
                for (const c of listaCargos) {
                    const idOrgao = extractId(c.orgao_associado);
                    if (c.nome.trim() && idOrgao) {
                        payload.push({ nome: c.nome, id_orgao: idOrgao, exclusivo: c.exclusivo ? 1 : 0, ativo: 1 });
                    }
                }
                if (payload.length === 0) return alert("Verifique os nomes e órgãos.");
                await api.post('/cargo/', payload);
                alert('Cargos inseridos com sucesso!');
                setListaCargos([{ id_temp: Date.now(), nome: '', orgao_associado: '', exclusivo: false }]);
            }
            if (tipo === 'vinculados') {
                const payload = [];
                for (const v of listaVinculos) {
                    const idPessoa = extractId(v.pessoa_v);
                    const idCargo = extractId(v.cargo_v);
                    if (idPessoa && idCargo) {
                        payload.push({ id_pessoa: idPessoa, id_cargo: idCargo, data_inicio: v.inicio_v || null, data_fim: v.fim_v || null, id_portaria: null, mandato: 1, observacoes: null });
                    }
                }
                if (payload.length === 0) return alert("Verifique as seleções.");
                await api.post('/ocupacao/', payload);
                alert('Vinculações inseridas com sucesso!');
                setListaVinculos([{ id_temp: Date.now(), pessoa_v: '', cargo_v: '', inicio_v: '', fim_v: '' }]);
            }

            // Recarrega datalists
            const [p, o, c] = await Promise.all([
                api.get<PessoaDB[]>('/pessoa/'),
                api.get<OrgaoDB[]>('/orgao/'),
                api.get<CargoDB[]>('/cargo/')
            ]);
            setDbPessoas(p.data); setDbOrgaos(o.data); setDbCargos(c.data);

        } catch (error) {
            console.error(error);
            alert("Erro ao enviar dados.");
        } finally {
            setLoading(false);
        }
    };

    const getOrgaoName = (id: number) => dbOrgaos.find(o => o.id_orgao === id)?.nome || 'Desc.';

    return (
        <div>
            {/* Datalists */}
            <datalist id="dl-orgaos">
                {dbOrgaos.map(o => o.ativo && <option key={o.id_orgao} value={`${o.id_orgao} - ${o.nome}`} />)}
            </datalist>
            <datalist id="dl-pessoas">
                {dbPessoas.map(p => p.ativo && <option key={p.id_pessoa} value={`${p.id_pessoa} - ${p.nome}`} />)}
            </datalist>
            <datalist id="dl-cargos">
                {dbCargos.map(c => c.ativo && <option key={c.id_cargo} value={`${c.id_cargo} - ${c.nome} (${getOrgaoName(c.id_orgao)})`} />)}
            </datalist>

            <div className="topo">
                <h1>INSERÇÃO DE DADOS</h1>
                <p>Inserindo dados</p>
                {loading && <p style={{color: 'orange'}}>Processando...</p>}
            </div>

            <div className="conteudo">
                <div className="form-box">

                    {/* === PESSOAS === */}
                    <div className="area">
                        <div className="arrayObj pessoa pessoas">
                            {listaPessoas.map((item, index) => (
                                <div key={item.id_temp} className={`obj pessoa pessoas ${index}`}>
                                    <h2>Pessoa:</h2>
                                    <div id="c_nome_pessoa" className="input_container normal">
                                        <div className="numero-item">
                                            Nome:<br />
                                            <input 
                                                type="text" 
                                                value={item.nome}
                                                onChange={(e) => handleChange('pessoa', item.id_temp, 'nome', e.target.value)}
                                                required 
                                            />
                                            {/* --- AQUI: Condicional adicionada --- */}
                                            {listaPessoas.length > 1 && (
                                                <button type="button" className="botao-remover" onClick={() => handleRemove('pessoa', item.id_temp)}>X</button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button type='button' className='botao-obj' onClick={() => handleAdd('pessoa')}>+ Pessoa</button>
                        <br /><br />
                        <button onClick={() => enviar('pessoas')} className="botao-confirmar" disabled={loading}>Inserir Pessoas</button>
                    </div>

                    {/* === ORGÃOS === */}
                    <div className="area">
                        <div className="arrayObj orgao orgaos">
                            {listaOrgaos.map((item, index) => (
                                <div key={item.id_temp} className={`obj orgao orgaos ${index}`}>
                                    <h2>Órgão:</h2>
                                    <div id="c_nome_orgao" className="input_container normal">
                                        <div className="numero-item">
                                            Nome do Órgão:<br />
                                            <input 
                                                type="text" 
                                                value={item.nome}
                                                onChange={(e) => handleChange('orgao', item.id_temp, 'nome', e.target.value)}
                                                required 
                                            />
                                            {/* --- AQUI: Condicional adicionada --- */}
                                            {listaOrgaos.length > 1 && (
                                                <button type="button" className="botao-remover" onClick={() => handleRemove('orgao', item.id_temp)}>X</button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button type='button' className='botao-obj' onClick={() => handleAdd('orgao')}>+ Orgão</button>
                        <br /><br />
                        <button onClick={() => enviar('orgaos')} className="botao-confirmar" disabled={loading}>Inserir Órgãos</button>
                    </div>

                    {/* === CARGOS === */}
                    <div className="area">
                        <div className="arrayObj cargo cargos">
                            {listaCargos.map((item, index) => (
                                <div key={item.id_temp} className={`obj cargo cargos ${index}`}>
                                    <h2>Cargo:</h2>
                                    <div id="c_nome_cargo" className="input_container normal">
                                        <div className="numero-item">
                                            Nome do cargo:<br />
                                            <input 
                                                type="text" 
                                                value={item.nome}
                                                onChange={(e) => handleChange('cargo', item.id_temp, 'nome', e.target.value)}
                                                required 
                                            />
                                        </div>
                                    </div>
                                    <div id="c_orgao_associado" className="input_container normal">
                                        <div className="numero-item">
                                            Órgão Associado:<br />
                                            <input 
                                                list="dl-orgaos"
                                                type="text" 
                                                placeholder="Busque o órgão..."
                                                value={item.orgao_associado}
                                                onChange={(e) => handleChange('cargo', item.id_temp, 'orgao_associado', e.target.value)}
                                                required 
                                            />
                                        </div>
                                    </div>
                                    <div id="c_exclusivo" className="input_container normal">
                                        <label className="numero-item">
                                            Cargo Exclusivo?<br />
                                            <input 
                                                type="checkbox" 
                                                checked={item.exclusivo}
                                                onChange={(e) => handleChange('cargo', item.id_temp, 'exclusivo', e.target.checked)}
                                            />
                                            <span className="checkmark"></span>
                                            
                                            {/* --- AQUI: Condicional adicionada --- */}
                                            {listaCargos.length > 1 && (
                                                <button type="button" className="botao-remover" onClick={() => handleRemove('cargo', item.id_temp)}>X</button>
                                            )}
                                        </label>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button type='button' className='botao-obj' onClick={() => handleAdd('cargo')}>+ Cargo</button>
                        <br /><br />
                        <button onClick={() => enviar('cargos')} className="botao-confirmar" disabled={loading}>Inserir Cargos</button>
                    </div>

                    {/* === VINCULAR === */}
                    <div className="area">
                        <div className="arrayObj vincular vinculados">
                            {listaVinculos.map((item, index) => (
                                <div key={item.id_temp} className={`obj vincular vinculados ${index}`}>
                                    <h2>Vincular Pessoa a Cargo:</h2>
                                    <div id="c_pessoa_v" className="input_container normal">
                                        <div className="numero-item">
                                            Pessoa:<br />
                                            <input 
                                                list="dl-pessoas"
                                                type="text" 
                                                placeholder="Busque a pessoa..."
                                                value={item.pessoa_v}
                                                onChange={(e) => handleChange('vinculo', item.id_temp, 'pessoa_v', e.target.value)}
                                                required 
                                            />
                                        </div>
                                    </div>
                                    <div id="c_cargo_v" className="input_container normal">
                                        <div className="numero-item">
                                            Cargo:<br />
                                            <input 
                                                list="dl-cargos"
                                                type="text" 
                                                placeholder="Busque o cargo..."
                                                value={item.cargo_v}
                                                onChange={(e) => handleChange('vinculo', item.id_temp, 'cargo_v', e.target.value)}
                                                required 
                                            />
                                        </div>
                                    </div>
                                    <div id="c_incio_v" className="input_container normal">
                                        <div className="numero-item">
                                            Data de Inicio<br />
                                            <input 
                                                type="text" 
                                                placeholder="AAAA-MM-DD"
                                                value={item.inicio_v}
                                                onChange={(e) => handleChange('vinculo', item.id_temp, 'inicio_v', e.target.value)}
                                                required 
                                            />
                                        </div>
                                    </div>
                                    <div id="c_fim_v" className="input_container normal">
                                        <div className="numero-item">
                                            Data de Fim<br />
                                            <input 
                                                type="text" 
                                                placeholder="AAAA-MM-DD"
                                                value={item.fim_v}
                                                onChange={(e) => handleChange('vinculo', item.id_temp, 'fim_v', e.target.value)}
                                            />
                                            
                                            {/* --- AQUI: Condicional adicionada --- */}
                                            {listaVinculos.length > 1 && (
                                                <button type="button" className="botao-remover" onClick={() => handleRemove('vinculo', item.id_temp)}>X</button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button type='button' className='botao-obj' onClick={() => handleAdd('vinculo')}>+ Vinculação</button>
                        <br /><br />
                        <button onClick={() => enviar('vinculados')} className="botao-confirmar" disabled={loading}>Inserir Vinculações</button>
                    </div>

                </div>
            </div>
        </div>
    );
}

export default InputPage;