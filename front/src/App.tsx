import { BrowserRouter, Route, Routes } from "react-router-dom";
import TestPage from "./views/InputPage";
import SearchPage from "./views/SearchPage";
import EditPage from "./views/EditPage";
import TicketsPage from "./views/TicketsPage";
import LogPage from "./views/LogPage";
import HomePage from "./views/HomePage";
import EligibilityPage from "./views/EligibilityPage";
import LoginPage from "./views/LoginPage";
import { AuthProvider } from "./context/auth_context";
import PrivateRoute from "./components/PrivateRoute";
import RegisterPage from "./views/RegisterPage";


function App() {

  return (
    <>
      <BrowserRouter>

      <AuthProvider>
        <Routes>

          {/* ROTAS PÚBLICAS */}
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/check" element={<EligibilityPage />} />

          {/* PROTEGIDAS POR AUTENTICAÇÃO - NÍVEL USUARIO */}
          <Route path="/insert" element={<PrivateRoute><TestPage /></PrivateRoute>} />
          <Route path="/edit" element={<PrivateRoute><EditPage /></PrivateRoute>} />
          <Route path="/log" element={<PrivateRoute><LogPage /></PrivateRoute>} />

          {/* PROTEGIDAS POR AUTENTICAÇÃO - NÍVEL ADMIN */}
          <Route path="/tickets" element={<PrivateRoute roles={["admin"]}><TicketsPage /></PrivateRoute>} />
          <Route path="/signup" element={<PrivateRoute roles= {["admin"]}><RegisterPage /></PrivateRoute>} />

        </Routes>

      </AuthProvider>
      </BrowserRouter>

    </>
  )
}

export default App
