import hashlib
import os
from django.db import models
from django.conf import settings
from user_management.models import User

# 定义文件上传路径函数（按用户分目录）
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.uploader.id, filename)

class Resource(models.Model):
    title = models.CharField(max_length=200, verbose_name="资源标题")
    file = models.FileField(upload_to=user_directory_path, verbose_name="资源文件")  # 按用户分目录存储
    md5 = models.CharField(max_length=32, verbose_name="文件MD5", unique=True, editable=False)
    version = models.CharField(max_length=20, default="V1.0", verbose_name="版本号")
    school = models.CharField(max_length=100, verbose_name="上传学校")
    subject = models.CharField(max_length=50, verbose_name="学科")
    grade = models.CharField(max_length=20, verbose_name="年级")
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_resources")
    # 新增：recall_pending（召回待审核）状态，与前端同步
    audit_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "待审核"), 
            ("approved", "已通过"),   # 前后端统一为approved
            ("rejected", "已驳回"),
            ("recall_pending", "召回待审核")  # 新增状态
        ],
        default="pending",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 生成文件MD5（仅当文件存在且MD5未生成时）
        if self.file and not self.md5:
            md5 = hashlib.md5()
            for chunk in self.file.chunks():
                md5.update(chunk)
            self.md5 = md5.hexdigest()
        super().save(*args, **kwargs)

class UploadTask(models.Model):
    """记录分片上传任务的状态"""
    file_md5 = models.CharField(max_length=32, unique=True, verbose_name="文件唯一标识(MD5)")
    filename = models.CharField(max_length=255, verbose_name="原始文件名")
    total_chunks = models.PositiveIntegerField(verbose_name="总分片数")
    uploaded_chunks = models.JSONField(default=list, verbose_name="已上传的分片索引列表")
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='upload_tasks', verbose_name="上传者")
    status = models.CharField(
        max_length=20,
        choices=[('pending', '上传中'), ('completed', '已完成'), ('failed', '上传失败')],
        default='pending',
        verbose_name="上传状态"
    )
    # 保留已添加的业务字段
    subject = models.CharField(max_length=50, default='未分类', verbose_name="学科")
    grade = models.CharField(max_length=20, default='未指定', verbose_name="年级")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "分片上传任务"
        verbose_name_plural = verbose_name