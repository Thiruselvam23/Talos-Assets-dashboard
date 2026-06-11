import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import ChartPage from "./pages/ChartPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chart/:chartId" element={<ChartPage />} />
      </Routes>
    </BrowserRouter>
  );
}