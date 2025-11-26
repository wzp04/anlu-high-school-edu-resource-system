# user_management/urls.py
from django.urls import path
from .views import UserRegisterView, UserLoginView  # 导入当前应用的视图

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user_register'),  # 注册接口
    path('login/', UserLoginView.as_view(), name='user_login'),          # 登录接口
]