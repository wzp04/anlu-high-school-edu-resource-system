import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';

// 路由懒加载
const HomeView = () => import('@/views/HomeView.vue');
const UploadView = () => import('@/views/UploadView.vue');
const LoginView = () => import('@/views/LoginView.vue');
const MyUploads = () => import('@/views/MyUploads.vue');
const RegisterView = () => import('@/views/RegisterPage.vue');
const ResourcesView = () => import('@/views/Resource/MyResourceView.vue');
const MainLayout = () => import('@/layout/MainLayout.vue');

const routes = [
  {
    path: '/',
    component: MainLayout, // 所有页面共享同一个布局
    children: [
      {
        path: '', // 首页路径：/
        name: 'home',
        component: HomeView,
      },
      {
        path: 'upload', // 资源上传：/upload
        name: 'upload',
        component: UploadView,
        meta: { requiresAuth: true },
      },
      {
        path: 'my-uploads', // 我的上传：/my-uploads
        name: 'myUploads',
        component: MyUploads,
        meta: { requiresAuth: true }
      },
      {
        path: 'resources', // 资源库：/resources
        name: 'resources',
        component: ResourcesView,
        meta: { requiresAuth: true }
      }
    ]
  },
  // 登录/注册页（不使用布局）
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
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