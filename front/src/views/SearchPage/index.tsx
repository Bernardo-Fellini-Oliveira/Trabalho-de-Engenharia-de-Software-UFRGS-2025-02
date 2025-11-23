import React, { useEffect, useState, useMemo } from 'react';
import api from '../../services/api'; 
import './SearchPage.css'; 

// === Ícones SVG Inline ===
const IconPencil = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
    </svg>
);

const IconSortUp = () => <span className="sort-icon">▲</span>;
const IconSortDown = () => <span className="sort-icon">▼</span>;

// === Tipos e Interfaces ===
interface Ocupacao {
    id_ocupacao: number;
    cargo?: string;
    orgao?: string;
    pessoa?: string;
    data_inicio: string;
    data_fim?: string | null;
    mandato: number;
}

interface Cargo {
    id_cargo: number;
    nome: string;
    orgao: string;
}

// Estruturas agrupadas vindas do backend
type PessoaAgrupada = { pessoa: string; cargos: Ocupacao[] };
type CargoAgrupado = { cargo: string; orgao: string; ocupacoes: Ocupacao[] };
type OrgaoAgrupado = { orgao: string; cargos: Ocupacao[] };

type Modo = 'pessoa' | 'orgao' | 'cargo' | 'flat';
type SortConfig = { key: string; direction: 'asc' | 'desc' } | null;

