// src/main.js
import { createApp } from 'vue'
import App from './App.vue'

// 1. 优先导入 Pinia（确保状态管理先初始化）
import pinia from './store'

// 2. 导入路由（路由可能依赖 Pinia 状态）
import router from './router'


// 其他导入
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
const app = createApp(App)

// 3. 先挂载 Pinia（关键：让路由守卫能访问 Pinia 状态）
app.use(pinia)

// 4. 再挂载 Router
app.use(router)

// 其他挂载
app.use(ElementPlus)

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}



console.log('Element Plus 核心+图标组件注册完成')
console.log('Pinia/路由/ElementPlus 挂载顺序正确')
app.mount('#app')