<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Pessoa;
use App\Models\Orgao;
use App\Models\Cargo;
use App\Models\Portaria;
use App\Models\Ocupacao;

class EntidadeController extends Controller
{
    // =========================================================================
    //  PESSOA (Endpoints: /api/pessoa)
    // =========================================================================

    /**
     * Adiciona uma nova pessoa ao banco de dados.
     * POST /api/pessoa
     */
    public function adicionarPessoa(Request $request)
    {
        // 1. Validação dos dados de entrada
        $request->validate([
            'nome' => 'required|string|max:255',
        ]);

        try {
            // 2. Criação da Pessoa usando Eloquent ORM
            $pessoa = Pessoa::create([
                'nome' => $request->input('nome'),
                'ativo' => 1, // Ativo por padrão
            ]);

            // Utiliza 'id_pessoa' como a chave de retorno (definida no Model)
            return response()->json([
                'status' => 'success',
                'message' => 'Pessoa adicionada com sucesso.',
                'id_pessoa' => $pessoa->id_pessoa,
            ], 201); // 201 Created
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Erro ao adicionar Pessoa.',
                'detail' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Carrega todas as pessoas (ativas e inativas).
     * GET /api/pessoa
     */
    public function carregarPessoas()
    {
        $pessoas = Pessoa::all(); 
        return response()->json($pessoas); 
    }

    /**
     * Remove (soft ou hard delete) uma pessoa pelo ID.
     * DELETE /api/pessoa/{id_pessoa}?soft=true
     */
    public function removerPessoa(Request $request, $id_pessoa)
    {
        $soft = $request->query('soft') === 'true';
        $pessoa = Pessoa::find($id_pessoa);

        if (!$pessoa) {
            return response()->json(['message' => 'Pessoa não encontrada.'], 404);
        }

        try {
            if ($soft) {
                // SOFT DELETE: Apenas inativa a pessoa (ativo = 0)
                if ($pessoa->ativo == 0) {
                    return response()->json(['message' => 'Pessoa já está inativa.'], 200);
                }
                $pessoa->ativo = 0;
                $pessoa->save();
                $message = 'Pessoa inativada (soft delete) com sucesso.';
            } else {
                // HARD DELETE: Exclusão permanente
                $pessoa->delete();
                $message = 'Pessoa removida permanentemente (hard delete) com sucesso.';
            }

            return response()->json(['status' => 'success', 'message' => $message], 200);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error', 
                'message' => 'Erro ao remover Pessoa. Verifique se existem vínculos ativos.', 
                'detail' => $e->getMessage()
            ], 500);
        }
    }

    // =========================================================================
    //  ÓRGÃO (Endpoints: /api/orgao)
    // =========================================================================

    /**
     * Adiciona um novo órgão ao banco de dados.
     * POST /api/orgao
     */
    public function adicionarOrgao(Request $request)
    {
        $request->validate([
            'nome' => 'required|string|max:255',
            'ativo' => 'required|boolean', // 0 ou 1
        ]);

        try {
            $orgao = Orgao::create([
                'nome' => $request->input('nome'),
                'ativo' => $request->input('ativo'),
            ]);

            return response()->json([
                'status' => 'success',
                'message' => 'Órgão adicionado com sucesso.',
                'id_orgao' => $orgao->id_orgao,
            ], 201);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Erro ao adicionar Órgão.',
                'detail' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Carrega todos os órgãos.
     * GET /api/orgao
     */
    public function carregarOrgaos()
    {
        $orgaos = Orgao::all(); 
        return response()->json($orgaos); 
    }

    /**
     * Remove (soft ou hard delete) um órgão pelo ID.
     * DELETE /api/orgao/{id_orgao}?soft=true
     */
    public function removerOrgao(Request $request, $id_orgao)
    {
    
        $soft = $request->query('soft') === 'true';
        $orgao = Orgao::find($id_orgao);

        if (!$orgao) {
            return response()->json(['message' => 'Órgão não encontrado.'], 404);
        }

        try {
            if ($soft) {
                // SOFT DELETE: Apenas inativa o órgão
                if ($orgao->ativo == 0) {
                    return response()->json(['message' => 'Órgão já está inativo.'], 200);
                }
                $orgao->ativo = 0;
                $orgao->save();
                $message = 'Órgão inativado (soft delete) com sucesso.';
            } else {
                // HARD DELETE: Exclusão permanente
                $orgao->delete();
                $message = 'Órgão removido permanentemente (hard delete) com sucesso.';
            }

            return response()->json(['status' => 'success', 'message' => $message], 200);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error', 
                'message' => 'Erro ao remover Órgão. Verifique se existem cargos vinculados.', 
                'detail' => $e->getMessage()
            ], 500);
        }
    }

    // =========================================================================
    //  CARGO (Endpoints: /api/cargo)
    // =========================================================================

    /**
     * Adiciona um novo cargo.
     * POST /api/cargo
     */
    public function adicionarCargo(Request $request)
    {
        $request->validate([
            'nome' => 'required|string|max:255',
            'ativo' => 'required|boolean', // 0 ou 1
            'id_orgao' => 'required|integer|exists:Orgao,id_orgao', // Valida se o Órgão existe
        ]);

        try {
            $cargo = Cargo::create($request->all());

            return response()->json([
                'status' => 'success',
                'message' => 'Cargo adicionado com sucesso.',
                'id_cargo' => $cargo->id_cargo,
            ], 201);
        } catch (\Exception $e) {
            return response()->json(['status' => 'error', 'message' => 'Erro ao adicionar Cargo.', 'detail' => $e->getMessage()], 500);
        }
    }

