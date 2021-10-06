import React from "react";
import {
  BrowserRouter as Router,
} from "react-router-dom";

import Navbar from './common/navbar';

function App() {
  return (
    <Router basename={process.env.REACT_APP_BASE_URL}>
      <Navbar />
    </Router>
  );
}

export default App