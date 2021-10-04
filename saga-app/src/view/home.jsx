import { useSelector, useDispatch } from 'react-redux'
import deepEqual from 'fast-deep-equal'
import { shallowEqual } from 'react-redux'

function Home() {
  console.log("render home");
  const dispatch = useDispatch()
  const user = useSelector((state) => state.user, shallowEqual)

  function login() {
    dispatch({type:'user.login'})
  }

  return (
    <div>
      <h2>Current user id: {user.userid}</h2>
      <button onClick={login}>login</button>
    </div>
  );
}

export default Home;