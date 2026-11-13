from django.contrib import admin
from .models import UserInfo

# Register your models here.
admin.site.site_header = "用户管理系统"
admin.site.site_title = "用户管理系统"
admin.site.index_title = "用户管理系统"


# 注册
# admin.site.register(UserInfo, IAdmin)
@admin.register(UserInfo)
class IAdmin(admin.ModelAdmin):
    list_display = ['user', 'pwd', 'email', 'age', 'sex']



