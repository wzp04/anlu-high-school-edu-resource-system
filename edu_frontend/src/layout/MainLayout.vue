<template>
  <div class="layout-container">
    <header class="layout-header">
      <div class="header-left">
        <router-link to="/" class="logo">
          <span class="logo-text">教育资源共享平台</span>
        </router-link>
      </div>

      <div class="header-middle">
        <!-- 
          关键：
          - 首页使用 exact-active-class，确保只有在路径完全匹配'/'时才高亮
          - 其他链接使用 active-class，当路径以其开头时就高亮（这是默认行为，但写出来更清晰）
        -->
        <router-link to="/" class="nav-link" exact-active-class="active">
          首页
        </router-link>
        <router-link to="/resources" class="nav-link" active-class="active">
          资源库
        </router-link>
        <router-link to="/upload" class="nav-link" active-class="active">
          资源上传
        </router-link>
        <router-link to="/my-uploads" class="nav-link" active-class="active">
          我的上传
        </router-link>
      </div>

      <div class="header-right">
        <template v-if="userStore.isLoggedIn">
          <span class="user-info">欢迎，{{ userStore.username }}</span>
          <button class="btn-logout" @click="handleLogout">退出登录</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn-login">登录</router-link>
          <router-link to="/register" class="btn-register">注册</router-link>
        </template>
      </div>
    </header>

    <main class="layout-content">
      <router-view />
    </main>

    <footer class="layout-footer">
      <div class="footer-text">© 2025 湖北省安陆县高中教师教育资源共享平台 版权所有</div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/store/user';

const router = useRouter();
const userStore = useUserStore();

const handleLogout = () => {
  userStore.logout();
  ElMessage.success('退出登录成功！');
  router.push('/login');
};
</script>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  background-color: #409EFF;
  color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 999;
}
.header-left .logo {
  text-decoration: none;
}
.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: #fff;
}
.header-middle {
  display: flex;
  gap: 25px;
}
.nav-link {
  text-decoration: none;
  color: #fff;
  font-size: 14px;
  padding: 0 5px;
  height: 60px;
  line-height: 60px;
  position: relative;
  transition: color 0.3s;
}
.nav-link:hover {
  color: #e6f7ff;
}
.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #fff;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
}
.user-info {
  color: #e6f7ff;
}
.btn-logout {
  background: transparent;
  border: 1px solid #fff;
  color: #fff;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}
.btn-logout:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
.btn-login, .btn-register {
  text-decoration: none;
  color: #fff;
  padding: 4px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}
.btn-login:hover {
  background-color: rgba(255, 255, 255, 0.1);
}
.btn-register {
  background-color: #1890ff;
  border: 1px solid #1890ff;
}
.btn-register:hover {
  background-color: #096dd9;
}
.layout-content {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
.layout-footer {
  height: 40px;
  line-height: 40px;
  text-align: center;
  background-color: #f5f5f5;
  color: #666;
  font-size: 12px;
}
</style>