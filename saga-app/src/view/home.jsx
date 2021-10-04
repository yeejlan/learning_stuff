import { useSelector, useDispatch } from 'react-redux'

function Home() {
  const dispatch = useDispatch()
  const user = useSelector((state) => state.user)

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