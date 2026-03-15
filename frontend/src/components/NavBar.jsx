import { NavLink } from "react-router-dom";
import "./NavBar.css";

const tabs = [
  { path: "/", icon: "🐱", label: "Gucci" },
  { path: "/goals", icon: "🎯", label: "Goals" },
  { path: "/day", icon: "📅", label: "Day" },
  { path: "/me", icon: "👤", label: "Me" },
];

export default function NavBar() {
  return (
    <nav className="navbar">
      {tabs.map((tab) => (
        <NavLink
          key={tab.path}
          to={tab.path}
          className={({ isActive }) => `nav-tab ${isActive ? "active" : ""}`}
          end={tab.path === "/"}
        >
          <span className="nav-icon">{tab.icon}</span>
          <span className="nav-label">{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
