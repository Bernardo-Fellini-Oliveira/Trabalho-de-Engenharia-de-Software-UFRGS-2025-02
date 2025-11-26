import React, { useState, useMemo } from 'react';
import api from '../../services/api'; 
import axios from 'axios';
import 'styles-historico.css';

export default function HistoricoAlteracoes() {

  const logs = [
    "DiaTal HoraQualquer Usuário1 Adicionou Cargo1",
    "DiaTal HoraQualquer Usuário2 Associou Pessoa1 a Cargo1",
    "DiaTal HoraQualquer Usuário3 Inativou Pessoa1",
    ...Array.from({ length: 40 }, (_, i) => `Log adicional número ${i + 1}`)
  ];

  // -------------------- PAGINAÇÃO --------------------
  const pageSize = 10;
  const [page, setPage] = React.useState(1);
  const totalPages = Math.ceil(logs.length / pageSize);
  const start = (page - 1) * pageSize;
  const pageLogs = logs.slice(start, start + pageSize);

  const goFirst = () => setPage(1);
  const goLast = () => setPage(totalPages);
  const goPrev = () => setPage((p) => Math.max(1, p - 1));
  const goNext = () => setPage((p) => Math.min(totalPages, p + 1));

  const pageRange = [];
  for (let p = page - 3; p <= page + 3; p++) {
    if (p >= 1 && p <= totalPages) {
      pageRange.push(p);
    }
  }
  // ---------------------------------------------------

  return (
    <div className="hist-root">
      <header className="hist-header">
        <button className="back-btn">↩</button>
        <h1>Histórico de Alterações</h1>
      </header>

      <section className="filter-bar">
        <div className="filter-title">Mostrar:</div>

        <div className="filter-groups">
          <label><input type="checkbox" defaultChecked /> Adições</label>
          <label><input type="checkbox" defaultChecked /> Remoções</label>
          <label><input type="checkbox" defaultChecked /> Associações</label>
          <label><input type="checkbox" defaultChecked /> Inativações</label>
          <label><input type="checkbox" defaultChecked /> Reativações</label>
        </div>

        <div className="search-area">
          <span>Busca por Texto</span>
          <input type="text" placeholder="Digite..." />
        </div>
      </section>

      <section className="rows-area">
        {pageLogs.map((l, i) => (
          <div className="row" key={i}>{l}</div>
        ))}
      </section>

      {/* -------- PAGINAÇÃO -------- */}
      <div className="pagination">

        <button className="page-btn" onClick={goFirst}>⟪</button>
        <button className="page-btn" onClick={goPrev}>‹</button>

        {pageRange.map((p) => (
          <button
            key={p}
            className={`page-btn ${p === page ? 'active' : ''}`}
            onClick={() => p !== page && setPage(p)}
          >
            {p}
          </button>
        ))}

        <button className="page-btn" onClick={goNext}>›</button>
        <button className="page-btn" onClick={goLast}>⟫</button>
      </div>
      {/* -------------------------- */}

    </div>
  );
}
