# user_management/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User  # 相对导入当前应用的User模型

class UserRegisterSerializer(serializers.ModelSerializer):
    """注册序列化器：处理注册信息校验"""
    password = serializers.CharField(write_only=True, required=True, min_length=6, label="密码")
    password_confirm = serializers.CharField(write_only=True, required=True, label="确认密码")

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm', 'school', 'subject', 'audit_material']
        extra_kwargs = {
            'audit_material': {'required': True, 'label': '佐证材料路径'}
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "两次密码不一致"})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class UserLoginSerializer(serializers.Serializer):
    """登录序列化器：处理登录参数校验"""
    username = serializers.CharField(required=True, label="用户名")
    password = serializers.CharField(required=True, write_only=True, label="密码")