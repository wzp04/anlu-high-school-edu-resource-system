from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploader', 'audit_status', 'school', 'subject', 'created_time', 'md5')
    readonly_fields = ('md5', 'created_time')  # MD5和创建时间由系统自动生成，设为只读
    fields = ('title', 'file', 'version', 'school', 'subject', 'grade', 'uploader', 'audit_status', 'md5', 'created_time')
