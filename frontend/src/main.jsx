import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Import Bootstrap CSS first, then our custom CSS
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Import MDB Bootstrap
import 'mdb-ui-kit/css/mdb.min.css';

// Initialize MDB Bootstrap
import { Collapse, Ripple, initMDB } from "mdb-ui-kit";

initMDB({ Collapse, Ripple });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)