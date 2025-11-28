import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/store/user';

const Home = () => import('@/views/Home.vue');
const UploadView = () => import('@/views/UploadView.vue');
const LoginView = () => import('@/views/LoginView.vue');
const MyUploads = () => import('@/views/MyUploads.vue');
const ResourceDetail = () => import('@/views/ResourceDetail.vue');
const ResourceList = () => import('@/views/ResourceList.vue');
const RegisterView = () => import('@/views/RegisterView.vue');
const ResourcesView = () => import('@/views/Resource/MyResourceView.vue');
const MainLayout = () => import('@/layout/MainLayout.vue');

const routes = [
  {
    path: '/',
    component: MainLayout, 
    children: [
      {
        path: '',
        name: 'home',
        component: Home,
        meta: { requiresAuth: true }
      },
      {
        path: 'upload',
        name: 'upload',
        component: UploadView,
        meta: { requiresAuth: true }
      },
      {
        path: 'my-uploads',
        name: 'myUploads',
        component: MyUploads,
        meta: { requiresAuth: true }
      },
       {
        path: 'resources/list',
        name: 'resourceList',
        component: ResourceList,
        meta: { requiresAuth: true }
      },
      {
        path: 'resources', 
        name: 'resources',
        component: ResourcesView,
        meta: { requiresAuth: true }
      },
      
      {
        path: 'resources/:id',
        name: 'resourceDetail',
        component: ResourceDetail,
        meta: { requiresAuth: true }
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresAuth: false }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

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