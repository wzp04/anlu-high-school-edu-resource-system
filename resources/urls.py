from django.urls import path
# 导入resources应用自己的视图（必须是resources.views，不是主路由的views）
from resources.views import (
    init_upload_task, 
    upload_chunk, 
    get_upload_status, 
    recall_resource_application,
    my_uploaded_resources,
    home_page,
    resource_list,
    resource_detail,
    comment_submit,
    feedback_submit,
    resource_like
)

urlpatterns = [
# 首页数据接口：/api/home/（根路径+功能名，与原有chunk-upload/init/风格一致）
    path('home/', home_page, name='home-page'),
    # 资源列表接口：/api/resources/list/（资源层级+功能名，层级清晰）
    path('resources/list/', resource_list, name='resource-list'),
    # 资源详情接口：/api/resources/<int:pk>/（资源ID+详情，符合RESTful规范，与召回接口层级一致）
    path('resources/<int:pk>/', resource_detail, name='resource-detail'),
    # 评论提交接口：/api/resources/<int:pk>/comments/（资源ID+评论操作，与召回接口操作风格一致）
    path('resources/<int:pk>/comments/', comment_submit, name='comment-submit'),
    # 纠错反馈接口：/api/resources/<int:pk>/feedbacks/（资源ID+反馈操作，保持操作路径一致性）
    path('resources/<int:pk>/feedbacks/', feedback_submit, name='feedback-submit'),
    # 点赞接口：/api/resources/<int:pk>/like/（资源ID+点赞操作，动词结尾，贴合操作类接口风格）
    path('resources/<int:pk>/like/', resource_like, name='resource-like'),



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