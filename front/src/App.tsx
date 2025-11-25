import { BrowserRouter, Route, Routes } from "react-router-dom";
import TestPage from "./views/TestPage";
import SearchPage from "./views/SearchPage";
import EditPage from "./views/EditPage";
import TicketsPage from "./views/TicketsPage";
import LogPage from "./views/LogPage";
import HomePage from "./views/HomePage";


function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/insert" element={<TestPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/edit" element={<EditPage />} />
          <Route path="/tickets" element={<TicketsPage />} />
          <Route path="/log" element={<LogPage />} />
        </Routes>
      </BrowserRouter>

    </>
  )
}

export default App
