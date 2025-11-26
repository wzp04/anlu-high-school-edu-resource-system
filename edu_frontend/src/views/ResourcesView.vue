<!-- src/views/ResourcesView.vue -->
<template>
  <div class="resources-page">
    <h1>教育资源库</h1>
    <p>欢迎访问资源库页面。这里将展示所有可供下载和使用的教育资源。</p>

    <!-- 你可以在这里添加资源列表、搜索框、分类筛选等功能 -->
    <div class="resource-list">
      <!-- 示例：一个简单的资源卡片 -->
      <div class="resource-card">
        <h3>高中数学必修一知识点总结</h3>
        <p>作者: 张老师</p>
        <p>类型: 文档</p>
        <button class="download-btn">下载</button>
      </div>
    </div>
  </div>
</template>

<script setup>
// 这里可以编写页面的逻辑，例如从API获取资源列表
</script>

<style scoped>
/* 这里可以编写页面的样式 */
.resources-page {
  padding: 20px;
}

.resource-list {
  margin-top: 30px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.resource-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 15px;
  width: 250px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.download-btn {
  background-color: #409EFF;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.download-btn:hover {
  background-color: #3388dd;
}
</style>