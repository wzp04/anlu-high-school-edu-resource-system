<!-- src/App.vue -->
<template>
  <div id="app">
    <!-- 路由出口：当前匹配的路由组件会在这里渲染 -->
    <router-view />
  </div>
</template>

<script setup>
// 无需额外逻辑
</script>

<style>
/* 可选：添加全局样式（如 body 边距清零） */
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>