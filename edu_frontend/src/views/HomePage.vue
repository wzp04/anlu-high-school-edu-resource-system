<template>
  <div class="home">
    <h1>欢迎使用教师注册系统</h1>
    <!-- 只保留基础 el-button，无复杂属性 -->
    <el-button>Element 按钮</el-button>
    <button @click="goToRegister">备用按钮</button>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  created() {
    console.log('HomePage 组件已创建');
  },
  methods: {
    goToRegister() {
      this.$router.push('/register');
    }
  }
};
</script>

<style scoped>
.home {
  text-align: center;
  padding: 50px;
}
</style>