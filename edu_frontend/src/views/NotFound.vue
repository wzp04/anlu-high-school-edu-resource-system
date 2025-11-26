<!-- src/views/NotFound.vue -->
<template>
  <div style="text-align: center; padding: 100px;">
    <h1 style="font-size: 100px; color: #409EFF;">404</h1>
    <p style="font-size: 24px; margin: 20px 0;">页面迷路了...</p>
    <!-- 跳转首页的按钮（用 router-link 或编程式导航） -->
    <router-link to="/">
      <el-button type="primary">返回首页</el-button>
    </router-link>
  </div>
</template>

<script setup>
// 无需额外逻辑，仅展示页面
</script>