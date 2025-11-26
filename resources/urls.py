from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .views import (
    init_upload_task, 
    upload_chunk, 
    get_upload_status, 
    recall_resource_application,
    my_uploaded_resources  # 新增：导入个人资源列表视图
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # 关键修改：将/api/resources/改为/api/，确保接口路径与前端预期一致（/api/chunk-upload/...）
    path('api/', include('resources.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 媒体文件路由（不变）
# resources/urls.py./
from django.urls import path
from .views import init_upload_task, upload_chunk, get_upload_status, recall_resource_application

urlpatterns = [
    path('chunk-upload/init/', init_upload_task, name='chunk-upload-init'),  # 直接使用函数名
    path('chunk-upload/', upload_chunk, name='chunk-upload'),
    path('chunk-upload/status/', get_upload_status, name='chunk-upload-status'),
    path('resources/<int:pk>/recall/', recall_resource_application, name='handle-recall-request'),
    path('my-uploads/', my_uploaded_resources, name='my-uploaded-resources'),
]