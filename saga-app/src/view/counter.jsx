import { useSelector, useDispatch } from 'react-redux'

function Counter(){
  console.log('render counter')
  const dispatch = useDispatch()
  const count = useSelector((state) => state.counter.value)

  function counterIncrement() {
      dispatch({type:'counter.increment'})
  }

  function counterDecrement() {
      dispatch({type:'counter.decrement'})
  }

  function counterSetFixedValue() {
      dispatch({type:'counter.setFixedValue'})
  }  

  return (
      <div>
        <h2>counter: {count}</h2>
        <button onClick={counterIncrement}>add</button>
        <button onClick={counterDecrement} style={ {marginLeft: '8px'} }>sub</button>
        <button onClick={counterSetFixedValue} style={ {marginLeft: '8px'} }>set fixed value</button>
      </div>
  );
}

export default Counter