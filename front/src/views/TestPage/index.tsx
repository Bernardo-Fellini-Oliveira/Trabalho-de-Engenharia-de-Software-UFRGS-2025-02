import React from "react";
import api from '../../services/api'; 
import axios from 'axios';
import "../../../styles-historico.css";


export default function TestPage() {
const logs = [
"DiaTal HoraQualquer Usuário com email1 Adicionou Cargo1",
"DiaTal HoraQualquer Usuário com email2 Associou Pessoa1 a Cargo1",
"DiaTal HoraQualquer Usuário com email3 Inativou Pessoa1",
];


return (
<div className="page">
<div className="header-row">
<button className="back-button">⟲</button>
<h1 className="title">Histórico de Alterações</h1>
</div>


<div className="filter-box">
<h2 className="filter-title">Mostrar:</h2>


<div className="filter-grid">
<label><input type="checkbox" defaultChecked /> Pessoas</label>
<label><input type="checkbox" defaultChecked /> Cargos</label>
<label><input type="checkbox" defaultChecked /> Comissões</label>


<label><input type="checkbox" defaultChecked /> Adições</label>
<label><input type="checkbox" defaultChecked /> Remoções</label>
<label><input type="checkbox" defaultChecked /> Associações</label>


<label><input type="checkbox" defaultChecked /> Inativações</label>
<label><input type="checkbox" defaultChecked /> Reativações</label>
</div>


<div className="search-row">
<input className="search-input" placeholder="Busca por Texto" />
</div>
</div>


<div className="log-list">
{logs.map((log, i) => (
<div key={i} className="log-item">{log}</div>
))}
</div>
</div>
);
}