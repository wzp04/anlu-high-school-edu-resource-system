<template>
  <div class="upload-container">
    <el-card shadow="hover">
      <h2 class="page-title">资源上传</h2>

      <el-upload
        class="upload-demo"
        drag
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
      >
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持上传视频、文档、图片等格式文件，单个文件最大支持100MB
          </div>
        </template>
      </el-upload>

      <div v-if="selectedFile" class="file-info">
        <p>
          <strong>文件名：</strong> {{ selectedFile.name }}
        </p>
        <p>
          <strong>文件大小：</strong> {{ formatFileSize(selectedFile.size) }}
        </p>
      </div>

      <el-form
        v-if="selectedFile"
        :model="uploadForm"
        :rules="uploadRules"
        ref="uploadFormRef"
        label-width="100px"
        class="upload-form"
      >
        <el-form-item label="学科" prop="subject">
          <el-select v-model="uploadForm.subject" placeholder="请选择学科">
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
        <el-form-item label="年级" prop="grade">
          <el-select v-model="uploadForm.grade" placeholder="请选择年级">
            <el-option label="高一" value="高一"></el-option>
            <el-option label="高二" value="高二"></el-option>
            <el-option label="高三" value="高三"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="资源描述" prop="description">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入资源描述（可选）"
          ></el-input>
        </el-form-item>
      </el-form>

      <div class="action-bar">
        <el-button
          type="primary"
          :disabled="!selectedFile || isUploading || isPaused"
          @click="handleStartUpload"
        >
          <i v-if="isUploading" class="el-icon-loading"></i>
          {{ isUploading ? '上传中...' : '开始上传' }}
        </el-button>
        <el-button
          type="info"
          :disabled="!selectedFile || !isUploading || isPaused"
          @click="handlePauseUpload"
        >
          暂停上传
        </el-button>
        <el-button
          type="danger"
          :disabled="isUploading"
          @click="handleReset"
        >
          重新选择
        </el-button>
      </div>

      <el-progress
        v-if="isUploading && progress > 0"
        :percentage="progress"
        status="success"
        class="upload-progress"
      ></el-progress>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import SparkMD5 from 'spark-md5';
import { ElMessage } from 'element-plus';
import axios from '@/utils/axios';
import { useUserStore } from '@/store/user';

// 路由实例
const router = useRouter();
const userStore = useUserStore();

// 表单引用
const uploadFormRef = ref(null);

// 文件列表
const fileList = ref([]);
// 选中的文件
const selectedFile = ref(null);
// 上传表单数据
const uploadForm = reactive({
  subject: '',
  grade: '',
  description: '',
});
// 上传表单验证规则
const uploadRules = ref({
  subject: [{ required: true, message: '请选择学科', trigger: 'change' }],
  grade: [{ required: true, message: '请选择年级', trigger: 'change' }],
});

// 上传状态
const isUploading = ref(false);
const isPaused = ref(false);
const progress = ref(0);
// 分块大小 (10MB)
const chunkSize = 10 * 1024 * 1024;
// 上传任务ID
let taskId = '';
// 当前上传的分块索引
let currentChunkIndex = 0;
// 文件MD5
let fileMd5 = '';

/**
 * 文件状态改变时触发
 */
const handleFileChange = (uploadFile, list) => {
  fileList.value = list.slice(-1); // 只保留最后一个文件
  selectedFile.value = fileList.value[0] ? fileList.value[0].raw : null;
  if (selectedFile.value) {
    calculateFileMd5(selectedFile.value);
  }
};

/**
 * 计算文件MD5
 */
const calculateFileMd5 = (file) => {
  const fileReader = new FileReader();
  const spark = new SparkMD5.ArrayBuffer();
  const md5ChunkSize = 2 * 1024 * 1024; // 2MB为一块计算MD5
  let chunks = Math.ceil(file.size / md5ChunkSize);
  let currentChunk = 0;

  fileReader.onload = (e) => {
    spark.append(e.target.result);
    currentChunk++;
    if (currentChunk < chunks) {
      loadNextChunk();
    } else {
      fileMd5 = spark.end();
      console.log('文件MD5计算完成:', fileMd5);
    }
  };

  fileReader.onerror = () => {
    ElMessage.error('文件MD5计算失败，请重新选择文件');
    console.error('文件MD5计算失败');
  };

  const loadNextChunk = () => {
    const start = currentChunk * md5ChunkSize;
    const end = start + md5ChunkSize >= file.size ? file.size : start + md5ChunkSize;
    fileReader.readAsArrayBuffer(file.slice(start, end));
  };

  loadNextChunk();
};

/**
 * 格式化文件大小
 */
const formatFileSize = (bytes) => {
  if (bytes < 1024) {
    return bytes + ' B';
  } else if (bytes < 1024 * 1024) {
    return (bytes / 1024).toFixed(2) + ' KB';
  } else if (bytes < 1024 * 1024 * 1024) {
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  } else {
    return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
  }
};

