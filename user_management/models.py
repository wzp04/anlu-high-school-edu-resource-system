# user_management/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    """扩展Django默认用户模型，适配毕设需求"""
    school = models.CharField(max_length=100, verbose_name="学校")
    subject = models.CharField(max_length=50, verbose_name="学科")
    AUDIT_STATUS = (
        ('pending', '待审核'),
        ('school_approved', '学校初审通过'),
        ('approved', '教育局终审通过'),
        ('rejected', '审核驳回')
    )
    audit_status = models.CharField(max_length=20, choices=AUDIT_STATUS, default='pending', verbose_name="审核状态")
    audit_material = models.CharField(max_length=255, null=True, blank=True, verbose_name="佐证材料加密路径")
    user_uuid = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="用户唯一标识")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username