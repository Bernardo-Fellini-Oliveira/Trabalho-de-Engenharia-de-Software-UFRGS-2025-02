import { BrowserRouter, Route, Routes } from "react-router-dom";
import TestPage from "./views/TestPage";
import SearchPage from "./views/SearchPage";
import EditPage from "./views/EditPage";
import TicketsPage from "./views/TicketsPage";
import LogPage from "./views/LogPage";
import HomePage from "./views/HomePage";
import EligibilityPage from "./views/EligibilityPage";
import RegisterScreen from "./views/RegisterScreen";
import LoginScreen from "./views/LoginScreen";
import { AuthProvider } from "./context/auth_context";
import PrivateRoute from "./components/PrivateRoute";


function App() {

  return (
    <>
      <BrowserRouter>

      <AuthProvider>
        <Routes>

          {/* ROTAS PÚBLICAS */}
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/login" element={<LoginScreen />} />
          <Route path="/check" element={<EligibilityPage />} />

          {/* PROTEGIDAS POR AUTENTICAÇÃO - NÍVEL ADMIN */}
          <Route path="/signup" element={<PrivateRoute><RegisterScreen/></PrivateRoute>} />
          <Route path="/insert" element={<PrivateRoute><TestPage /></PrivateRoute>} />
          <Route path="/edit" element={<PrivateRoute><EditPage /></PrivateRoute>} />
          <Route path="/log" element={<PrivateRoute><LogPage /></PrivateRoute>} />

          {/* PROTEGIDAS POR AUTENTICAÇÃO - NÍVEL SUPER ADMIN */}
          <Route path="/tickets" element={<PrivateRoute roles={["admin"]}><TicketsPage /></PrivateRoute>} />


        </Routes>

      </AuthProvider>
      </BrowserRouter>

    </>
  )
}

export default App
