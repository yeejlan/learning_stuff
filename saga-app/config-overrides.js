module.exports = {
  webpack: function(config, env) {
    config.output = {
      // 需要配置成 umd 规范
      libraryTarget: 'umd',
      // 修改不规范的代码格式，避免逃逸沙箱
      globalObject: 'window',
      // 请求确保每个子应用该值都不相同，否则可能出现 webpack chunk 互相影响的可能
      jsonpFunction: 'saga-app-jsonpFunction',
      // 保证子应用的资源路径变为绝对路径，避免子应用的相对资源在变为主应用上的相对资源，因为子应用和主应用在同一个文档流，相对路径是相对于主应用而言的
      publicPath: 'http://localhost:9000/',
    };
    return config;
  },

  devServer: function(configFunction) {
   
    return function(proxy, allowedHost) {
      // Create the default config by clling configFunction with the proxy/allowedHost parameters
      const config = configFunction(proxy, allowedHost);
      config.headers = {
        'Access-Control-Allow-Origin': '*',
      }
      return config;
    };  
  }
}