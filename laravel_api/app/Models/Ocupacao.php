<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

/**
 * Representa a entidade Ocupacao (Vínculo Pessoa-Cargo).
 */
class Ocupacao extends Model
{
    use HasFactory;

    protected $table = 'Ocupacao';
    protected $primaryKey = 'id_ocupacao';
    public $incrementing = true;

    protected $fillable = [
        'id_pessoa',
        'id_cargo',
        'id_portaria',
        'data_inicio',
        'data_fim',
        'mandato',
        'observacoes',
    ];

    // Relações de Chave Estrangeira
    public function pessoa()
    {
        return $this->belongsTo(Pessoa::class, 'id_pessoa', 'id_pessoa');
    }

    public function cargo()
    {
        return $this->belongsTo(Cargo::class, 'id_cargo', 'id_cargo');
    }

    public function portaria()
    {
        return $this->belongsTo(Portaria::class, 'id_portaria', 'id_portaria');
    }
}
