<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

/**
 * Representa a entidade Cargo.
 */
class Cargo extends Model
{
    use HasFactory;

    protected $table = 'Cargo';
    protected $primaryKey = 'id_cargo';
    public $incrementing = true;

    protected $fillable = [
        'nome',
        'ativo',
        'id_orgao',
    ];

    protected $dateFormat = 'Y-m-d H:i:s';

    // Relação: Um cargo pertence a um órgão
    public function orgao()
    {
        return $this->belongsTo(Orgao::class, 'id_orgao', 'id_orgao');
    }
}
