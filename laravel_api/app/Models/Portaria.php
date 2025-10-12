<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

/**
 * Representa a entidade Portaria.
 */
class Portaria extends Model
{
    use HasFactory;

    protected $table = 'Portaria';
    protected $primaryKey = 'id_portaria';
    public $incrementing = true;

    protected $fillable = [
        'numero',
        'data',
        'observacoes',
    ];

    // O campo 'data' é armazenado como TEXT no DB (Y-m-d), então não é necessário casting complexo aqui.
    protected $dateFormat = 'Y-m-d';
}
