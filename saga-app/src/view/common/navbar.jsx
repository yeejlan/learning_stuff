import { Nav } from 'react-bootstrap';
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
  <div className={classnames('mt-2', 'app_container')} >
      <Nav variant="tabs" className='navbar_top' defaultActiveKey="/">
      <a className="ms-2 me-1 pt-1 text-danger" href={process.env.REACT_APP_BASE_URL}>
        <svg xmlns="http://www.w3.org/2000/svg" width="1.5rem" height="1.5rem" fill="currentColor" viewBox="0 0 16 16">
          <path d="m11.42 2 3.428 6-3.428 6H4.58L1.152 8 4.58 2h6.84zM4.58 1a1 1 0 0 0-.868.504l-3.428 6a1 1 0 0 0 0 .992l3.428 6A1 1 0 0 0 4.58 15h6.84a1 1 0 0 0 .868-.504l3.429-6a1 1 0 0 0 0-.992l-3.429-6A1 1 0 0 0 11.42 1H4.58z"/>
          <path d="M6.848 5.933a2.5 2.5 0 1 0 2.5 4.33 2.5 2.5 0 0 0-2.5-4.33zm-1.78 3.915a3.5 3.5 0 1 1 6.061-3.5 3.5 3.5 0 0 1-6.062 3.5z"/>
        </svg>
      </a>
      <span className="me-2 pt-2 text-danger">Nuts</span>
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
  </div>
</>
  );
}

export default Navbar;