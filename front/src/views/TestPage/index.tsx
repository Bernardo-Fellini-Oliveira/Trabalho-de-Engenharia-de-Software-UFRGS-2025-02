import { useState } from "react";

function TestPage() {
  const [pessoas, setPessoas] = useState<string[]>([]);
  const [orgaos, setOrgaos] = useState<string[]>([]);
  const [cargos, setCargos] = useState<{ nome: string; orgao: string }[]>([]);
  const [vinculos, setVinculos] = useState<{ pessoa: string; cargo: string }[]>([]);

  const [nomePessoa, setNomePessoa] = useState<string>("");
  const [nomeOrgao, setNomeOrgao] = useState<string>("");
  const [nomeCargo, setNomeCargo] = useState<string>("");
  const [orgaoSelecionado, setOrgaoSelecionado] = useState<string>("");
  const [pessoaSelecionada, setPessoaSelecionada] = useState<string>("");
  const [cargoSelecionado, setCargoSelecionado] = useState<string>("");

  return (
    <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "16px" }}>
      <h1>Página de Teste</h1>

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
          value={cargoSelecionado}
          onChange={(e) => setCargoSelecionado(e.target.value)}
        >
          <option value="">Selecione um cargo</option>
          {cargos.map((c, i) => (
            <option key={i} value={`${c.nome} (${c.orgao})`}>
              {c.nome} ({c.orgao})
            </option>
          ))}
        </select>

        <button
          onClick={() => {
            if (pessoaSelecionada && cargoSelecionado) {
              setVinculos([...vinculos, { pessoa: pessoaSelecionada, cargo: cargoSelecionado }]);
              setPessoaSelecionada("");
              setCargoSelecionado("");
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
        <p>
          <strong>Vínculos:</strong>{" "}
          {vinculos.length
            ? vinculos.map((v) => `${v.pessoa} -> ${v.cargo}`).join(", ")
            : "Nenhum"}
        </p>
      </div>
    </div>
  );
}

export default TestPage;
