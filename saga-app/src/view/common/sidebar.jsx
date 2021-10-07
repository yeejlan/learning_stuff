import { Nav } from 'react-bootstrap';
import {
  Switch,
  Route,
  useLocation,
  Link,
} from "react-router-dom";
import classnames from 'classnames';

function Sidebar(props) {

  const location = useLocation();
  return (
<>
  <div className={classnames('d-flex')} >
      <div className={classnames('col=auto')}>
        <div className={classnames('sidebar_left_panel', 'd-flex', 'flex-column', 'flex-shrink-0', 'p-3', 'bg-light',
          'border', 'shadow-sm')}>
          aaa
        </div>
      </div>
      <div className={classnames('sidebar_right_panel', 'col')}>
        bbb
      </div>
  </div>
</>
  );
}

export default Sidebar;