/**
 * 开始上传
 */
const handleStartUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件');
    return;
  }

  // 表单验证
  if (!uploadFormRef.value) return;
  try {
    await uploadFormRef.value.validate();
  } catch (error) {
    console.log('表单验证失败');
    return;
  }

  // 文件大小限制 (100MB)
  const maxFileSize = 100 * 1024 * 1024;
  if (selectedFile.value.size > maxFileSize) {
    ElMessage.error(`文件大小超过限制（最大 ${maxFileSize / (1024 * 1024)} MB）`);
    return;
  }

  if (isPaused.value) {
    // 继续上传
    isPaused.value = false;
    isUploading.value = true;
    uploadChunks();
  } else {
    // 新上传
    try {
      await initUploadTask();
      isUploading.value = true;
      uploadChunks();
    } catch (error) {
      ElMessage.error(error.message || '初始化上传任务失败');
    }
  }
};

/**
 * 暂停上传
 */
const handlePauseUpload = () => {
  isPaused.value = true;
  isUploading.value = false;
  ElMessage.info('上传已暂停，点击"开始上传"可继续');
};

/**
 * 重置上传
 */
const handleReset = () => {
  fileList.value = [];
  selectedFile.value = null;
  uploadForm.subject = '';
  uploadForm.grade = '';
  uploadForm.description = '';
  progress.value = 0;
  isUploading.value = false;
  isPaused.value = false;
  currentChunkIndex = 0;
  taskId = '';
  fileMd5 = '';
  uploadFormRef.value?.clearValidate();
};

/**
 * 初始化上传任务
 */
const initUploadTask = async () => {
  const fileName = selectedFile.value.name;
  const fileSize = selectedFile.value.size;
  const totalChunks = Math.ceil(fileSize / chunkSize);

  // --- MODIFIED: Added Authorization header ---
  const response = await axios.post('/api/chunk-upload/init/', {
    file_md5: fileMd5,
    filename: fileName,
    total_chunks: totalChunks,
    subject: uploadForm.subject,
    grade: uploadForm.grade,
    description: uploadForm.description,
  }, {
    headers: {
      'Authorization': `Bearer ${userStore.token}`
    }
  });

  taskId = response.data.id;
  currentChunkIndex = 0;
  progress.value = 0;

  console.log('初始化上传任务成功，任务ID:', taskId);
  ElMessage.success('初始化上传任务成功');
  
};

/**
 * 上传分块（循环实现，避免栈溢出）
 */
const uploadChunks = async () => {
  if (isPaused.value) return;
  
  const file = selectedFile.value;
  const totalChunks = Math.ceil(file.size / chunkSize);

  // 循环处理所有分块
  while (currentChunkIndex < totalChunks && !isPaused.value) {
    const start = currentChunkIndex * chunkSize;
    const end = Math.min(start + chunkSize, file.size);
    const chunk = file.slice(start, end);

    const formData = new FormData();
    formData.append('task_id', taskId);
    formData.append('chunk_index', currentChunkIndex);
    formData.append('chunk_file', chunk);
    formData.append('file_md5', fileMd5);

    try {
      // --- MODIFIED: Added Authorization header ---
      const response = await axios.post('/api/chunk-upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${userStore.token}`
        },
      });

      currentChunkIndex++;
      progress.value = Math.round((currentChunkIndex / totalChunks) * 100);

      // 检查是否是最后一个分块且上传完成
      if (currentChunkIndex === totalChunks) {
        console.log('所有分块上传完成，后端正在合并...');
        // 直接从最后一个分块的响应中获取结果
        if (response.data.status === 'completed') {
          isUploading.value = false;
          ElMessage.success(`文件上传成功！资源ID: ${response.data.resource_id}`);
          console.log('文件合并完成，上传成功！资源ID:', response.data.resource_id);
          // 上传成功后重置状态
          setTimeout(() => {
            handleReset();
          }, 2000);
        }
      }

    } catch (error) {
      isUploading.value = false;
      console.error('上传分块失败:', error);
      ElMessage.error(`上传分块 ${currentChunkIndex + 1} 失败，请检查网络后重试`);
      return; // 失败后退出循环
    }
  }
};

/**
 * 组件挂载时检查登录状态
 */
onMounted(() => {
  if (!userStore.isLoggedIn) {
    ElMessage.warning('请先登录');
    router.push('/login');
  }
});
</script>

<style scoped>
.upload-container {
  padding: 20px;
  background-color: #f9f9f9;
  min-height: 100vh;
}
.page-title {
  text-align: center;
  margin-bottom: 20px;
  color: #1989fa;
}
.file-info {
  margin: 15px 0;
  padding: 10px;
  background-color: #f0f9fb;
  border-left: 3px solid #409eff;
  border-radius: 4px;
}
.upload-form {
  margin-top: 20px;
}
.action-bar {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
.upload-progress {
  margin-top: 20px;
}
</style>