<template>
  <el-form :model="form" label-width="120px" class="register-form">
    <el-form-item label="用户名">
      <el-input v-model="form.username" placeholder="请输入用户名" />
    </el-form-item>
    <el-form-item label="密码">
      <el-input type="password" v-model="form.password" placeholder="请输入密码" />
    </el-form-item>
    <el-form-item label="所属学校">
      <el-input v-model="form.school" placeholder="请输入学校名称" />
    </el-form-item>
    <el-form-item label="任教科目">
      <el-input v-model="form.subject" placeholder="请输入任教科目" />
    </el-form-item>
    <el-form-item label="佐证材料">
      <el-upload
        action="/api/users/upload-cert/"
        :on-success="handleCertUpload"
        :on-error="handleCertError"
        accept=".jpg,.png,.pdf"
        :limit="1"
      >
        <el-button type="primary">点击上传佐证材料</el-button>
      </el-upload>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="submitRegister">提交注册</el-button>
    </el-form-item>
  </el-form>
</template>

<script>
import axios from 'axios';

export default {
  name: 'RegisterForm',
  data() {
    return {
      form: {
        username: '',
        password: '',
        school: '',
        subject: '',
        certificate_path: ''
      }
    };
  },
  methods: {
    handleCertUpload(response) {
      this.form.certificate_path = response.data.path;
    },
    handleCertError() {
      this.$message.error('佐证材料上传失败，请重试');
    },
    submitRegister() {
      axios.post('/api/users/register/', this.form)
        .then(res => {
          if (res.data.code === 201) {
            this.$message.success('注册成功，等待学校初审');
            this.$router.push('/login');
          }
        })
        .catch(err => {
          this.$message.error(err.response?.data?.message || '注册失败，请检查信息后重试');
        });
    }
  }
};
</script>

<style scoped>
.register-form {
  width: 400px;
  margin: 50px auto;
}
</style>