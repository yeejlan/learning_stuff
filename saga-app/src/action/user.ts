import {put, take, call, fork} from 'redux-saga/effects'
import client from 'api/client'

interface AuthData{
  username: string,
  password: string,
}


function* login(authData :AuthData) :Generator<any, any, any>{
  yield put({ type: 'user_login' });
  try {
    return yield call(client.post, "/question/post", authData);
  } catch (error) {
    yield put({
      type: 'user_login_error',
      message: error,
    });
  } finally {
    yield put({ type: 'user_login_success' });
  }
}

export default function* a(){}