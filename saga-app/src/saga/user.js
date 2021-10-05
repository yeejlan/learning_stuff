import {put, take, call, fork} from 'redux-saga/effects'
import client from 'api/client'


function login(username, password) {
    // return {code:0, data:{userid:8790}}
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
        }else{
            console.log(response)
            yield put({ type: 'user.login:failed', message: response});
        }
    }
}


export default function* rootSaga() {
  yield fork(loginFlow)
}