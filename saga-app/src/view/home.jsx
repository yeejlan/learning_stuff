import { useSelector, useDispatch } from 'react-redux'
//import deepEqual from 'fast-deep-equal'
import { shallowEqual } from 'react-redux'
import { Button } from 'react-bootstrap';
import Welcome from 'view/common/welcome';
import NotFound from 'view/common/notfound';
import NoPermission from 'view/common/nopermission';

function Home() {
  console.log("render home");
  const dispatch = useDispatch()
  const user = useSelector((state) => state.user, shallowEqual)

  function login() {
    dispatch({type:'user.login'})
  }

  return (
    <div>
      <Welcome />
      {/*<Welcome />*/}
      <h2 className='pt-4'>Current user id: {user.userid}</h2>
      <Button variant="outline-primary" onClick={login}>login</Button>
    </div>
  );
}

export default Home;