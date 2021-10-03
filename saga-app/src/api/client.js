import axios from "axios";

const config = {
  baseURL: process.env.REACT_APP_API_URL,
  transformRequest: [
    function(data) {
      if (data) {
        let ret = "";
        Object.keys(data).forEach(function(key) {
          ret +=
            encodeURIComponent(key) + "=" + encodeURIComponent(data[key]) + "&";
        });
        return ret;
      }
      return data;
    }
  ],

  transformResponse: [
    function(data) {
      return data;
    }
  ],
  headers: {
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
  },
  timeout: 10000,
  responseType: "json"
};

axios.interceptors.response.use(function(res) {
  //corresponding interceptor
  return res.data;
});

// axios.defaults.headers.authorization = localStorage.getItem("jwttoken") || '';

export default {
	get: (url) => {
		axios.get(url, config);
	},
	post: (url, data) => {
		axios.post(url, data, config);
	}
}