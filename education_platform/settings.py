from pathlib import Path
import os
from datetime import timedelta  # 新增：用于JWT有效期配置

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-nmn1j)0y#!!9$k1q7@&6)e2ttt%a4t-gt(s0dh&u6(-m&(+8__'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # 生产环境需改为 False

# 开发环境允许的主机（生产环境需改为具体域名，如 ['yourdomain.com']）
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方工具
    'django_extensions',
    'rest_framework',
    'corsheaders',  # 跨域插件（仅保留一次）
    'rest_framework_simplejwt',  # JWT认证
    # 自定义应用（关键修改：users → user_management；注释未创建的courses）
    'user_management',  # 用户模块（与AUTH_USER_MODEL一致）
    'resources',  # 资源模块
    # 'courses',  # 暂未创建，注释掉避免报错（后续创建后再取消注释）
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 跨域中间件（仅保留一次，且在CommonMiddleware之前）
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'education_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # 若有全局模板，可添加路径（如 BASE_DIR / 'templates'）
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'education_platform.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'education_system_db',  # 确保该数据库已创建
        'USER': 'root',  # 本地MySQL用户名（默认root）
        'PASSWORD': '2647387827wzp',  # 你的MySQL密码
        'HOST': 'localhost',  # 本地主机（生产环境填数据库服务器IP）
        'PORT': '3306',  # MySQL默认端口
        # 可选优化：避免MySQL连接超时
        'CONN_MAX_AGE': 60,  # 连接最大存活时间（秒）
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6}  # 密码最小长度6位（可调整）
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework 配置
REST_FRAMEWORK = {
    # 1. JWT认证
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    # 2. 全局权限：默认所有接口需认证
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    # 3. 开发环境支持浏览器调试接口
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    # 4. 分页配置
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # 每页10条数据
}

# JWT Token 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # 访问令牌有效期1小时
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),  # 刷新令牌有效期1天
    'ROTATE_REFRESH_TOKENS': False,  # 不自动刷新令牌
    'BLACKLIST_AFTER_ROTATION': True,  # 刷新后拉黑旧令牌
}

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'zh-hans'  # 语言改为中文
TIME_ZONE = 'Asia/Shanghai'  # 时区改为中国上海
USE_I18N = True
USE_TZ = True  # 启用时区支持

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
# 生产环境静态文件收集目录
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# 额外的静态文件目录
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files (上传的文件)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # 用Path对象更规范

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 自定义用户模型（关键：与user_management应用的User模型对应）
AUTH_USER_MODEL = 'user_management.User'

# 跨域配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8080",  # 前端开发环境地址
    "http://127.0.0.1:8080",
    # 生产环境需添加前端实际域名，如 "https://your-frontend.com"
]
CORS_ALLOW_CREDENTIALS = True  # 允许携带Cookie
# 允许的HTTP方法
CORS_ALLOW_METHODS = [
    "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS",
]

# 开发环境调试配置（启用SQL查询日志）
if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django.db.backends': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
        },
    }