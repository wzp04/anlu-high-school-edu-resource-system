from django.urls import path
# 导入resources应用自己的视图（必须是resources.views，不是主路由的views）
from resources.views import (
    init_upload_task, 
    upload_chunk, 
    get_upload_status, 
    recall_resource_application,
    my_uploaded_resources
)

urlpatterns = [
    # 分片上传初始化：/api/chunk-upload/init/
    path('chunk-upload/init/', init_upload_task, name='chunk-upload-init'),
    # 分片上传：/api/chunk-upload/
    path('chunk-upload/', upload_chunk, name='chunk-upload'),
    # 上传状态查询：/api/chunk-upload/status/
    path('chunk-upload/status/', get_upload_status, name='chunk-upload-status'),
    # 资源召回：/api/resources/<int:pk>/recall/
    path('resources/<int:pk>/recall/', recall_resource_application, name='handle-recall-request'),
    # 我的上传列表：/api/my-uploads/
    path('my-uploads/', my_uploaded_resources, name='my-uploaded-resources'),
]