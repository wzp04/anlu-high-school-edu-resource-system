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

from .models import Resource, UploadTask, Comment, Feedback
from .serializers  import (
    UploadTaskSerializer, ResourceSerializer,
    ResourceListSerializer, ResourceDetailSerializer,
    CommentSerializer, FeedbackSerializer
)

logger = logging.getLogger(__name__)

# 1. 首页数据接口（轮播图+筛选选项+推荐资源）
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def home_page(request):
    """
    首页核心数据接口：返回轮播图（优质资源）、三级筛选选项、热门推荐资源
    路径风格：符合现有 /api/xxx/ 规范，权限与原有接口一致（需登录）
    """
    try:
        # 1. 轮播图数据：安陆一中+已通过审核+优质资源+正常状态（优先级最高）
        carousel_resources = Resource.objects.filter(
            school="安陆一中",
            audit_status="approved",
            is_high_quality=True,
            status_tag="normal"
        ).order_by("-created_time")[:5]  # 限制5条，避免轮播过长

        # 2. 三级筛选选项（去重，保证前端筛选无重复值）
        subjects = Resource.objects.filter(audit_status="approved", status_tag="normal").values_list("subject", flat=True).distinct()
        grades = Resource.objects.filter(audit_status="approved", status_tag="normal").values_list("grade", flat=True).distinct()
        schools = Resource.objects.filter(audit_status="approved", status_tag="normal").values_list("school", flat=True).distinct()

        # 3. 热门推荐资源：已通过+正常状态+按下载量倒序（用户更关注热门资源）
        recommended_resources = Resource.objects.filter(
            audit_status="approved",
            status_tag="normal"
        ).order_by("-download_count")[:8]  # 限制8条，保证页面加载性能

        # 序列化（用列表序列化器，字段精简，提升传输速度）
        carousel_serializer = ResourceListSerializer(carousel_resources, many=True)
        recommended_serializer = ResourceListSerializer(recommended_resources, many=True)

        return Response({
            "code": 200,
            "message": "首页数据获取成功",
            "data": {
                "carousel_resources": carousel_serializer.data,  # 轮播图资源
                "filter_options": {  # 三级筛选选项
                    "subjects": list(subjects),
                    "grades": list(grades),
                    "schools": list(schools)
                },
                "recommended_resources": recommended_serializer.data  # 热门推荐
            }
        })
    except Exception as e:
        logger.error(f"首页数据获取失败：{str(e)}", exc_info=True)
        return Response({
            "code": 500,
            "message": f"首页数据获取失败：{str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 2. 资源列表接口（支持筛选+分页，用于资源列表页）
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def resource_list(request):
    """
    资源列表接口：支持按学科、年级、学校、优质资源筛选，带分页
    路径风格：/api/resources/list/ 符合现有层级规范，与首页接口区分
    """
    # 1. 获取筛选参数（前端三级筛选传递的参数）
    subject = request.query_params.get('subject')
    grade = request.query_params.get('grade')
    school = request.query_params.get('school')
    is_high_quality = request.query_params.get('is_high_quality')  # 布尔值：true/false

    # 2. 基础查询集：仅显示已通过审核+正常状态的资源（屏蔽待审核/驳回/下架资源）
    queryset = Resource.objects.filter(
        audit_status="approved",
        status_tag="normal"
    ).order_by("-created_time")  # 按上传时间倒序，最新资源在前

    # 3. 应用筛选条件（参数存在时才筛选，支持多条件组合）
    if subject:
        queryset = queryset.filter(subject=subject)
    if grade:
        queryset = queryset.filter(grade=grade)
    if school:
        queryset = queryset.filter(school=school)
    if is_high_quality in ["true", "True", "1"]:  # 兼容前端不同参数格式
        queryset = queryset.filter(is_high_quality=True)

    # 4. 分页（复用原有分页组件，保持分页格式一致）
    paginator = PageNumberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    # 5. 序列化（列表页用精简序列化器）
    serializer = ResourceListSerializer(paginated_queryset, many=True)
    return paginator.get_paginated_response({
        "code": 200,
        "message": "资源列表获取成功",
        "data": serializer.data
    })

# 3. 资源详情接口（含资源信息+已通过评论，用于详情页）
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def resource_detail(request, pk):
    """
    资源详情接口：返回资源完整信息+关联的已通过评论
    路径风格：/api/resources/<int:pk>/ 符合RESTful规范，与现有ID参数传递一致
    """
    try:
        # 1. 查询资源（仅显示已通过+正常状态，避免访问无效资源）
        resource = Resource.objects.get(
            id=pk,
            audit_status="approved",
            status_tag="normal"
        )

        # 2. 关联查询该资源的已通过评论（按评论时间倒序）
        comments = Comment.objects.filter(
            resource=resource,
            audit_status="approved"
        ).order_by("-created_time")[:10]  # 限制10条，避免评论过多影响加载

        # 3. 序列化（详情页用完整序列化器，评论用评论序列化器）
        resource_serializer = ResourceDetailSerializer(resource, context={"request": request})
        comment_serializer = CommentSerializer(comments, many=True)

        # 4. 下载量+1（仅统计有效访问，提升数据准确性）
        resource.download_count += 1
        resource.save()
        logger.info(f"用户 {request.user.username} 访问资源详情：{resource.title}（ID：{pk}），下载量更新为 {resource.download_count}")

        return Response({
            "code": 200,
            "message": "资源详情获取成功",
            "data": {
                "resource": resource_serializer.data,
                "comments": comment_serializer.data  # 关联返回评论，减少前端请求次数
            }
        })
    except Resource.DoesNotExist:
        return Response({
            "code": 404,
            "message": "资源不存在或已下架"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"资源详情获取失败（ID：{pk}）：{str(e)}", exc_info=True)
        return Response({
            "code": 500,
            "message": f"资源详情获取失败：{str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 4. 评论提交接口（关联资源ID）
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def comment_submit(request, pk):
    """
    评论提交接口：关联指定资源，自动关联当前用户
    路径风格：/api/resources/<int:pk>/comments/ 层级清晰，与详情接口关联
    """
    user = request.user
    try:
        # 1. 验证资源是否存在（仅允许对有效资源评论）
        resource = Resource.objects.get(
            id=pk,
            audit_status="approved",
            status_tag="normal"
        )
    except Resource.DoesNotExist:
        return Response({
            "code": 404,
            "message": "资源不存在或已下架，无法评论"
        }, status=status.HTTP_404_NOT_FOUND)

    # 2. 获取并验证评论内容
    content = request.data.get('content')
    if not content or content.strip() == "":
        return Response({
            "code": 400,
            "message": "评论内容不能为空"
        }, status=status.HTTP_400_BAD_REQUEST)

    # 3. 保存评论（自动关联用户、资源，审核状态默认待审核）
    comment = Comment.objects.create(
        resource=resource,
        user=user,
        content=content.strip(),
        audit_status="pending"  # 评论需审核后才显示，避免垃圾评论
    )
    logger.info(f"用户 {user.username} 提交评论：资源ID {pk}，评论ID {comment.id}")

    # 4. 序列化返回
    serializer = CommentSerializer(comment)
    return Response({
        "code": 201,
        "message": "评论提交成功，等待管理员审核",
        "data": serializer.data
    }, status=status.HTTP_201_CREATED)

# 5. 纠错反馈提交接口（关联资源ID）
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def feedback_submit(request, pk):
    """
    纠错反馈提交接口：关联指定资源，支持反馈类型分类
    路径风格：/api/resources/<int:pk>/feedbacks/ 与评论接口风格一致，便于前端记忆
    """
    user = request.user
    try:
        # 1. 验证资源是否存在
        resource = Resource.objects.get(
            id=pk,
            audit_status="approved",
            status_tag="normal"
        )
    except Resource.DoesNotExist:
        return Response({
            "code": 404,
            "message": "资源不存在或已下架，无法提交反馈"
        }, status=status.HTTP_404_NOT_FOUND)

    # 2. 获取并验证参数
    feedback_type = request.data.get('feedback_type')
    content = request.data.get('content')
    if not feedback_type or feedback_type not in ["content_error", "format_error", "other"]:
        return Response({
            "code": 400,
            "message": "反馈类型无效（仅支持 content_error/format_error/other）"
        }, status=status.HTTP_400_BAD_REQUEST)
    if not content or content.strip() == "":
        return Response({
            "code": 400,
            "message": "反馈内容不能为空"
        }, status=status.HTTP_400_BAD_REQUEST)

    # 3. 保存反馈
    feedback = Feedback.objects.create(
        resource=resource,
        user=user,
        feedback_type=feedback_type,
        content=content.strip()
    )
    logger.info(f"用户 {user.username} 提交纠错反馈：资源ID {pk}，反馈ID {feedback.id}")

    # 4. 序列化返回
    serializer = FeedbackSerializer(feedback)
    return Response({
        "code": 201,
        "message": "纠错反馈提交成功，我们会尽快处理",
        "data": serializer.data
    }, status=status.HTTP_201_CREATED)

# 6. 资源点赞接口（切换点赞状态：点赞/取消点赞）
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def resource_like(request, pk):
    """
    资源点赞接口：支持点赞和取消点赞（单次请求切换状态）
    路径风格：/api/resources/<int:pk>/like/ 符合动词+资源ID的规范，与现有操作接口一致
    """
    user = request.user
    try:
        # 1. 验证资源是否存在
        resource = Resource.objects.get(
            id=pk,
            audit_status="approved",
            status_tag="normal"
        )
    except Resource.DoesNotExist:
        return Response({
            "code": 404,
            "message": "资源不存在或已下架，无法点赞"
        }, status=status.HTTP_404_NOT_FOUND)

    # 2. 模拟点赞状态（因未建点赞关联表，简化为切换like_count；实际项目可新增Like模型记录用户-资源关联）
    # 注：此处为简化方案，若需防止重复点赞，需新增Like模型（user+resource唯一约束）
    resource.like_count += 1 if request.data.get('like', True) else -1
    resource.like_count = max(0, resource.like_count)  # 确保点赞数不小于0
    resource.save()

    action = "点赞" if request.data.get('like', True) else "取消点赞"
    logger.info(f"用户 {user.username} 对资源 {resource.title}（ID：{pk}）进行{action}，当前点赞数：{resource.like_count}")

    return Response({
        "code": 200,
        "message": f"{action}成功",
        "data": {
            "like_count": resource.like_count
        }
    })

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