<template>
  <div class="chunk-uploader">
    <!-- 1. 文件选择区域 -->
    <el-upload
      class="upload-demo"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      action="#"
      :file-list="fileList"
      :disabled="uploadStatus === 'uploading'"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <div class="el-upload__tip" slot="tip">
        <span>支持大文件分片上传（默认5MB/片）</span>
        <span class="text-danger" v-if="file"> - 已选择: {{ file.name }} ({{ formatFileSize(file.size) }})</span>
      </div>
    </el-upload>

    <!-- 2. 上传控制区域 (文件选择后显示) -->
    <div v-if="file" class="upload-controls mt-4">
      <el-progress 
        :percentage="uploadProgress" 
        :status="uploadStatus === 'success' ? 'success' : uploadStatus === 'error' ? 'exception' : ''"
        class="mb-3"
        :text-inside="true"
        :stroke-width="2"
      ></el-progress>
      
      <el-button 
        type="primary" 
        icon="el-icon-upload" 
        @click="startUpload" 
        :disabled="uploadStatus !== 'idle' && uploadStatus !== 'paused'"
        class="mr-2"
      >
        {{ uploadStatus === 'paused' ? '继续上传' : '开始上传' }}
      </el-button>
      
      <el-button 
        type="warning" 
        icon="el-icon-pause" 
        @click="pauseUpload" 
        :disabled="uploadStatus !== 'uploading'"
        class="mr-2"
      >
        暂停上传
      </el-button>
      
      <el-button 
        type="danger" 
        icon="el-icon-close" 
        @click="cancelUpload" 
        :disabled="['idle', 'success'].includes(uploadStatus)"
        class="mr-2"
      >
        取消上传
      </el-button>
      
      <!-- 上传状态文本提示 -->
      <span class="upload-status-text ml-3">
        {{ statusText }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import SparkMD5 from 'spark-md5';

// ------------------- 1. 新增：接收资源额外信息（供审核员查看） -------------------
const props = defineProps({
  // 资源额外信息，如描述、分类、标签等（从父组件传递，如上传表单）
  resourceInfo: {
    type: Object,
    default: () => ({
      desc: '', // 资源描述
      type: '', // 资源分类（如文档、视频、图片）
      tags: []  // 资源标签（如教学、资料、工具）
    })
  }
});

// ------------------- 2. 响应式状态 -------------------
const file = ref(null);             // 当前选择的文件对象
const fileList = ref([]);           // Element Plus Upload 组件的文件列表
const fileMd5 = ref('');            // 文件的 MD5 值（用于唯一标识文件）
const chunks = ref([]);             // 分片信息数组
const chunkSize = ref(5 * 1024 * 1024); // 分片大小（5MB，可调整）
const uploadProgress = ref(0);      // 整体上传进度（0-100）
const uploadStatus = ref('idle');   // 上传状态：idle/paused/uploading/success/error
const currentChunkIndex = ref(0);   // 当前正在上传的分片索引
const abortController = ref(null);  // 用于中断当前分片上传的控制器

// ------------------- 3. 计算属性（优化状态提示） -------------------
const statusText = computed(() => {
  switch (uploadStatus.value) {
    case 'idle': return '等待上传...';
    case 'uploading': return `正在上传分片 ${currentChunkIndex.value + 1}/${chunks.value.length}`;
    case 'paused': return `已暂停（当前进度：${uploadProgress.value}%）`;
    case 'success': return '上传完成，已进入待审核队列！';
    case 'error': return '上传失败，请检查网络或文件后重试';
    default: return '';
  }
});

// ------------------- 4. 工具函数 -------------------
/**
 * 格式化文件大小（B -> KB/MB/GB）
 */
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
};

/**
 * 重置所有上传状态
 */
const resetUploadState = () => {
  file.value = null;
  fileList.value = [];
  fileMd5.value = '';
  chunks.value = [];
  uploadProgress.value = 0;
  uploadStatus.value = 'idle';
  currentChunkIndex.value = 0;
  abortController.value = null;
};

// ------------------- 5. 核心逻辑 -------------------
/**
 * 文件选择变化时触发
 */
const handleFileChange = (uploadFile) => {
  resetUploadState();
  file.value = uploadFile.raw;
  if (!file.value) return;
  fileList.value = [uploadFile];
  calculateFileMd5(file.value);
};

/**
 * 计算文件的 MD5 值
 */
const calculateFileMd5 = (file) => {
  const fileReader = new FileReader();
  const spark = new SparkMD5.ArrayBuffer();
  let chunkIndex = 0;

  const loadNextChunk = () => {
    const start = chunkIndex * chunkSize.value;
    const end = Math.min(start + chunkSize.value, file.size);
    fileReader.readAsArrayBuffer(file.slice(start, end));
  };

  fileReader.onload = (e) => {
    spark.append(e.target.result);
    chunkIndex++;
    if (chunkIndex < Math.ceil(file.size / chunkSize.value)) {
      loadNextChunk();
    } else {
      fileMd5.value = spark.end();
      initChunks();
    }
  };

  fileReader.onerror = () => {
    ElMessage.error('文件 MD5 计算失败，请重新选择文件！');
    uploadStatus.value = 'error';
  };

  loadNextChunk();
};

/**
 * 初始化分片信息
 */
