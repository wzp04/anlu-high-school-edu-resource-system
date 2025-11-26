from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 关键修改：资源模块路由前缀改为 /api/，使前端请求 /api/my-uploads/ 能直接匹配
    path('api/', include('resources.urls')),
    # 保留用户模块路由（之前配置的 /api/users/ 接口）
    path('api/users/', include('user_management.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 媒体文件访问路由（不变）