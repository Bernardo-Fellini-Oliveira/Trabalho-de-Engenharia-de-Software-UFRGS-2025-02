import React, { useEffect, useState } from 'react';
// Importação direta do Axios para garantir que o código compila em ambientes isolados
// Em um ambiente de projeto local real, você usaria 'import api from "../../services/api";'
import api from '../../services/api';

// === Componente Principal ===================================================

function SearchPage() {
    // === Interfaces ===========================================================

    interface Ocupacao {
        cargo?: string;
        orgao?: string;
        pessoa?: string;
        data_inicio: string;
        data_fim?: string | null;
        mandato: number;
        id_ocupacao: number;
    }

    interface Cargo {
        id_cargo: number;
        nome: string;
        ativo: boolean;
        exclusivo: boolean;
        id_orgao: number;
        orgao: string;
        substituto_para?: number;
        substituto?: number;
    }



    type Modo = 'pessoa' | 'orgao' | 'cargo' | 'flat';

    type PessoaAgrupada = { pessoa: string; cargos: Ocupacao[] };
    type CargoAgrupado = { cargo: string; orgao: string; ocupacoes: Ocupacao[] };
    type OrgaoAgrupado = { orgao: string; cargos: Ocupacao[] };

    // === Estados ==============================================================

    const [loading, setLoading] = useState(true);

    const [modo, setModo] = useState<Modo>("pessoa");
    const [dados, setDados] = useState<PessoaAgrupada[] | CargoAgrupado[] | OrgaoAgrupado[] | Ocupacao[]>([]);

    // Estados de filtros
    const [filtroBusca, setFiltroBusca] = useState<string>("");
    const [filtroAtivo, setFiltroAtivo] = useState<"todos" | "ativos" | "inativos">("todos");
    const [filtroMandato, setFiltroMandato] = useState<"todos" | "vigente" | "encerrado">("todos");
    const [filtroCargo, setFiltroCargo] = useState<[string, string]>(["", ""]);


    const [cargos, setCargos] = useState<Cargo[]>([]);

    // === Efeitos ===============================================================


        const fetchData = async () => {
        setLoading(true);
        console.log("Iniciando busca de dados...");
        try {            
            const res = await api.get(`/busca?search_type=${modo}`, {
                params: {
                    busca: filtroBusca,
                    ativo: filtroAtivo,
                    mandato: filtroMandato
                }
            });

            setDados(res.data);
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
                setCargos(res.data);
            } catch (err) {
                console.error("Erro ao buscar cargos:", err);
            }
        };

        fetchCargos();
    }, []);


    useEffect(() => {
        fetchData();
    }, [modo]);

    // === Funções ===============================================================
    

    const handleSelectChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedValue = event.target.value;
        setModo(selectedValue as Modo);
    };



    // === Renderização =========================================================

    const renderTabela = () => {
        console.log(dados);

        if (loading) return <p>Carregando...</p>;
        if (!dados.length) return <p>Nenhum dado encontrado.</p>;

        if( modo === "flat") {
            return (
                <table style={{width: "100%", maxWidth: "1000px", textAlign: "center"}}>
                <thead>
                    <tr>
                    <th>Pessoa</th>
                    <th>Cargo</th>
                    <th>Órgão</th>
                    <th>Início</th>
                    <th>Fim</th>
                    <th>Mandato Consecutivo</th>
                    </tr>
                </thead>
                <tbody>
                    {(dados as Ocupacao[]).map((o, i) => (
                        <tr key={`${o.pessoa}-${i}`}>
                        <td>{o.pessoa}</td>
                        <td>{o.cargo}</td>
                        <td>{o.orgao}</td>
                        <td>{o.data_inicio}</td>
                        <td>{o.data_fim ?? "-"}</td>
                        <td>{o.mandato}</td>
                        </tr>
                    ))}
                </tbody>
                </table>
            );
        }

        if (modo === "pessoa") {
        return (
            <table style={{width: "100%", maxWidth: "1000px", textAlign: "center"}}>
            <thead>
                <tr>
                <th>Pessoa</th>
                <th>Cargo</th>
                <th>Órgão</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Mandato Consecutivo</th>
                </tr>
            </thead>
            <tbody>
                {(dados as PessoaAgrupada[]).map((pessoa) =>
                pessoa.cargos?.map((c, i) => (
                    <tr key={`${pessoa.pessoa}-${i}`}>
                    <td>{pessoa.pessoa}</td>
                    <td>{c.cargo}</td>
                    <td>{c.orgao}</td>
                    <td>{c.data_inicio ?? "-"}</td>
                    <td>{c.data_fim ?? "-"}</td>
                    <td>{c.mandato}</td>
                    </tr>
                ))
                )}
            </tbody>
            </table>
        );
        }

        if (modo === "cargo") {
        return (
            <table style={{width: "100%", maxWidth: "1000px", textAlign: "center"}}>
            <thead>
                <tr>
                <th>Cargo</th>
                <th>Órgão</th>
                <th>Pessoa</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Mandato Consecutivo</th>
                </tr>
            </thead>
            <tbody>
                {(dados as CargoAgrupado[]).map((cargo) =>

                cargo.ocupacoes?.map((o, i) => (
                    <tr key={`${cargo.cargo}-${cargo.orgao}-${i}`}>
                    <td>{cargo.cargo}</td>
                    <td>{cargo.orgao}</td>
                    <td>{o.pessoa}</td>
                    <td>{o.data_inicio}</td>
                    <td>{o.data_fim ?? "-"}</td>
                    <td>{o.mandato}</td>
                    </tr>
                ))
                )}
            </tbody>
            </table>
        );
        } 
        

        return (
        <table style={{width: "100%", maxWidth: "1000px", textAlign: "center"}}>
            <thead>
            <tr>
                <th>Órgão</th>
                <th>Cargo</th>
                <th>Pessoa</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Mandato Consecutivo</th>
            </tr>
            </thead>
            <tbody>
            {(dados as OrgaoAgrupado[]).map((orgao) =>
                orgao.cargos?.map((c, i) => (
                <tr key={`${orgao.orgao}-${i}`}>
                    <td>{orgao.orgao}</td>
                    <td>{c.cargo}</td>
                    <td>{c.pessoa}</td>
                    <td>{c.data_inicio}</td>
                    <td>{c.data_fim ?? "-"}</td>
                    <td>{c.mandato}</td>
                </tr>
                ))
            )}
            </tbody>
        </table>
        );
    };


    console.log(filtroCargo);
    const renderFilters = () => {

        return (

            <>
            <div>

                <label>Ativo:</label>
                <select onChange={(e) => setFiltroAtivo(e.target.value as "todos" | "ativos" | "inativos")}>
                    <option value={"todos"}>Todos</option>
                    <option value={"ativos"}>Ativos</option>
                    <option value={"inativos"}>Inativos</option>
                </select>

                <label>Mandato:</label>
                <select onChange={(e) => setFiltroMandato(e.target.value as "todos" | "vigente" | "encerrado")}>
                    <option value={"todos"}>Todos</option>
                    <option value={"vigente"}>Vigente</option>
                    <option value={"encerrado"}>Encerrado</option>
                </select>
                
            
            </div>


        {modo == "pessoa" && (
            <div>
                <label>Elegível Para:</label>
                <select
                value={filtroCargo.join("||")}
                onChange={(e) => setFiltroCargo(e.target.value.split("||") as [string, string])}
                >
                <option value={["", ""]}>Selecione um cargo</option>
                {cargos.map((cargo) => (
                    <option
                    key={cargo.id_cargo}
                    value={`${cargo.nome}||${cargo.orgao}`}
                    >
                    {cargo.nome} - {cargo.orgao}
                    </option>
                ))}
                </select>

                <button disabled={!filtroCargo[0] || !filtroCargo[1]} onClick={() => setFiltroBusca(filtroBusca ? (filtroBusca + ` AND ELECTABLE TO "${filtroCargo[0]}" DE "${filtroCargo[1]}"`) : `ELECTABLE TO "${filtroCargo[0]}" DE "${filtroCargo[1]}"`)}>Add</button>
            </div>
        )}

        </>


        )

    }



    return (
        
        <div style={{display: "flex", flexDirection: "column", gap: "30px"}}>

        <div style={{display: "flex", width: "100%", maxWidth: "600px", gap: "10px"}}>

            <input style={{width: "350px"}} type="text" placeholder="Digite sua busca..." value={filtroBusca} onChange={(e) => setFiltroBusca(e.target.value)}></input>

            <select onChange={handleSelectChange}>
                <option value={"pessoa"}>Pessoa</option>
                <option value={"orgao"}>Órgão</option>
                <option value={"cargo"}>Cargo</option>
                <option value={"flat"}>Sem Agrupamento</option>
            </select>


            <button onClick={fetchData}>Buscar</button>

            

        </div>


        {renderFilters()}



        {renderTabela()}

        </div>
    )


}


export default SearchPage;