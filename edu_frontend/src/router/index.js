import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';

// 路由懒加载：仅修改注册页组件路径（原RegisterPage.vue → 新建的RegisterView.vue）
const HomeView = () => import('@/views/HomeView.vue');
const UploadView = () => import('@/views/UploadView.vue');
const LoginView = () => import('@/views/LoginView.vue');
const MyUploads = () => import('@/views/MyUploads.vue');
// 修改点1：组件路径从 RegisterPage.vue 改为 阶段三新建的 RegisterView.vue
const RegisterView = () => import('@/views/RegisterView.vue');
const ResourcesView = () => import('@/views/Resource/MyResourceView.vue');
const MainLayout = () => import('@/layout/MainLayout.vue');

const routes = [
  {
    path: '/',
    component: MainLayout, // 保留原有共享布局，不修改
    children: [
      {
        path: '',
        name: 'home',
        component: HomeView,
      },
      {
        path: 'upload',
        name: 'upload',
        component: UploadView,
        meta: { requiresAuth: true },
      },
      {
        path: 'my-uploads',
        name: 'myUploads',
        component: MyUploads,
        meta: { requiresAuth: true }
      },
      {
        path: 'resources',
        name: 'resources',
        component: ResourcesView,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 登录/注册页（不使用布局，保留原有结构）
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    // 修改点2：补充meta配置（明确未登录可访问，与原有守卫逻辑兼容）
    meta: { requiresAuth: false }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫：完全保留原有逻辑，不修改
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  if (to.meta.requiresAuth) {
    if (userStore.isLoggedIn) {
      next();
    } else {
      next('/login');
    }
  } else {
    next();
  }
});

export default router;