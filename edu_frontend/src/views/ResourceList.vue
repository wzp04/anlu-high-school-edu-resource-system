<template lang="html">
  <div v-if="isComponentReady && !isLoading" class="resource-list-container">
    <div class="page-header">
      <h1>资源列表</h1>
      <p class="subtitle">共 <span class="count">{{ totalCount || 0 }}</span> 条资源</p>
    </div>

    <div class="filter-container" v-if="Array.isArray(filterOptions.subjects)">
      <el-select 
        v-model="selectedSubject" 
        placeholder="请选择学科" 
        class="filter-select"
        @change="handleFilterChange"
        clearable
      >
        <el-option label="全部学科" value=""></el-option>
        <el-option v-for="sub in filterOptions.subjects" :key="`sub-${sub}`" :label="sub" :value="sub"></el-option>
      </el-select>

      <el-select 
        v-model="selectedGrade" 
        placeholder="请选择年级" 
        class="filter-select"
        @change="handleFilterChange"
        clearable
      >
        <el-option label="全部年级" value=""></el-option>
        <el-option v-for="grade in filterOptions.grades" :key="`grade-${grade}`" :label="grade" :value="grade"></el-option>
      </el-select>

      <el-select 
        v-model="selectedSchool" 
        placeholder="请选择学校" 
        class="filter-select"
        @change="handleFilterChange"
        clearable
      >
        <el-option label="全部学校" value=""></el-option>
        <el-option v-for="school in filterOptions.schools" :key="`school-${school}`" :label="school" :value="school"></el-option>
      </el-select>

      <el-select 
        v-model="selectedType" 
        placeholder="资源类型" 
        class="filter-select"
        @change="handleFilterChange"
        clearable
      >
        <el-option label="全部类型" value=""></el-option>
        <el-option label="文档" value="document"></el-option>
        <el-option label="视频" value="video"></el-option>
        <el-option label="音频" value="audio"></el-option>
        <el-option label="图片" value="image"></el-option>
      </el-select>

      <el-select 
        v-model="sortType" 
        placeholder="排序方式" 
        class="filter-select"
        @change="handleFilterChange"
      >
        <el-option label="最新上传" value="newest"></el-option>
        <el-option label="下载最多" value="downloads"></el-option>
        <el-option label="点赞最多" value="likes"></el-option>
      </el-select>

      <el-checkbox 
        v-model="isHighQuality" 
        label="仅看优质资源" 
        class="high-quality-checkbox"
        @change="handleFilterChange"
      ></el-checkbox>
    </div>

    <div v-if="filteredResources.length > 0" class="resource-grid">
      <el-card 
        v-for="res in filteredResources" 
        :key="`res-${res.id}`" 
        class="resource-card"
        @click="goToDetail(res.id)"
      >
        <div class="card-header">
          <span class="resource-tag" v-if="res.is_high_quality">优质资源</span>
          <span class="resource-type">{{ getResourceTypeName(res.type) }}</span>
          <h3 class="resource-title">{{ res.title || '未知资源' }}</h3>
        </div>
        <div class="card-body">
          <p class="resource-meta">
            <span>{{ res.school_name || '未知学校' }}</span>
            <span>{{ res.subject || '未知学科' }} · {{ res.grade || '未知年级' }}</span>
            <span>上传时间：{{ formatDate(res.upload_time) }}</span>
          </p>
          <div class="resource-stats">
            <span><i class="el-icon-download"></i> {{ res.download_count || 0 }} 下载</span>
            <span><i class="el-icon-thumbs-up"></i> {{ res.like_count || 0 }} 点赞</span>
            <span><i class="el-icon-file-text"></i> {{ formatFileSize(res.file_size || 0) }}</span>
          </div>
        </div>
        <div class="card-footer">
          <el-button 
            type="success" 
            size="small" 
            @click.stop="handleDownload(res.id)"
          >
            <i class="el-icon-download"></i> 下载
          </el-button>
          <el-button 
            type="primary" 
            size="small" 
            @click.stop="goToDetail(res.id)"
          >
            查看详情
          </el-button>
        </div>
      </el-card>
    </div>

    <div class="empty-placeholder" v-else>
      <el-empty description="暂无符合条件的资源"></el-empty>
    </div>

    <div class="pagination-container" v-if="totalCount > 0">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 30, 50]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalCount"
        background
      ></el-pagination>
    </div>
  </div>
</template>