function SearchPage() {
    // === Estados ===
    const [loading, setLoading] = useState(true);
    const [dados, setDados] = useState<any[]>([]);
    const [cargosList, setCargosList] = useState<Cargo[]>([]);

    // Filtros
    const [modo, setModo] = useState<Modo>("pessoa");
    const [filtroBusca, setFiltroBusca] = useState<string>("");
    const [filtroAtivo, setFiltroAtivo] = useState<"todos" | "ativos" | "inativos">("todos");
    const [filtroMandato, setFiltroMandato] = useState<"todos" | "vigente" | "encerrado">("todos");
    const [filtroCargo, setFiltroCargo] = useState<[string, string]>(["", ""]);

    // Configuração de Ordenação (Coluna e Direção)
    const [sortConfig, setSortConfig] = useState<SortConfig>(null);

    // === Busca de Dados (Backend) ===
    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/busca?ativo=${filtroAtivo}&mandato=${filtroMandato}&search_type=${modo}`);
            setDados(res.data);
            setSortConfig(null); // Reseta ordenação ao buscar novos dados
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const fetchCargos = async () => {
            try {
                const res = await api.get('/cargo/');
                setCargosList(res.data);
            } catch (err) { console.error(err); }
        };
        fetchCargos();
    }, []);

    useEffect(() => {
        fetchData();
    }, [modo]); // Recarrega se mudar o tipo de visualização

    // === Lógica Local: Ordenação e Filtragem ===
    
    // Função acionada ao clicar no cabeçalho da tabela
    const requestSort = (key: string) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    // Processa os dados brutos (Filtro Texto Local + Ordenação Local)
    const processedData = useMemo(() => {
        let dataToSort = [...dados];

        // 1. Filtro de Texto (Local)
        if (filtroBusca) {
            const lowerBusca = filtroBusca.toLowerCase();
            dataToSort = dataToSort.filter(item => {
                // Procura no campo principal do agrupamento
                if (modo === 'pessoa') return (item as PessoaAgrupada).pessoa.toLowerCase().includes(lowerBusca);
                if (modo === 'orgao') return (item as OrgaoAgrupado).orgao.toLowerCase().includes(lowerBusca);
                if (modo === 'cargo') return (item as CargoAgrupado).cargo.toLowerCase().includes(lowerBusca);
                if (modo === 'flat') {
                    const i = item as Ocupacao;
                    return (i.pessoa?.toLowerCase().includes(lowerBusca) || 
                            i.cargo?.toLowerCase().includes(lowerBusca) || 
                            i.orgao?.toLowerCase().includes(lowerBusca));
                }
                return true;
            });
        }

        // 2. Ordenação Avançada (Grupos e Sub-itens)
        if (sortConfig !== null) {
            const { key, direction } = sortConfig;
            const multiplier = direction === 'asc' ? 1 : -1;

            // Função auxiliar de comparação
            const compare = (a: any, b: any) => {
                const valA = a[key] ?? ''; 
                const valB = b[key] ?? '';
                if (valA < valB) return -1 * multiplier;
                if (valA > valB) return 1 * multiplier;
                return 0;
            };

            if (modo === 'flat') {
                // Ordenação simples
                dataToSort.sort(compare);
            } else {
                // Modos Agrupados:
                // Se a chave clicada for a chave do Grupo (ex: clicou em 'Pessoa'), ordena os grupos.
                // Se clicou em outra coluna (ex: 'Início'), ordena os itens DENTRO de cada grupo.
                
                const groupKey = modo; // 'pessoa', 'orgao', 'cargo'
                
                if (key === groupKey) {
                    // Ordena os Grupos Principais
                    dataToSort.sort(compare);
                } else {
                    // Ordena os itens DENTRO de cada grupo
                    dataToSort = dataToSort.map(group => {
                        let innerKey = 'cargos'; 
                        if (modo === 'cargo') innerKey = 'ocupacoes';
                        
                        if (group[innerKey] && Array.isArray(group[innerKey])) {
                            // Cria uma cópia do array interno e ordena
                            const sortedInner = [...group[innerKey]].sort(compare);
                            return { ...group, [innerKey]: sortedInner };
                        }
                        return group;
                    });
                }
            }
        }
        return dataToSort;
    }, [dados, sortConfig, filtroBusca, modo]);


    // === Ações dos Botões ===

    const handleGoToEdit = () => {
        // Placeholder: aqui você usaria navigate('/editar')
        alert("Redirecionando para a página de Edição/Inserção de Dados...");
    };

    const handleExportCSV = () => {
        alert("Emitindo relatório CSV... (Funcionalidade pendente no Backend)");
    };

    const handleExportPDF = () => {
        alert("Emitindo relatório PDF... (Funcionalidade pendente no Backend)");
    };

    // === Helper para renderizar TH com ícone de sort ===
    const renderHeader = (label: string, sortKey: string) => (
        <th onClick={() => requestSort(sortKey)} title="Clique para ordenar">
            {label}
            {sortConfig?.key === sortKey ? (sortConfig.direction === 'asc' ? <IconSortUp/> : <IconSortDown/>) : null}
        </th>
    );

    // === Renderização ===
    return (
        <div className="search-container">
            <h1 className="search-title">Consulta de Dados</h1>
            <p className='search-description'>Consulta de dados</p>

            {/* CARD DE FILTROS */}
            <div className="filter-card">
                <div className="filter-row">
                    
                    {/* Busca Textual */}
                    <div className="filter-group" style={{flex: 2}}>
                        <label>Busca Textual</label>
                        <input 
                            className="filter-input"
                            type="text" 
                            placeholder="Nome, Cargo ou Órgão..." 
                            value={filtroBusca} 
                            onChange={(e) => setFiltroBusca(e.target.value)}
                        />
                    </div>

                    {/* Modo de Visualização */}
                    <div className="filter-group">
                        <label>Agrupar por</label>
                        <select className="filter-select" value={modo} onChange={(e) => setModo(e.target.value as Modo)}>
                            <option value="pessoa">Pessoa</option>
                            <option value="orgao">Órgão</option>
                            <option value="cargo">Cargo</option>
                            <option value="flat">Sem Agrupamento (Lista)</option>
                        </select>
                    </div>

                    {/* Filtro Status */}
                    <div className="filter-group">
                        <label>Status</label>
                        <select className="filter-select" onChange={(e) => setFiltroAtivo(e.target.value as any)}>
                            <option value="todos">Todos</option>
                            <option value="ativos">Ativos</option>
                            <option value="inativos">Inativos</option>
                        </select>
                    </div>

                    {/* Botões de Ação do Filtro */}
                    <div className="button-group">
                        <button className="btn btn-primary" onClick={() => fetchData()}>
                            Filtrar
                        </button>
                        <button className="btn btn-secondary" onClick={() => {
                            setFiltroBusca("");
                            setFiltroAtivo("todos");
                            fetchData();
                        }}>
                            Limpar
                        </button>
                    </div>
                </div>

                {/* Filtro Extra Condicional (Cargo) */}
                {modo === 'pessoa' && (
                    <div className="filter-row" style={{marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '15px'}}>
                        <div className="filter-group">
                            <label>Elegível para Cargo Específico:</label>
                            <select
                                className="filter-select"
                                value={filtroCargo.join("||")}
                                onChange={(e) => setFiltroCargo(e.target.value.split("||") as [string, string])}
                            >
                                <option value={["", ""]}>Selecione um cargo...</option>
                                {cargosList.map((c) => (
                                    <option key={c.id_cargo} value={`${c.nome}||${c.orgao}`}>
                                        {c.nome} - {c.orgao}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <button 
                            className="btn btn-outline3"
                            disabled={!filtroCargo[0]}
                            onClick={() => alert("Adicionar lógica de filtro complexo aqui...")}
                            style={{alignSelf: 'flex-end'}}
                        >
                            + Adicionar Regra
                        </button>
                    </div>
                )}
            </div>

            {/* BARRA DE AÇÕES (Relatórios e Edição) */}
            <div className="actions-bar">
                <button className="btn btn-warning-outline" onClick={handleGoToEdit}>
                    <IconPencil /> Editar Dados
                </button>
                <button className="btn btn-outline1" onClick={handleExportCSV}>📄 Emitir CSV</button>
                <button className="btn btn-outline2" onClick={handleExportPDF}>🖨️ Emitir PDF</button>
            </div>

            {/* TABELA DE RESULTADOS */}
            <div className="table-container">
                {loading ? (
                    <div style={{padding: '30px', textAlign: 'center', color: '#6c757d'}}>Carregando dados...</div>
                ) : !processedData.length ? (
                    <div style={{padding: '30px', textAlign: 'center', color: '#6c757d'}}>Nenhum dado encontrado.</div>
                ) : (
                    <table className="data-table">
                        <thead>
                            {/* HEADERS DINÂMICOS BASEADOS NO MODO */}
                            {modo === 'flat' && (
                                <tr>
                                    {renderHeader("Pessoa", "pessoa")}
                                    {renderHeader("Cargo", "cargo")}
                                    {renderHeader("Órgão", "orgao")}
                                    {renderHeader("Início", "data_inicio")}
                                    {renderHeader("Fim", "data_fim")}
                                    {renderHeader("Mandato", "mandato")}
                                </tr>
                            )}
                            {modo === 'pessoa' && (
                                <tr>
                                    {renderHeader("Pessoa (Grupo)", "pessoa")}
                                    {renderHeader("Cargo", "cargo")}
                                    {renderHeader("Órgão", "orgao")}
                                    {renderHeader("Início", "data_inicio")}
                                    {renderHeader("Fim", "data_fim")}
                                    {renderHeader("Mandato", "mandato")}
                                </tr>
                            )}
                            {modo === 'orgao' && (
                                <tr>
                                    {renderHeader("Órgão (Grupo)", "orgao")}
                                    {renderHeader("Cargo", "cargo")}
                                    {renderHeader("Pessoa", "pessoa")}
                                    {renderHeader("Início", "data_inicio")}
                                    {renderHeader("Fim", "data_fim")}
                                    {renderHeader("Mandato", "mandato")}
                                </tr>
                            )}
                            {modo === 'cargo' && (
                                <tr>
                                    {renderHeader("Cargo (Grupo)", "cargo")}
                                    {renderHeader("Órgão", "orgao")}
                                    {renderHeader("Pessoa", "pessoa")}
                                    {renderHeader("Início", "data_inicio")}
                                    {renderHeader("Fim", "data_fim")}
                                    {renderHeader("Mandato", "mandato")}
                                </tr>
                            )}
                        </thead>
                        <tbody>
                            {/* --- MODO FLAT (LISTA SIMPLES) --- */}
                            {modo === 'flat' && (processedData as Ocupacao[]).map((row, i) => (
                                <tr key={i}>
                                    <td>{row.pessoa}</td>
                                    <td>{row.cargo}</td>
                                    <td>{row.orgao}</td>
                                    <td>{row.data_inicio}</td>
                                    <td>{row.data_fim || '-'}</td>
                                    <td>{row.mandato}</td>
                                </tr>
                            ))}

                            {/* --- MODO AGRUPADO POR PESSOA --- */}
                            {modo === 'pessoa' && (processedData as PessoaAgrupada[]).map((group, i) => (
                                group.cargos?.map((subItem, j) => (
                                    <tr key={`${i}-${j}`}>
                                        <td style={{fontWeight: '600'}}>{group.pessoa}</td>
                                        <td>{subItem.cargo}</td>
                                        <td>{subItem.orgao}</td>
                                        <td>{subItem.data_inicio}</td>
                                        <td>{subItem.data_fim || '-'}</td>
                                        <td>{subItem.mandato}</td>
                                    </tr>
                                ))
                            ))}

                            {/* --- MODO AGRUPADO POR ORGÃO --- */}
                            {modo === 'orgao' && (processedData as OrgaoAgrupado[]).map((group, i) => (
                                group.cargos?.map((subItem, j) => (
                                    <tr key={`${i}-${j}`}>
                                        <td style={{fontWeight: '600'}}>{group.orgao}</td>
                                        <td>{subItem.cargo}</td>
                                        <td>{subItem.pessoa}</td>
                                        <td>{subItem.data_inicio}</td>
                                        <td>{subItem.data_fim || '-'}</td>
                                        <td>{subItem.mandato}</td>
                                    </tr>
                                ))
                            ))}

                            {/* --- MODO AGRUPADO POR CARGO --- */}
                            {modo === 'cargo' && (processedData as CargoAgrupado[]).map((group, i) => (
                                group.ocupacoes?.map((subItem, j) => (
                                    <tr key={`${i}-${j}`}>
                                        <td style={{fontWeight: '600'}}>{group.cargo}</td>
                                        <td>{group.orgao}</td>
                                        <td>{subItem.pessoa}</td>
                                        <td>{subItem.data_inicio}</td>
                                        <td>{subItem.data_fim || '-'}</td>
                                        <td>{subItem.mandato}</td>
                                    </tr>
                                ))
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}

export default SearchPage;