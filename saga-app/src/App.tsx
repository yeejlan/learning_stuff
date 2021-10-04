import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
import { connect } from 'react-redux'

import routers from 'router';

function App() {
  return (
    <Router basename={process.env.REACT_APP_BASE_URL}>
      <div>
        <ul>
          {routers.map((one, index) => {
            return (<React.Fragment key={index}>
              <li>
                <Link to={one.path}>{one.name}</Link>
              </li>
            </React.Fragment>)
          })}
        </ul>

        <hr />

        {/*
          A <Switch> looks through all its children <Route>
          elements and renders the first one whose path
          matches the current URL. Use a <Switch> any time
          you have multiple routes, but you want only one
          of them to render at a time
        */}
        <Switch>
        {routers.map((one, index) => {
          return (<Route key={index} {...one} />)
        })}
        </Switch>
      </div>
    </Router>
  );
}

export default connect()(App)