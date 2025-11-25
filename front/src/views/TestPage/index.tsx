// Updated NotificationPage.jsx
import React from 'react';
import api from "../../services/api";
import axios from "axios";
import "../../../style-notificacoes.css";

export default function NotificationPage() {
  const allRows = [
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

  const [page, setPage] = React.useState(1);
  const pageSize = 10;
  const totalPages = Math.ceil(allRows.length / pageSize) || 1;
  const [selected, setSelected] = React.useState([]);

  const pageRows = allRows.slice((page - 1) * pageSize, page * pageSize);

  const toggleSelect = (index) => {
    setSelected((prev) =>
      prev.includes(index) ? prev.filter((i) => i !== index) : [...prev, index]
    );
  };

  const selectAll = () => {
    const indices = pageRows.map((_, i) => i);
    setSelected(indices);
  };

  const goFirst = () => setPage(1);
  const goLast = () => setPage(totalPages);
  const goPrev = () => setPage((p) => Math.max(1, p - 1));
  const goNext = () => setPage((p) => Math.min(totalPages, p + 1));

  const pageNumbers = [];
  for (let i = page - 3; i <= page + 3; i++) {
    if (i >= 1 && i <= totalPages) pageNumbers.push(i);
  }

  const [showPopup, setShowPopup] = React.useState(false);
  const [popupMessage, setPopupMessage] = React.useState("");

  React.useEffect(() => {
    const h = (e) => {
      if (e.key === "Enter") {
        document.querySelector(".decidir-btn")?.click();
      }
    };
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, []);

  return (
    <div className="page-root">
      <header className="top-bar">
        <button className="back-btn" aria-label="voltar">↺</button>
        <h1 className="title">Notificações</h1>
      </header>

      <section className="tab-strip">
        <div className="tab-left">Alteração</div>
        <div className="tab-right">Regras<br />Violadas</div>
      </section>

      <div className="bulk-actions">
        <button className="custom-btn" onClick={selectAll}>Selecionar todas</button>
        <button
          className="decidir-btn custom-btn"
          onClick={() => {
            if (selected.length === 0) {
              setPopupMessage("Nenhuma violação selecionada para decidir");
              setShowPopup(true);
            } else {
              setPopupMessage("Ignorar regras e aceitar alterações?");
              setShowPopup(true);
            }
          }}
        >
          Decidir
        </button>
      </div>

      <main className="list-area">
        {pageRows.map((r, i) => (
          <article
            key={i}
            className={
              "notif-row " + (selected.includes(i) ? "selected" : "")
            }
            onClick={() => toggleSelect(i)}
          >
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

        <div className="pagination">
          <button onClick={goFirst}>&laquo;</button>
          <button onClick={goPrev}>&lsaquo;</button>

          {pageNumbers.map((num) => (
            <button
              key={num}
              onClick={() => setPage(num)}
              className={num === page ? "current" : ""}
            >
              {num}
            </button>
          ))}

          <button onClick={goNext}>&rsaquo;</button>
          <button onClick={goLast}>&raquo;</button>
        </div>
      </main>

      {showPopup && (
        <div className="popup-overlay" onClick={() => setShowPopup(false)}>
          <div className="popup-box" onClick={(e) => e.stopPropagation()}>
            <div className="popup-text">{popupMessage}</div>

            {popupMessage !== "Nenhuma violação selecionada para decidir" && (
              <div className="popup-buttons">
                <button
                  className="custom-btn"
                  onClick={() => setShowPopup(false)}
                >
                  Permitir
                </button>

                <button
                  className="custom-btn"
                  onClick={() => setShowPopup(false)}
                >
                  Recusar
                </button>
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
}
