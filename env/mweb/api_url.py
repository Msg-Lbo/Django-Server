from django.urls import path
from mweb import api


urlpatterns = [
    # 文章管理
    # 文章查看
    path('article-data/', api.article_data),
    # 文章发布
    path('add-article/', api.add_article),
    # 文章删除
    path('delete-article/', api.delete_article),
    # 文章列表
    path('article-list/', api.article_list),
    # 文章归档
    path('article-archives/', api.article_archives),
    # 图片上传
    path('upload-image/', api.upload_image),
    # 用户管理
    # 登录
    path('ylmty-login/', api.ylmty_login),
    # 注册
    path('ylmty-register/', api.ylmty_register),
    # 自动登录
    path('auto-login/', api.ylmty_autologin),
    # 登出
    path('ylmty-logout/', api.ylmty_logout),
    # 鉴权
    path('ylmty-checkperm/',api.ylmty_checkperm),
    # 用户列表 
    path('ylmty-userlist/',api.ylmty_userlist),
    # 获取分类
    path('get-category/',api.get_category),
    # 提交分类
    path('post-category/',api.post_category),
    # 删除分类
    path('delete-category/',api.delete_category),
    # 文章用户互动
    path('comments/',api.ylmty_comments),
    path('user-article-info/',api.user_article_info),
    path('article-like/',api.article_like),
    path('add-navigation/',api.add_navigation),
    path('article-top/',api.article_top),
    path('add-barrage/',api.add_barrage),
    path('get-barrage/',api.get_barrage),
    path('get-verify/',api.get_verify)


]
