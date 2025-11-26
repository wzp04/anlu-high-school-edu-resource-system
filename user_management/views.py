from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # 关键：导入允许所有用户访问的权限类
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User  # 相对导入User模型
from .serializers import UserRegisterSerializer, UserLoginSerializer  # 导入序列化器

class UserRegisterView(APIView):
    """注册接口：处理用户注册请求"""
    # 关键：允许任何用户（包括未登录用户）访问该接口
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"code": 200, "message": "注册成功，等待学校初审", "data": {"username": user.username}},
                status=status.HTTP_201_CREATED
            )
        return Response({"code": 400, "message": "注册失败", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """登录接口：处理用户登录请求并返回JWT令牌"""
    # 关键：允许任何用户（包括未登录用户）访问该接口
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "code": 200,
                    "message": "登录成功",
                    "data": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user_id": user.id,
                        "username": user.username
                    }
                })
            return Response({"code": 401, "message": "用户名或密码错误"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"code": 400, "message": "参数错误", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)