import { combineReducers } from "redux";
import userReducer from './user'
import counterReducer from './counter'

export default combineReducers({
  counterReducer,
  userReducer,
});
