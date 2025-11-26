from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User  # 相对导入当前应用的User模型

class UserRegisterSerializer(serializers.ModelSerializer):
    """注册序列化器：处理注册信息校验"""
    password = serializers.CharField(write_only=True, required=True, min_length=6, label="密码")
    # 修改点1：确认密码字段名从 password_confirm → passwordConfirm（与前端表单字段一致）
    passwordConfirm = serializers.CharField(write_only=True, required=True, label="确认密码")

    class Meta:
        model = User
        # 修改点2：移除 audit_material 字段（前端基础注册页无该字段，无需必填）
        fields = ['username', 'password', 'passwordConfirm', 'school', 'subject']
        # 修改点3：删除 audit_material 的 extra_kwargs 配置（字段已移除，配置无用）

    def validate(self, data):
        # 适配修改点1：校验逻辑从 password_confirm 改为 passwordConfirm
        if data['password'] != data['passwordConfirm']:
            raise serializers.ValidationError({"passwordConfirm": "两次密码不一致"})
        return data

    def create(self, validated_data):
        # 适配修改点1：删除的字段从 password_confirm 改为 passwordConfirm
        validated_data.pop('passwordConfirm')
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class UserLoginSerializer(serializers.Serializer):
    """登录序列化器：处理登录参数校验"""
    username = serializers.CharField(required=True, label="用户名")
    password = serializers.CharField(required=True, write_only=True, label="密码")