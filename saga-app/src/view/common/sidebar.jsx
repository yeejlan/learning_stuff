import { Nav } from 'react-bootstrap';
import {
  Switch,
  Route,
  useLocation,
  Link,
} from "react-router-dom";
import classnames from 'classnames';
import { useState } from 'react';

const sidebar_menus = [
  { path: "/other", name: "Other"},
  { path: "/getting-started", name: "Getting started", submenu: [
      { path: "/getting-started/introduction", name: "Introduction"},
      { path: "/getting-started/download", name: "Download"},
      { path: "/getting-started/contents", name: "Contents"},
      { path: "/getting-started/browsers-devices", name: "Browsers & devices"},
      { path: "/getting-started/javaScript", name: "JavaScript"},
    ]},
  
  { path: "/dashboard", name: "Dashboard", submenu: [
      { path: "/getting-started/introduction", name: "Introduction"},
      { path: "/getting-started/download", name: "Download"},
      { path: "/getting-started/contents", name: "Contents"},
      { path: "/getting-started/browsers-devices", name: "Browsers & devices"},
      { path: "/getting-started/javaScript", name: "JavaScript"},
    ]},
  { path: "/loader", name: "Loader"},
  { path: "/counter", name: "Counter", submenu: [
      { path: "/getting-started/introduction", name: "Introduction"},
      { path: "/getting-started/download", name: "Download"},
      { path: "/getting-started/contents", name: "Contents"},
      { path: "/getting-started/browsers-devices", name: "Browsers & devices"},
      { path: "/getting-started/javaScript", name: "JavaScript"},
    ]},
  
  
  { path: "/plugin", name: "Plugin"},
  { path: "/target", name: "Target"},
]

function SideBarContent(props) {
  const {content} = props;
  return(
    <>
      <span className="p-3">{content}</span>
    </>
  );
}

function SidebarMenu(props) {
  const [isOpen, setOpen] = useState(true);
  const {one} = props;

  function toggleMenu() {
    setOpen(!isOpen);
  }

  return (
    <>
      <div className={classnames('sidebar_item', {'sidebar_item_open': isOpen})}>
        {one.submenu !== undefined && 
        <>
        <svg onClick={toggleMenu} className="sidebar_item_toggle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" width="15" height="17" 
          fill="#175d96">
        <path d="M9.2 4.5l4.5 4.7c.2.2.3.5.3.8s-.1.6-.3.8l-4.5 4.7c-.5.4-1.2.4-1.7 0-.4-.5-.4-1 0-1.6l3.8-3.9-3.8-4c-.4-.4-.4-1 0-1.5.5-.4 1.2-.4 1.7 0z"></path>
        </svg>
        <a className="sidebar_item_title font-monospace" onClick={toggleMenu} href="#!">{one.name}</a>
        </>
        }
        {one.submenu === undefined && 
        <>
        <svg className="sidebar_item_decorate" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" width="15" height="17" fill="#175d96">
        <path d="M10 3.3c-.6 0-1 .4-1.1 1.1v11.2c0 .3.2.6.4.8s.5.4.8.4c.6 0 1-.4 1.1-1.1V4.5c0-.3-.2-.6-.4-.8s-.5-.4-.8-.4z"></path>
        </svg>
        <Link aria-current="page" className="sidebar_item_title font-monospace" to={one.path}>{one.name}</Link>
        </>
        }
       
        {isOpen && one.submenu !== undefined && 
        <ul className="sidebar_item_parent">
          {one['submenu'].map((subone, j) => (
          <li key={j} className="sidebar_item_child">
            <Link aria-current="page" className="font-monospace" to={subone.path}>{subone.name}</Link>
          </li>
          ))}
        </ul>
        }
      </div>
    </>
  )
}

function Sidebar(props) {

  const location = useLocation();
  return (
<>
  <div className={classnames('d-flex')} >
      <div className={classnames('col=auto', 'mt-1')}>
        <div className={classnames('sidebar_left_panel', 'd-flex', 'flex-column', 'flex-shrink-0', 'p-3', 
          'border-end', 'shadow-sm')}>
            {sidebar_menus.map((one, i) => (
              <SidebarMenu key={i} one={one} />            
              
            ))}
        </div>
      </div>
      <div className="content_right_panel col">
            <Switch>
              {sidebar_menus.map((one, i) => (
                <Route key={i} exact={one.exact} path={one.path} render={ () => <SideBarContent content={one.name} />} />
              ))}
            </Switch>
      </div>
  </div>
</>
  );
}

export default Sidebar;