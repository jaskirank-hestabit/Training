import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [message, setMessage] = useState("Loading...");

  useEffect(() => {
  fetch(process.env.REACT_APP_BACKEND_URL)
    .then((res) => res.text())
    .then((data) => setMessage(data))
    .catch(() => setMessage("Server not reachable"));
}, []);

  return (
    <div className="container">
      <h1>Docker Multi-Container App</h1>

      <div className="card">
        <h2>Client</h2>
        <p>React app running inside Docker container</p>
      </div>

      <div className="card">
        <h2>Server Response</h2>
        <p>{message}</p>
      </div>

      <div className="card">
        <h2>Architecture</h2>
        <p>React → Node → MongoDB via Docker Compose</p>
      </div>
    </div>
  );
}

export default App;
