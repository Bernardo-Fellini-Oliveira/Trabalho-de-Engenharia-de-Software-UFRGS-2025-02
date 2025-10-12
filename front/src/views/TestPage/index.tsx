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
        ativo: number;
    }

    interface Orgao {
        id_orgao: number;
        nome: string;
        ativo: number; // No DB é INTEGER (0 ou 1)
    }

    interface Cargo {
        id_cargo: number;
        nome: string;
        ativo: number; // No DB é INTEGER (0 ou 1)
        id_orgao: number;
    }

    interface Portaria {
        id_portaria: number;
        numero: number; // Corrigido para number, já que no DB é INTEGER
        data: string;
        observacoes: string | null;
        ativo: number;
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

    // Estados dos inputs de criação
    const [nomePessoa, setNomePessoa] = useState("");
    const [nomeOrgao, setNomeOrgao] = useState("");
    const [nomeCargo, setNomeCargo] = useState("");
    const [orgaoSelecionadoId, setOrgaoSelecionadoId] = useState<number | null>(null);

    // Estados dos inputs de Ocupação (Vínculo)
    const [pessoaSelecionadaId, setPessoaSelecionadaId] = useState<number | null>(null);
    const [cargoSelecionadoId, setCargoSelecionadoId] = useState<number | null>(null);
    const [dataInicio, setDataInicio] = useState("");
    
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
                id_orgao: orgaoSelecionadoId 
            };
            const response = await api.post("/cargo/", payload);
            setFeedback(`Cargo adicionado com ID: ${response.data.id_cargo}`);
            setNomeCargo("");
            setOrgaoSelecionadoId(null);
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
                id_portaria: null, 
                data_inicio: dataInicio.trim() || null,
                data_fim: null,
                mandato: mandatoValue,
                observacoes: null
            };
            const response = await api.post("/ocupacao/", payload);
            setFeedback(`Ocupação adicionada com ID: ${response.data.id_ocupacao}`);
            setPessoaSelecionadaId(null);
            setCargoSelecionadoId(null);
            setDataInicio("");
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


    // Função para renderizar botões de remoção (Soft/Hard)
    const renderDeleteButtons = (entity: string, id: number, isSoftDeletable: boolean) => {
        if (!isSoftDeletable) {
            // Hard Delete simples para Portaria e Ocupação
            return (
                <button 
                    onClick={() => handleDeleteEntity(entity, id, false)}
                    className="text-white bg-red-500 hover:bg-red-700 font-bold ml-2 text-xs p-1 rounded-md transition disabled:bg-gray-400"
                    disabled={loading}
                    title={`Excluir permanentemente ${entity} (ID: ${id})`}
                >
                    Excluir
                </button>
            );
        }

        // Botões duplos para Pessoa, Órgão, Cargo, Portaria
        return (
            <div className="flex space-x-1">
                <button 
                    onClick={() => handleDeleteEntity(entity, id, true)}
                    className="text-white bg-yellow-500 hover:bg-yellow-600 font-bold text-xs p-1 rounded-md transition disabled:bg-gray-400"
                    disabled={loading}
                    title={`Inativar ${entity} (Soft Delete) (ID: ${id})`}
                >
                    Inativar
                </button>
                <button 
                    onClick={() => handleDeleteEntity(entity, id, false)}
                    className="text-white bg-red-500 hover:bg-red-700 font-bold text-xs p-1 rounded-md transition disabled:bg-gray-400"
                    disabled={loading}
                    title={`Excluir permanentemente ${entity} (Hard Delete) (ID: ${id})`}
                >
                    Excluir
                </button>
            </div>
        );
    };

    // === Render ===============================================================
    return (
        <div className="p-5 flex flex-col gap-6 max-w-4xl mx-auto bg-gray-50 min-h-screen">
            <h1 className="text-3xl font-bold text-center text-blue-600 mb-4">
                Teste de Integração FastAPI/SQLite (CRUD Básico)
            </h1>

            <div className={`p-3 text-center rounded-lg font-medium ${loading ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                {loading ? "Aguarde..." : feedback}
            </div>

            <div className="flex flex-col md:flex-row gap-8">
                {/* Coluna de Adição (POST) */}
                <div className="flex flex-col gap-6 w-full md:w-1/2 p-4 bg-white shadow-lg rounded-xl">
                    <h2 className="text-xl font-semibold text-blue-700 border-b pb-2">Adicionar Entidades</h2>

                    {/* Adicionar Pessoa */}
                    <div className="space-y-2">
                        <h3 className="font-semibold">Pessoa</h3>
                        <input
                            type="text"
                            placeholder="Nome da pessoa"
                            value={nomePessoa}
                            onChange={(e) => setNomePessoa(e.target.value)}
                            className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                        <button 
                            onClick={handleCreatePessoa} 
                            disabled={loading || !nomePessoa.trim()}
                            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md disabled:bg-gray-400 transition"
                        >
                            Adicionar Pessoa
                        </button>
                    </div>

                    {/* Adicionar Órgão */}
                    <div className="space-y-2">
                        <h3 className="font-semibold">Órgão</h3>
                        <input
                            type="text"
                            placeholder="Nome do órgão"
                            value={nomeOrgao}
                            onChange={(e) => setNomeOrgao(e.target.value)}
                            className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                        <button
                            onClick={handleCreateOrgao}
                            disabled={loading || !nomeOrgao.trim()}
                            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md disabled:bg-gray-400 transition"
                        >
                            Adicionar Órgão (Ativo: 1)
                        </button>
                    </div>

                    {/* Adicionar Cargo */}
                    <div className="space-y-2">
                        <h3 className="font-semibold">Cargo</h3>
                        <input
                            type="text"
                            placeholder="Nome do cargo"
                            value={nomeCargo}
                            onChange={(e) => setNomeCargo(e.target.value)}
                            className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 mb-2"
                        />
                        <select 
                            value={orgaoSelecionadoId || ""} 
                            onChange={(e) => setOrgaoSelecionadoId(parseInt(e.target.value))}
                            className="w-full p-2 border rounded-md bg-white focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="">Selecione um órgão</option>
                            {orgaos.map((orgao) => (
                              orgao.ativo === 1 && (
                                <option key={orgao.id_orgao} value={orgao.id_orgao}>
                                    {orgao.nome} ({orgao.id_orgao})
                                </option>)
                            ))}
                        </select>
                        <button
                            onClick={handleCreateCargo}
                            disabled={loading || !nomeCargo.trim() || orgaoSelecionadoId === null}
                            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md disabled:bg-gray-400 transition mt-2"
                        >
                            Adicionar Cargo
                        </button>
                    </div>

                    {/* Adicionar Portaria */}
                    <div className="space-y-2">
                        <h3 className="font-semibold">Portaria</h3>
                        <input
                            type="number"
                            placeholder="Número da Portaria (Ex: 100)"
                            value={numeroPortaria}
                            onChange={(e) => setNumeroPortaria(e.target.value)}
                            className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                        <input
                            type="text"
                            placeholder="Data (AAAA-MM-DD)"
                            value={dataPortaria}
                            onChange={(e) => setDataPortaria(e.target.value)}
                            className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                        <input
                            type="text"
                            placeholder="Observações (Opcional)"
                            value={obsPortaria}
                            onChange={(e) => setObsPortaria(e.target.value)}
                            className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                        <button
                            onClick={handleCreatePortaria}
                            disabled={loading || !numeroPortaria.trim() || !dataPortaria.trim()}
                            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md disabled:bg-gray-400 transition"
                        >
                            Adicionar Portaria
                        </button>
                    </div>

                    {/* Adicionar Ocupação (Vínculo) */}
                    <div className="space-y-2 border-t pt-4">
                        <h3 className="font-semibold">Vincular Pessoa a Cargo (Ocupação)</h3>
                        <select 
                            value={pessoaSelecionadaId || ""} 
                            onChange={(e) => setPessoaSelecionadaId(parseInt(e.target.value))}
                            className="w-full p-2 border rounded-md bg-white mb-2"
                        >
                            <option value="">Selecione uma pessoa</option>
                            {pessoas.map((p) => (
                              p.ativo === 1 && (
                                <option key={p.id_pessoa} value={p.id_pessoa}>
                                    {p.nome} (ID: {p.id_pessoa})
                                </option>
                              )
                            ))}
                        </select>

                        <select
                            value={cargoSelecionadoId || ""}
                            onChange={(e) => setCargoSelecionadoId(parseInt(e.target.value))}
                            className="w-full p-2 border rounded-md bg-white mb-2"
                        >
                            <option value="">Selecione um cargo</option>
                            {cargos.map((c) => (
                              c.ativo === 1 && ( 
                                <option key={c.id_cargo} value={c.id_cargo}>
                                    {c.nome} ({getOrgaoName(c.id_orgao)})
                                </option>
                              )
                            ))}
                        </select>

                        <input
                            type="text"
                            placeholder="Data de início (AAAA-MM-DD)"
                            value={dataInicio}
                            onChange={(e) => setDataInicio(e.target.value)}
                            className="w-full p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
                        />
                        
                        <button
                            onClick={handleCreateOcupacao}
                            disabled={loading || pessoaSelecionadaId === null || cargoSelecionadoId === null}
                            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-md disabled:bg-gray-400 transition mt-2"
                        >
                            Criar Ocupação (Vínculo)
                        </button>
                    </div>

                </div>

                {/* Coluna de Listas (GET) */}
                <div className="flex flex-col gap-6 w-full md:w-1/2 p-4 bg-white shadow-lg rounded-xl">
                    <h2 className="text-xl font-semibold text-green-700 border-b pb-2">Dados Carregados (GET)</h2>
                    
                    {/* Lista de Pessoas */}
                    <div className="border p-3 rounded-md">
                        <strong className="block mb-1">Pessoas ({pessoas.length}):</strong>
                        <ul className="list-disc list-inside text-sm max-h-32 overflow-y-auto">
                            {pessoas.map((p) => (
                                <li key={p.id_pessoa}>
                                  <span>
                                    [ID {p.id_pessoa}] {p.nome} ({p.ativo === 1 ? 'Ativo' : 'Inativo'})
                                  </span>
                                    {renderDeleteButtons('pessoa', p.id_pessoa, true)}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Lista de Órgãos */}
                    <div className="border p-3 rounded-md">
                        <strong className="block mb-1">Órgãos ({orgaos.length}):</strong>
                        <ul className="list-disc list-inside text-sm max-h-32 overflow-y-auto">
                            {orgaos.map((o) => (
                                <li key={o.id_orgao}>
                                  <span>
                                    [ID {o.id_orgao}] {o.nome} (Ativo: {o.ativo})
                                  </span>
                                    {renderDeleteButtons('orgao', o.id_orgao, true)}

                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Lista de Cargos */}
                    <div className="border p-3 rounded-md">
                        <strong className="block mb-1">Cargos ({cargos.length}):</strong>
                        <ul className="list-disc list-inside text-sm max-h-32 overflow-y-auto">
                            {cargos.map((c) => (
                                <li key={c.id_cargo}>
                                  <span>
                                    [ID {c.id_cargo}] {c.nome} ({getOrgaoName(c.id_orgao)}) (Ativo: {c.ativo})
                                  </span>
                                    {renderDeleteButtons('cargo', c.id_cargo, true)}
                                 
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Lista de Portarias */}
                    <div className="border p-3 rounded-md">
                        <strong className="block mb-1">Portarias ({portarias.length}):</strong>
                        <ul className="list-disc list-inside text-sm max-h-32 overflow-y-auto">
                            {portarias.map((p) => (
                                <li key={p.id_portaria}>
                                  <span>
                                    [ID {p.id_portaria}] N° {p.numero} - {p.data} Ativo: {p.ativo}
                                  </span>
                                    {renderDeleteButtons('portaria', p.id_portaria, true)}
                                </li>
                            ))}
                        </ul>
                    </div>

                    {/* Lista de Ocupações (Vínculos Persistentes) */}
                    <div className="border p-3 rounded-md">
                        <strong className="block mb-1">Ocupações ({ocupacoes.length}):</strong>
                        <ul className="list-disc list-inside text-sm max-h-48 overflow-y-auto">
                            {ocupacoes.map((oc, index) => {
                                const pessoa = pessoas.find(p => p.id_pessoa === oc.id_pessoa);
                                const cargo = cargos.find(c => c.id_cargo === oc.id_cargo);
                                const nomePessoa = pessoa ? pessoa.nome : 'Pessoa Não Encontrada';
                                const nomeCargo = cargo ? cargo.nome : 'Cargo Não Encontrado';
                                return (
                                    <li key={oc.id_ocupacao || index}>
                                      <span>
                                        [ID {oc.id_ocupacao}] <strong>{nomePessoa}</strong> &rarr; <strong>{nomeCargo}</strong>
                                        (Início: {oc.data_inicio || 'N/A'})
                                      </span>
                                        {renderDeleteButtons('ocupacao', oc.id_ocupacao, false)}
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
