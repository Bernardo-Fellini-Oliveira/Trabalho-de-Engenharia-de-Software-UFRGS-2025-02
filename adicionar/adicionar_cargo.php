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
    if (isset($data['id_cargo'])) {
        
        // SQL com placeholders para todos os valores que vêm do cliente
        $sql = "INSERT INTO Cargo (id_cargo, nome, ativo, id_orgao) VALUES (?, ?, ?, ?)";
        $stmt = $pdo->prepare($sql);
        
        // Executa a query passando os valores em um array
        $success = $stmt->execute([
            $data['id_cargo'],
            $data['nome'],
            $data['ativo'],
            $data['id_orgao']
        ]);

        if ($success) {
            // Retorna uma resposta de sucesso para o Python
            echo json_encode(['status' => 'success', 'message' => 'Cargo criado com sucesso!', 'id_cargo' => $data['id_cargo']]);
        } else {
            http_response_code(500); // Erro interno do servidor
            echo json_encode(['status' => 'error', 'message' => 'Falha ao inserir o cargo no banco de dados.']);
        }

    } else {
        http_response_code(400); // Bad Request
        echo json_encode(['status' => 'error', 'message' => 'Dados incompletos recebidos.']);
    }
}

?>