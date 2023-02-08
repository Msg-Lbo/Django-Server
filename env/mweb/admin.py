from django.contrib import admin
from mweb.models import Article, Userinfo, Category, Comments, Favorite, Like, Navigations, tmp, Barrage
# Register your models here.


# 文章
@admin.register(Article)
class Article(admin.ModelAdmin):
    list_display = ('id', 'title', 'belong', 'category_belong', 'create_time', 'update_time')
    list_display_links = ('title',)
    ordering = ('id',)


# 置顶文章
@admin.register(tmp)
class tmp(admin.ModelAdmin):
    list_display = ('id', 'belong')
    list_display_links = ('belong',)
    ordering = ('id',)


@admin.register(Userinfo)
class Userinfo(admin.ModelAdmin):
    list_display = ('id', 'belong', 'nickName')
    list_display_links = ('belong',)
    ordering = ('id',)


admin.site.register(Category)


# 点赞
@admin.register(Like)
class Like(admin.ModelAdmin):
    list_display = ('id', 'belong_user', 'belong')
    ordering = ('id',)


# 收藏
@admin.register(Favorite)
class Favorite(admin.ModelAdmin):
    list_display = ('id', 'belong_user', 'belong')
    ordering = ('id',)


# 链接
@admin.register(Navigations)
class Navigations(admin.ModelAdmin):
    list_display = ('id', 'logo', 'link')
    ordering = ('id',)


# 弹幕
@admin.register(Barrage)
class Barrage(admin.ModelAdmin):
    list_display = ('id', 'text', 'color')
    list_display_links = ('text',)
    ordering = ('id',)


# 评论
@admin.register(Comments)
class Comments(admin.ModelAdmin):
    list_display = ('id', 'reply_user','reply_comment', 'reply_email','reply_web','belong','create_time')
    list_display_links = ('reply_comment',)
    ordering = ('create_time',)