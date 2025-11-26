import os
import uuid
import shutil
import logging
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

from .models import Resource, UploadTask
from .serializers import UploadTaskSerializer, ResourceSerializer

logger = logging.getLogger(__name__)

# ========================================================
#  功能：1. 个人资源管理（我的上传）列表接口
#  调整：在状态筛选中加入 'recall_pending'
# ========================================================
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_uploaded_resources(request):
    """
    获取当前登录用户上传的所有资源列表。
    支持按审核状态筛选（包括 'recall_pending'）和分页。
    """
    user = request.user
    # 1. 获取状态筛选参数 (all, pending, approved, rejected, recall_pending)
    status_filter = request.query_params.get('status')

    # 2. 构建查询集：筛选当前用户的资源，并按上传时间倒序排列
    queryset = Resource.objects.filter(uploader=user).order_by('-created_time')

    # 3. 如果有状态筛选参数，则应用筛选
    #    调整点：在允许的状态列表中增加 'recall_pending'
    if status_filter and status_filter in ['pending', 'approved', 'rejected', 'removed', 'recall_pending']:
        queryset = queryset.filter(audit_status=status_filter)

    # 4. 应用分页
    paginator = PageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    # 5. 序列化数据并返回
    serializer = ResourceSerializer(paginated_queryset, many=True)
    return paginator.get_paginated_response(serializer.data)

