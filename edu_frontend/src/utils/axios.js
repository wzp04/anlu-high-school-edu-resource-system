// src/utils/axios.js
import axios from 'axios';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';

// 创建 axios 实例
const request = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 后端接口基础地址
  timeout: 5000,
});

// 请求拦截器：在发送请求前添加 Token
request.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    // 如果有 Token，添加到请求头
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理 401 错误（Token 无效/过期）
request.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 如果是 401 错误，说明 Token 无效，强制退出登录
    if (error.response && error.response.status === 401) {
      const userStore = useUserStore();
      userStore.logout(); // 清除本地 Token
      ElMessage.error('登录已过期，请重新登录');
      window.location.href = '/login'; // 跳回登录页
    }
    return Promise.reject(error);
  }
);

export default request;