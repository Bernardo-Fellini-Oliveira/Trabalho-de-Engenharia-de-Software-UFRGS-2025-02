import React, { useEffect, useState } from 'react';
// Importação direta do Axios para garantir que o código compila em ambientes isolados
// Em um ambiente de projeto local real, você usaria 'import api from "../../services/api";'
import api from '../../services/api';
import axios from 'axios';

// === Componente Principal ===================================================

function TestPage() {
    // === Interfaces ===========================================================
    interface Pessoa {
        id_pessoa: number;
        nome: string;
        ativo: boolean;
    }

    interface Orgao {
        id_orgao: number;
        nome: string;
        ativo: boolean;
    }

    interface Cargo {
        id_cargo: number;
        nome: string;
        ativo: boolean;
        exclusivo: boolean;
        id_orgao: number;
        orgao: string;
    }

    interface Portaria {
        id_portaria: number;
        numero: number; // Corrigido para number, já que no DB é INTEGER
        data_portaria: string;
        observacoes: string | null;
        ativo: boolean;
    }

    interface Ocupacao {
        id_ocupacao: number;
        id_pessoa: number;
        id_cargo: number;
        id_portaria: number | null;
        data_inicio: string | null;
        data_fim: string | null;
        mandato: number;
        observacoes: string | null;
    }

    // === Estados ==============================================================
    const [pessoas, setPessoas] = useState<Pessoa[]>([]);
    const [orgaos, setOrgaos] = useState<Orgao[]>([]);
    const [cargos, setCargos] = useState<Cargo[]>([]);
    const [portarias, setPortarias] = useState<Portaria[]>([]);
    const [ocupacoes, setOcupacoes] = useState<Ocupacao[]>([]);

    console.log(portarias);

    // Estados dos inputs de criação
    const [nomePessoa, setNomePessoa] = useState("");
    const [nomeOrgao, setNomeOrgao] = useState("");
    const [nomeCargo, setNomeCargo] = useState("");
    
    // Estados para Cargo
    const [orgaoSelecionadoId, setOrgaoSelecionadoId] = useState<number | null>(null);
    const [exclusivoCargo, setExclusivoCargo] = useState(1); // Padrão 1 (true)

    // Estados dos inputs de Ocupação (Vínculo)
    const [pessoaSelecionadaId, setPessoaSelecionadaId] = useState<number | null>(null);
    const [cargoSelecionadoId, setCargoSelecionadoId] = useState<number | null>(null);
    const [portariaSelecionadaId, setPortariaSelecionadaId] = useState<number | null>(null);
    const [dataInicio, setDataInicio] = useState("");
    const [dataFim, setDataFim] = useState("");
    
    // Inputs para Portaria
    const [numeroPortaria, setNumeroPortaria] = useState("");
    const [dataPortaria, setDataPortaria] = useState("");
    const [obsPortaria, setObsPortaria] = useState("");

    const [loading, setLoading] = useState(true);
    const [feedback, setFeedback] = useState("");

    // --- Funções de API de Carregamento (GET) ----------------------------------

    const fetchAllData = async () => {
        try {
            setLoading(true);
            setFeedback("A carregar dados iniciais...");

            // Usando Promise.all para carregar todos os dados em paralelo
            const [pessoasRes, orgaosRes, cargosRes, portariasRes, ocupacoesRes] = await Promise.all([
                api.get<Pessoa[]>("/pessoa/"),
                api.get<Orgao[]>("/orgao/"),
                api.get<Cargo[]>("/cargo/"),
                api.get<Portaria[]>("/portaria/"),
                api.get<Ocupacao[]>("/ocupacao/"),
            ]);

            const ocupacoes_agrupadas_pessoa = await api.get("/busca/agrupada/pessoa");
            console.log("Ocupações agrupadas por pessoa:", ocupacoes_agrupadas_pessoa.data);

            
            setPessoas(pessoasRes.data);
            setOrgaos(orgaosRes.data);
            setCargos(cargosRes.data);
            setPortarias(portariasRes.data);
            setOcupacoes(ocupacoesRes.data);

            setFeedback("Dados carregados com sucesso!");

        } catch (error: unknown) {
            console.error("Erro ao carregar dados:", error);
            // Type guard para garantir que 'error' tem a propriedade 'message' ou 'response.data.detail'
            let errorMessage = "Erro desconhecido ao carregar dados.";
            if (axios.isAxiosError(error) && error.response) {
                // Tenta extrair a mensagem do erro do FastAPI, se existir
                errorMessage = error.response.data.detail ? JSON.stringify(error.response.data.detail) : error.message;
            } else if (error instanceof Error) {
                errorMessage = error.message;
            }
            setFeedback(`Erro ao carregar dados: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };


    // === Carregar dados iniciais ==============================================
    useEffect(() => {
        fetchAllData();
    }, []);

    // --- Funções de API de Adição (POST) --------------------------------------

    const handleCreatePessoa = async () => {
        if (!nomePessoa.trim()) {
            setFeedback("O nome da pessoa é obrigatório.");
            return;
        }
        try {
            setFeedback(`A adicionar Pessoa: ${nomePessoa}...`);
            const start = performance.now();
            const payload = { nome: nomePessoa };
            const response = await api.post("/pessoa/", payload);
            const end = performance.now();
            console.log(`Pessoa adicionada com ID: ${response.data.id_pessoa} (Tempo: ${(end - start).toFixed(2)} ms)`);
            setNomePessoa("");
            fetchAllData(); 
        } catch (error: unknown) {
            let errorMessage = "Erro desconhecido ao adicionar pessoa.";
            if (axios.isAxiosError(error) && error.response) {
                errorMessage = error.response.data.detail ? JSON.stringify(error.response.data.detail) : error.message;
            } else if (error instanceof Error) errorMessage = error.message;
            setFeedback(`Erro: ${errorMessage}`);
            console.error("Erro ao adicionar pessoa:", error);
        }
    };

    const handleCreateOrgao = async () => {
        if (!nomeOrgao.trim()) {
            setFeedback("O nome do órgão é obrigatório.");
            return;
        }
        try {
            setFeedback(`A adicionar Órgão: ${nomeOrgao}...`);
            const payload = { nome: nomeOrgao, ativo: 1 }; // Ativo: 1 é INTEGER no DB
            const response = await api.post("/orgao/", payload);
            setFeedback(`Órgão adicionado com ID: ${response.data.id_orgao}`);
            setNomeOrgao("");
            fetchAllData(); 
        } catch (error: unknown) {
            let errorMessage = "Erro desconhecido ao adicionar órgão.";
            if (axios.isAxiosError(error) && error.response) {
                errorMessage = error.response.data.detail ? JSON.stringify(error.response.data.detail) : error.message;
            } else if (error instanceof Error) errorMessage = error.message;
            setFeedback(`Erro: ${errorMessage}`);
            console.error("Erro ao adicionar órgão:", error);
        }
    };

    const handleCreateCargo = async () => {
        if (!nomeCargo.trim() || orgaoSelecionadoId === null) {
            setFeedback("Nome do cargo e órgão são obrigatórios.");
            return;
        }
        try {
            setFeedback(`A adicionar Cargo: ${nomeCargo}...`);
            const payload = { 
                nome: nomeCargo, 
                ativo: 1, 
                id_orgao: orgaoSelecionadoId,
                exclusivo: exclusivoCargo? 1 : 0
            };
            const response = await api.post("/cargo/", payload);
            setFeedback(`Cargo adicionado com ID: ${response.data.id_cargo}`);
            setNomeCargo("");
            setOrgaoSelecionadoId(null);
            setExclusivoCargo(1);
            fetchAllData();
        } catch (error: unknown) {
            let errorMessage = "Erro desconhecido ao adicionar cargo.";
            if (axios.isAxiosError(error) && error.response) {
                errorMessage = error.response.data.detail ? JSON.stringify(error.response.data.detail) : error.message;
            } else if (error instanceof Error) errorMessage = error.message;
            setFeedback(`Erro: ${errorMessage}`);
            console.error("Erro ao adicionar cargo:", error);
        }
    };
    
    const handleCreatePortaria = async () => {
        if (!numeroPortaria.trim() || !dataPortaria.trim()) {
            setFeedback("Número e Data da Portaria são obrigatórios.");
            return;
        }
        try {
            setFeedback(`A adicionar Portaria N° ${numeroPortaria}...`);
            const payload = { 
                numero: parseInt(numeroPortaria), 
                data_portaria: dataPortaria,
                observacoes: obsPortaria.trim() || null
            };
            const response = await api.post("/portaria/", payload);
            setFeedback(`Portaria adicionada com ID: ${response.data.id_portaria}`);
            setNumeroPortaria("");
            setDataPortaria("");
            setObsPortaria("");
            fetchAllData();
        } catch (error: unknown) {
            let errorMessage = "Erro desconhecido ao adicionar portaria.";
            if (axios.isAxiosError(error) && error.response) {
                errorMessage = error.response.data.detail ? JSON.stringify(error.response.data.detail) : error.message;
            } else if (error instanceof Error) errorMessage = error.message;
            setFeedback(`Erro: ${errorMessage}`);
            console.error("Erro ao adicionar portaria:", error);
        }
    };

    const handleCreateOcupacao = async () => {
        if (pessoaSelecionadaId === null || cargoSelecionadoId === null) {
            setFeedback("Pessoa e Cargo devem ser selecionados.");
            return;
        }

        const mandatoValue = 1; // Usando valor padrão
        
        try {
            setFeedback(`A vincular Pessoa ${pessoaSelecionadaId} ao Cargo ${cargoSelecionadoId}...`);
            const payload = { 
                id_pessoa: pessoaSelecionadaId,
                id_cargo: cargoSelecionadoId,
                id_portaria: portariaSelecionadaId, 
                data_inicio: dataInicio.trim() || null,
                data_fim: dataFim.trim() || null,
                mandato: mandatoValue,
                observacoes: null
            };
            const response = await api.post("/ocupacao/", payload);
            setFeedback(`Ocupação adicionada com ID: ${response.data.id_ocupacao}`);
            setPessoaSelecionadaId(null);
            setCargoSelecionadoId(null);
            setPortariaSelecionadaId(null);
            setDataInicio("");
            setDataFim("");
            fetchAllData();
        } catch (error: unknown) {
            let errorMessage = "Erro desconhecido ao adicionar ocupação.";
            if (axios.isAxiosError(error) && error.response) {
                errorMessage = error.response.data.detail ? JSON.stringify(error.response.data.detail) : error.message;
            } else if (error instanceof Error) errorMessage = error.message;
            setFeedback(`Erro: ${errorMessage}`);
            console.error("Erro ao adicionar ocupação:", error);
        }
    };


    // --- Funções de API de Remoção (DELETE) ------------------------------------

    const handleReactivateEntity = async (entity: string, id: number) => {
        if (!window.confirm(`Tem certeza que deseja reativar o(a) ${entity} com ID ${id}?`)) {
            return;
        }
        try {
            setFeedback(`A reativar ${entity} com ID ${id}...`);
            const response = await api.put(`/${entity}/reativar/${id}`);
            setFeedback(response.data.message || `${entity} reativado com sucesso.`);
            fetchAllData();
        } catch (error: unknown) {
            let errorMessage = `Erro ao reativar ${entity}.`;
            if (axios.isAxiosError(error) && error.response) {
                errorMessage = error.response.data.detail ?
                    (Array.isArray(error.response.data.detail) ? error.response.data.detail[0].msg : error.response.data.detail)
                    : error.message;
            }
            else if (error instanceof Error) {
                errorMessage = error.message;
            }
            setFeedback(`Erro: ${errorMessage}`);
            console.error(`Erro ao reativar ${entity}:`, error);
        }
    };


    const handleDeleteEntity = async (entity: string, id: number, soft: boolean = false) => {
        const type = soft ? 'Inativação (Soft Delete)' : 'Exclusão Permanente (Hard Delete)';
        
        if (!window.confirm(`Tem certeza que deseja realizar a operação de ${type} no(a) ${entity} com ID ${id}?`)) {
            return;
        }
        
        try {
            setFeedback(`A executar ${type} em ${entity} com ID ${id}...`);
            
            let url = `/${entity}/delete/${id}`;
            if (soft) {
                url += '?soft=true';
            }
            
            const response = await api.delete(url);
            setFeedback(response.data.message || `${entity} removido/inativado com sucesso.`);
            fetchAllData();
        } catch (error: unknown) {
            let errorMessage = `Erro ao realizar a operação em ${entity}.`;
            if (axios.isAxiosError(error) && error.response) {
                // Tenta extrair a mensagem de erro do FastAPI/chave estrangeira
                errorMessage = error.response.data.detail ? 
                    (Array.isArray(error.response.data.detail) ? error.response.data.detail[0].msg : error.response.data.detail) 
                    : error.message;
            } else if (error instanceof Error) {
                errorMessage = error.message;
            }
            // Verifica se é erro de chave estrangeira
            if (errorMessage.includes("FOREIGN KEY constraint failed")) {
                errorMessage = `Não pode remover o(a) ${entity} com ID ${id}. Existem outras entidades (ex: Cargos ou Ocupações) que dependem dele(a).`;
            }

            setFeedback(`Erro: ${errorMessage}`);
            console.error(`Erro ao remover ${entity}:`, error);
        }
    };


    // --- Funções Auxiliares ---------------------------------------------------
    
    // Função para obter o nome do órgão a partir do ID
    const getOrgaoName = (id: number) => {
        return orgaos.find(o => o.id_orgao === id)?.nome || 'Órgão Desconhecido';
    };


    const handleEndOcupacao = async (id_ocupacao: number) => {
        if (!window.confirm(`Tem certeza que deseja finalizar a Ocupação com ID ${id_ocupacao}?`)) {
            return;
        }
        try {
            setFeedback(`A finalizar Ocupação com ID ${id_ocupacao}...`);
            const response = await api.put(`/ocupacao/finalizar/${id_ocupacao}`);
            setFeedback(response.data.message || `Ocupação finalizada com sucesso.`);
            fetchAllData();
        } catch (error: unknown) {
            let errorMessage = `Erro ao finalizar Ocupação.`;
            if (axios.isAxiosError(error) && error.response) {
                errorMessage = error.response.data.detail ?
                    (Array.isArray(error.response.data.detail) ? error.response.data.detail[0].msg : error.response.data.detail)
                    : error.message;
            }
            else if (error instanceof Error) {
                errorMessage = error.message;
            }
            setFeedback(`Erro: ${errorMessage}`);
            console.error(`Erro ao finalizar Ocupação:`, error);
        }
    };


    // Função para renderizar botões de remoção (Soft/Hard)
    const renderDeleteButtons = (entity: string, id: number, isSoftDeletable: boolean, isActive: boolean) => {
        if (!isSoftDeletable) {
            // Hard Delete simples para Portaria e Ocupação
            return (
                <button 
                    onClick={() => handleDeleteEntity(entity, id, false)}
                    
                    disabled={loading}
                    title={`Excluir permanentemente ${entity} (ID: ${id})`}
                >
                    Excluir
                </button>
            );
        }

        // Botões duplos para Pessoa, Órgão, Cargo, Portaria
        return (
            <>
                <button 
                    onClick={isActive? () => handleDeleteEntity(entity, id, true) : () => handleReactivateEntity(entity, id)}
                    
                    disabled={loading}
                    title={isActive? `Inativar ${entity} (Soft Delete) (ID: ${id})` : `Reativar ${entity} (ID: ${id})`}
                >
                    {isActive? "Inativar" : "Reativar"}

                </button>
                <button 
                    onClick={() => handleDeleteEntity(entity, id, false)}
                    
                    disabled={loading}
                    title={`Excluir permanentemente ${entity} (Hard Delete) (ID: ${id})`}
                >
                    Excluir
                </button>
            </>
        );
    };

    // === Render ===============================================================
    return (
        <div >
            <h1 >
                Teste de Integração
            </h1>

            <div>
                {loading ? "Aguarde..." : feedback}
            </div>

            <div >
                {/* Coluna de Adição (POST) */}
                <div >
                    <h2 >Adicionar Entidades</h2>

                    {/* Adicionar Pessoa */}
                    <div >
                        <h3 >Pessoa</h3>
                        <input
                            type="text"
                            placeholder="Nome da pessoa"
                            value={nomePessoa}
                            onChange={(e) => setNomePessoa(e.target.value)}
                            
                        />
                        <button 
                            onClick={handleCreatePessoa} 
                            disabled={loading || !nomePessoa.trim()}
                            
                        >
                            Adicionar Pessoa
                        </button>
                    </div>

                    {/* Adicionar Órgão */}
                    <div >
                        <h3 >Órgão</h3>
                        <input
                            type="text"
                            placeholder="Nome do órgão"
                            value={nomeOrgao}
                            onChange={(e) => setNomeOrgao(e.target.value)}
                            
                        />
                        <button
                            onClick={handleCreateOrgao}
                            disabled={loading || !nomeOrgao.trim()}
                            
                        >
                            Adicionar Órgão
                        </button>
                    </div>

                    {/* Adicionar Cargo */}
                    <div >
                        <h3 >Cargo</h3>
                        <input
                            type="text"
                            placeholder="Nome do cargo"
                            value={nomeCargo}
                            onChange={(e) => setNomeCargo(e.target.value)}
                            
                        />
                        <select 
                            value={orgaoSelecionadoId || ""} 
                            onChange={(e) => setOrgaoSelecionadoId(parseInt(e.target.value))}
                            
                        >
                            <option value="">Selecione um órgão</option>
                            {orgaos.map((orgao) => (
                              orgao.ativo && (
                                <option key={orgao.id_orgao} value={orgao.id_orgao}>
                                    {orgao.nome} ({orgao.id_orgao})
                                </option>)
                            ))}
                        </select>

                        <label htmlFor="exclusivoCargo">Cargo Exclusivo?</label>
                        <input id="exclusivoCargo" type="checkbox" style={{ width: '20px', height: '20px' }} value={exclusivoCargo} checked={exclusivoCargo === 1} onChange={(e) => setExclusivoCargo(e.target.checked ? 1 : 0)} />

                        <button
                            onClick={handleCreateCargo}
                            disabled={loading || !nomeCargo.trim() || orgaoSelecionadoId === null}
                            
                        >
                            Adicionar Cargo
                        </button>
                    </div>

                    {/* Adicionar Portaria */}
                    <div >
                        <h3 >Portaria</h3>
                        <input
                            type="number"
                            placeholder="Número da Portaria (Ex: 100)"
                            value={numeroPortaria}
                            onChange={(e) => setNumeroPortaria(e.target.value)}
                            
                        />
                        <input
                            type="text"
                            placeholder="Data (AAAA-MM-DD)"
                            value={dataPortaria}
                            onChange={(e) => setDataPortaria(e.target.value)}
                            
                        />
                        <input
                            type="text"
                            placeholder="Observações (Opcional)"
                            value={obsPortaria}
                            onChange={(e) => setObsPortaria(e.target.value)}
                            
                        />
                        <button
                            onClick={handleCreatePortaria}
                            disabled={loading || !numeroPortaria.trim() || !dataPortaria.trim()}
                            
                        >
                            Adicionar Portaria
                        </button>
                    </div>

                    {/* Adicionar Ocupação (Vínculo) */}
                    <div >
                        <h3 >Vincular Pessoa a Cargo (Ocupação)</h3>
                        <select 
                            value={pessoaSelecionadaId || ""} 
                            onChange={(e) => setPessoaSelecionadaId(parseInt(e.target.value))}
                            
                        >
                            <option value="">Selecione uma pessoa</option>
                            {pessoas.map((p) => (
                              p.ativo && (
                                <option key={p.id_pessoa} value={p.id_pessoa}>
                                    {p.nome} (ID: {p.id_pessoa})
                                </option>
                              )
                            ))}
                        </select>

                        <select
                            value={cargoSelecionadoId || ""}
                            onChange={(e) => setCargoSelecionadoId(parseInt(e.target.value))}
                            
                        >
                            <option value="">Selecione um cargo</option>
                            {cargos.map((c) => (
                              c.ativo && ( 
                                <option key={c.id_cargo} value={c.id_cargo}>
                                    {c.nome} ({getOrgaoName(c.id_orgao)})
                                </option>
                              )
                            ))}
                        </select>

                        <select
                            value={portariaSelecionadaId || ""}
                            onChange={(e) => setPortariaSelecionadaId(parseInt(e.target.value))}
                            
                        >
                            <option value="">Selecione uma portaria</option>
                            {portarias.map((p) => (
                            
                              p.ativo && ( 
                                <option key={p.id_portaria} value={p.id_portaria}>
                                    N° {p.numero} - {p.data_portaria}
                                </option>
                              )
                            ))}
                        </select>

                        <input
                            type="text"
                            placeholder="Data de início (AAAA-MM-DD)"
                            value={dataInicio}
                            onChange={(e) => setDataInicio(e.target.value)}
                            
                        />

                        <input
                            type="text"
                            placeholder="Data de fim (AAAA-MM-DD)"
                            value={dataFim}
                            onChange={(e) => setDataFim(e.target.value)}

                        />

                        <button
                            onClick={handleCreateOcupacao}
                            disabled={loading || pessoaSelecionadaId === null || cargoSelecionadoId === null}
                            
                        >
                            Criar Ocupação (Vínculo)
                        </button>
                    </div>

                </div>

                {/* Coluna de Listas (GET) */}
                <div >
                    <h2 >Dados Carregados (GET)</h2>
                    
                    {/* Lista de Pessoas */}
                    <div>
                        <strong >Pessoas ({pessoas.length}):</strong>
                        <ul >
                            {pessoas.map((p) => (
                                <li key={p.id_pessoa}>
                                  <span>
                                    [ID {p.id_pessoa}] {p.nome} ({p.ativo ? 'Ativo' : 'Inativo'})
                                  </span>
                                    {renderDeleteButtons('pessoa', p.id_pessoa, true, p.ativo)}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Lista de Órgãos */}
                    <div >
                        <strong >Órgãos ({orgaos.length}):</strong>
                        <ul >
                            {orgaos.map((o) => (
                                <li key={o.id_orgao}>
                                  <span>
                                    [ID {o.id_orgao}] {o.nome} ({o.ativo ? 'Ativo' : 'Inativo'})
                                  </span>
                                    {renderDeleteButtons('orgao', o.id_orgao, true, o.ativo)}

                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Lista de Cargos */}
                    <div >
                        <strong >Cargos ({cargos.length}):</strong>
                        <ul >
                            {cargos.map((c) => (
                                <li key={c.id_cargo}>
                                  <span>
                                    [ID {c.id_cargo}] {c.nome} ({getOrgaoName(c.id_orgao)}) ({c.ativo ? "Ativo" : "Inativo"}) (Exclusivo: {c.exclusivo ? 'Sim' : 'Não'})
                                  </span>
                                    {renderDeleteButtons('cargo', c.id_cargo, true, c.ativo)}
                                 
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Lista de Portarias */}
                    <div >
                        <strong >Portarias ({portarias.length}):</strong>
                        <ul >
                            {portarias.map((p) => (
                                <li key={p.id_portaria}>
                                  <span>
                                    [ID {p.id_portaria}] N° {p.numero} - {p.data_portaria} {p.ativo ? '(Ativo)' : '(Inativo)'}
                                  </span>
                                    {renderDeleteButtons('portaria', p.id_portaria, true, p.ativo)}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Lista de Ocupações (Vínculos Persistentes) */}
                    <div >
                        <strong >Ocupações ({ocupacoes.length}):</strong>
                        <ul >
                            {ocupacoes.map((oc, index) => {
                                const pessoa = pessoas.find(p => p.id_pessoa === oc.id_pessoa);
                                const cargo = cargos.find(c => c.id_cargo === oc.id_cargo);
                                const nomePessoa = pessoa ? pessoa.nome : 'Pessoa Não Encontrada';
                                const nomeCargo = cargo ? cargo.nome : 'Cargo Não Encontrado';
                                const portaria = oc.id_portaria ? portarias.find(p => p.id_portaria === oc.id_portaria) : null;
                                const nomeOrgao = cargo ? getOrgaoName(cargo.id_orgao) : 'Órgão Desconhecido';
                                return (
                                    <li key={oc.id_ocupacao || index}>
                                      <span>
                                        [ID {oc.id_ocupacao}] <strong>{nomePessoa}</strong> &rarr; <strong>{nomeCargo} ({nomeOrgao})</strong>
                                         (Início: {oc.data_inicio || 'N/A'})
                                         (Fim: {oc.data_fim || 'N/A'})
                                         (Portaria: {portaria ? `N° ${portaria.numero} - ${portaria.data_portaria}` : 'Nenhuma'})
                                      </span>
                                        {renderDeleteButtons('ocupacao', oc.id_ocupacao, false, true)}

                                        {!oc.data_fim &&
                                        <button 
                                            onClick={() => handleEndOcupacao(oc.id_ocupacao)}
                                            disabled={loading}
                                        >
                                            Finalizar
                                        </button>
                                        }

                                    </li>
                                );
                            })}
                        </ul>
                    </div>

                </div>
            </div>
        </div>
    );
}

export default TestPage;
