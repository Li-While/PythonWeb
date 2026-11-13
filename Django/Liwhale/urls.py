"""Liwhale URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from li import views

urlpatterns = [
    # 管理员登陆
    path("admin/", admin.site.urls),
    path('index/', views.index),
    path('index/delete/', views.info_delete),
    path('chartjs/', views.chartjs),
    path('buttons/', views.buttons),
    path('dropdowns/', views.dropdowns),
    path('typography/', views.typography),
    path('basic_elements/', views.basic_elements),
    path('basic-table/', views.basic_table),
    path('mdi/', views.mdi),
    path('login/', views.login),
    path('register/', views.register),
    path('documentation/', views.documentation),
    path('draft/', views.draft),


]

handler404 = views.page_not_found