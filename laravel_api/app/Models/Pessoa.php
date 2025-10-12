<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

/**
 * Representa a entidade Pessoa.
 * O campo 'ativo' é usado para soft delete/inativação.
 */
class Pessoa extends Model
{
    use HasFactory;

    /**
     * Define o nome da tabela no banco de dados.
     * @var string
     */
    protected $table = 'Pessoa';

    /**
     * Define o nome da chave primária, se for diferente de 'id'.
     * @var string
     */
    protected $primaryKey = 'id_pessoa';

    /**
     * Indica se o ID é auto-incrementado.
     * @var bool
     */
    public $incrementing = true;

    /**
     * Os atributos que são preenchíveis em massa (mass assignable).
     * @var array<int, string>
     */
    protected $fillable = [
        'nome',
        'ativo',
    ];

    /**
     * Define o formato de data para o Eloquent.
     * @var string
     */
    protected $dateFormat = 'Y-m-d H:i:s';

    // Se a tabela 'Pessoa' tivesse o Soft Deletes do Laravel, usaria:
    // use Illuminate\Database\Eloquent\SoftDeletes;
}
