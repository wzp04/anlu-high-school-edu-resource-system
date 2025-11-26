from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="分类名称")
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name="children", verbose_name="父分类")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "资源分类"
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.name