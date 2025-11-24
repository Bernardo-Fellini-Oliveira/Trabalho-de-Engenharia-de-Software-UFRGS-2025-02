import React, { useEffect, useState } from 'react';
// Importação direta do Axios para garantir que o código compila em ambientes isolados
// Em um ambiente de projeto local real, você usaria 'import api from "../../services/api";'
import api from '../../services/api';
import axios from 'axios';

import "../../../style-notificacoes.css";


// The design reference image is included at the path provided by you:
// /mnt/data/Tela de Notificações.png


export default function TestPage() {
const rows = [
{
time: "DiaTal HoraQualquer",
user: "Usuário1",
action: "Adicionou",
target: "Cargo1",
rules: ["Regra1", "Regra3"],
},
{
time: "DiaTal HoraQualquer",
user: "Usuário2",
action: "Associou",
target: "Pessoa1 a Cargo1",
rules: ["Regra1"],
},
{
time: "DiaTal HoraQualquer",
user: "Usuário3",
action: "Inativou",
target: "Pessoa1",
rules: ["Regra2"],
},
];


return (
<div className="page-root">
<header className="top-bar">
<button className="back-btn" aria-label="voltar">↺</button>
<h1 className="title">Notificações</h1>
</header>


<section className="tab-strip">
<div className="tab-left">Alteração</div>
<div className="tab-right">Regras<br/>Violadas</div>
</section>


<main className="list-area">
{rows.map((r, i) => (
<article key={i} className="notif-row">
<div className="notif-left">
<div className="col time">{r.time}</div>
<div className="col user">{r.user}</div>
<div className="col action">{r.action}</div>
<div className="col target">{r.target}</div>
</div>
<div className="notif-right">
{r.rules.map((rule, j) => (
<div key={j} className="rule">{rule}</div>
))}
</div>
</article>
))}
</main>


<footer className="reference">
{/* reference image shown only for comparison / optional */}
<img src="/mnt/data/Tela de Notificações.png" alt="design reference" />
</footer>
</div>
);
}
