import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

import routers from 'router';

function App() {
  return (
    <Router basename={process.env.REACT_APP_BASE_URL}>
      <div>
        <ul>
          {routers.map((one, i) => (
            <React.Fragment key={i}>
              <li>
                <Link to={one.path}>{one.name}</Link>
              </li>
            </React.Fragment>
          ))}
        </ul>

        <hr />

        <Switch>
        {routers.map((one, i) => (
          <Route key={i} {...one} />
        ))}
        </Switch>
      </div>
    </Router>
  );
}

export default App