<?php
$db_file = __DIR__ . '/../Banco.db';
header('Content-Type: application/json');

try {
    $pdo = new PDO('sqlite:' . $db_file);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['status' => 'error', 'message' => 'Erro no servidor ao conectar ao banco: ' . $e->getMessage()]);
    exit();
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Pega os dados JSON enviados pelo Python
    $data = json_decode(file_get_contents('php://input'), true);

    // Verifica se os dados necessários foram recebidos
    if (isset($data['id_portaria'])) {
        
        // SQL com placeholders para todos os valores que vêm do cliente
        $sql = "INSERT INTO Portaria (id_portaria, numero, data, observacoes) VALUES (?, ?, ?, ?)";
        $stmt = $pdo->prepare($sql);
        
        // Executa a query passando os valores em um array
        $success = $stmt->execute([
            $data['id_portaria'],
            $data['numero'],
            $data['data'],
            $data['observacoes']
        ]);

        if ($success) {
            // Retorna uma resposta de sucesso para o Python
            echo json_encode(['status' => 'success', 'message' => 'Portaria criada com sucesso!', 'id_portaria' => $data['id_portaria']]);
        } else {
            http_response_code(500); // Erro interno do servidor
            echo json_encode(['status' => 'error', 'message' => 'Falha ao inserir portaria no banco de dados.']);
        }

    } else {
        http_response_code(400); // Bad Request
        echo json_encode(['status' => 'error', 'message' => 'Dados incompletos recebidos.']);
    }
}

?>