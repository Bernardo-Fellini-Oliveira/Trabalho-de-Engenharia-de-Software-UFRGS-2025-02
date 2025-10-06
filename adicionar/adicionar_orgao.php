<?php
$db_file = './Banco.db';
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
    if (isset($data['id_orgao']) {
        
        // SQL com placeholders para todos os valores que vêm do cliente
        $sql = "INSERT INTO Orgao (id_orgao, nome, ativo) VALUES (?, ?, ?)";
        $stmt = $pdo->prepare($sql);
        
        // Executa a query passando os valores em um array
        $success = $stmt->execute([
            $data['id_orgao'],
            $data['nome'],
            $data['ativo']
        ]);

        if ($success) {
            // Retorna uma resposta de sucesso para o Python
            echo json_encode(['status' => 'success', 'message' => 'Orgao criada com sucesso!', 'id_orgao' => $data['id_orgao']]);
        } else {
            http_response_code(500); // Erro interno do servidor
            echo json_encode(['status' => 'error', 'message' => 'Falha ao inserir orgao no banco de dados.']);
        }

    } else {
        http_response_code(400); // Bad Request
        echo json_encode(['status' => 'error', 'message' => 'Dados incompletos recebidos.']);
    }
}

?>