import { useEffect, useState } from "react";
import api from "../../services/api";

function TestPage() {


  interface Pessoa{
    "id_pessoa": number,
    "nome": string
  }

  interface Cargo{
    "id_cargo": number,
    "nome": string,
    "ativo": boolean,
    "id_orgao": number

  }

  interface Orgao{
    "id_orgao": number,
    "nome": string
    "ativo": boolean
  }

  interface Portaria{
      "id_portaria": number,
      "numero": string,
      "data": string,
  }

  interface Ocupacao{
      "id_ocupacao": number,
      "id_pessoa": number,
      "id_cargo": number,
      "id_portaria": number,
      "data_inicio": string,
      "data_fim": string | null
      "observacoes": string | null
  }

  const [historicoPessoas, setHistoricoPessoas] = useState<Pessoa[]>([]);
  const [pessoas, setPessoas] = useState<Pessoa[]>([]);

  const [historicoOrgaos, setHistoricoOrgaos] = useState<Orgao[]>([]);
  const [orgaos, setOrgaos] = useState<Orgao[]>([]);

  const [historicoCargos, setHistoricoCargos] = useState<Cargo[]>([]);
  const [cargos, setCargos] = useState<Cargo[]>([]);

  const [vinculos, setVinculos] = useState<{ pessoa: string; cargo: {nome: string; orgao: string}; data: string }[]>([]);


  const [nomePessoa, setNomePessoa] = useState<string>("");
  const [nomePessoaRemovida, setNomePessoaRemovida] = useState<string>("");


  const [nomeOrgao, setNomeOrgao] = useState<string>("");
  const [nomeOrgaoRemovido, setNomeOrgaoRemovido] = useState<string>("");
  const [nomeCargo, setNomeCargo] = useState<string>("");
  const [nomeCargoRemovido, setNomeCargoRemovido] = useState<string>("");
  const [orgaoSelecionado, setOrgaoSelecionado] = useState<string>("");
  const [orgaoSelecionadoRemovido, setOrgaoSelecionadoRemovido] = useState<string>("");
  const [pessoaSelecionada, setPessoaSelecionada] = useState<string>("");
  const [pessoaSelecionadaRemovida, setPessoaSelecionadaRemovida] = useState<string>("");
  const [date, setDate] = useState<string>("");
  const [cargoSelecionado, setCargoSelecionado] = useState<{ nome: string; orgao: string } | null>(null);
  const [cargoSelecionadoRemovido, setCargoSelecionadoRemovido] = useState<{ nome: string; orgao: string } | null>(null);

  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchData() {
    try{
      const response_cargos =  await api.get('/carregar/carregar_cargo.php', 
      {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    const response_pessoas = await api.get('/carregar/carregar_pessoa.php', 
      {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    setCargos(response_cargos.data);
    setPessoas(response_pessoas.data);
    setLoading(false);
  }
  catch(error){
    console.error("Erro ao carregar dados:", error);
    setLoading(false);
    }    
  }
    fetchData();

  });
  


  function handleRemoveVinculo(v: { pessoa: string; cargo: { nome: string; orgao: string; }; data: string; }): void {
    console.log('Removendo vínculo:', v.pessoa, v.cargo, v.data);
    setVinculos(vinculos.filter((item) => item !== v));
  }


  const handleCreatePessoa = async (nomePessoa: string) => {
try{
      const response =  await api.post('/adicionar/adicionar_pessoa.php', 
      {"idPessoa": 10, "nome": nomePessoa},
      {
      headers: {
        'Content-Type': 'application/json'
      }
    });


    const pessoa = {"id_pessoa": response.data.id_pessoa, "nome": nomePessoa};
    setHistoricoPessoas([...historicoPessoas, pessoa]);
    setPessoas([...pessoas, pessoa]);
    setNomePessoa("");
  }
  catch(error){


    console.error("Erro ao carregar dados:", error);
    setLoading(false);
    }    
  }

 async function criar_cargo(nome: string, orgao: number) {
    const response = await api.post('/adicionar/adicionar_cargo.php', {
      id_cargo: 1,
      nome: nome,
      ativo: 1,
      id_orgao: orgao
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });


    setCargos([])
    
  }



  if (loading) return <div>Carregando usuários...</div>;


  return (
    <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "16px" }}>
      <h1>Página de Teste</h1>

    <div style={{display: "flex", gap: "24px"}}>

    <div style={{display: "flex", flexDirection: "column", gap: "24px", width: "50%"}}>

      {/* Adicionar pessoa */}
      <div>
        <h3>Adicionar Pessoa</h3>
        <input
          type="text"
          placeholder="Nome da pessoa"
          value={nomePessoa}
          onChange={(e) => setNomePessoa(e.target.value)}
        />
        <button
          onClick={() => handleCreatePessoa(nomePessoa)}

        >
          Adicionar
        </button>
      </div>

      {/* Adicionar órgão */}
      <div>
        <h3>Adicionar Órgão</h3>
        <input
          type="text"
          placeholder="Nome do órgão"
          value={nomeOrgao}
          onChange={(e) => setNomeOrgao(e.target.value)}
        />
        <button
          onClick={() => {
            if (nomeOrgao.trim()) {
              //setOrgaos([...orgaos, nomeOrgao]);
              //setHistoricoOrgaos([...historicoOrgaos, nomeOrgao]);
              //setNomeOrgao("");
            }
          }}
        >
          Adicionar
        </button>
      </div>

      {/* Adicionar cargo (associado a órgão) */}
      <div>
        <h3>Adicionar Cargo</h3>
        <input
          type="text"
          placeholder="Nome do cargo"
          value={nomeCargo}
          onChange={(e) => setNomeCargo(e.target.value)}
        />
        <select
          value={orgaoSelecionado}
          onChange={(e) => setOrgaoSelecionado(e.target.value)}
        >
          <option value="">Selecione um órgão</option>
          {orgaos.map((orgao, i) => (
            <option key={i} value={orgao.nome}>
              {orgao.nome}
            </option>
          ))}
        </select>
        <button
          onClick={() => {
           // if (nomeCargo.trim()) {
           //   setCargos([...cargos, { nome: nomeCargo, orgao: orgaoSelecionado }]);
           //   setHistoricoCargos([...historicoCargos, { nome: nomeCargo, orgao: orgaoSelecionado }]);
           //   setNomeCargo("");
           //   setOrgaoSelecionado("");
            }
        //  }
        }
        >
          Adicionar
        </button>
      </div>

      {/* Vincular pessoa a cargo */}
      <div>
        <h3>Vincular Pessoa a Cargo</h3>
        <select
          value={pessoaSelecionada}
          onChange={(e) => setPessoaSelecionada(e.target.value)}
        >
          <option value="">Selecione uma pessoa</option>
          {pessoas.map((p, i) => (
            <option key={i} value={p.nome}>
              {p.nome}
            </option>
          ))}
        </select>

        <select
          value={cargoSelecionado ? `${cargoSelecionado.nome} (${cargoSelecionado.orgao})` : ""}
          onChange={(e) => {
            const [nome, orgao] = e.target.value.split(" (");
            setCargoSelecionado({ nome, orgao: orgao.replace(")", "") });
          }}
        >
          <option value="">Selecione um cargo</option>
          {/* {cargos.map((c, i) => (
            <option key={i} value={`${c.nome} (${c.orgao})`}>
              {c.nome} ({c.orgao})
            </option>
          ))} */}
        </select>

        <input
          type="text"
          placeholder="Data de início"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />

        <button
          onClick={() => {
            if (pessoaSelecionada && cargoSelecionado) {
              setVinculos([...vinculos, { pessoa: pessoaSelecionada, cargo: cargoSelecionado, data: date }]);
              setPessoaSelecionada("");
              setCargoSelecionado(null);
              setDate("");
            }
          }}
        >
          Adicionar
        </button>
      </div>

      {/* Exibir resultados */}
      <div>
        <h3>Listas</h3>
        <p><strong>Pessoas:</strong> {pessoas.join(", ") || "Nenhuma"}</p>
        <p><strong>Órgãos:</strong> {orgaos.join(", ") || "Nenhum"}</p>
        <p>
          <strong>Cargos:</strong>{" "}
          {/* {cargos.length
            ? cargos.map((c) => `${c.nome} (${c.orgao})`).join(", ")
            : "Nenhum"} */}
        </p>
        
        <div>
        <strong>Vínculos:</strong>{" "} 

        {vinculos.length
          ? vinculos.map((v) => (
              <div key={`${v.pessoa}-${v.cargo}-${v.data}`}>
                <span>{`${v.pessoa} -> ${v.cargo.nome} (${v.cargo.orgao}) com começo em ${v.data ? v.data : "data não especificada"}`}</span>
                <button onClick={() => handleRemoveVinculo(v)}>X</button>
              </div>
            ))
          : "Nenhum"}

        </div>

        <p><strong>Histórico de Pessoas:</strong> {historicoPessoas.join(", ") || "Nenhuma"}</p>
        <p><strong>Histórico de Órgãos:</strong> {historicoOrgaos.join(", ") || "Nenhum"}</p>
        <p>
          <strong>Histórico de Cargos:</strong>{" "}
          {/* {historicoCargos.length
            ? historicoCargos.map((c) => `${c.nome} (${c.orgao})`).join(", ")
            : "Nenhum"} */}
        </p>
      </div>


    </div>


     <div style={{display: "flex", flexDirection: "column", gap: "24px", width: "50%"}}>
        {/* Remover Pessoa */}
        <div>
          <h3>Remover Pessoa</h3>
          <input
            type="text"
            placeholder="Nome da pessoa a remover"
            value={nomePessoaRemovida}
            onChange={(e) => setNomePessoaRemovida(e.target.value)}
          />
          <button
            // onClick={() => {
            //   if (nomePessoaRemovida.trim()) {
            //     setPessoas(pessoas.filter(p => p !== nomePessoaRemovida));
            //     setNomePessoaRemovida("");
            //   }
            // }}
          >
            Soft Remove
          </button>

          <button
            // onClick={() => {
            //   if (nomePessoaRemovida.trim()) {
            //     setPessoas(pessoas.filter(p => p !== nomePessoaRemovida));
            //     setHistoricoPessoas(historicoPessoas.filter(p => p !== nomePessoaRemovida));
            //     setVinculos(vinculos.filter(v => v.pessoa !== nomePessoaRemovida));
            //     setNomePessoaRemovida("");
            //   }
            // }}
          >
            Hard Remove
          </button>


        </div>


        {/* Remover Órgão */}
        <div>
          <h3>Remover Órgão</h3>
          <input
            type="text"
            placeholder="Nome do órgão a remover"
            value={nomeOrgaoRemovido}
            onChange={(e) => setNomeOrgaoRemovido(e.target.value)}
          />
          <button
            // onClick={() => {
            //   if (nomeOrgaoRemovido.trim()) {
            //     setOrgaos(orgaos.filter(o => o !== nomeOrgaoRemovido));
            //     setCargos(cargos.filter(c => c.orgao !== nomeOrgaoRemovido));
            //     setNomeOrgao("");
            //   }
            // }}
          >
            Soft Remove
          </button>

          <button
            // onClick={() => {
            //   if (nomeOrgaoRemovido.trim()) {
            //     setOrgaos(orgaos.filter(o => o !== nomeOrgaoRemovido));
            //     setCargos(cargos.filter(c => c.orgao !== nomeOrgaoRemovido));
            //     setHistoricoCargos(historicoCargos.filter(c => c.orgao !== nomeOrgaoRemovido));
            //     setHistoricoOrgaos(historicoOrgaos.filter(o => o !== nomeOrgaoRemovido));
            //     setVinculos(vinculos.filter(v => v.cargo !== null && v.cargo.orgao !== nomeOrgaoRemovido));
            //     setNomeOrgaoRemovido("");
            //   }
            // }}
          >
            Hard Remove
          </button>


        </div>



        {/* Remover Cargo */}
        <div>
          <h3>Remover Cargo</h3>
          <input
            type="text"
            placeholder="Nome do cargo a remover"
            value={nomeCargoRemovido}
            onChange={(e) => setNomeCargoRemovido(e.target.value)}
          />

        <select
          value={orgaoSelecionadoRemovido}
          onChange={(e) => setOrgaoSelecionadoRemovido(e.target.value)}
        >
          {/* <option value="">Selecione um órgão</option>
          {historicoOrgaos.map((orgao, i) => (
            <option key={i} value={orgao}>
              {orgao}
            </option>
          ))} */}
        </select>

          <button
            // onClick={() => {
            //   if (nomeCargoRemovido.trim()) {
            //     setCargos(cargos.filter(c => c.nome !== nomeCargoRemovido || c.orgao !== orgaoSelecionadoRemovido));
            //     setNomeCargoRemovido("");
            //   }
            // }}
          >
            Soft Remove
          </button>

          <button
            // onClick={() => {
            //   if (nomeCargoRemovido.trim()) {
            //     setCargos(cargos.filter(c => c.nome !== nomeCargoRemovido || c.orgao !== orgaoSelecionadoRemovido));
            //     setHistoricoCargos(historicoCargos.filter(c => c.nome !== nomeCargoRemovido || c.orgao !== orgaoSelecionadoRemovido));
            //     setVinculos(vinculos.filter(v => v.cargo.nome !== nomeCargoRemovido || v.cargo.orgao !== orgaoSelecionadoRemovido));
            //     setNomeCargoRemovido("");
            //   }
            // }}
          >
            Hard Remove
          </button>


        </div>





     </div>

    </div>

  </div>


  );
}

export default TestPage;
