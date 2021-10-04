import {put, take, call, fork} from 'redux-saga/effects'
import client from 'api/client'

interface AuthData{
  username: string,
  password: string,
}


function* login(username, password) :Generator<any, any, any>{
  yield {code:0, data: {userid:123, token:12345}}
}

export function* loginFlow() {
    while (true) {
        let request = yield take('user.login');
        console.log(request);
        let response = yield call(login, request.username, request.password);
        console.log(response);
        if(response&&response.code === 0){
            yield put({ type: 'user.login:success', ...response.data});
        }
        yield put({ type: 'user.login:success', userid: 1001});
    }
}


export default function* rootSaga() {
  yield fork(loginFlow)
}