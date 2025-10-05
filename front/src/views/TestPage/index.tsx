import { useState } from "react";

function TestPage() {
  const [historicoPessoas, setHistoricoPessoas] = useState<string[]>([]);
  const [pessoas, setPessoas] = useState<string[]>([]);

  const [historicoOrgaos, setHistoricoOrgaos] = useState<string[]>([]);
  const [orgaos, setOrgaos] = useState<string[]>([]);

  const [historicoCargos, setHistoricoCargos] = useState<{ nome: string; orgao: string }[]>([]);
  const [cargos, setCargos] = useState<{ nome: string; orgao: string }[]>([]);

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

  
  function handleRemoveVinculo(v: { pessoa: string; cargo: { nome: string; orgao: string; }; data: string; }): void {
    console.log('Removendo vínculo:', v.pessoa, v.cargo, v.data);
    setVinculos(vinculos.filter((item) => item !== v));
  }

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
          onClick={() => {
            if (nomePessoa.trim()) {
              setHistoricoPessoas([...historicoPessoas, nomePessoa]);
              setPessoas([...pessoas, nomePessoa]);
              setNomePessoa("");
            }
          }}
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
              setOrgaos([...orgaos, nomeOrgao]);
              setHistoricoOrgaos([...historicoOrgaos, nomeOrgao]);
              setNomeOrgao("");
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
            <option key={i} value={orgao}>
              {orgao}
            </option>
          ))}
        </select>
        <button
          onClick={() => {
            if (nomeCargo.trim()) {
              setCargos([...cargos, { nome: nomeCargo, orgao: orgaoSelecionado }]);
              setHistoricoCargos([...historicoCargos, { nome: nomeCargo, orgao: orgaoSelecionado }]);
              setNomeCargo("");
              setOrgaoSelecionado("");
            }
          }}
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
            <option key={i} value={p}>
              {p}
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
          {cargos.map((c, i) => (
            <option key={i} value={`${c.nome} (${c.orgao})`}>
              {c.nome} ({c.orgao})
            </option>
          ))}
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
          {cargos.length
            ? cargos.map((c) => `${c.nome} (${c.orgao})`).join(", ")
            : "Nenhum"}
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
          {historicoCargos.length
            ? historicoCargos.map((c) => `${c.nome} (${c.orgao})`).join(", ")
            : "Nenhum"}
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
            onClick={() => {
              if (nomePessoaRemovida.trim()) {
                setPessoas(pessoas.filter(p => p !== nomePessoaRemovida));
                setNomePessoaRemovida("");
              }
            }}
          >
            Soft Remove
          </button>

          <button
            onClick={() => {
              if (nomePessoaRemovida.trim()) {
                setPessoas(pessoas.filter(p => p !== nomePessoaRemovida));
                setHistoricoPessoas(historicoPessoas.filter(p => p !== nomePessoaRemovida));
                setVinculos(vinculos.filter(v => v.pessoa !== nomePessoaRemovida));
                setNomePessoaRemovida("");
              }
            }}
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
            onClick={() => {
              if (nomeOrgaoRemovido.trim()) {
                setOrgaos(orgaos.filter(o => o !== nomeOrgaoRemovido));
                setCargos(cargos.filter(c => c.orgao !== nomeOrgaoRemovido));
                setNomeOrgao("");
              }
            }}
          >
            Soft Remove
          </button>

          <button
            onClick={() => {
              if (nomeOrgaoRemovido.trim()) {
                setOrgaos(orgaos.filter(o => o !== nomeOrgaoRemovido));
                setCargos(cargos.filter(c => c.orgao !== nomeOrgaoRemovido));
                setHistoricoCargos(historicoCargos.filter(c => c.orgao !== nomeOrgaoRemovido));
                setHistoricoOrgaos(historicoOrgaos.filter(o => o !== nomeOrgaoRemovido));
                setVinculos(vinculos.filter(v => v.cargo !== null && v.cargo.orgao !== nomeOrgaoRemovido));
                setNomeOrgaoRemovido("");
              }
            }}
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
          <option value="">Selecione um órgão</option>
          {historicoOrgaos.map((orgao, i) => (
            <option key={i} value={orgao}>
              {orgao}
            </option>
          ))}
        </select>

          <button
            onClick={() => {
              if (nomeCargoRemovido.trim()) {
                setCargos(cargos.filter(c => c.nome !== nomeCargoRemovido || c.orgao !== orgaoSelecionadoRemovido));
                setNomeCargoRemovido("");
              }
            }}
          >
            Soft Remove
          </button>

          <button
            onClick={() => {
              if (nomeCargoRemovido.trim()) {
                setCargos(cargos.filter(c => c.nome !== nomeCargoRemovido || c.orgao !== orgaoSelecionadoRemovido));
                setHistoricoCargos(historicoCargos.filter(c => c.nome !== nomeCargoRemovido || c.orgao !== orgaoSelecionadoRemovido));
                setVinculos(vinculos.filter(v => v.cargo.nome !== nomeCargoRemovido || v.cargo.orgao !== orgaoSelecionadoRemovido));
                setNomeCargoRemovido("");
              }
            }}
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
