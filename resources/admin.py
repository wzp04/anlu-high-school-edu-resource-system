from django.contrib import admin
from .models import Resource, Comment, Feedback

@admin.register(Resource)


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploader', 'audit_status', 'school', 'subject', 'created_time', 'md5')
    readonly_fields = ('md5', 'created_time')  # MD5和创建时间由系统自动生成，设为只读
    fields = ('title', 'file', 'version', 'school', 'subject', 'grade', 'uploader', 'audit_status', 'md5', 'created_time')

# 新增：Comment（评论）模型后台管理配置
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # 列表页显示的字段：管理员能快速查看评论核心信息，无需进入详情
    list_display = ('id', 'user', 'resource', 'content', 'audit_status', 'created_time')
    # 只读字段：用户、资源、创建时间由系统自动关联/生成，不允许手动修改
    readonly_fields = ('user', 'resource', 'created_time')
    # 详情页编辑字段：仅允许修改评论内容和审核状态（核心管理需求）
    fields = ('user', 'resource', 'content', 'audit_status', 'created_time')
    # 筛选器：支持按审核状态、资源、用户筛选，提升管理效率
    list_filter = ('audit_status', 'resource', 'user')
    # 搜索框：支持按评论内容、资源标题搜索，快速定位目标评论
    search_fields = ('content', 'resource__title')

# 新增：Feedback（纠错反馈）模型后台管理配置
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    # 列表页显示的字段：覆盖反馈核心信息，符合管理场景需求
    list_display = ('id', 'user', 'resource', 'feedback_type', 'content', 'created_time')
    # 只读字段：用户、资源、反馈类型、创建时间不允许手动修改（避免数据混乱）
    readonly_fields = ('user', 'resource', 'feedback_type', 'created_time')
    # 详情页编辑字段：仅允许查看关键信息，修改反馈内容（如需补充说明）
    fields = ('user', 'resource', 'feedback_type', 'content', 'created_time')
    # 筛选器：支持按反馈类型、资源筛选，便于分类处理
    list_filter = ('feedback_type', 'resource')
    # 搜索框：支持按反馈内容、资源标题搜索，快速找到目标反馈
    search_fields = ('content', 'resource__title')