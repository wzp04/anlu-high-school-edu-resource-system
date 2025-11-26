from rest_framework import serializers
from .models import UploadTask, Resource

class UploadTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadTask
        fields = ['id', 'file_md5', 'filename', 'total_chunks', 'uploaded_chunks', 'status']  # 含 id
        read_only_fields = ['uploaded_chunks', 'status']

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
        read_only_fields = ['md5', 'created_time']