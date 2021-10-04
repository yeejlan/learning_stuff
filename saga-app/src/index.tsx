import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import { createStore, applyMiddleware, compose } from 'redux'
import createSagaMiddleware from 'redux-saga'
import {Provider} from 'react-redux'
import myReducer from 'reducer'
import myAction from 'action'

const composeEnhancers = (typeof window !== 'undefined' && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__) || compose;

const sagaMiddleware = createSagaMiddleware()

const store = createStore(
  myReducer,
  composeEnhancers(applyMiddleware(sagaMiddleware)),
)
sagaMiddleware.run(myAction)

ReactDOM.render(
    <Provider store={store}>
        <App/>
    </Provider>
, document.getElementById('root'));

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
