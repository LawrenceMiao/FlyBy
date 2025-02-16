import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Homepage from "./pages/Homepage";
import { BentoDemo } from "./pages/Demo";

function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route path="/" element={<Homepage />}></Route>
          <Route path="/demo" element={<BentoDemo />}></Route>
        </Routes>
      </Router>
    </>
  );
}

export default App;