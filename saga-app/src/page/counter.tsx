import {Provider} from 'react-redux'
import { useSelector, useDispatch } from 'react-redux'

export default function Counter(props){

  const dispatch = useDispatch()

  function counter_add(e) {
      dispatch({type:'counter_increment'})
  }

  return (
      <div>
        <h2>counter: {props.store}</h2>
        <button onClick={counter_add}>add</button>
      </div>
  );
}