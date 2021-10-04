const initialState = {
  userid: 0,
  token: '',
  avatar: '',
};

export default function reducer(state = initialState, action: any) {
  switch (action.type) {
    case 'user.login:success':
      return {
        ...state,
        userid: action.userid,
        token: action.token,
      };
    default:
      return state;
  }
}
