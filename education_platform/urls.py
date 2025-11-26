from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django默认后台
    # 资源模块路由：/api/xxx（分片上传、我的上传等）
    path('api/', include('resources.urls')),
    # 用户模块路由：/api/users/xxx（注册、登录）
    path('api/users/', include('user_management.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 媒体文件访问路由（不变）