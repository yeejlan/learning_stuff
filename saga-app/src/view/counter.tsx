import { useSelector, useDispatch } from 'react-redux'

function Counter(props){

  const dispatch = useDispatch()
  const count = useSelector((state) => state.counter.value)

  function counterIncrement() {
      dispatch({type:'counter.increment'})
  }

  function counterDecrement() {
      dispatch({type:'counter.decrement'})
  }

  return (
      <div>
        <h2>counter: {count}</h2>
        <button onClick={counterIncrement}>add</button>
        <button onClick={counterDecrement}>sub</button>
      </div>
  );
}

export default Counter