const initialState = {
	value: 0
};

export default function reducer(state = initialState, action: any){
	switch (action.type) {
		case 'counter_increment':
			return {
				...state,
				value: state.value + 1
			};
		case 'counter_decrement':
			return {
				...state,
				value: state.value - 1
			};
		case 'counter_incrementByAmount':
			return {
				...state,
				value: state.value + action.amount
			};
		default:
			return state
	}
}