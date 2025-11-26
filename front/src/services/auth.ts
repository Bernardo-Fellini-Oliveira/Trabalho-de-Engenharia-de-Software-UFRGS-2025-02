import api from "./api";


export async function loginRequest(username: string, password: string) {
  const data = new URLSearchParams();
  data.append("username", username);
  data.append("password", password);
  data.append("grant_type", "password");

  const resp = await api.post("/auth/token", data, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  console.log("loginRequest: received response:", resp.data);

  return resp.data.access_token as string;
}


// 💡 MUDANÇA: O retorno agora é Promise<void> ou o tipo de dados simples
// que o backend retornar (ex: dados do usuário sem o token).
// Vamos retornar Promise<void> para simplificar.
export async function signUpRequest(username: string, password: string): Promise<void> {
    
    const endpoint = "/auth/register/"; 

    const data = {
        username: username,
        password: password,
        // Adicione outros campos obrigatórios do seu modelo Pydantic User aqui
    };
    
    try {
        // Envia a requisição. Não precisamos do retorno, apenas do status de sucesso.
        await api.post(endpoint, data); 

        // Se o post for bem-sucedido, a função retorna implicitamente.
        
    } catch (error) {
        console.error("signUpRequest: Registration failed.", error);
        // Lança o erro para que a tela possa exibir a mensagem apropriada
        throw error; 
    }
}
export async function getUserMe() {
  const resp = await api.get("/auth/users/me/");
  return resp.data;
}

//
// LOGOUT
//
export function logout() {
  localStorage.removeItem("token");
}

//
// PEGAR USUÁRIO LOGADO
//
export async function getCurrentUser() {
  const response = await api.get("/auth/users/me/");
  return response.data;
}

//
// PEGAR ROLE DO USUÁRIO (se existir no seu backend)
//
export async function getUserRole() {
  const user = await getCurrentUser();
  return user.role || user.roles || null;
}

//
// VERIFICAR SE ESTÁ AUTENTICADO
//
export function isAuthenticated() {
  return !!localStorage.getItem("token");
}
