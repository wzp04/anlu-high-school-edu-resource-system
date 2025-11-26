<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <h2 class="login-title">教师资源共享平台</h2>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        label-position="right"
        class="login-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>

        <el-form-item class="login-btn-group">
          <el-button type="primary" @click="handleLogin" :loading="isLoading">登录</el-button>
          <el-button @click="resetForm">重置</el-button>
          <!-- 新增：注册入口文本按钮（与原有按钮横向对齐，不破坏布局） -->
          <el-button type="text" @click="goToRegister" style="color: #1989fa;">立即注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/user';
import { ElMessage } from 'element-plus';

// 表单引用
const loginFormRef = ref(null);
// 路由实例
const router = useRouter();
// 用户状态
const userStore = useUserStore();

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
});

// 表单验证规则
const loginRules = ref({
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
});

// 登录按钮加载状态
const isLoading = ref(false);

/**
 * 处理登录逻辑
 */
const handleLogin = async () => {
  // 先验证表单
  if (!loginFormRef.value) return;
  await loginFormRef.value.validate((valid) => {
    if (!valid) {
      console.log('表单验证失败');
      return false;
    }
    return true;
  });

  isLoading.value = true;

  try {
    // 调用 Pinia 中的 login action
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password,
    });
    // 登录成功后，跳转到上传页面
    ElMessage.success('登录成功');
    router.push('/upload');
  } catch (error) {
    // 捕获 login action 抛出的错误，并显示给用户
    ElMessage.error(error.message || '登录失败，请稍后重试');
  } finally {
    isLoading.value = false;
  }
};

/**
 * 重置表单
 */
const resetForm = () => {
  loginFormRef.value?.clearValidate(); // 清除表单验证
  loginForm.username = '';
  loginForm.password = '';
};

// 新增：跳转注册页方法（最简逻辑，仅跳转路由）
const goToRegister = () => {
  router.push('/register');
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
  padding: 20px;
}
.login-card {
  width: 100%;
  max-width: 400px;
  padding: 30px 20px;
}
.login-title {
  text-align: center;
  margin-bottom: 20px;
  color: #1989fa;
}
.login-form {
  margin-top: 20px;
}
.login-btn-group {
  display: flex;
  justify-content: center;
  gap: 20px;
} 
</style>