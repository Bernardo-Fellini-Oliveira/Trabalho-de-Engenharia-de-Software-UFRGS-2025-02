import { createContext, useContext, useState, useEffect } from "react";
import api from "../services/api"; // axios com interceptor
import { getUserMe } from "../services/auth"; // função que chama GET /auth/users/me

interface UserData {
  username: string;
  role: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserData | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  getToken: () => string | null;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<UserData | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    try {
      const data = await getUserMe();
      setUser(data);
      setIsAuthenticated(true);
    } catch {
      setUser(null);
      setIsAuthenticated(false);
    }
    setLoading(false);
  }

  // Carrega ao iniciar
  useEffect(() => {
    const token = localStorage.getItem("token");
      if (token) {
        loadUser();
    } else {
        setLoading(false);
  }
  }, []);

  async function login(token: string) {
    localStorage.setItem("token", token);
    await loadUser();
  }

  function logout() {
    localStorage.removeItem("token");
    setUser(null);
    setIsAuthenticated(false);
    setLoading(false);
  }

  function hasRole(role: string) {
    return user?.role === role;
  }

  function hasAnyRole(roles: string[]) {
    return roles.includes(user?.role ?? "");
  }

  function getToken() {
    return localStorage.getItem("token");
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        login,
        logout,
        getToken,
        hasRole,
        hasAnyRole,
        loading
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de AuthProvider");
  return ctx;
}
