import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';
const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // 与后端接口前缀一致
  timeout: 30000, // 超时时间30秒（适配大文件分片上传）
  headers: { 'Content-Type': 'application/json' }
});
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`; // Token格式按后端要求调整
    }
    return config;
  },
  (error) => Promise.reject(error)
);
service.interceptors.response.use(
  (response) => response.data, // 直接返回响应体，简化前端调用
  (error) => {
    const msg = error.response?.data?.msg || '请求失败，请重试';
    // 错误分类提示
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录');
      const userStore = useUserStore();
      userStore.logout(); // 后续Pinia中实现退出逻辑
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      ElMessage.error('无权限访问该功能');
    } else {
      ElMessage.error(msg);
    }
    return Promise.reject(error);
  }
);
export default service;