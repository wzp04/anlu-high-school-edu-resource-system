const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // 后端地址（正确）
        changeOrigin: true, // 跨域配置（正确）
        // 关键修改：保留/api前缀，不做改写（和后端接口路径匹配）
        pathRewrite: { '^/api': '/api' } 
      }
    }
  },

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

  productionSourceMap: false,
  css: {
    extract: {
      filename: 'css/[name].[contenthash:8].css',
      chunkFilename: 'css/[name].[contenthash:8].chunk.css'
    }
  }
});