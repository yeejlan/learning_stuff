const initialState = {
	value: 0
};

export default function reducer(state = initialState, action){
	switch (action.type) {
		case 'counter.increment':
			return {
				...state,
				value: state.value + 1
			};
		case 'counter.decrement':
			return {
				...state,
				value: state.value - 1
			};
		case 'counter.incrementByAmount':
			return {
				...state,
				value: state.value + action.amount
			};
		default:
			return state
	}
}