let path = require("path");
module.exports = {
mode: "development",   
   entry: {
   '1' : './src/1.js',
   },
   output: {
     filename: '[name].js',
     path: path.resolve(__dirname, 'dist'),
     clean: true,
   },
  module: {
    rules: [
      {
        test: /\.css$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'style-loader',
          },
          {
            loader: 'css-loader',
            options: {
              importLoaders: 1,
            }
          },
          {
            loader: 'postcss-loader'
          }
        ]
      }
    ]
  }
}