const initChunks = () => {
  chunks.value = [];
  const totalChunks = Math.ceil(file.value.size / chunkSize.value);
  for (let i = 0; i < totalChunks; i++) {
    const start = i * chunkSize.value;
    const end = Math.min(start + chunkSize.value, file.value.size);
    chunks.value.push({ index: i, start, end, size: end - start });
  }
};

/**
 * 开始上传（主入口）
 */
const startUpload = async () => {
  if (!file.value || !fileMd5.value || chunks.value.length === 0) {
    ElMessage.warning('请先选择文件并等待 MD5 计算完成！');
    return;
  }

  uploadStatus.value = 'uploading';

  try {
    // 步骤 1：初始化上传任务（携带资源额外信息，供审核员查看）
    const initResponse = await axios.post('/api/resources/chunk-upload/init/', {
      file_md5: fileMd5.value,
      filename: file.value.name,
      total_chunks: chunks.value.length,
      // 新增：传递资源额外信息（后端需对应接收并存储到Resource模型）
      resource_desc: props.resourceInfo.desc,
      resource_type: props.resourceInfo.type,
      resource_tags: props.resourceInfo.tags.join(','), // 转为字符串存储
    });

    // 步骤 2：检查已上传分片（断点续传）
    const statusResponse = await getUploadStatus();
    if (statusResponse.data.uploaded_chunks && statusResponse.data.uploaded_chunks.length > 0) {
      currentChunkIndex.value = Math.max(...statusResponse.data.uploaded_chunks) + 1;
      uploadProgress.value = Math.floor((currentChunkIndex.value / chunks.value.length) * 100);
      ElMessage.info(`发现已上传 ${currentChunkIndex.value} 个分片，将从第 ${currentChunkIndex.value + 1} 个分片继续上传`);
    }

    // 步骤 3：逐个上传分片
    await uploadChunksSequentially();

  } catch (error) {
    console.error('上传失败：', error.response ? error.response.data : error.message);
    ElMessage.error(`上传失败：${error.response ? error.response.data.error : error.message}`);
    uploadStatus.value = 'error';
    emit('upload-error', error);
  }
};

/**
 * 逐个上传分片
 */
const uploadChunksSequentially = async () => {
  for (let i = currentChunkIndex.value; i < chunks.value.length; i++) {
    if (uploadStatus.value !== 'uploading') break;

    currentChunkIndex.value = i;
    const chunk = chunks.value[i];
    const chunkBlob = file.value.slice(chunk.start, chunk.end);
    const formData = new FormData();
    formData.append('file_md5', fileMd5.value);
    formData.append('chunk_index', chunk.index);
    formData.append('chunk_file', chunkBlob, `chunk_${chunk.index}_${file.value.name}`);

    try {
      abortController.value = new AbortController();
      const response = await axios.post('/api/resources/chunk-upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        signal: abortController.value.signal,
        onUploadProgress: (progressEvent) => {
          const chunkProgress = progressEvent.loaded / progressEvent.total;
          uploadProgress.value = Math.floor(((i + chunkProgress) / chunks.value.length) * 100);
        },
      });

      if (response.data.status === 'completed') {
        uploadProgress.value = 100;
        uploadStatus.value = 'success';
        // 优化：明确提示用户进入待审核队列
        ElMessage.success(`文件上传成功！已进入待审核队列，审核员将尽快处理`);
        // 传递资源ID和额外信息给父组件（方便刷新列表、跳转详情）
        emit('upload-success', {
          file_md5: fileMd5.value,
          filename: file.value.name,
          file_size: file.value.size,
          resource_id: response.data.resource_id,
          resource_info: props.resourceInfo // 回传资源额外信息
        });
        setTimeout(resetUploadState, 3000); // 3秒后重置状态
        break;
      }

    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error(`分片 ${chunk.index + 1} 上传失败：`, error);
        ElMessage.error(`分片 ${chunk.index + 1} 上传失败，请检查网络后重试！`);
        uploadStatus.value = 'error';
        throw error;
      }
    }
  }
};

/**
 * 暂停上传
 */
const pauseUpload = () => {
  if (uploadStatus.value !== 'uploading') return;
  if (abortController.value) abortController.value.abort();
  uploadStatus.value = 'paused';
  ElMessage.info('上传已暂停');
};

/**
 * 取消上传
 */
const cancelUpload = () => {
  pauseUpload();
  resetUploadState();
  ElMessage.info('上传已取消');
};

/**
 * 查询上传状态（断点续传用）
 */
const getUploadStatus = async () => {
  try {
    return await axios.get('/api/resources/chunk-upload/status/', {
      params: { file_md5: fileMd5.value },
    });
  } catch (error) {
    if (error.response && error.response.status === 404) {
      return { data: { uploaded_chunks: [] } };
    }
    throw error;
  }
};

// ------------------- 6. 组件通信 -------------------
const emit = defineEmits(['upload-success', 'upload-error']);

// ------------------- 7. 生命周期钩子 -------------------
onUnmounted(() => {
  pauseUpload();
  resetUploadState();
});
</script>

<style scoped>
.chunk-uploader {
  border: 1px solid #ebeef5;
  padding: 20px;
  border-radius: 4px;
  transition: border-color 0.3s ease;
}

.chunk-uploader:hover {
  border-color: #409EFF;
}

.upload-controls {
  display: flex;
  align-items: center;
}

.upload-status-text {
  color: #606266;
  font-size: 14px;
}

.text-danger {
  color: #F56C6C;
}
</style>