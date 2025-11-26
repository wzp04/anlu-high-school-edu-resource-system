# user_management/admin.py
from django.contrib import admin
from .models import User  # 导入User模型

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """配置用户模型在admin后台的显示"""
    list_display = ('id', 'username', 'school', 'subject', 'audit_status', 'created_time')  # 列表页显示的字段
    search_fields = ('username', 'school', 'subject')  # 可搜索的字段
    list_filter = ('audit_status',)  # 可筛选的字段
    readonly_fields = ('user_uuid', 'created_time')  # 只读字段（不允许编辑）