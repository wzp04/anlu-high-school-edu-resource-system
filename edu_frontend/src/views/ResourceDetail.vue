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

    <!-- 详情内容：添加 resourceData 存在判断，避免空指针 -->
    <div v-else-if="resourceData" class="detail-content">
      <!-- 顶部操作栏：样式统一，按钮间距一致 -->
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
          <!-- 下载按钮：样式统一，禁用状态清晰 -->
          <el-button 
            type="success" 
            icon="el-icon-download" 
            @click="handleDownload"
            :loading="isDownloading"
            :disabled="!resourceData.file_url"
            class="download-btn"
          >
            下载资源
            <el-tooltip v-if="!resourceData.file_url" content="暂无下载链接" placement="top">
              <i class="el-icon-question"></i>
            </el-tooltip>
          </el-button>
          <!-- 点赞按钮：已实现切换功能，样式强化 -->
          <el-button 
            type="primary" 
            icon="el-icon-thumbs-up" 
            @click="handleLike"
            :class="{ 'liked': resourceData.is_liked }"
            class="like-btn"
          >
            {{ resourceData.is_liked ? '已点赞' : '点赞' }}
            <span class="like-count" v-if="resourceData.like_count > 0">
              ({{ resourceData.like_count }})
            </span>
          </el-button>
          <!-- 收藏按钮：修复图标使用规范，消除警告 -->
          <el-button 
            type="warning" 
            @click="handleCollect"
            :class="{ collected: isCollected }"
            class="collect-btn"
          >
            <template #icon>
              <el-icon :size="16"> <!-- 显式设置图标大小，更规范 -->
                <StarOffFilled v-if="!isCollected" />
                <StarFilled v-else />
              </el-icon>
            </template>
            {{ isCollected ? '已收藏' : '收藏' }}
            <span class="collect-count" v-if="resourceData.collect_count > 0">
              ({{ resourceData.collect_count }})
            </span>
          </el-button>
        </div>
      </div>

      <!-- 资源基本信息卡片：完善审核状态标签，优化排版 -->
      <el-card class="info-card">
        <div class="resource-title">
          <h1>{{ resourceData.title || '未知资源' }}</h1>
          <el-tag v-if="resourceData.is_high_quality" type="success">优质资源</el-tag>
          <el-tag type="info">{{ getResourceTypeName(resourceData?.type) }}</el-tag>
          <!-- 审核状态标签：优化类型颜色，调整间距，符合用户认知 -->
          <el-tag 
            v-if="resourceData.is_approved !== undefined" 
            :type="resourceData.is_approved ? 'success' : 'warning'"
            style="margin-left: 8px;"
          >
            {{ resourceData.is_approved ? '已审核' : '待审核' }}
          </el-tag>
        </div>

        <div class="resource-meta">
          <div class="meta-item">
            <span class="meta-label">上传学校：</span>
            <span class="school-name">{{ resourceData.school_name || '未知学校' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">上传者：</span>
            <span>{{ resourceData.uploader_name || '匿名用户' }}</span>
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
          <div class="meta-item">
            <span class="meta-label">收藏数：</span>
            <span>{{ resourceData.collect_count || 0 }}</span>
          </div>
        </div>
      </el-card>

      <!-- 资源描述：样式统一，间距规范 -->
      <el-card class="desc-card" header="资源描述">
        <div class="resource-desc">
          {{ resourceData.description || '该资源未添加描述信息' }}
        </div>
      </el-card>

      <!-- 资源预览区：完善加载/错误状态，优化PDF预览，新增无预览引导 -->
      <el-card class="preview-card" header="资源预览" v-if="canPreview">
        <div class="preview-container">
          <!-- 图片预览：支持放大，加载/错误状态友好 -->
          <template v-if="resourceData?.type === 'image'">
            <el-image 
              :src="resourceData.file_url" 
              fit="contain" 
              preview-teleported
              :preview-src-list="[resourceData.file_url]"
              class="preview-image"
            >
              <template #loading>
                <div class="image-loading">
                  <el-spinner size="40" />
                  <p style="margin-top: 10px; color: #999;">图片加载中...</p>
                </div>
              </template>
              <template #error>
                <div class="image-error">
                  <el-icon style="font-size: 40px; color: #f56c6c;">
                    <PictureFilled />
                  </el-icon>
                  <p style="margin-top: 10px; color: #999;">图片预览失败</p>
                </div>
              </template>
            </el-image>
          </template>

          <!-- PDF预览：支持浏览器兼容，降级提示 -->
          <template v-else-if="resourceData?.type === 'document' && isPdf">
            <div class="pdf-container">
              <embed 
                :src="resourceData.file_url" 
                type="application/pdf" 
                width="100%" 
                height="600px"
                class="pdf-embed"
              >
              <!-- 浏览器不支持PDF时显示下载引导 -->
              <div class="pdf-fallback">
                <el-icon style="font-size: 40px; color: #c0c4cc; margin-bottom: 16px;"><FileTextFilled /></el-icon>
                <p style="color: #999; margin-bottom: 16px;">浏览器不支持PDF在线预览</p>
                <el-button type="primary" size="small" @click="handleDownload">
                  <el-icon style="margin-right: 4px;"><Download /></el-icon>下载PDF
                </el-button>
              </div>
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #999;">
              提示：PDF预览需浏览器支持，若无法显示请直接下载
            </p>
          </template>

          <!-- 其他文档：无预览，引导下载 -->
          <template v-else-if="canPreview">
            <div class="no-preview">
              <el-icon style="font-size: 60px; color: #c0c4cc; margin-bottom: 16px;"><FileTextFilled /></el-icon>
              <h3 style="font-size: 16px; color: #666; margin-bottom: 8px;">该资源不支持在线预览</h3>
              <p style="color: #999; margin-bottom: 16px;">文件类型：{{ getResourceTypeName(resourceData?.type) }}</p>
              <el-button type="primary" @click="handleDownload">
                <el-icon style="margin-right: 4px;"><Download /></el-icon>立即下载
              </el-button>
            </div>
          </template>
        </div>
      </el-card>

      <!-- 评论区：优化样式，贴合Element Plus风格 -->
      <el-card class="comment-card" header="用户评论">
        <!-- 评论输入框：规范属性，移除非法字符 -->
        <div class="comment-input">
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="3"
            placeholder="请输入你的评论..."
            :border="true"
            class="comment-textarea"
          ></el-input>
          <el-button 
            type="primary" 
            @click="submitComment"
            :disabled="!newComment.trim()"
            class="submit-comment-btn"
          >
            提交评论
          </el-button>
        </div>

        <!-- 评论列表：无评论时显示Element Plus默认空状态 -->
        <el-empty 
          v-if="comments.length === 0" 
          description="暂无评论，快来沙发～"
          style="margin: 40px 0;"
          :image="ElEmpty.PLACEHOLDER_IMAGE_DEFAULT"
        ></el-empty>
        <el-list 
          v-else 
          :data="comments" 
          border 
          class="comment-list"
        >
          <el-list-item 
            v-for="(comment, index) in comments" 
            :key="index"
            class="comment-item"
          >
            <div class="comment-header">
              <span class="comment-author">匿名用户</span>
              <span class="comment-time">{{ formatCommentTime(comment.time) }}</span>
              <el-button 
                type="text" 
                class="delete-comment-btn"
                @click="deleteComment(index)"
                size="small"
              >
                <el-icon style="font-size: 14px;"><Delete /></el-icon> 删除
              </el-button>
            </div>
            <div class="comment-content">
              {{ comment.content }}
            </div>
          </el-list-item>
        </el-list>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="js">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import request from '@/utils/request';
// 导入Element Plus组件和图标（确保星星图标正确导入，无拼写错误）
import { 
  ElMessage, ElEmpty, ElSkeleton, ElTag, ElImage, ElTooltip, ElIcon,
  ElInput, ElButton, ElList, ElListItem, ElSpinner
} from 'element-plus';
import { 
  StarFilled,    // 正确导入：实心星星（已收藏）
  StarOffFilled, // 正确导入：空心星星（未收藏）
  PictureFilled, 
  Download, 
  FileTextFilled, 
  Delete 
} from '@element-plus/icons-vue';

// 路由实例
const router = useRouter();
const route = useRoute();

// 状态管理：确保初始值为对象，不会为null
const resourceData = ref({
  collect_count: 0,
  is_liked: false,
  like_count: 0,
  type: '', // 新增默认type，避免访问null.type
  file_url: '', // 新增默认file_url，避免空指针
  file_name: '' // 新增默认file_name，兼容isPdf计算属性
});
const isLoading = ref(true);
const hasError = ref(false);
const isComponentReady = ref(false);
const isDownloading = ref(false);
let isUnmounted = ref(false);
const isCollected = ref(false);

// 评论区状态：前端临时存储评论
const newComment = ref(''); // 评论输入框绑定值
const comments = ref([]); // 评论列表数据

// 计算属性：添加resourceData.value存在判断，避免空指针
const canPreview = computed(() => {
  if (!resourceData.value) return false;
  const type = resourceData.value.type;
  return ['image', 'document'].includes(type) && resourceData.value.file_url;
});

// 计算属性：添加file_name存在判断，兼容PDF判断
const isPdf = computed(() => {
  if (!resourceData.value) return false;
  const fileName = resourceData.value.file_name || '';
  return fileName.toLowerCase().endsWith('.pdf');
});

// 组件初始化
onMounted(async () => {
  try {
    await nextTick();
    isComponentReady.value = true;
    
    // 解析资源ID（纯数字过滤，避免无效ID）
    let resourceId = route.params.id;
    resourceId = resourceId?.toString().replace(/[^0-9]/g, '') || '';
    const pureId = Number(resourceId);
    
    if (!resourceId || isNaN(pureId) || pureId <= 0) {
      throw new Error('资源ID无效（必须是正整数）');
    }
    
    await fetchResourceDetail(pureId);
  } catch (error) {
    console.error('详情页初始化失败：', error.message);
    ElMessage.error(`加载失败：${error.message}`);
    isLoading.value = false;
    hasError.value = true;
    resourceData.value = { ...resourceData.value };
  }
});

// 获取资源详情：确保resourceData不会被设为null
const fetchResourceDetail = async (resourceId) => {
  if (!isComponentReady.value || isUnmounted.value) return;
  
  isLoading.value = true;
  try {
    const res = await request.get(`/resources/${resourceId}/`); 
    console.log('资源详情接口返回：', res);

    if (!isUnmounted.value) {
      if (res.code === 200 && res.data) {
        // 合并数据，保留默认值，避免字段缺失
        resourceData.value = {
          ...resourceData.value,
          ...res.data
        };
        // 二次兜底，确保关键字段存在
        resourceData.value.is_liked = resourceData.value.is_liked ?? false;
        resourceData.value.like_count = resourceData.value.like_count ?? 0;
        resourceData.value.collect_count = resourceData.value.collect_count ?? 0;
        resourceData.value.type = resourceData.value.type ?? '';
        resourceData.value.file_url = resourceData.value.file_url ?? '';
        resourceData.value.file_name = resourceData.value.file_name ?? '';
        
        isCollected.value = false;
        hasError.value = false;
        ElMessage.success('资源详情加载成功');
      } else if (res.code === 404) {
        hasError.value = true;
        ElMessage.error('该资源不存在或已被删除');
        resourceData.value = { ...resourceData.value };
      } else {
        console.error('资源详情返回异常：', res.message || '后端格式错误');
        hasError.value = true;
        ElMessage.error(res.message || '资源加载失败');
        resourceData.value = { ...resourceData.value };
      }
    }
  } catch (error) {
    console.error('资源详情请求失败：', {
      接口: `/resources/${resourceId}/`,
      错误: error.message,
      状态码: error.response?.status
    });
    hasError.value = true;
    const errorMsg = error.response?.status === 404 
      ? '资源不存在（404）' 
      : error.response?.status === 500 
        ? '服务器内部错误' 
        : '网络异常，无法连接服务器';
    ElMessage.error(`加载失败：${errorMsg}`);
    resourceData.value = { ...resourceData.value };
  } finally {
    if (!isUnmounted.value) {
      isLoading.value = false;
    }
  }
};

// 返回资源列表
const goBack = () => {
  router.push('/resources/list').catch(err => {
    console.error('返回列表失败：', err);
    ElMessage.error('无法返回列表，请刷新页面');
  });
};

// 下载资源（支持权限验证接口）
const handleDownload = async () => {
  if (!resourceData.value?.file_url) {
    ElMessage.warning('暂无下载链接');
    return;
  }

  const resourceId = resourceData.value.id?.toString().replace(/[^0-9]/g, '');
  if (!resourceId || isDownloading.value) return;

  isDownloading.value = true;
  try {
    const res = await request.get(`/resources/${resourceId}/download/`, { 
      responseType: 'blob' 
    });

    // 解析文件名（兼容 Content-Disposition 两种格式）
    const contentDisposition = res.headers['content-disposition'] || res.headers['Content-Disposition'];
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
    resourceData.value.download_count = (resourceData.value.download_count || 0) + 1;
  } catch (error) {
    console.error('下载失败：', error.message);
    ElMessage.error('下载失败，请检查接口或网络');
  } finally {
    isDownloading.value = false;
  }
};

// 点赞功能（已实现取消，优化空指针判断）
const handleLike = () => {
  if (!resourceData.value) return;
  const newLikedState = !resourceData.value.is_liked;
  resourceData.value.is_liked = newLikedState;
  
  // 计数更新（避免负数）
  resourceData.value.like_count = newLikedState 
    ? (resourceData.value.like_count || 0) + 1 
    : Math.max(0, (resourceData.value.like_count || 0) - 1);
  
  ElMessage[newLikedState ? 'success' : 'info'](
    newLikedState ? '点赞成功' : '已取消点赞'
  );
};

// 收藏功能（优化空指针判断）
const handleCollect = () => {
  if (!resourceData.value) return;
  isCollected.value = !isCollected.value;
  
  // 计数更新（避免负数）
  resourceData.value.collect_count = isCollected.value 
    ? (resourceData.value.collect_count || 0) + 1 
    : Math.max(0, (resourceData.value.collect_count || 0) - 1);
  
  ElMessage[isCollected.value ? 'success' : 'info'](
    isCollected.value ? '收藏成功' : '已取消收藏'
  );
};

// 评论提交功能（前端临时存储）
const submitComment = () => {
  const commentContent = newComment.value.trim();
  if (!commentContent) return;
  
  // 添加评论到列表（包含时间戳）
  comments.value.push({
    content: commentContent,
    time: new Date().getTime() // 存储时间戳，用于格式化
  });
  
  // 清空输入框
  newComment.value = '';
  ElMessage.success('评论提交成功');
};

// 评论删除功能
const deleteComment = (index) => {
  comments.value.splice(index, 1);
  ElMessage.info('评论已删除');
};

// 资源类型中文转换（优化类型映射，覆盖更多场景）
const getResourceTypeName = (type) => {
  if (!type) return '其他';
  const typeMap = { 
    'document': '文档', 'video': '视频', 'audio': '音频', 'image': '图片',
    'doc': '文档', 'docx': '文档', 'pdf': '文档', 'jpg': '图片', 'png': '图片',
    'jpeg': '图片', 'gif': '图片', 'mp4': '视频', 'mp3': '音频', 'wav': '音频'
  };
  return typeMap[type.toLowerCase()] || '其他';
};

// 日期格式化（兼容多种格式）
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

// 评论时间格式化（显示相对时间或具体时间）
const formatCommentTime = (timestamp) => {
  const now = new Date().getTime();
  const diff = now - timestamp; // 时间差（毫秒）
  
  // 1分钟内：刚刚
  if (diff < 60 * 1000) return '刚刚';
  // 1小时内：X分钟前
  if (diff < 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 1000))}分钟前`;
  }
  // 1天内：X小时前
  if (diff < 24 * 60 * 60 * 1000) {
    return `${Math.floor(diff / (60 * 60 * 1000))}小时前`;
  }
  // 超过1天：显示具体日期时间
  const date = new Date(timestamp);
  return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
};

// 文件大小格式化
const formatFileSize = (size) => {
  if (isNaN(size) || size < 0) return '0 B';
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
};

// 组件卸载清理（避免内存泄漏）
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

/* 顶部操作栏：样式统一，间距规范 */
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

  .like-btn, .collect-btn, .download-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 16px; // 统一按钮内边距
  }

  /* 已点赞样式：强化视觉反馈 */
  .like-btn.liked {
    background-color: #2d8cf0;
    border-color: #2d8cf0;
    color: #fff;
    box-shadow: 0 2px 8px rgba(45, 140, 240, 0.3);
    transition: all 0.3s ease;

    &:hover {
      background-color: #1e88e5;
      border-color: #1e88e5;
    }
  }

  /* 已收藏样式：统一选中状态 */
  .collect-btn.collected {
    background-color: #f9c74f;
    border-color: #f9c74f;
    color: #fff;

    &:hover {
      background-color: #f7b731;
      border-color: #f7b731;
    }
  }

  .like-count, .collect-count {
    margin-left: 4px;
  }

  /* 下载按钮禁用样式：清晰区分 */
  .download-btn.is-disabled {
    background-color: #f5f5f5 !important;
    border-color: #d9d9d9 !important;
    color: #bfbfbf !important;
    cursor: not-allowed;
    opacity: 0.8;
  }
}

/* 资源信息卡：优化排版，避免换行混乱 */
.info-card {
  margin-bottom: 24px;
  border: none;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);
  padding: 24px; // 统一内边距

  .resource-title {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap; // 自适应换行，避免拥挤

    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: #333;
      flex: 1;
      min-width: 200px; // 最小宽度，避免标题过短
    }

    .el-tag {
      margin-bottom: 4px;
      height: 28px;
      line-height: 28px; // 统一标签行高
    }
  }

  .resource-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 24px;
    padding-top: 20px;
    border-top: 1px solid #f5f5f5;

    .meta-item {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      color: #666;
      min-width: 180px; // 固定最小宽度，排版整齐

      .meta-label {
        color: #999;
        font-weight: 500;
        white-space: nowrap; // 标签不换行
      }

      .school-name {
        color: #1989fa;
        font-weight: 500;
      }
    }
  }
}

/* 资源描述：样式统一，提升可读性 */
.desc-card {
  margin-bottom: 24px;
  border: none;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);
  padding: 24px;

  .resource-desc {
    padding: 16px;
    font-size: 15px;
    color: #555;
    line-height: 1.8;
    white-space: pre-line;
    background-color: #fafafa;
    border-radius: 4px;
    min-height: 120px; // 最小高度，避免内容过短时布局塌陷
  }
}

/* 预览区：完善加载/错误状态样式，响应式适配 */
.preview-card {
  margin-bottom: 24px;
  border: none;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);
  padding: 24px;

  .preview-container {
    position: relative;
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

  // 图片加载状态
  .image-loading, .image-error {
    width: 100%;
    height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: #f5f5f5;
    border-radius: 4px;
  }

  // PDF预览容器
  .pdf-container {
    position: relative;
    width: 100%;
    height: 600px;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    overflow: hidden;
  }

  // PDF不支持时的降级显示
  .pdf-fallback {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    background: rgba(255, 255, 255, 0.9);
    padding: 24px;
    border-radius: 4px;
    width: 300px;
  }

  // 无预览资源样式
  .no-preview {
    width: 100%;
    height: 300px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background-color: #fafafa;
    border-radius: 4px;
    padding: 20px;
  }
}

/* 评论区：核心优化，贴合Element Plus风格 */
.comment-card {
  margin-top: 24px; // 与上方预览区保持统一间距（24px）
  border: none;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.08);
  padding: 24px; // 与其他卡片内边距一致

  // 评论输入区：优化间距和样式
  .comment-input {
    margin-bottom: 24px; // 输入区与列表区间距放大，提升层次感
  }

  // 评论输入框：使用Element Plus默认样式，去除自定义边框
  .comment-textarea {
    --el-input-border-color: var(--el-border-color); // 继承默认边框色
    --el-input-focus-border-color: var(--el-color-primary); // 聚焦时主色调
    margin-bottom: 12px; // 输入框与按钮间距（12px，符合Element规范）
  }

  // 提交按钮：与顶部点赞按钮样式完全统一
  .submit-comment-btn {
    padding: 6px 16px;
    font-size: 14px;
    border-radius: var(--el-border-radius-base); // 继承默认圆角
  }

  // 评论列表：优化边框和内边距
  .comment-list {
    border-radius: var(--el-border-radius-base);
    --el-list-item-padding: 16px; // 列表项内边距统一
  }

  .comment-item {
    border-bottom: 1px solid var(--el-border-color-lighter); // 浅色分隔线，更柔和

    &:last-child {
      border-bottom: none;
    }
  }

  .comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;

    .comment-author {
      font-weight: 500;
      color: #333;
      font-size: 14px;
    }

    .comment-time {
      font-size: 12px;
      color: #999;
    }

    .delete-comment-btn {
      color: #f56c6c;
      padding: 0;

      &:hover {
        color: #ff4d4f;
        background-color: transparent; // 去除hover背景，更简洁
      }
    }
  }

  .comment-content {
    font-size: 14px;
    color: #666;
    line-height: 1.6;
    white-space: pre-line;
    padding-bottom: 4px; // 与底部间距平衡
  }
}

/* 响应式适配 - 手机端：优化布局，避免溢出 */
@media (max-width: 768px) {
  .resource-detail-container {
    padding: 12px;
    min-height: calc(100vh - 80px);
  }

  .detail-content {
    padding: 8px;
  }

  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .header-actions {
      width: 100%;
      justify-content: space-between;
    }

    .like-btn, .collect-btn, .download-btn {
      padding: 4px 12px;
      font-size: 13px;
    }
  }

  .info-card {
    padding: 16px;
  }

  .info-card .resource-title h1 {
    font-size: 20px;
  }

  .resource-meta {
    gap: 16px;
  }

  .meta-item {
    min-width: 100% !important; // 移动端独占一行，避免拥挤
  }

  .preview-container {
    min-height: 200px;
  }

  .pdf-container {
    height: 400px;
  }

  .comment-card {
    padding: 16px;
  }

  .comment-textarea {
    --el-input-height: 100px; // 移动端输入框高度适配
  }
}

/* 响应式适配 - 平板端：平衡布局和可读性 */
@media (min-width: 769px) and (max-width: 1024px) {
  .resource-meta {
    gap: 20px;
  }

  .meta-item {
    min-width: 140px;
  }

  .pdf-container {
    height: 500px;
  }
}
</style>