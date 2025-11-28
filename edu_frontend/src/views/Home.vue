<template>
  <div class="home-container">
    <!-- 1. 轮播图区域（优质资源） -->
    <el-carousel 
      class="home-carousel" 
      :interval="5000" 
      arrow="always" 
      indicator-position="outside"
    >
      <!-- 轮播图无数据占位 -->
      <el-carousel-item v-if="!carouselResources.length">
        <div class="carousel-placeholder">暂无轮播资源</div>
      </el-carousel-item>
      <!-- 轮播图数据渲染 -->
      <el-carousel-item v-for="(item, idx) in carouselResources" :key="idx">
        <div class="carousel-item" @click="goToDetail(item.id)">
          <div class="carousel-mask">
            <h3 class="carousel-title">{{ item.title }}</h3>
            <p class="carousel-info">
              {{ item.school_name }} · {{ item.subject }} · {{ item.grade }}
            </p>
          </div>
          <!-- 占位图（实际项目可替换为资源封面图，需后端返回cover字段） -->
          <div class="carousel-img" :style="{ backgroundImage: `url('https://picsum.photos/1200/400?random=${idx}')` }"></div>
        </div>
      </el-carousel-item>
    </el-carousel>

    <!-- 2. 三级筛选区域（学科+年级+学校） -->
    <div class="filter-container">
      <el-select 
        v-model="selectedSubject" 
        placeholder="请选择学科" 
        class="filter-select"
        @change="handleFilterChange"
      >
        <el-option label="全部学科" value=""></el-option>
        <el-option v-for="sub in filterOptions.subjects" :key="sub" :label="sub" :value="sub"></el-option>
      </el-select>

      <el-select 
        v-model="selectedGrade" 
        placeholder="请选择年级" 
        class="filter-select"
        @change="handleFilterChange"
      >
        <el-option label="全部年级" value=""></el-option>
        <el-option v-for="grade in filterOptions.grades" :key="grade" :label="grade" :value="grade"></el-option>
      </el-select>

      <el-select 
        v-model="selectedSchool" 
        placeholder="请选择学校" 
        class="filter-select"
        @change="handleFilterChange"
      >
        <el-option label="全部学校" value=""></el-option>
        <el-option v-for="school in filterOptions.schools" :key="school" :label="school" :value="school"></el-option>
      </el-select>

      <el-checkbox 
        v-model="isHighQuality" 
        label="仅看优质资源" 
        class="high-quality-checkbox"
        @change="handleFilterChange"
      ></el-checkbox>
    </div>

    <!-- 3. 热门推荐资源区域 -->
    <div class="recommend-container">
      <div class="recommend-header">
        <h2>热门推荐</h2>
        <el-button type="text" @click="goToResourceList">查看全部 →</el-button>
      </div>

      <!-- 推荐资源无数据占位 -->
      <div class="recommend-placeholder" v-if="!recommendedResources.length">
        <el-empty description="暂无推荐资源"></el-empty>
      </div>

      <!-- 推荐资源列表（网格布局） -->
      <div class="resource-grid" v-else>
        <el-card 
          v-for="(res, idx) in recommendedResources" 
          :key="idx" 
          class="resource-card"
          @click="goToDetail(res.id)"
        >
          <div class="card-header">
            <span class="resource-tag" v-if="res.is_high_quality">优质资源</span>
            <h3 class="resource-title">{{ res.title }}</h3>
          </div>
          <div class="card-body">
            <p class="resource-meta">
              <span>{{ res.school_name }}</span>
              <span>{{ res.subject }} · {{ res.grade }}</span>
            </p>
            <div class="resource-stats">
              <span><i class="el-icon-download"></i> {{ res.download_count }} 下载</span>
              <span><i class="el-icon-thumbs-up"></i> {{ res.like_count }} 点赞</span>
            </div>
          </div>
          <div class="card-footer">
            <el-button type="primary" size="small" @click.stop="goToDetail(res.id)">查看详情</el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
// 修改点1：替换原生axios为项目封装的request.js
// 理由：request.js已配置后端baseURL、自动携带Token、统一错误处理，复用避免重复代码
import request from '@/utils/request';
import { ElMessage } from 'element-plus';

// 路由实例
const router = useRouter();

// 状态管理：筛选条件+接口数据（无修改）
const selectedSubject = ref(''); // 选中的学科
const selectedGrade = ref('');   // 选中的年级
const selectedSchool = ref('');  // 选中的学校
const isHighQuality = ref(false); // 是否仅看优质资源
const carouselResources = ref([]); // 轮播图资源
const filterOptions = ref({      // 三级筛选选项（学科/年级/学校）
  subjects: [],
  grades: [],
  schools: []
});
const recommendedResources = ref([]); // 热门推荐资源

