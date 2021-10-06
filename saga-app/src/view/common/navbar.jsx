import { Container, Nav } from 'react-bootstrap';
import {
  Switch,
  Route,
  useLocation,
  Link,
} from "react-router-dom";
import routers from 'router';
import classnames from 'classnames';

function Navbar() {

  const location = useLocation();
  return (
<>
  <Container className="mt-2" >
      <Nav variant="tabs" defaultActiveKey="/">
        {routers.map((one, i) => (
          <Nav.Item key={i}>
            <Link role="button" 
              className={classnames('nav-link', location.pathname === one.path ? 'active' : '')} 
              to={one.path}>{one.name}
            </Link>
          </Nav.Item>
        ))}
      </Nav>
      <Switch>
        {routers.map((one, i) => (
          <Route key={i} exact={one.exact} path={one.path} component={one.component} />  
        ))}
      </Switch>
  </Container>
</>
  );
}

export default Navbar;