<script setup lang="js">
import { ref, onMounted, watch, onUnmounted, nextTick, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import request from '@/utils/request'; // 响应格式：直接返回后端数据，无status属性
import { ElMessage, ElEmpty } from 'element-plus';

// 路由实例
const router = useRouter();
const route = useRoute();

// 状态管理
const resources = ref([]);
const totalCount = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const filterOptions = ref({
  subjects: [],
  grades: [],
  schools: []
});
const isLoading = ref(false);
const isComponentReady = ref(false);

// 筛选条件
const selectedSubject = ref(String(route.query.subject || ''));
const selectedGrade = ref(String(route.query.grade || ''));
const selectedSchool = ref(String(route.query.school || ''));
const selectedType = ref('');
const isHighQuality = ref(route.query.is_high_quality === 'true');
const sortType = ref('newest');

// 防止组件卸载后执行异步操作
let isUnmounted = ref(false);
onUnmounted(() => {
  isUnmounted.value = true;
  isComponentReady.value = false;
});

// 计算属性：过滤有效资源
const filteredResources = computed(() => {
  console.log('🔍 计算属性 - 原始资源数据：', resources.value);
  const validResources = Array.isArray(resources.value) 
    ? resources.value.filter(res => res?.id && typeof res.id === 'number') 
    : [];
  console.log('🔍 计算属性 - 过滤后有效资源：', validResources);
  return validResources;
});

// 组件初始化
onMounted(async () => {
  try {
    console.log('📌 组件开始初始化');
    await nextTick();
    console.log('📌 组件实例初始化完成');
    isComponentReady.value = true;
    
    await fetchFilterOptions();
    fetchResourceList();
  } catch (error) {
    console.error('❌ 组件初始化失败：', error);
    ElMessage.error('页面加载异常，请刷新重试');
    isComponentReady.value = false;
  }
});

// 获取筛选选项（适配请求工具格式）
const fetchFilterOptions = async () => {
  if (!isComponentReady.value || isUnmounted.value) return;
  
  try {
    console.log('📥 开始获取筛选选项');
    const res = await request.get('/home'); // 直接返回后端响应体（{code:200, data:{...}}）
    console.log('📥 筛选选项接口响应：', res);
    
    if (!isUnmounted.value) {
      filterOptions.value = {
        subjects: Array.isArray(res?.data?.filter_options?.subjects) ? res.data.filter_options.subjects : [],
        grades: Array.isArray(res?.data?.filter_options?.grades) ? res.data.filter_options.grades : [],
        schools: Array.isArray(res?.data?.filter_options?.schools) ? res.data.filter_options.schools : []
      };
      console.log('📥 筛选选项最终数据：', filterOptions.value);
    }
  } catch (error) {
    console.error('❌ 获取筛选选项失败：', error);
    ElMessage.error('筛选条件加载失败，不影响资源浏览');
    filterOptions.value = { subjects: [], grades: [], schools: [] };
  }
};

// 核心修复：适配请求工具的响应格式（无status属性，直接返回后端数据）
const fetchResourceList = async () => {
  if (!isComponentReady.value || isUnmounted.value) return;
  
  isLoading.value = true;
  try {
    console.log('📥 开始获取资源列表');
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      subject: selectedSubject.value,
      grade: selectedGrade.value,
      school: selectedSchool.value,
      type: selectedType.value,
      is_high_quality: isHighQuality.value ? 1 : 0,
      sort: sortType.value
    };
    console.log('📥 资源列表请求参数：', params);

    const res = await request.get('/resources/list', { params }); // 直接返回后端根数据（{count:2, results:{...}}）
    console.log('📥 资源列表完整响应：', res);

    if (!isUnmounted.value) {
      const rootData = res || {}; // 响应体即根数据，无需res.data
      const results = rootData.results || {};

      console.log('📥 解析 - 总条数：', rootData.count);
      console.log('📥 解析 - 业务状态：', results.code);
      console.log('📥 解析 - 资源数组：', results.data);

      if (results.code === 200) { // 仅通过后端业务状态码判断成功
        resources.value = Array.isArray(results.data) ? results.data : [];
        totalCount.value = Number(rootData.count) || 0;
        
        console.log('✅ 资源加载成功 - 总条数：', totalCount.value);
        ElMessage.success(results.message || '资源加载成功');
      } else {
        const errorMsg = results.message || '未知业务错误';
        console.error('❌ 资源加载失败：', errorMsg);
        ElMessage.error(`获取资源列表失败：${errorMsg}`);
        resources.value = [];
        totalCount.value = 0;
      }
    }
  } catch (error) {
    console.error('❌ 资源列表请求异常（网络/跨域）：', error);
    ElMessage.error('网络异常，无法连接服务器');
    resources.value = [];
    totalCount.value = 0;
  } finally {
    isLoading.value = false;
  }
};

// 监听路由参数变化
watch(
  () => route.query,
  (newQuery) => {
    if (!isComponentReady.value || isUnmounted.value) return;
    
    selectedSubject.value = String(newQuery.subject || '');
    selectedGrade.value = String(newQuery.grade || '');
    selectedSchool.value = String(newQuery.school || '');
    isHighQuality.value = newQuery.is_high_quality === 'true';
    
    setTimeout(() => fetchResourceList(), 100);
  },
  { immediate: true, deep: true }
);

// 筛选条件变化处理
const handleFilterChange = () => {
  if (isLoading.value || !isComponentReady.value) return;
  
  currentPage.value = 1;
  fetchResourceList();
  
  router.push({
    name: 'resourceList',
    query: {
      subject: selectedSubject.value,
      grade: selectedGrade.value,
      school: selectedSchool.value,
      is_high_quality: isHighQuality.value ? 'true' : '',
      type: selectedType.value,
      sort: sortType.value
    }
  }).catch(err => console.error('❌ 路由跳转失败：', err));
};

