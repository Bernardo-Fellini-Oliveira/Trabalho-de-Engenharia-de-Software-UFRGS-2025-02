import { BrowserRouter, Route, Routes } from "react-router-dom";
import TestPage from "./views/TestPage";
import SearchPage from "./views/SearchPage";
import TicketsPage from "./views/TicketsPage";


function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<TestPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/tickets" element={<TicketsPage />} />
        </Routes>
      </BrowserRouter>

    </>
  )
}

export default App
