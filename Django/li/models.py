from django.db import models

# Create your models here.


class UserInfo(models.Model):
    # id默认生成
    user = models.CharField(max_length=20, verbose_name="用户名")
    pwd = models.CharField(max_length=32, verbose_name="密码")
    email = models.CharField(max_length=32, verbose_name="邮件")
    age = models.IntegerField(default=3, verbose_name="年龄")
    sex = models.CharField(max_length=5, verbose_name="性别")

    class Meta:
        db_table = "li_userinfo"
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id



