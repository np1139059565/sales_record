const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  devServer: {
    port: 80, // 您想要设置的新端口号
    proxy: {
      '/py':{
        target:'http://localhost:8000/',//请求域名
        //secure: false, // 如果是https接口，需要配置这个参数
        changeOrigin:true,//如果是跨域访问，需要配置这个参数
        pathRewrite:{
          '^/py': '/'
        }
      }
    }
  },
  transpileDependencies: true
})
