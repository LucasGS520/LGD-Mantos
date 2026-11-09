import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { NavProvider } from "./app/nav";
import { Session } from "./modules/auth";
import { configureAuthentication } from "./shared/api/http";
import "./styles/global.css";
import "./styles/tokens.css";
import "./styles/workspace.css";

configureAuthentication(Session);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <NavProvider>
      <App />
    </NavProvider>
  </StrictMode>,
);
