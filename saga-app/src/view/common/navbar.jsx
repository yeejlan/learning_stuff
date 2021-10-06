import { Tabs, Tab } from 'react-bootstrap';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";

function Navbar() {
  return (
<>
<Tabs id="navbar-tab-menu" className="mb-3">
{routers.map((one, i) => (
  <Tab title={one.name}>
    <li>
      <Link to={one.path}>{one.name}</Link>
    </li>
  </React.Fragment>
))}
  <Tab eventKey="home" title="Home">
    <Button style={{marginLeft: '10px'}} variant="primary">Primary</Button>
  </Tab>
  <Tab eventKey="profile" title="Profile">
    bbb
  </Tab>
  <Tab eventKey="contact" title="Contact">
    ccc
  </Tab>
</Tabs>
<Switch>
{routers.map((one, i) => (
  <Route key={i} {...one} />
))}
</Switch>
</>
  );
}

export default Navbar;