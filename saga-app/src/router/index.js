import loadable from '@loadable/component'

const Home = loadable(() => import('view/home'));
const About = loadable(() => import('view/about'));
const Dashboard = loadable(() => import('view/dashboard'));
const Counter = loadable(() => import('view/counter'));

const routers = [
  { path: "/", name: "Home", component: Home, exact: true, permission: {'a':1}},
  { path: "/about", name: "About", component: About },
  { path: "/dashboard", name: "Dashboard", component: Dashboard },
  { path: "/counter", name: "Counter", component: Counter },
]

export default routers;