// 分页大小变化
const handleSizeChange = (val) => {
  if (isLoading.value || !isComponentReady.value) return;
  pageSize.value = val;
  currentPage.value = 1;
  fetchResourceList();
};

// 页码变化
const handleCurrentChange = (val) => {
  if (isLoading.value || !isComponentReady.value) return;
  currentPage.value = val;
  fetchResourceList();
};

// 跳转到详情页
const goToDetail = (resourceId) => {
  if (!resourceId || !isComponentReady.value) return;
  
  router.push({ name: 'resourceDetail', params: { id: resourceId } }).catch(err => {
    console.error('❌ 跳转详情页失败：', err);
    ElMessage.error('无法打开详情页，请重试');
  });
};

// 补全下载资源逻辑（适配请求工具格式，处理blob类型）
const handleDownload = async (resourceId) => {
  if (!resourceId || !isComponentReady.value) {
    ElMessage.warning('资源ID无效');
    return;
  }

  try {
    console.log('📥 开始下载资源 - ID：', resourceId);
    // 请求工具支持blob类型，直接返回blob数据（无status属性，响应体即blob）
    const res = await request.get(`/resources/download/${resourceId}`, { responseType: 'blob' });
    console.log('📥 下载响应（blob类型）：', res);

    // 从响应头获取文件名（适配不同后端返回格式）
    const contentDisposition = res.headers?.['content-disposition'] || res.headers?.['Content-Disposition'];
    let fileName = '未知资源';
    
    if (contentDisposition) {
      // 匹配 filename=xxx 或 filename*=UTF-8''xxx 格式
      const match = contentDisposition.match(/filename=([^;]+)|filename\*=UTF-8''([^;]+)/i);
      if (match) {
        fileName = match[1] || match[2];
        // 解码URL编码的文件名（如空格→%20）
        fileName = decodeURIComponent(fileName.replace(/["']/g, ''));
      }
    }

    // 创建下载链接并触发下载
    const url = window.URL.createObjectURL(res); // 直接使用res（blob类型）
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();

    // 延迟清理资源，避免内存泄漏
    setTimeout(() => {
      window.URL.revokeObjectURL(url); // 释放blob URL
      document.body.removeChild(a); // 移除临时a标签
      console.log('✅ 下载资源清理完成 - 文件名：', fileName);
    }, 100);

    ElMessage.success(`下载开始：${fileName}`);
  } catch (error) {
    console.error('❌ 资源下载失败：', error);
    ElMessage.error('下载失败，请检查网络或资源是否存在');
  }
};

// 辅助函数：资源类型转换
const getResourceTypeName = (type) => {
  if (!type) return '其他';
  const typeMap = { 'document': '文档', 'video': '视频', 'audio': '音频', 'image': '图片' };
  return typeMap[type] || '其他';
};

// 辅助函数：日期格式化
const formatDate = (dateString) => {
  if (!dateString) return '未知时间';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '未知时间';
    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
  } catch (error) {
    return '未知时间';
  }
};

// 辅助函数：文件大小格式化
const formatFileSize = (size) => {
  if (isNaN(size) || size < 0) size = 0;
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
};
</script>

<style scoped lang="scss">
.resource-list-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.page-header {
  margin-bottom: 20px;

  h1 {
    font-size: 24px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
  }

  .subtitle {
    color: #666;
    .count {
      color: #1989fa;
      font-weight: 600;
    }
  }
}

.filter-container {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 30px;
  flex-wrap: wrap;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;

  .filter-select {
    width: 150px;
  }

  .high-quality-checkbox {
    margin-left: auto;
    color: #1989fa;
  }
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.resource-card {
  height: 100%;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  }

  .card-header {
    position: relative;
    margin-bottom: 12px;
    padding-top: 8px;

    .resource-tag {
      position: absolute;
      top: 0;
      right: 36px;
      background: #409eff;
      color: #fff;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 4px;
    }

    .resource-type {
      position: absolute;
      top: 0;
      right: 0;
      background: #67c23a;
      color: #fff;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 4px;
    }

    .resource-title {
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin: 0;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
  }

  .card-body {
    margin-bottom: 16px;

    .resource-meta {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 13px;
      color: #666;
      margin-bottom: 12px;
    }

    .resource-stats {
      display: flex;
      gap: 16px;
      font-size: 12px;
      color: #999;

      i {
        margin-right: 4px;
      }
    }
  }

  .card-footer {
    text-align: right;
  }
}

.empty-placeholder {
  padding: 80px 0;
  text-align: center;
}

.pagination-container {
  text-align: center;
  margin-top: 20px;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .filter-container {
    gap: 12px;

    .filter-select {
      width: calc(50% - 6px);
    }

    .high-quality-checkbox {
      margin-left: 0;
      width: 100%;
      margin-top: 8px;
      text-align: left;
    }
  }

  .resource-grid {
    grid-template-columns: 1fr;
  }
}
</style>