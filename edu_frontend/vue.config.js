const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  // 选项1：配置跨域代理（前端请求后端接口时，自动转发到后端服务）
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // 后端 Django 服务地址
        changeOrigin: true, // 开启跨域
        pathRewrite: { '^/api': '' } // 去掉请求路径中的 /api 前缀
      }
    }
  },

  // 选项2：配置路径别名（如 @ 代表 src 目录）
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src'),
        'components': '@/components',
        'stores': '@/stores',
        'views': '@/views'
      }
    }
  },

  // 选项3：生产环境优化（可选）
  productionSourceMap: false, // 关闭生产环境 SourceMap（提升打包速度、减少体积）
  css: {
    extract: {
      filename: 'css/[name].[contenthash:8].css',
      chunkFilename: 'css/[name].[contenthash:8].chunk.css'
    }
  }
});