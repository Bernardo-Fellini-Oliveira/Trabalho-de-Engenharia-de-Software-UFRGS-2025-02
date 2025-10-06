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
    if (isset($data['id_pessoa']) {
        
        // SQL com placeholders para todos os valores que vêm do cliente
        $sql = "INSERT INTO Pessoa (id_pessoa, nome) VALUES (?, ?)";
        $stmt = $pdo->prepare($sql);
        
        // Executa a query passando os valores em um array
        $success = $stmt->execute([
            $data['id_pessoa'],
            $data['nome']
        ]);

        if ($success) {
            // Retorna uma resposta de sucesso para o Python
            echo json_encode(['status' => 'success', 'message' => 'Pessoa criada com sucesso!', 'id_pessoa' => $data['id_pessoa']]);
        } else {
            http_response_code(500); // Erro interno do servidor
            echo json_encode(['status' => 'error', 'message' => 'Falha ao inserir pessoa no banco de dados.']);
        }

    } else {
        http_response_code(400); // Bad Request
        echo json_encode(['status' => 'error', 'message' => 'Dados incompletos recebidos.']);
    }
}

?>