<?php
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\EntidadeController; // Certifique-se de que o namespace e o nome da classe estão corretos.

// ... suas rotas ...

Route::get('/', function () {
    return response()->json(['message' => 'API is running']);
});

// Rotas para Pessoa
Route::post('/pessoa', [EntidadeController::class, 'adicionarPessoa']);
Route::get('/pessoa', [EntidadeController::class, 'carregarPessoas']);
Route::delete('/pessoa/delete/{id_pessoa}', [EntidadeController::class, 'removerPessoa']);

// Rotas para Órgão
Route::post('/orgao', [EntidadeController::class, 'adicionarOrgao']);
Route::get('/orgao', [EntidadeController::class, 'carregarOrgaos']);
Route::delete('/orgao/delete/{id_orgao}', [EntidadeController::class, 'removerOrgao']);

// Rotas para Portaria
Route::post('/portaria', [EntidadeController::class, 'adicionarPortaria']);
Route::get('/portaria', [EntidadeController::class, 'carregarPortarias']);
Route::delete('/portaria/delete/{id_portaria}', [EntidadeController::class, 'removerPortaria']);

// Rotas para Cargo
Route::post('/cargo', [EntidadeController::class, 'adicionarCargo']);
Route::get('/cargo', [EntidadeController::class, 'carregarCargos']);
Route::delete('/cargo/delete/{id_cargo}', [EntidadeController::class, 'removerCargo']);

// Rotas para Ocupacao
Route::post('/ocupacao', [EntidadeController::class, 'adicionarOcupacao']);
Route::get('/ocupacao', [EntidadeController::class, 'carregarOcupacoes']);
Route::delete('/ocupacao/delete/{id_ocupacao}', [EntidadeController::class, 'removerOcupacao']);