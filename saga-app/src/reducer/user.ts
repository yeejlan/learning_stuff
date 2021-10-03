const initialState = {
  userId: 0,
  token: '',
  avatar: '',
};

export default function reducer(state = initialState, action: any) {
  switch (action.type) {
    case 'user_login':
      return {
        ...state,
        userId: action.userId,
        token: action.token,
      };
    default:
      return state;
  }
}
