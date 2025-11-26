import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import '../../../styles.css' 
import './EligibilityPage.css';
import Header from '../../components/Header';
import { useAuth } from '../../context/auth_context';

// === Interfaces de Tipagem ===
interface PessoaDB { id_pessoa: number; nome: string; ativo: boolean; }
interface OrgaoDB { id_orgao: number; nome: string; ativo: boolean; }
interface CargoDB { id_cargo: number; nome: string; ativo: boolean; id_orgao: number; }

const EligibilityPage: React.FC = () => {
    // === Estados para Armazenar Dados da API ===
    const [dbPessoas, setDbPessoas] = useState<PessoaDB[]>([]);
    const [dbOrgaos, setDbOrgaos] = useState<OrgaoDB[]>([]);
    const [dbCargos, setDbCargos] = useState<CargoDB[]>([]);

    // === Estados do Formulário ===
    const [selectedPessoa, setSelectedPessoa] = useState('');
    const [selectedCargo, setSelectedCargo] = useState('');
    const [selectedDate, setSelectedDate] = useState('');

    const [loading, setLoading] = useState(false);

    const {user} = useAuth();

    
    // === 1. Carregar dados ao montar a página ===
    useEffect(() => {
        const loadData = async () => {
            try {
                const [p, o, c] = await Promise.all([
                    api.get<PessoaDB[]>('/pessoa/'),
                    api.get<OrgaoDB[]>('/orgao/'),
                    api.get<CargoDB[]>('/cargo/')
                ]);
                setDbPessoas(p.data);
                setDbOrgaos(o.data);
                setDbCargos(c.data);
            } catch (err) {
                console.error("Erro ao carregar dados para verificação", err);
                alert("Erro ao carregar listas de seleção.");
            }
        };
        loadData();
    }, []);

    // === Helpers ===
    const getOrgaoName = (id: number) => dbOrgaos.find(o => o.id_orgao === id)?.nome || 'Desc.';

    const extractId = (val: string): number | null => {
        if (!val) return null;
        const parts = val.split(' - ');
        const id = parseInt(parts[0]);
        return isNaN(id) ? null : id;
    };

    // === Ação de Verificar ===
    const handleVerify = async () => {
        const idPessoa = extractId(selectedPessoa);
        const idCargo = extractId(selectedCargo);

        if (!idPessoa || !idCargo || !selectedDate) {
            alert("Por favor, preencha todos os campos corretamente (selecione opções da lista).");
            return;
        }

        // Prepara o payload para futura chamada ao backend
        const payload = {
            id_pessoa: idPessoa,
            id_cargo: idCargo,
            data_inicio: selectedDate
        };

        setLoading(true);
        
        // --- PLACEHOLDER: Aqui chamaremos o backend no futuro ---

        try{
            const response = await api.get('/elegibilidade/verificar_elegibilidade?id_pessoa=' + payload.id_pessoa + '&id_cargo=' + payload.id_cargo + '&data_inicio=' + payload.data_inicio);
            alert(response.data.elegivel ? "A pessoa é elegível para o cargo." : `A pessoa NÃO é elegível para o cargo. Motivo: ${response.data.detalhe || 'Não especificado.'}`);
        } catch (error : any) {
            alert("Erro na verificação: " + error.message);
        }

        setLoading(false);

    };

    return (
        <div className="eligibility-wrapper">

            <Header role={user?.role} />

 
            {/* DATALISTS (Invisíveis, usados pelos inputs) */}
            <datalist id="dl-pessoas-eleg">
                {dbPessoas.map(p => p.ativo && (
                    <option key={p.id_pessoa} value={`${p.id_pessoa} - ${p.nome}`} />
                ))}
            </datalist>

            <datalist id="dl-cargos-eleg">
                {dbCargos.map(c => c.ativo && (
                    <option key={c.id_cargo} value={`${c.id_cargo} - ${c.nome} (${getOrgaoName(c.id_orgao)})`} />
                ))}
            </datalist>

            {/* CONTEÚDO DA PÁGINA */}
            <div className="topo">
                <h1>Verificar Elegibilidade</h1>
                <p>
                    Coloque a pessoa, o cargo desejado e a possível data de início do mandato.<br></br> 
                    Deve aparecer na tela se a pessoa pode se candidatar a essa vaga ou não.
                </p>
            </div>

            <div className="conteudo">
                <div className="form-box">
                    
                    {/* Input Pessoa */}
                    <div id="c_pessoa" className="input_container normal input">
                        <div className="numero-item">
                            Pessoa:<br />
                            <input 
                                list="dl-pessoas-eleg"
                                type="text" 
                                placeholder="Busque a pessoa..."
                                value={selectedPessoa}
                                onChange={(e) => setSelectedPessoa(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    {/* Input Cargo */}
                    <div id="c_cargo" className="input_container normal input">
                        <div className="numero-item">
                            Cargo:<br />
                            <input 
                                list="dl-cargos-eleg"
                                type="text" 
                                placeholder="Busque o cargo..."
                                value={selectedCargo}
                                onChange={(e) => setSelectedCargo(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    {/* Input Data */}
                    <div id="c_data_c" className="input_container normal input">
                        <div className="numero-item">
                            Data de Começo:<br />
                            <input 
                                type="date" 
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                required
                            />
                        </div>
                    </div>

                    <button 
                        onClick={handleVerify} 
                        className="botao botao-confirmar"
                        disabled={loading}
                    >
                        {loading ? 'Verificando...' : 'Verificar'}
                    </button>

                </div>
            </div>
        </div>
    );
};

export default EligibilityPage;