import { createApp } from 'vue'
import App from './App.vue'

// 1. 优先导入 Pinia（状态管理）
import pinia from './store'

// 2. 导入路由
import router from './router'

// 其他导入：只保留必需项，去掉语言包相关（避免报错）
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const app = createApp(App)

// 3. 挂载顺序不变（Pinia → 路由 → ElementPlus）
app.use(pinia)
app.use(router)
app.use(ElementPlus) // 去掉语言包配置，避免编译错误

// 注册所有 Element Plus 图标（关键：解决图标警告）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

console.log('Element Plus 核心+图标组件注册完成')
console.log('Pinia/路由/ElementPlus 挂载顺序正确')
app.mount('#app')