// 初始化：获取首页数据（无修改）
onMounted(() => {
  fetchHomeData();
});

// 对接后端首页接口：核心修改区域
const fetchHomeData = async () => {
  try {
    // 修改点2：删除手动获取localStorage Token的代码
    // 理由：request.js的请求拦截器会自动从Pinia的userStore获取token，无需手动处理
    // const token = localStorage.getItem('token'); 

    // 修改点3：请求方式从axios.get改为request.get，路径从'/api/home/'改为'/home/'
    // 理由：request.js的baseURL已配置为'http://127.0.0.1:8000/api'，拼接后完整地址为'http://127.0.0.1:8000/api/home/'，与后端接口一致；且无需手动添加headers（拦截器自动添加）
    const res = await request.get('/home/');

    // 修改点4：响应处理从res.data.code改为res.code，res.data.data改为res.data
    // 理由：request.js的响应拦截器已自动返回response.data（后端原始响应体），无需再次解析res.data
    if (res.code === 200) {
      carouselResources.value = res.data.carousel_resources;
      filterOptions.value = res.data.filter_options;
      recommendedResources.value = res.data.recommended_resources;
    } else {
      ElMessage.error(res.message || '首页数据获取失败');
    }
  } catch (error) {
    console.error('首页接口请求失败：', error);
    // 修改点5：删除手动错误提示（仅保留控制台打印）
    // 理由：request.js的响应拦截器已统一处理错误（401跳转登录、403提示无权限、网络错误提示），避免重复弹窗
    // ElMessage.error('网络错误，无法获取首页数据');
  }
};

// 筛选条件变更：跳转到资源列表页，携带筛选参数（无修改）
const handleFilterChange = () => {
  router.push({
    name: 'resourceList', // 对应路由配置中的资源列表页name
    query: {
      subject: selectedSubject.value,
      grade: selectedGrade.value,
      school: selectedSchool.value,
      is_high_quality: isHighQuality.value ? 'true' : '' // 适配后端参数格式
    }
  });
};

// 跳转到资源详情页（无修改）
const goToDetail = (resourceId) => {
  router.push({
    name: 'resourceDetail', // 对应路由配置中的资源详情页name
    params: { id: resourceId } // 传递资源ID
  });
};

// 跳转到资源列表页（查看全部）（无修改）
const goToResourceList = () => {
  router.push({ name: 'resourceList' });
};
</script>

<!-- 新增：非setup脚本块，定义多单词组件名，解决ESLint报错（无修改） -->
<script>
export default {
  name: 'HomePage' // 多单词组件名，符合 vue/multi-word-component-names 规则
};
</script>

<style scoped lang="scss">
// 全局容器样式
.home-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px 0;
}

// 轮播图样式
.home-carousel {
  height: 400px;
  margin-bottom: 30px;
  border-radius: 8px;
  overflow: hidden;

  .carousel-item {
    position: relative;
    height: 100%;
    cursor: pointer;

    .carousel-img {
      width: 100%;
      height: 100%;
      background-size: cover;
      background-position: center;
    }

    .carousel-mask {
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 20px 30px;
      background: linear-gradient(transparent, rgba(0,0,0,0.7));
      color: #fff;

      .carousel-title {
        font-size: 24px;
        margin-bottom: 8px;
      }

      .carousel-info {
        font-size: 14px;
        opacity: 0.9;
      }
    }
  }

  .carousel-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f5f5f5;
    color: #999;
    font-size: 18px;
  }
}

// 筛选区域样式
.filter-container {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 30px;
  flex-wrap: wrap;

  .filter-select {
    width: 180px;
  }

  .high-quality-checkbox {
    margin-left: auto;
    color: #1989fa;
  }
}

// 推荐资源区域样式
.recommend-container {
  .recommend-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      font-size: 20px;
      font-weight: 600;
      color: #333;
    }

    .el-button {
      color: #1989fa;
      margin-left: auto;
    }
  }

  .recommend-placeholder {
    padding: 80px 0;
    text-align: center;
  }

  .resource-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
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

      .resource-tag {
        position: absolute;
        top: 0;
        right: 0;
        background: #409eff;
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
}

// 响应式适配（移动端）
@media (max-width: 768px) {
  .home-container {
    padding: 16px;
  }

  .home-carousel {
    height: 200px;
  }

  .filter-container {
    gap: 12px;

    .filter-select {
      width: 140px;
    }

    .high-quality-checkbox {
      margin-left: 0;
      width: 100%;
      margin-top: 8px;
    }
  }

  .resource-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}
</style>