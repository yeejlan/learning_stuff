import { useSelector, useDispatch } from 'react-redux'
import { Button } from 'react-bootstrap';

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
        <Button variant="outline-primary" onClick={counterIncrement}>add</Button>
        <Button variant="outline-primary" onClick={counterDecrement} style={ {marginLeft: '8px'} }>sub</Button>
        <Button variant="outline-primary" onClick={counterSetFixedValue} style={ {marginLeft: '8px'} }>set fixed value</Button>
      </div>
  );
}

export default Counter