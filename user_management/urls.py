from django.urls import path
# 导入user_management应用自己的视图
from user_management.views import UserRegisterView, UserLoginView

urlpatterns = [
    # 注册接口：/api/users/register/
    path('register/', UserRegisterView.as_view(), name='user_register'),
    # 登录接口：/api/users/login/
    path('login/', UserLoginView.as_view(), name='user_login'),
]