import {Home, About, Dashboard, Counter} from 'view';

const routers = [
  { path: "/", name: "Home", component: Home, exact: true, permission: {'a':1}},
  { path: "/home", name: "About", component: About },
  { path: "/dashboard", name: "Dashboard", component: Dashboard },
  { path: "/counter", name: "Counter", component: Counter },
]

export default routers;