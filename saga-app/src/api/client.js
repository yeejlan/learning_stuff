import axios from 'axios'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css' 
// NProgress.configure({showSpinner: false})

const instance = axios.create({
  baseURL: process.env.REACT_APP_API_URL, 
  timeout: 5000,
  headers: {},
  withCredentials: false,
})

instance.interceptors.request.use(
  (config) => {
    NProgress.start()
    return config
  },
  (err) => {
    NProgress.done()
    console.log(err)
    return err
  }
)
instance.interceptors.response.use(
  (res) => {
    NProgress.done()
    return res.data
  },
  (err) => {
    NProgress.done()
    console.log(err)
    return err
  }
)

export default instance