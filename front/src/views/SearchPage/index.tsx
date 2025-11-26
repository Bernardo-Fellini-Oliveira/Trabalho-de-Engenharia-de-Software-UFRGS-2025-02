import React, { useEffect, useState, useMemo } from 'react';
import api from '../../services/api';
import '../../../styles.css' 
import './SearchPage.css'; 
import { useNavigate } from 'react-router';
import { useAuth } from '../../context/auth_context';
import Header from '../../components/Header';

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
    observacoes?: string; 
    substituto_para?: number | string | null;
    mandato: number;
    exclusivo?: boolean;
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

    const navigate = useNavigate();
    
    // === Estados ===
    const [loading, setLoading] = useState(true);
    const [dados, setDados] = useState<any[]>([]);
    const [cargosList, setCargosList] = useState<Cargo[]>([]);

    // Filtros
    const [modo, setModo] = useState<Modo>("pessoa");
    const [filtroBusca, setFiltroBusca] = useState<string>("");
    const [filtroBuscaComplexa, setFiltroBuscaComplexa] = useState<string>("");
    const [filtroAtivo, setFiltroAtivo] = useState<"todos" | "ativos" | "inativos">("todos");
    const [filtroVigencia, setFiltroVigencia] = useState<"todos" | "vigente" | "encerrado" | "futuro">("todos");
    const [filtroCargo, setFiltroCargo] = useState<[string, string]>(["", ""]);

    const [lastFetchParams, setLastFetchParams] = useState<{ modo: Modo; ativo: string; mandato: string; busca: string; vigencia: string }>({modo, ativo: filtroAtivo, mandato: filtroVigencia, busca: filtroBusca, vigencia: filtroVigencia});

    // Configuração de Ordenação (Coluna e Direção)
    const [sortConfig, setSortConfig] = useState<SortConfig>(null);


    const {user} = useAuth();

    console.log("Renderizando SearchPage com dados:", dados);
    
    // === Busca de Dados (Backend) ===
    const fetchData = async () => {
        setLoading(true);
        try {
            const res = await api.get(`/busca?ativo=${filtroAtivo}&mandato=${filtroVigencia}&tipo=${modo}&busca=${filtroBuscaComplexa}`);
            setDados(res.data);
            setLastFetchParams({modo, ativo: filtroAtivo, mandato: filtroVigencia, busca: filtroBuscaComplexa, vigencia: filtroVigencia});
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
                // Helper para verificar se ALGUM sub-item corresponde à busca
                const checkSubItems = (lista: Ocupacao[]) => {
                    if (!lista) return false;
                    return lista.some(sub => 
                        sub.cargo?.toLowerCase().includes(lowerBusca) ||
                        sub.orgao?.toLowerCase().includes(lowerBusca) ||
                        sub.pessoa?.toLowerCase().includes(lowerBusca) ||
                        sub.observacoes?.toLowerCase().includes(lowerBusca) // Opcional: buscar na obs também
                    );
                };

                // Lógica por Modo
                if (modo === 'pessoa') {
                    const i = item as PessoaAgrupada;
                    // Retorna TRUE se: Nome da Pessoa der match OU algum dos cargos dela der match
                    return i.pessoa.toLowerCase().includes(lowerBusca) || checkSubItems(i.cargos);
                }
                
                if (modo === 'orgao') {
                    const i = item as OrgaoAgrupado;
                    // Retorna TRUE se: Nome do Órgão der match OU algum dos cargos lá dentro der match
                    return i.orgao.toLowerCase().includes(lowerBusca) || checkSubItems(i.cargos);
                }
                
                if (modo === 'cargo') {
                    const i = item as CargoAgrupado;
                    return i.cargo.toLowerCase().includes(lowerBusca) || checkSubItems(i.ocupacoes);
                }
                
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
        navigate('/edit');
    };

    const handleExportCSV = async () => {

          const response = await api.post('relatorio/export/csv', 
            {
            tipo: lastFetchParams.modo,
            ativo: lastFetchParams.ativo,
            mandato: lastFetchParams.mandato,
            busca: lastFetchParams.busca,
            sort_by: sortConfig ? `${sortConfig.key},${sortConfig.direction}` : ""
        }, {
            responseType: 'blob',
            headers: { 'Content-Type': 'application/json' }
        }
    );

    try {

    // 2. Tratar Erros HTTP
        if (response.status !== 200) {
            // Em caso de erro, o Axios/navegador pode tentar ler a resposta como JSON se for o caso
            // Se for 4xx/5xx, o corpo pode ser um JSON de erro
            console.error("Erro ao gerar CSV:", response.data);
            alert("Falha ao gerar o relatório CSV. Código de status: " + response.status);
            return;
        }

        // 3. Obter o Nome do Arquivo
        const contentDisposition = response.headers['content-disposition'];
        let filename = 'relatorio.csv'; // Nome padrão
        
        if (contentDisposition) {
            // Regex para extrair o nome do arquivo do header Content-Disposition
            const filenameMatch = contentDisposition.match(/filename=["']?([^"']+)["']?/i);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1];
            }
        }

        // 4. Criar um Link de Download e Disparar o Download
        // response.data já é o Blob (devido ao responseType: 'blob')
        const blob = response.data;
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        
        document.body.appendChild(a);
        a.click();
        
        // 5. Limpeza
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    
    }catch (error) {
        // Erros de rede ou erros não HTTP (e.g., Axios timeout)
        console.error("Erro no download:", error);
        alert("Ocorreu um erro de rede ao tentar baixar o CSV.");
    }

    };

    const handleExportPDF = async () => {
        const response = await api.post('relatorio/export/pdf', 
            {
            tipo: lastFetchParams.modo,
            ativo: lastFetchParams.ativo,
            mandato: lastFetchParams.mandato,
            busca: lastFetchParams.busca,
            sort_by: sortConfig ? `${sortConfig.key},${sortConfig.direction}` : ""
        }, {
            responseType: 'blob',
            headers: { 'Content-Type': 'application/json' }
        }
    );

    try {

    // 2. Tratar Erros HTTP
        if (response.status !== 200) {
            // Em caso de erro, o Axios/navegador pode tentar ler a resposta como JSON se for o caso
            // Se for 4xx/5xx, o corpo pode ser um JSON de erro
            console.error("Erro ao gerar PDF:", response.data);
            alert("Falha ao gerar o relatório PDF. Código de status: " + response.status);
            return;
        }

        // 3. Obter o Nome do Arquivo
        const contentDisposition = response.headers['content-disposition'];
        let filename = 'relatorio.pdf'; // Nome padrão
        
        if (contentDisposition) {
            // Regex para extrair o nome do arquivo do header Content-Disposition
            const filenameMatch = contentDisposition.match(/filename=["']?([^"']+)["']?/i);
            if (filenameMatch && filenameMatch[1]) {
                filename = filenameMatch[1];
            }
        }

        // 4. Criar um Link de Download e Disparar o Download
        // response.data já é o Blob (devido ao responseType: 'blob')
        const blob = response.data;
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        
        document.body.appendChild(a);
        a.click();
        
        // 5. Limpeza
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    
    }catch (error) {
        // Erros de rede ou erros não HTTP (e.g., Axios timeout)
        console.error("Erro no download:", error);
        alert("Ocorreu um erro de rede ao tentar baixar o PDF.");
    }

    };

    // === Helper para renderizar TH com ícone de sort ===
    const renderHeader = (label: string, sortKey: string) => (
        <th onClick={() => requestSort(sortKey)} title="Clique para ordenar">
            {label}
            {sortConfig?.key === sortKey ? (sortConfig.direction === 'asc' ? <IconSortUp/> : <IconSortDown/>) : null}
        </th>
    );

    const handleAddRule = () => {
        const [cargo, orgao] = filtroCargo;

        if (!cargo) return;

        const novaRegra = `ELECTABLE TO "${cargo}" FROM "${orgao}"`;

        setFiltroBuscaComplexa(prev => {
            // Se já tiver texto, adiciona " AND " antes
            if (prev && prev.trim() !== "") {
                return `${prev} AND ${novaRegra}`;
            }

            return novaRegra;
        });

        setFiltroCargo(["", ""]);
    };

    // === Renderização ===
    return (
        <div className="search-page">
            <Header role={user?.role} />
            <div className="search-container">
                <div className='topo'>
                    <h1>Consulta de Dados</h1>
                    <p>Consulta de dados</p>
                </div>

                {/* CARD DE FILTROS */}
                <div className="filtro-container">
                    <div className="filtro-linha">
                        
                        {/* Busca Textual */}
                        <div className="filtro-grupo" style={{flex: 2}}>
                            <label>Busca Textual</label>
                            <input 
                                className="filtro-input"
                                type="text" 
                                placeholder="Nome, Cargo ou Órgão..." 
                                value={filtroBusca} 
                                onChange={(e) => setFiltroBusca(e.target.value)}
                            />
                        </div>

                        {/* Modo de Visualização */}
                        <div className="filtro-grupo">
                            <label>Agrupar por</label>
                            <select className="filtro-select" value={modo} onChange={(e) => setModo(e.target.value as Modo)}>
                                <option value="pessoa">Pessoa</option>
                                <option value="orgao">Órgão</option>
                                <option value="cargo">Cargo</option>
                                <option value="flat">Sem Agrupamento (Lista)</option>
                            </select>
                        </div>

                        {/* Filtro Atividade */}
                        <div className="filtro-grupo">
                            <label>Status</label>
                            <select className="filtro-select" onChange={(e) => setFiltroAtivo(e.target.value as any)}>
                                <option value="todos">Todos</option>
                                <option value="ativos">Ativos</option>
                                <option value="inativos">Inativos</option>
                            </select>
                        </div>

                        {/* Filtro Vigencia */}
                        <div className="filtro-grupo">
                            <label>Vigência</label>
                            <select className="filtro-select" onChange={(e) => setFiltroVigencia(e.target.value as any)}>
                                <option value="todos">Todos</option>
                                <option value="vigente">Vigente</option>
                                <option value="encerrado">Encerrado</option>
                                <option value="futuro">Futuro</option>
                            </select>
                        </div>



                        {/* Botões de Ação do Filtro */}
                        <div className="botao-container">
                            <button className="botao" onClick={() => fetchData()}>
                                Filtrar
                            </button>
                            <button className="botao botao-cinza" onClick={() => {
                                setFiltroBusca("");
                                setFiltroAtivo("todos");
                                fetchData();
                            }}>
                                Limpar
                            </button>
                        </div>
                    </div>

                    <div className="filtro-linha" style={{marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '15px'}}>
                        <div className="filtro-grupo">
                            <label>Pesquisa Complexa</label>
                            <input 
                                className="filtro-input"
                                type="text" 
                                placeholder={"Ex: pessoa = \"João\" AND (cargo = \"Diretor\" OR orgao = \"INT\")..."}
                                value={filtroBuscaComplexa} 
                                onChange={(e) => setFiltroBuscaComplexa(e.target.value)}
                            />
                        </div>
                    
                    </div>

                    {/* Filtro Extra Condicional (Cargo) */}
                    {modo === 'pessoa' && (
                        <div className="filtro-linha" style={{marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '15px'}}>
                            <div className="filtro-grupo">
                                <label>Elegível para Cargo Específico:</label>
                                <select
                                    className="filtro-select"
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
                                className="botao"
                                disabled={!filtroCargo[0]}
                                onClick={handleAddRule}
                                style={{alignSelf: 'flex-end'}}
                            >
                                + Adicionar Regra
                            </button>
                        </div>
                    )}
                </div>

                {/* BARRA DE AÇÕES (Relatórios e Edição) */}
                <div className="acoes-container">
                    <button className="botao botao-amarelo" onClick={handleGoToEdit}>
                        <IconPencil /> Editar Dados
                    </button>
                    <button className="botao botao-verde" onClick={handleExportCSV}>📄 Emitir CSV</button>
                    <button className="botao botao-vermelho" onClick={handleExportPDF}>🖨️ Emitir PDF</button>
                </div>

                {/* TABELA DE RESULTADOS */}
                <div className="tabela-container">
                    {loading ? (
                        <div style={{padding: '30px', textAlign: 'center', color: '#6c757d'}}>Carregando dados...</div>
                    ) : !processedData.length ? (
                        <div style={{padding: '30px', textAlign: 'center', color: '#6c757d'}}>Nenhum dado encontrado.</div>
                    ) : (
                        <table className="dado-tabela">
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
                                        {renderHeader("Substituto de", "substituto_para")}
                                        {renderHeader("Observações", "observacoes")}
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
                                        {renderHeader("Substituto de", "substituto_para")}
                                        {renderHeader("Observações", "observacoes")}
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
                                        {renderHeader("Substituto de", "substituto_para")}
                                        {renderHeader("Observações", "observacoes")}
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
                                        {renderHeader("Substituto de", "substituto_para")}
                                        {renderHeader("Observações", "observacoes")}
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
                                        <td>{row.data_fim ?? (row.id_ocupacao ? '-' : '')}</td>
                                        <td>{row.exclusivo ? row.mandato : (row.id_ocupacao ? '-' : '')}</td>
                                        <td>{row.substituto_para ?? (row.id_ocupacao ? '-' : '')}</td>
                                        <td>{row.observacoes ?? (row.id_ocupacao ? '-' : '')}</td>
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
                                            <td>{subItem.data_fim ?? (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.exclusivo ? subItem.mandato : (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.substituto_para ?? (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.observacoes ?? (subItem.id_ocupacao ? '-' : '')}</td>
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
                                            <td>{subItem.data_fim ?? (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.exclusivo ? subItem.mandato : (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.substituto_para ?? (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.observacoes ?? (subItem.id_ocupacao ? '-' : '')}</td>
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
                                            <td>{subItem.data_fim ?? (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.exclusivo ? subItem.mandato : (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.substituto_para ?? (subItem.id_ocupacao ? '-' : '')}</td>
                                            <td>{subItem.observacoes ?? (subItem.id_ocupacao ? '-' : '')}</td>
                                        </tr>
                                    ))
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}

export default SearchPage;