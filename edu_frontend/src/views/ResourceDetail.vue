<template>
  <div class="resource-detail-container" v-if="isComponentReady">
    <!-- 加载状态 -->
    <el-skeleton v-if="isLoading" class="loading-skeleton" :loading="isLoading">
      <template #template>
        <div class="skeleton-header" style="height: 60px;"></div>
        <div class="skeleton-body" style="margin-top: 20px;">
          <div style="height: 200px; margin-bottom: 20px;"></div>
          <div style="height: 16px; margin-bottom: 10px; width: 80%;"></div>
          <div style="height: 16px; margin-bottom: 10px; width: 60%;"></div>
          <div style="height: 16px; margin-bottom: 10px; width: 70%;"></div>
          <div style="height: 16px; margin-bottom: 10px; width: 90%;"></div>
        </div>
      </template>
    </el-skeleton>

    <!-- 错误状态 -->
    <div v-else-if="hasError" class="error-container">
      <el-empty 
        description="资源不存在或已被删除" 
        :image="ElEmpty.PLACEHOLDER_IMAGE_SIMPLE"
      >
        <el-button type="primary" @click="goBack">返回资源列表</el-button>
      </el-empty>
    </div>

    <!-- 详情内容 -->
    <div v-else class="detail-content">
      <!-- 顶部操作栏 -->
      <div class="detail-header">
        <el-button 
          type="default" 
          icon="el-icon-back" 
          @click="goBack"
          class="back-btn"
        >
          返回列表
        </el-button>
        <div class="header-actions">
          <el-button 
            type="success" 
            icon="el-icon-download" 
            @click="handleDownload"
            :loading="isDownloading"
          >
            下载资源
          </el-button>
          <el-button 
            type="primary" 
            icon="el-icon-thumbs-up" 
            @click="handleLike"
            :loading="isLiking"
            :disabled="resourceData.is_liked"
          >
            {{ resourceData.is_liked ? '已点赞' : '点赞' }}
            <span class="like-count" v-if="resourceData.like_count > 0">
              ({{ resourceData.like_count }})
            </span>
          </el-button>
        </div>
      </div>

      <!-- 资源基本信息卡片 -->
      <el-card class="info-card">
        <div class="resource-title">
          <h1>{{ resourceData.title || '未知资源' }}</h1>
          <el-tag v-if="resourceData.is_high_quality" type="success">优质资源</el-tag>
          <el-tag type="info">{{ getResourceTypeName(resourceData.type) }}</el-tag>
        </div>

        <div class="resource-meta">
          <div class="meta-item">
            <span class="meta-label">上传学校：</span>
            <span>{{ resourceData.school_name || '未知学校' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">学科年级：</span>
            <span>{{ resourceData.subject || '未知学科' }} · {{ resourceData.grade || '未知年级' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">上传时间：</span>
            <span>{{ formatDate(resourceData.upload_time) || '未知时间' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">文件大小：</span>
            <span>{{ formatFileSize(resourceData.file_size) || '0 B' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">下载次数：</span>
            <span>{{ resourceData.download_count || 0 }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">点赞数：</span>
            <span>{{ resourceData.like_count || 0 }}</span>
          </div>
        </div>
      </el-card>

      <!-- 资源描述 -->
      <el-card class="desc-card" header="资源描述">
        <div class="resource-desc">
          {{ resourceData.description || '该资源未添加描述信息' }}
        </div>
      </el-card>

      <!-- 资源预览 -->
      <el-card class="preview-card" header="资源预览" v-if="canPreview">
        <div class="preview-container">
          <template v-if="resourceData.type === 'image'">
            <el-image 
              :src="resourceData.file_url" 
              fit="contain" 
              preview-teleported
              :preview-src-list="[resourceData.file_url]"
              class="preview-image"
            >
              <template #error>
                <div class="image-error">图片预览失败</div>
              </template>
            </el-image>
          </template>
          <template v-if="resourceData.type === 'document' && isPdf">
            <div class="pdf-preview">
              <embed 
                :src="resourceData.file_url" 
                type="application/pdf" 
                width="100%" 
                height="600px"
                class="pdf-embed"
              >
              <div class="pdf-tip">提示：PDF预览需浏览器支持，若无法预览请直接下载</div>
            </div>
          </template>
          <template v-else-if="canPreview && !isPdf">
            <el-empty description="该文档格式暂不支持在线预览，请下载查看"></el-empty>
          </template>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="js">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import request from '@/utils/request';
import { ElMessage, ElEmpty, ElSkeleton, ElTag, ElImage } from 'element-plus';

// 路由实例
const router = useRouter();
const route = useRoute();

// 状态管理
const resourceData = ref({});
const isLoading = ref(true);
const hasError = ref(false);
const isComponentReady = ref(false);
const isDownloading = ref(false);
const isLiking = ref(false);
let isUnmounted = ref(false);

// 计算属性
const canPreview = computed(() => {
  const type = resourceData.value.type;
  return ['image', 'document'].includes(type) && resourceData.value.file_url;
});

const isPdf = computed(() => {
  const fileName = resourceData.value.file_name || '';
  return fileName.toLowerCase().endsWith('.pdf');
});

// 组件初始化：匹配后端 pk 参数（资源ID）
onMounted(async () => {
  try {
    await nextTick();
    isComponentReady.value = true;
    
    // 从路由参数获取资源ID（后端用 pk 接收，前端传递纯数字ID）
    let resourceId = route.params.id;
    resourceId = resourceId?.toString().replace(/[^0-9]/g, '') || '';
    const pureId = Number(resourceId);
    
    if (!resourceId || isNaN(pureId) || pureId <= 0) {
      throw new Error('资源ID无效（必须是正整数）');
    }
    
    console.log('后端 pk 参数值：', pureId);
    await fetchResourceDetail(pureId);
  } catch (error) {
    console.error('详情页初始化失败：', error.message);
    ElMessage.error(`加载失败：${error.message}`);
    isLoading.value = false;
    hasError.value = true;
  }
});

// 核心：完全匹配后端资源详情接口（RESTful 风格：/api/resources/<int:pk>/）
const fetchResourceDetail = async (resourceId) => {
  if (!isComponentReady.value || isUnmounted.value) return;
  
  isLoading.value = true;
  try {
    // 后端接口：GET /api/resources/<int:pk>/（request.js 已拼接 baseURL）
    const res = await request.get(`/resources/${resourceId}/`); 
    console.log('请求后端接口：', `http://127.0.0.1:8000/api/resources/${resourceId}/`);
    console.log('后端返回数据：', res);

    if (!isUnmounted.value) {
      // 适配后端返回格式（假设后端返回 {code:200, data:{...}}，若直接返回资源对象则改为 resourceData.value = res）
      if (res.code === 200 && res.data) {
        resourceData.value = res.data;
        hasError.value = false;
        ElMessage.success('资源详情加载成功');
      } else if (res.code === 404) {
        hasError.value = true;
        ElMessage.error('该资源不存在或已被删除');
      } else {
        console.error('资源详情获取失败：', res.message || '后端返回格式异常');
        hasError.value = true;
        ElMessage.error(res.message || '资源加载失败');
      }
    }
  } catch (error) {
    console.error('资源详情请求异常：', {
      接口路径: `http://127.0.0.1:8000/api/resources/${resourceId}/`,
      错误信息: error.message,
      状态码: error.response?.status
    });
    hasError.value = true;
    if (error.response?.status === 404) {
      ElMessage.error('该资源不存在（后端返回404）');
    } else if (error.response?.status === 500) {
      ElMessage.error('服务器内部错误，请联系后端排查');
    } else {
      ElMessage.error('网络异常，无法连接服务器');
    }
  } finally {
    if (!isUnmounted.value) {
      isLoading.value = false;
    }
  }
};

// 返回资源列表页（匹配后端 /api/resources/list/）
const goBack = () => {
  router.push('/resources/list').catch(err => {
    console.error('返回列表页失败：', err);
    ElMessage.error('无法返回列表页，请刷新页面');
  });
};

// 资源下载接口（按后端风格推测：/api/resources/<int:pk>/download/，若后端路径不同可修改）
const handleDownload = async () => {
  const resourceId = resourceData.value.id;
  if (!resourceId || isDownloading.value) return;

  isDownloading.value = true;
  try {
    // 后端下载接口：GET /api/resources/<int:pk>/download/（与点赞接口同层级，符合后端URL设计规范）
    const res = await request.get(`/resources/${resourceId}/download/`, { 
      responseType: 'blob' 
    });
    console.log('请求下载接口：', `http://127.0.0.1:8000/api/resources/${resourceId}/download/`);

    // 解析后端返回的文件名（Content-Disposition）
    const contentDisposition = res.headers?.['content-disposition'] || res.headers?.['Content-Disposition'];
    let fileName = resourceData.value.file_name || '未知资源';
    
    if (contentDisposition) {
      const match = contentDisposition.match(/filename=([^;]+)|filename\*=UTF-8''([^;]+)/i);
      if (match) {
        fileName = match[1] || match[2];
        fileName = decodeURIComponent(fileName.replace(/["']/g, ''));
      }
    }

    // 触发浏览器下载
    const url = window.URL.createObjectURL(res);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();

    // 清理临时资源
    setTimeout(() => {
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    }, 100);

    ElMessage.success(`下载开始：${fileName}`);
    // 前端临时更新下载次数（实际以后端接口返回为准）
    resourceData.value.download_count = (resourceData.value.download_count || 0) + 1;
  } catch (error) {
    console.error('资源下载失败：', {
      接口路径: `http://127.0.0.1:8000/api/resources/${resourceId}/download/`,
      错误信息: error.message
    });
    ElMessage.error('下载失败，请确认后端下载接口路径是否为 /api/resources/<int:pk>/download/');
  } finally {
    isDownloading.value = false;
  }
};

// 资源点赞接口（完全匹配后端：POST /api/resources/<int:pk>/like/）
const handleLike = async () => {
  const resourceId = resourceData.value.id;
  if (!resourceId || isLiking.value || resourceData.value.is_liked) return;

  isLiking.value = true;
  try {
    // 后端点赞接口：POST /api/resources/<int:pk>/like/（路径参数 pk=resourceId）
    const res = await request.post(`/resources/${resourceId}/like/`);
    console.log('请求点赞接口：', `http://127.0.0.1:8000/api/resources/${resourceId}/like/`);

    if (res.code === 200) {
      ElMessage.success('点赞成功');
      resourceData.value.is_liked = true;
      resourceData.value.like_count = (resourceData.value.like_count || 0) + 1;
    } else {
      ElMessage.error(res.message || '点赞失败');
    }
  } catch (error) {
    console.error('点赞请求异常：', {
      接口路径: `http://127.0.0.1:8000/api/resources/${resourceId}/like/`,
      错误信息: error.message,
      状态码: error.response?.status
    });
    ElMessage.error('点赞失败，请检查后端接口是否正常');
  } finally {
    isLiking.value = false;
  }
};

// 辅助函数：资源类型转换（匹配后端可能返回的类型值）
const getResourceTypeName = (type) => {
  if (!type) return '其他';
  const typeMap = { 
    'document': '文档', 
    'video': '视频', 
    'audio': '音频', 
    'image': '图片',
    'doc': '文档',
    'pdf': '文档',
    'jpg': '图片',
    'png': '图片'
  };
  return typeMap[type.toLowerCase()] || '其他';
};

// 辅助函数：日期格式化（适配后端可能返回的日期格式）
const formatDate = (dateString) => {
  if (!dateString) return null;
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return null;
    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  } catch (error) {
    return null;
  }
};

// 辅助函数：文件大小格式化
const formatFileSize = (size) => {
  if (isNaN(size) || size < 0) return '0 B';
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
};

// 组件卸载时清理状态
onUnmounted(() => {
  isUnmounted.value = true;
});
</script>

<style scoped lang="scss">
.resource-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
  background-color: #fafafa;
  min-height: calc(100vh - 120px);
}

.loading-skeleton {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
}

.error-container {
  padding: 80px 0;
  text-align: center;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;

  .back-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #666;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }

  .like-count {
    margin-left: 4px;
  }
}

.info-card {
  margin-bottom: 24px;
  border: none;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);

  .resource-title {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;

    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: #333;
      flex: 1;
      min-width: 200px;
    }

    .el-tag {
      margin-bottom: 4px;
    }
  }

  .resource-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
    padding-top: 16px;
    border-top: 1px solid #f5f5f5;

    .meta-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      color: #666;
      min-width: 180px;

      .meta-label {
        color: #999;
        font-weight: 500;
      }
    }
  }
}

.desc-card {
  margin-bottom: 24px;
  border: none;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);

  .resource-desc {
    padding: 16px;
    font-size: 15px;
    color: #555;
    line-height: 1.8;
    white-space: pre-line;
    background-color: #fafafa;
    border-radius: 4px;
  }
}

.preview-card {
  border: none;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);

  .preview-container {
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;
    background-color: #fafafa;
    border-radius: 4px;
  }

  .preview-image {
    max-width: 100%;
    max-height: 600px;
    border-radius: 4px;
  }

  .image-error {
    width: 100%;
    height: 300px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #999;
    background-color: #f5f5f5;
    border-radius: 4px;
  }

  .pdf-preview {
    width: 100%;
    height: 600px;
    position: relative;

    .pdf-embed {
      border: none;
      border-radius: 4px;
    }

    .pdf-tip {
      position: absolute;
      bottom: 10px;
      right: 20px;
      font-size: 12px;
      color: #999;
    }
  }
}

/* 响应式适配 - 手机端 */
@media (max-width: 768px) {
  .resource-detail-container {
    padding: 12px;
    min-height: calc(100vh - 80px);
  }

  .detail-content {
    padding: 16px;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .header-actions {
      width: 100%;
      justify-content: space-between;
    }
  }

  .info-card .resource-title h1 {
    font-size: 20px;
  }

  .resource-meta {
    gap: 16px;
  }

  .meta-item {
    min-width: 100% !important;
  }

  .preview-container {
    min-height: 200px;
  }

  .pdf-preview {
    height: 400px;
  }
}

/* 响应式适配 - 平板端 */
@media (min-width: 769px) and (max-width: 1024px) {
  .resource-meta {
    gap: 20px;
  }

  .meta-item {
    min-width: 140px;
  }

  .pdf-preview {
    height: 500px;
  }
}
</style>