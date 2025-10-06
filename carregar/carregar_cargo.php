<?php
$db_file = __DIR__ . '/Banco.db';

// Define o cabeçalho da resposta como JSON
header('Content-Type: application/json');

//Conectando no banco
try
{
    $pdo = new PDO('sqlite:' . $db_file);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
}
catch (Exception $e) {
    // Se a conexão com o banco falhar, envia um erro 500
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Erro no servidor ao conectar ao banco: ' . $e->getMessage()]);
    exit(); // Para a execução do script
}

//Vendo se estamos recebendo ou enviando
//POST salvando
//GET load
$method = $_SERVER['REQUEST_METHOD'];

// ...
if ($method === 'GET') {

    $stmt = $pdo->query('SELECT * FROM Cargo');
    
    // Use fetchAll() para obter todas as linhas como um array
    $results = $stmt->fetchAll(PDO::FETCH_ASSOC); 

    // O fetchAll retorna um array vazio se não houver resultados,
    // então a verificação 'if' não é estritamente necessária,
    // mas é uma boa prática.
    if ($results) {
        // Simplesmente codifique o array de resultados para JSON
        echo json_encode($results);
    } else {
        // Opcional: retornar um array vazio se a tabela estiver vazia
        echo json_encode([]);
    }
}
//...

?>