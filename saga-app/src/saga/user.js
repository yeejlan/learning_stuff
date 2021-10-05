import {put, take, call, fork} from 'redux-saga/effects'
import client from 'api/client'


function login(username, password) {
    try{
        return client.post('/a/c', {username:username, password: password});
    }catch(e){
        return e.message;
    }
}

export function* loginFlow() {
    while (true) {
        let request = yield take('user.login');
        let response = yield call(login, request.username, request.password);
        if(response&&response.code === 0){
            yield put({ type: 'user.login:success', ...response.data});
        }
        yield put({ type: 'user.login:success', userid: 1001});
    }
}


export default function* rootSaga() {
  yield fork(loginFlow)
}