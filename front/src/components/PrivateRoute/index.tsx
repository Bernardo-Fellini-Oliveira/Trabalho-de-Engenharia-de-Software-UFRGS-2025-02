import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/auth_context";
import { useEffect, useState, type JSX } from "react";

interface PrivateRouteProps {
  children: JSX.Element;
  roles?: string[]; // EX: ["admin"]
}

export default function PrivateRoute({ children, roles }: PrivateRouteProps) {
  const { isAuthenticated, hasAnyRole, loading } = useAuth();

  if (loading) {
    return <div style={{width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center"}}>Carregando...</div>;
  }

  // Se está autenticado mas não tem a role necessária, dá um alerta e redireciona para a home
  if (roles && !hasAnyRole(roles)){
    return <AccessDeniedRedirect />;
  }


  function AccessDeniedRedirect() {
    const [notified, setNotified] = useState(false);

    useEffect(() => {
      if (!notified) {
        alert("Você não tem permissão para acessar esta página.");
        setNotified(true);
      }
    }, [notified]);

    console.log("Redirecionando usuário sem permissão para a página inicial.");
    console.log("Current path:", window.location.pathname);
    if (window.location.pathname !== "/")
      return <Navigate to="/" replace />;
    return null;
  }


  return children;
}
