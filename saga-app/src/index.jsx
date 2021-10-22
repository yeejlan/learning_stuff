import React from 'react';
import ReactDOM from 'react-dom';
import App from 'view/app';
import reportWebVitals from './reportWebVitals';
import { createStore, applyMiddleware, compose } from 'redux'
import createSagaMiddleware from 'redux-saga'
import {Provider} from 'react-redux'
import myReducer from 'reducer'
import mySaga from 'saga'

import 'style.scss'

const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

const sagaMiddleware = createSagaMiddleware()

const store = createStore(
  myReducer,
  composeEnhancers(applyMiddleware(sagaMiddleware)),
)
sagaMiddleware.run(mySaga)

const render = ({ dom, basename }) => {
  ReactDOM.render(
    // 使用 Garfish 框架提供的 basename，子应用的所有子路由都基于该 basename，已到达路由隔离、刷新路由加载子应用组件的目标
    <Provider store={store}>
        <App basename={basename} />
    </Provider>,
    // 这里的 document 是 Garfish 构造的一个子应用容器，所有的内容都会被放在这里面
    // 如果是 js 入口直接渲染在 dom 即可（因为没有其他节点了）
    // 如果是 html 入口则要通过选择器渲染在自身html的dom节点里
    dom.querySelector('#root'),
  );
};

// 在首次加载和执行时会触发该函数
export const provider = () => {
  return {
    render, // 应用在渲染时会触发该 hook
    destroy({ dom }) {
      // 应用在销毁时会触发该 hook
      const root = (dom && dom.querySelector('#root')) || dom; // 若为 JS 入口直接将传入节点作为挂载点和销毁节点
      if (root) {
        // 做对应的销毁逻辑，保证子应用在销毁时对应的副作用也被移除
        ReactDOM.unmountComponentAtNode(root);
      }
    },
  };
};

// 这能够让子应用独立运行起来，以保证后续子应用能脱离主应用独立运行，方便调试、开发
if (!window.__GARFISH__) {
  render({ dom: document, basename: '/' });
}