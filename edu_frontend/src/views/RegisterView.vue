<template>
  <div class="register-container" style="width:400px;margin:50px auto;padding:20px;border:1px solid #eee;border-radius:8px;">
    <h2 style="text-align:center;margin-bottom:20px;">教师注册</h2>
    <el-form 
      :model="registerForm" 
      :rules="formRules" 
      ref="registerFormRef" 
      label-width="100px"
    >
      <!-- 用户名 -->
      <el-form-item label="用户名" prop="username">
        <el-input 
          v-model="registerForm.username" 
          placeholder="请输入用户名（如：zhanglaoshi）"
          clearable
        ></el-input>
      </el-form-item>

      <!-- 密码 -->
      <el-form-item label="密码" prop="password">
        <el-input 
          type="password" 
          v-model="registerForm.password" 
          placeholder="请输入密码（≥6位）"
          clearable
          show-password
        ></el-input>
      </el-form-item>

      <!-- 确认密码 -->
      <el-form-item label="确认密码" prop="passwordConfirm">
        <el-input 
          type="password" 
          v-model="registerForm.passwordConfirm" 
          placeholder="请再次输入密码"
          clearable
          show-password
        ></el-input>
      </el-form-item>

      <!-- 所属学校 -->
      <el-form-item label="所属学校" prop="school">
        <el-select v-model="registerForm.school" placeholder="请选择学校">
          <el-option label="安陆一中" value="安陆一中"></el-option>
          <el-option label="安陆二中" value="安陆二中"></el-option>
          <el-option label="安陆三中" value="安陆三中"></el-option>
        </el-select>
      </el-form-item>

      <!-- 任教科目 -->
      <el-form-item label="任教科目" prop="subject">
        <el-select v-model="registerForm.subject" placeholder="请选择学科">
          <el-option label="语文" value="语文"></el-option>
          <el-option label="数学" value="数学"></el-option>
          <el-option label="英语" value="英语"></el-option>
          <el-option label="物理" value="物理"></el-option>
          <el-option label="化学" value="化学"></el-option>
          <el-option label="生物" value="生物"></el-option>
          <el-option label="政治" value="政治"></el-option>
          <el-option label="历史" value="历史"></el-option>
          <el-option label="地理" value="地理"></el-option>
        </el-select>
      </el-form-item>

      <!-- 提交/重置按钮 -->
      <el-form-item style="text-align:center;">
        <el-button type="primary" @click="handleRegister" :loading="isLoading">提交注册</el-button>
        <el-button type="text" @click="resetForm" style="margin-left:10px;">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from 'axios';

const router = useRouter();
const registerFormRef = ref(null);
const isLoading = ref(false);

const registerForm = ref({
  username: '',
  password: '',
  passwordConfirm: '',
  school: '',
  subject: ''
});

const formRules = ref({
  username: [
    { required: true, message: '请输入用户名', trigger: ['blur', 'change'] },
    { min: 3, max: 20, message: '用户名长度3-20位', trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: ['blur', 'change'] },
    { min: 6, message: '密码至少6位', trigger: ['blur', 'change'] }
  ],
  passwordConfirm: [
    { required: true, message: '请确认密码', trigger: ['blur', 'change'] },
    { 
      validator: (rule, value, callback) => {
        if (value !== registerForm.value.password) {
          callback(new Error('两次密码不一致'));
        } else {
          callback();
        }
      },
      trigger: ['blur', 'change']
    }
  ],
  school: [
    { required: true, message: '请选择学校', trigger: 'change' }
  ],
  subject: [
    { required: true, message: '请选择学科', trigger: 'change' }
  ]
});

const resetForm = () => {
  registerFormRef.value.resetFields();
};

const handleRegister = async () => {
  const isValid = await registerFormRef.value.validate().catch(() => false);
  if (!isValid) return;

  try {
    isLoading.value = true;
    const res = await axios({
      url: '/api/users/register/',
      method: 'POST',
      data: registerForm.value
    });
    ElMessage.success(res.data.message || '注册成功，等待学校初审！');
    setTimeout(() => router.push('/login'), 1500);
  } catch (error) {
    isLoading.value = false;
    if (error.response) {
      const errMsg = error.response.data.errors?.username?.[0] || error.response.data.message || '注册失败';
      ElMessage.error(errMsg);
    } else {
      ElMessage.error('网络异常，请检查网络连接');
    }
  }
};
</script>

<style scoped>
.register-container {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  background-color: #fff;
}
</style>