<template>
  <div class="my-uploads-container">
    <el-card shadow="hover">
      <h2 class="page-title">我的上传</h2>

      <!-- 状态筛选标签页 -->
      <el-tabs v-model="activeTab" type="card" @tab-change="fetchResources">
        <el-tab-pane label="全部" name="all"></el-tab-pane>
        <el-tab-pane label="待审核" name="pending"></el-tab-pane>
        <el-tab-pane label="已通过" name="approved"></el-tab-pane>
        <el-tab-pane label="已驳回" name="rejected"></el-tab-pane>
        <el-tab-pane label="召回待审核" name="recall_pending"></el-tab-pane>
      </el-tabs>

      <!-- 资源列表表格 -->
      <el-table 
        :data="resourceList" 
        border 
        style="width: 100%; margin-top: 20px;" 
        empty-text="暂无资源上传记录"
        :header-cell-style="{ background: '#f5f5f5' }"
      >
        <el-table-column prop="title" label="资源名称" width="220">
          <template #default="scope">
            <el-link type="primary" @click="viewResource(scope.row)" class="resource-title">
              {{ scope.row.title }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="学科" width="100"></el-table-column>
        <el-table-column prop="grade" label="年级" width="100"></el-table-column>
        <el-table-column prop="version" label="版本" width="120"></el-table-column>
        <el-table-column prop="created_time" label="上传时间" width="180">
          <template #default="scope">
            {{ formatDateTime(scope.row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="audit_status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="statusTagType(scope.row.audit_status)" class="status-tag">
              {{ formatStatusText(scope.row.audit_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button type="text" icon="el-icon-view" @click="viewResource(scope.row)">查看</el-button>
            <!-- 已驳回状态：重新提交 -->
            <el-button
              v-if="scope.row.audit_status === 'rejected'"
              type="text"
              icon="el-icon-edit"
              @click="reuploadResource(scope.row)"
              class="text-blue-500"
              >重新提交</el-button
            >
            <!-- 已通过状态：申请召回 -->
            <el-button
              v-if="scope.row.audit_status === 'approved'"
              type="text"
              icon="el-icon-warning"
              @click="openRecallDialog(scope.row)"
              class="text-orange-500"
              >申请召回</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        class="pagination"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
        background
      >
      </el-pagination>
    </el-card>

    <!-- 召回申请弹窗 -->
    <el-dialog v-model="isRecallDialogOpen" title="申请资源召回" width="500px" center>
      <el-form :model="recallForm" label-width="80px" :rules="recallRules" ref="recallFormRef">
        <el-form-item label="召回理由" prop="reason">
          <el-input 
            v-model="recallForm.reason" 
            type="textarea" 
            :rows="4" 
            placeholder="请说明召回原因（如内容错误、版本更新等）"
            maxlength="500"
            show-word-limit
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="isRecallDialogOpen = false">取消</el-button>
        <el-button type="primary" @click="submitRecall">提交申请</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>

import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import axios from '@/utils/axios';  // 导入封装的axios
import { useUserStore } from '@/store/user';
// 路由实例
const router = useRouter();

// 1. 表格与分页数据
const resourceList = ref([]);  // 资源列表
const total = ref(0);          // 总资源数
const pageSize = ref(10);      // 每页条数
const currentPage = ref(1);    // 当前页码
const activeTab = ref('all');  // 当前激活的筛选标签页

// 2. 召回弹窗数据
const isRecallDialogOpen = ref(false);  // 弹窗显示状态
const recallFormRef = ref(null);        // 表单引用
const recallForm = reactive({
  reason: '',         // 召回理由
  resourceId: ''      // 待召回资源ID
});
// 召回表单校验规则
const recallRules = {
  reason: [
    { required: true, message: '请输入召回理由', trigger: 'blur' },
    { min: 5, message: '召回理由至少5个字符', trigger: 'blur' }
  ]
};

// 3. 辅助函数：格式化状态文本（前后端状态映射）
const formatStatusText = (status) => {
  const statusMap = {
    'pending': '待审核',
    'approved': '已通过',
    'rejected': '已驳回',
    'recall_pending': '召回待审核',
    'removed': '已下架'
  };
  return statusMap[status] || '未知状态';
};

// 4. 辅助函数：状态标签样式映射（Element Plus合法类型）
const statusTagType = (status) => {
  const typeMap = {
    'pending': 'info',         // 待审核→蓝色
    'approved': 'success',     // 已通过→绿色
    'rejected': 'danger',      // 已驳回→红色
    'recall_pending': 'warning',// 召回待审核→橙色
    'removed': 'warning'       // 已下架→橙色
  };
  return typeMap[status] || 'warning';  // 无效状态默认橙色
};

// 5. 辅助函数：格式化时间（ISO格式→本地时间）
const formatDateTime = (timeStr) => {
  if (!timeStr) return '';
  const date = new Date(timeStr);
  // 增加时间有效性判断
  if (isNaN(date.getTime())) return '无效时间';
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// 6. 核心函数：获取资源列表
const fetchResources = async () => {
  // 显示加载状态（可添加全局加载组件）
  try {
    const userStore = useUserStore();
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      // 筛选状态：非“全部”时添加status参数
      ...(activeTab.value !== 'all' && { status: activeTab.value })
    };
    // 确保API路径与后端一致（根据实际情况调整）
    const res = await axios.get('/api/my-uploads/', { params,
     headers: {
        Authorization: `Bearer ${userStore.token}` // 从Pinia取Token
      }
      });
    resourceList.value = res.data.results || [];
    total.value = res.data.count || 0;
  } catch (error) {
    ElMessage.error('获取资源列表失败，请稍后重试');
    console.error('资源列表请求错误：', error);
  }
};

// 7. 分页变化事件
const handlePageChange = (page) => {
  currentPage.value = page;
  fetchResources();
};

// 8. 操作事件：查看资源详情
const viewResource = (resource) => {
  router.push(`/resources/detail/${resource.id}`);
};

// 9. 操作事件：重新提交资源（已驳回状态）
const reuploadResource = (resource) => {
  // 跳转到上传页面并携带编辑ID，方便回显数据
  router.push({ path: '/upload', query: { editId: resource.id } });
};

// 10. 操作事件：打开召回弹窗
const openRecallDialog = (resource) => {
  recallForm.resourceId = resource.id;  // 赋值资源ID
  recallForm.reason = '';               // 清空输入框
  isRecallDialogOpen.value = true;      // 显示弹窗
  // 重置表单校验
  recallFormRef.value?.clearValidate();
};

// 11. 操作事件：提交召回申请（核心功能）
const submitRecall = async () => {
  // 表单校验
  await recallFormRef.value.validate();

  try {
    // 调用后端召回接口（路径与后端路由匹配）
    await axios.post(`/api/resources/${recallForm.resourceId}/recall/`, {
      reason: recallForm.reason  // 传递召回理由
    });

    // 提交成功反馈
    ElMessage.success('召回申请已提交，等待管理员审核');
    isRecallDialogOpen.value = false;  // 关闭弹窗
    fetchResources();  // 刷新资源列表（更新状态为“召回待审核”）
  } catch (error) {
    // 错误处理
    const errorMsg = error.response?.data?.reason || error.response?.data?.error || '提交召回申请失败，请稍后重试';
    ElMessage.error(errorMsg);
    console.error('召回申请错误：', error);
  }
};

// 12. 组件挂载时初始化数据
onMounted(() => {
  const userStore = useUserStore();
  // 如果Token为空，直接跳登录页（不触发401登出）
  if (!userStore.token) {
    ElMessage.warning('请先登录');
    router.push('/login');
    return;
  }
  // Token存在再请求数据
  fetchResources();
});
</script>

<style scoped>
.my-uploads-container {
  padding: 20px;
  background-color: #f9f9f9;
  min-height: calc(100vh - 100px);
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
}

/* 分页样式优化 */
.pagination {
  margin-top: 20px;
  text-align: right;
  padding: 10px 0;
}

/* 资源名称样式优化，防止过长 */
.resource-title {
  display: inline-block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
}

/* 状态标签样式优化 */
.status-tag {
  padding: 2px 8px;
  font-size: 12px;
}

/* 操作按钮间距调整 */
:deep(.el-table__fixed-right .el-button) {
  margin-left: 10px;
}

/* 召回弹窗输入框样式优化 */
:deep(.el-textarea__inner) {
  resize: none;
  border-radius: 4px;
}

/* 表格头部样式 */
:deep(.el-table__header-wrapper th) {
  font-weight: 500;
}
</style>