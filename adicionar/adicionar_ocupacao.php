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
    if (isset($data['id_ocupacao'])) {
        
        // SQL com placeholders para todos os valores que vêm do cliente
        $sql = "INSERT INTO Ocupacao (id_ocupacao, id_pessoa, id_cargo, id_portaria, data_inicio, data_fim, mandato, observacoes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        $stmt = $pdo->prepare($sql);
        
        // Executa a query passando os valores em um array
        $success = $stmt->execute([
            $data['id_ocupacao'],
            $data['id_pessoa'],
            $data['id_cargo'],
            $data['id_portaria'],
            $data['data_inicio'],
            $data['data_fim'],
            $data['mandato'],
            $data['observacoes']
        ]);

        if ($success) {
            // Retorna uma resposta de sucesso para o Python
            echo json_encode(['status' => 'success', 'message' => 'Ocupacao criada com sucesso!', 'id_ocupacao' => $data['id_ocupacao']]);
        } else {
            http_response_code(500); // Erro interno do servidor
            echo json_encode(['status' => 'error', 'message' => 'Falha ao inserir ocupacao no banco de dados.']);
        }

    } else {
        http_response_code(400); // Bad Request
        echo json_encode(['status' => 'error', 'message' => 'Dados incompletos recebidos.']);
    }
}

?>