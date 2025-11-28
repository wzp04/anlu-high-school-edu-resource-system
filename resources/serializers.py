from rest_framework import serializers
from .models import UploadTask, Resource, Comment, Feedback

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

class ResourceListSerializer(serializers.ModelSerializer):
    # 复用原有字段：直接映射模型字段，无需重复定义
    school_name = serializers.CharField(source="school", read_only=True)  # 复用school字段，重命名为school_name更直观
    status_tag_text = serializers.SerializerMethodField(read_only=True)  # 新增：状态标签中文转换（如normal→正常）
    is_high_quality_text = serializers.SerializerMethodField(read_only=True)  # 新增：优质资源标签中文（True→优质资源）

    class Meta:
        model = Resource
        # 精选核心字段：列表页无需展示所有字段，减少数据传输，提升性能
        fields = [
            "id", "title", "subject", "grade", "school_name", "version",
            "download_count", "like_count", "resource_type", "status_tag",
            "status_tag_text", "is_high_quality", "is_high_quality_text", "created_time"
        ]
        read_only_fields = fields  # 列表页仅用于展示，所有字段均为只读

    def get_status_tag_text(self, obj):
        """状态标签中文转换：提升前端展示友好性"""
        tag_map = {"normal": "正常", "to_fix": "待修正", "removed": "已下架"}
        return tag_map.get(obj.status_tag, "正常")

    def get_is_high_quality_text(self, obj):
        """优质资源标签中文转换：前端直接显示中文，无需二次处理"""
        return "优质资源" if obj.is_high_quality else ""

# 2. 资源详情序列化器（用于资源详情页）
class ResourceDetailSerializer(serializers.ModelSerializer):
    # 复用原有字段，补充详情页所需的展示字段
    uploader_name = serializers.SerializerMethodField(read_only=True)  # 新增：上传者姓名脱敏（合规需求）
    school_name = serializers.CharField(source="school", read_only=True)  # 复用school字段，重命名更直观
    status_tag_text = serializers.SerializerMethodField(read_only=True)  # 新增：状态标签中文
    preview_url = serializers.SerializerMethodField(read_only=True)  # 新增：预览文件完整URL（前端直接访问）

    class Meta:
        model = Resource
        # 完整字段：详情页需要展示所有核心信息，同时排除无用字段（如uploader_id直接关联，前端用脱敏姓名）
        fields = [
            "id", "title", "subject", "grade", "school_name", "version",
            "download_count", "like_count", "resource_type", "usage_scenario",
            "status_tag", "status_tag_text", "is_high_quality", "uploader_name",
            "preview_url", "created_time"
        ]
        read_only_fields = fields  # 详情页仅用于展示，所有字段均为只读

    def get_uploader_name(self, obj):
        """上传者姓名脱敏：仅显示姓氏+星号（如“张**”），保障用户隐私（合规需求）"""
        # 复用uploader关联字段，提取用户名并脱敏
        username = obj.uploader.username or getattr(obj.uploader, "name", "")
        if len(username) >= 2:
            return username[0] + "**"
        return username  # 若姓名只有1个字，直接显示（避免无意义脱敏）

    def get_status_tag_text(self, obj):
        """状态标签中文转换：同列表序列化器，保持一致性"""
        tag_map = {"normal": "正常", "to_fix": "待修正", "removed": "已下架"}
        return tag_map.get(obj.status_tag, "正常")

    def get_preview_url(self, obj):
        """预览文件完整URL拼接：前端直接使用，无需手动拼接域名（提升开发效率）"""
        if obj.preview_file:
            # 复用preview_file字段，通过request上下文拼接完整URL（支持本地/线上环境）
            return self.context["request"].build_absolute_uri(obj.preview_file.url)
        return None  # 无预览文件时返回None，前端显示“暂无预览”

# 3. 评论序列化器（用于详情页评论展示）
class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField(read_only=True)  # 新增：评论用户姓名脱敏（合规需求）

    class Meta:
        model = Comment
        # 仅展示前端需要的字段，排除audit_status（前端无需显示审核状态）
        fields = ["id", "user_name", "content", "created_time"]
        read_only_fields = ["user", "id", "created_time"]  # 用户、ID、时间均为只读，无法手动修改

    def get_user_name(self, obj):
        """评论用户姓名脱敏：同上传者脱敏规则，保持一致性"""
        username = obj.user.username or getattr(obj.user, "name", "")
        if len(username) >= 2:
            return username[0] + "**"
        return username

# 4. 纠错反馈序列化器（用于详情页纠错反馈提交+展示）
class FeedbackSerializer(serializers.ModelSerializer):
    feedback_type_text = serializers.SerializerMethodField(read_only=True)  # 新增：反馈类型中文转换

    class Meta:
        model = Feedback
        fields = ["id", "feedback_type", "feedback_type_text", "content", "created_time"]
        read_only_fields = ["user", "resource", "id", "created_time"]  # 关联资源、用户、时间均为只读

    def get_feedback_type_text(self, obj):
        """反馈类型中文转换：前端直接显示中文，无需二次处理"""
        type_map = {"content_error": "内容错误", "format_error": "格式错误", "other": "其他问题"}
        return type_map.get(obj.feedback_type, "其他问题")

    def create(self, validated_data):
        """复用父类create方法，补充上下文用户（前端无需传递用户ID，通过登录态获取）"""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)