# ========================================================
#  功能：2. 资源召回申请接口 (您已提供，无需修改)
# ========================================================
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def recall_resource_application(request, pk):
    """
    提交资源召回申请。
    只有资源的上传者才能申请，且资源必须处于 'approved' 状态。
    """
    user = request.user
    try:
        # 1. 查找资源，确保资源存在且属于当前用户
        resource = Resource.objects.get(id=pk, uploader=user)
    except Resource.DoesNotExist:
        return Response(
            {"error": "资源不存在或您没有权限操作此资源。"},
            status=status.HTTP_404_NOT_FOUND
        )

    # 2. 检查资源状态是否为 'approved'，只有已通过的资源才能申请召回
    if resource.audit_status != 'approved':
        return Response(
            {"error": "只有审核通过的资源才能申请召回。"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. 获取并验证召回理由
    recall_reason = request.data.get('reason')
    if not recall_reason or recall_reason.strip() == '':
        return Response(
            {"error": "请提供有效的召回理由。"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4. 【核心逻辑】处理召回申请
    #    - 将资源状态改为 'recall_pending'
    resource.audit_status = 'recall_pending'
    resource.save()

    logger.info(f"用户 {user.username} 已为资源 {resource.title} (ID: {resource.id}) 提交召回申请。")

    # 5. 返回成功响应
    return Response({
        "message": "召回申请已提交成功，等待管理员审核。",
        "resource_id": resource.id,
        "status": resource.audit_status
    })

# ========================================================
#  以下为您原有的代码，已保持不变
# ========================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def init_upload_task(request):
    uploader = request.user
    file_md5 = request.data.get('file_md5')
    filename = request.data.get('filename')
    total_chunks = request.data.get('total_chunks')
    subject = request.data.get('subject', '未分类')
    grade = request.data.get('grade', '未指定')

    if not all([file_md5, filename, total_chunks]):
        return Response({"error": "缺少 file_md5、filename 或 total_chunks 参数"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        total_chunks = int(total_chunks)
    except ValueError:
        return Response({"error": "total_chunks 必须是有效的整数"}, status=status.HTTP_400_BAD_REQUEST)

    if UploadTask.objects.filter(file_md5=file_md5, status='completed').exists():
        return Response({"error": "文件已存在，请勿重复上传"}, status=status.HTTP_409_CONFLICT)

    task, created = UploadTask.objects.get_or_create(
        file_md5=file_md5,
        uploader=uploader,
        defaults={
            'filename': filename,
            'total_chunks': total_chunks,
            'status': 'pending',
            'subject': subject,
            'grade': grade
        }
    )
    
    if not created and task.status != 'pending':
        return Response({"error": "存在一个非上传中的任务记录，请刷新页面或稍后重试"}, status=status.HTTP_409_CONFLICT)

    return Response(UploadTaskSerializer(task).data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_chunk(request):
    uploader = request.user

    # -------------------------- 新增调试代码 --------------------------
    file_md5 = request.data.get('file_md5')
    print(f"\n[调试] 接收到的 file_md5: {file_md5}")  # 打印 file_md5
    print(f"[调试] 请求数据中的所有参数: {list(request.data.keys())}")  # 查看所有传递的参数
    # -----------------------------------------------------------------

    chunk_index_str = request.data.get('chunk_index')
    chunk_file = request.FILES.get('chunk_file')

    if not chunk_index_str or not chunk_index_str.isdigit():
        return Response({"error": "chunk_index 必须是有效的整数"}, status=status.HTTP_400_BAD_REQUEST)
    chunk_index = int(chunk_index_str)

    if not chunk_file:
        return Response({"error": "未收到 chunk_file 文件"}, status=status.HTTP_400_BAD_REQUEST)
        
    max_chunk_size = 10 * 1024 * 1024
    if chunk_file.size > max_chunk_size:
        return Response({"error": f"单个分片大小不能超过 {max_chunk_size / (1024 * 1024)} MB"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = UploadTask.objects.get(
            file_md5=file_md5,
            uploader=uploader,
            status='pending'
        )
    except UploadTask.DoesNotExist:
        return Response({"error": "上传任务不存在或已完成"}, status=status.HTTP_404_NOT_FOUND)

    if chunk_index < 0 or chunk_index >= task.total_chunks:
        return Response({"error": f"分片索引无效，必须在 0 到 {task.total_chunks - 1} 之间"}, status=status.HTTP_400_BAD_REQUEST)

    if chunk_index in task.uploaded_chunks:
        return Response({"message": "分片已存在，无需重复上传", "chunk_index": chunk_index}, status=status.HTTP_200_OK)

    chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', file_md5)
    os.makedirs(chunk_dir, exist_ok=True)
    chunk_path = os.path.join(chunk_dir, f'chunk_{chunk_index}')

    with open(chunk_path, 'wb+') as destination:
        for chunk in chunk_file.chunks():
            destination.write(chunk)

    task.uploaded_chunks.append(chunk_index)
    task.save()

    if len(task.uploaded_chunks) == task.total_chunks:
        return merge_chunks(task)

    progress = len(task.uploaded_chunks) / task.total_chunks * 100
    return Response(
        {
            "message": "分片上传成功",
            "chunk_index": chunk_index,
            "uploaded_chunks_count": len(task.uploaded_chunks),
            "total_chunks": task.total_chunks,
            "progress": f"{progress:.2f}%",
            "subject": task.subject,
            "grade": task.grade
        },
        status=status.HTTP_200_OK
    )

def merge_chunks(task):
    chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', task.file_md5)
    try:
        random_prefix = str(uuid.uuid4())[:8]
        original_filename = task.filename
        new_filename = f"{random_prefix}_{original_filename}"
        
        final_dir = os.path.join(settings.MEDIA_ROOT, 'resources', str(task.uploader.id))
        os.makedirs(final_dir, exist_ok=True)
        final_path = os.path.join(final_dir, new_filename)

        with open(final_path, 'wb') as outfile:
            for i in range(task.total_chunks):
                chunk_path = os.path.join(chunk_dir, f'chunk_{i}')
                with open(chunk_path, 'rb') as infile:
                    outfile.write(infile.read())

        school_name = task.uploader.school if hasattr(task.uploader, 'school') else "未知学校"
        
        resource = Resource.objects.create(
            title=original_filename,
            file=os.path.relpath(final_path, settings.MEDIA_ROOT),
            md5=task.file_md5,
            version="V1.0",
            school=school_name,
            subject=task.subject,
            grade=task.grade,
            uploader=task.uploader,
            audit_status="pending"
        )

        task.status = 'completed'
        task.save()
        logger.info(f"文件合并成功：{task.file_md5}，生成资源ID：{resource.id}")

        shutil.rmtree(chunk_dir)

        return Response(
            {
                "message": "文件上传完成，已生成资源记录",
                "resource_id": resource.id,
                "resource_title": resource.title,
                "subject": resource.subject,
                "grade": resource.grade,
                "audit_status": resource.audit_status,
                "status": "completed"
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        task.status = 'failed'
        task.save()
        
        if os.path.exists(chunk_dir):
            shutil.rmtree(chunk_dir)
            
        logger.error(f"合并分片失败 - 任务MD5：{task.file_md5}，错误信息：{str(e)}", exc_info=True)
        return Response({"error": f"合并分片失败：{str(e)}，请稍后重试"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_upload_status(request):
    uploader = request.user
    file_md5 = request.query_params.get('file_md5')

    if not file_md5:
        return Response({"error": "缺少 file_md5 参数"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = UploadTask.objects.get(file_md5=file_md5, uploader=uploader)
        progress = 0
        if task.total_chunks > 0:
            progress = len(task.uploaded_chunks) / task.total_chunks * 100
            
        response_data = UploadTaskSerializer(task).data
        response_data['progress'] = f"{progress:.2f}%"
        response_data['subject'] = task.subject
        response_data['grade'] = task.grade
        
        return Response(response_data)
        
    except UploadTask.DoesNotExist:
        return Response({"error": "上传任务不存在"}, status=status.HTTP_404_NOT_FOUND)