    /**
     * Carrega todos os cargos.
     * GET /api/cargo
     */
    public function carregarCargos()
    {
        // Retorna os cargos com a relação 'orgao' carregada
        $cargos = Cargo::with('orgao')->get(); 
        return response()->json($cargos);
    }

    /**
     * Remove (soft ou hard delete) um cargo pelo ID.
     * DELETE /api/cargo/{id_cargo}?soft=true
     */
    public function removerCargo(Request $request, $id_cargo)
    {
        $soft = $request->query('soft') === 'true';
        $cargo = Cargo::find($id_cargo);

        if (!$cargo) {
            return response()->json(['message' => 'Cargo não encontrado.'], 404);
        }

        try {
            if ($soft) {
                // SOFT DELETE: Apenas inativa o cargo
                if ($cargo->ativo == 0) {
                    return response()->json(['message' => 'Cargo já está inativo.'], 200);
                }
                $cargo->ativo = 0;
                $cargo->save();
                $message = 'Cargo inativado (soft delete) com sucesso.';
            } else {
                // HARD DELETE: Exclusão permanente
                $cargo->delete();
                $message = 'Cargo removido permanentemente (hard delete) com sucesso.';
            }

            return response()->json(['status' => 'success', 'message' => $message], 200);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error', 
                'message' => 'Erro ao remover Cargo. Verifique se existem ocupações vinculadas.', 
                'detail' => $e->getMessage()
            ], 500);
        }
    }

    // =========================================================================
    //  PORTARIA (Endpoints: /api/portaria)
    // =========================================================================

    /**
     * Adiciona uma nova portaria.
     * POST /api/portaria
     */
    public function adicionarPortaria(Request $request)
    {
        $request->validate([
            'numero' => 'required|integer',
            'data' => 'required|date_format:Y-m-d', // Formato de data rigoroso
            'observacoes' => 'nullable|string',
        ]);

        try {
            $portaria = Portaria::create($request->all());

            return response()->json([
                'status' => 'success',
                'message' => 'Portaria adicionada com sucesso.',
                'id_portaria' => $portaria->id_portaria,
            ], 201);
        } catch (\Exception $e) {
            return response()->json(['status' => 'error', 'message' => 'Erro ao adicionar Portaria.', 'detail' => $e->getMessage()], 500);
        }
    }

    /**
     * Carrega todas as portarias.
     * GET /api/portaria
     */
    public function carregarPortarias()
    {
        $portarias = Portaria::all();
        return response()->json($portarias);
    }

    /**
     * Remove (Hard Delete) uma portaria pelo ID.
     * DELETE /api/portaria/{id_portaria}
     */
    public function removerPortaria($id_portaria)
    {
        try {
            $deleted = Portaria::destroy($id_portaria);

            if (!$deleted) {
                 return response()->json(['message' => 'Portaria não encontrada ou já removida.'], 404);
            }

            return response()->json(['status' => 'success', 'message' => 'Portaria removida permanentemente com sucesso.'], 200);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error', 
                'message' => 'Erro ao remover Portaria. Verifique se existem ocupações vinculadas.', 
                'detail' => $e->getMessage()
            ], 500);
        }
    }

    // =========================================================================
    //  OCUPAÇÃO (Endpoints: /api/ocupacao)
    // =========================================================================

    /**
     * Adiciona um novo vínculo de ocupação.
     * POST /api/ocupacao
     */
    public function adicionarOcupacao(Request $request)
    {
        // 1. Validação com verificação de existência das chaves estrangeiras
        $request->validate([
            'id_pessoa' => 'required|integer|exists:Pessoa,id_pessoa',
            'id_cargo' => 'required|integer|exists:Cargo,id_cargo',
            'id_portaria' => 'nullable|integer|exists:Portaria,id_portaria',
            'data_inicio' => 'required|date_format:Y-m-d',
            'data_fim' => 'nullable|date_format:Y-m-d',
            'mandato' => 'required|integer',
            'observacoes' => 'nullable|string',
        ]);

        try {
            $ocupacao = Ocupacao::create($request->all());

            return response()->json([
                'status' => 'success',
                'message' => 'Ocupação adicionada com sucesso.',
                'id_ocupacao' => $ocupacao->id_ocupacao,
            ], 201);
        } catch (\Exception $e) {
            return response()->json(['status' => 'error', 'message' => 'Erro ao adicionar Ocupação.', 'detail' => $e->getMessage()], 500);
        }
    }

    /**
     * Carrega todas as ocupações com detalhes das relações.
     * GET /api/ocupacao
     */
    public function carregarOcupacoes()
    {
        // Carrega as ocupações e as relações (Pessoa, Cargo, Portaria)
        $ocupacoes = Ocupacao::with(['pessoa', 'cargo.orgao', 'portaria'])->get();
        return response()->json($ocupacoes);
    }

    /**
     * Remove (Hard Delete) uma ocupação pelo ID.
     * DELETE /api/ocupacao/{id_ocupacao}
     */
    public function removerOcupacao($id_ocupacao)
    {
        try {
            $deleted = Ocupacao::destroy($id_ocupacao);

            if (!$deleted) {
                 return response()->json(['message' => 'Ocupação não encontrada ou já removida.'], 404);
            }

            return response()->json(['status' => 'success', 'message' => 'Ocupação removida permanentemente com sucesso.'], 200);
        } catch (\Exception $e) {
            return response()->json(['status' => 'error', 'message' => 'Erro ao remover Ocupação.', 'detail' => $e->getMessage()], 500);
        }
    }
}
