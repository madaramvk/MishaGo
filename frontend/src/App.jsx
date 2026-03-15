import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState, useEffect } from "react";
import NavBar from "./components/NavBar";
import GucciHome from "./pages/GucciHome";
import Goals from "./pages/Goals";
import DayCanvas from "./pages/DayCanvas";
import Me from "./pages/Me";
import GoalChat from "./components/GoalChat";
import ErrorBoundary from "./components/ErrorBoundary";
import "./themes/variables.css";
import "./App.css";

export default function App() {
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <ErrorBoundary>
        <div className="app">
          <div className="page-content">
            <Routes>
              <Route path="/" element={<GucciHome />} />
              <Route path="/goals" element={<Goals />} />
              <Route path="/goals/:goalId/chat" element={<GoalChat />} />
              <Route path="/day" element={<DayCanvas />} />
              <Route path="/me" element={<Me setTheme={setTheme} theme={theme} />} />
            </Routes>
          </div>
          <NavBar />
        </div>
      </ErrorBoundary>
    </BrowserRouter>
  );
}
