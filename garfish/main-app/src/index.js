import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';

import Garfish from 'garfish';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);


Garfish.run({
  // 主应用的基础路径，该值需要保证与主应用的基础路径一致
  basename: '/',
  // 注意在执行 run 时请确保 #subApp 节点已在页面中存在，可为函数（为函数时将使用函数返回时作为挂载点）
  domGetter: '#subApp',
  apps: [
    {
      // 每个应用的 name 需要保持唯一
      name: 'app01',
      // 可为函数，当函数返回值为 true 时，标识满足激活条件，该应用将会自动挂载至页面中，手动挂载时可不填写该参数
      activeWhen: '/app01',
      // 子应用的入口地址，可以为 HTML 地址和 JS 地址（为不同模式时，渲染函数的处理有所不同）
      entry: 'http://localhost:3000',
    },
    {
      name: 'saga-app',
      activeWhen: '/saga-app',
      entry: 'http://localhost:9000',
    },
  ],
});