// src/store/user.js
import { defineStore } from 'pinia';
import axios from '@/utils/axios';

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '', // 初始从localStorage读取
    username: '',
    userId: ''
  }),
  actions: {
    async login(credentials) {
      try {
        // 1. 发送登录请求（参数与后端要求的username/password一致）
        const response = await axios.post('/api/users/login/', credentials);
        
        // 2. 从后端返回的data中提取access Token（匹配Postman返回的结构）
        const { access, user_id, username } = response.data.data;
        if (!access) {
          throw new Error('登录失败：未获取到Token');
        }

        // 3. 存储Token、用户信息到状态和localStorage
        this.token = access;
        this.userId = user_id;
        this.username = username;
        localStorage.setItem('token', access);
        localStorage.setItem('username', username);
        localStorage.setItem('userId', user_id);

        console.log('登录成功，Token已存储');
        return response.data;
      } catch (error) {
        const errMsg = error.response?.data?.message || error.message || '登录失败';
        throw new Error(errMsg);
      }
    },
    logout() {
      // 登出时清空状态和localStorage
      this.token = '';
      this.username = '';
      this.userId = '';
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('userId');
    }
  },
  getters: {
    isLoggedIn: (state) => !!state.token // 基于token是否存在判断登录状态
  }
});