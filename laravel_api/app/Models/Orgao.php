<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

/**
 * Representa a entidade Orgao.
 * O campo 'ativo' é usado para soft delete/inativação.
 */
class Orgao extends Model
{
    use HasFactory;

    /**
     * Define o nome da tabela no banco de dados.
     * @var string
     */
    protected $table = 'Orgao';

    /**
     * Define o nome da chave primária.
     * @var string
     */
    protected $primaryKey = 'id_orgao';

    /**
     * Indica se o ID é auto-incrementado.
     * @var bool
     */
    public $incrementing = true;

    /**
     * Os atributos que são preenchíveis em massa.
     * @var array<int, string>
     */
    protected $fillable = [
        'nome',
        'ativo',
    ];

    /**
     * Define o formato de data.
     * @var string
     */
    protected $dateFormat = 'Y-m-d H:i:s';
}
