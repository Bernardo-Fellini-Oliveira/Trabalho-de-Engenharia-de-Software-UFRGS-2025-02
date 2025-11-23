import { BrowserRouter, Route, Routes } from "react-router-dom";
import TestPage from "./views/TestPage";
import SearchPage from "./views/SearchPage";
import EditPage from "./views/EditPage";


function App() {

  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<TestPage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/edit" element={<EditPage />} />
        </Routes>
      </BrowserRouter>

    </>
  )
}

export default App
