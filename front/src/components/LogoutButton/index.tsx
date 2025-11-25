import { useAuth } from "../../context/auth_context";
import { useNavigate } from "react-router-dom";

export default function LogoutButton({logoutText}: {logoutText?: string}) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <button
      onClick={handleLogout}
      style={{backgroundColor: "rgb(154, 0, 0)", color: "white", border: "none", padding: "8px 16px", borderRadius: "4px", cursor: "pointer", marginTop: "20px"}}
    >
        {logoutText || "Sair"}
    </button>
  );
}
