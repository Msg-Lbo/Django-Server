from django.db import models
from django.contrib.auth.models import User
# Create your models here.


# 用户信息
class Userinfo(models.Model):
    headImg = models.CharField(null=True, blank=True, max_length=200)
    nickName = models.CharField(null=True, blank=True, default="00001", max_length=200, verbose_name="昵称")
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='最后登录时间')
    belong = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="账号")

    def __int__(self):
        return self.id

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name


# 文章分类
class Category(models.Model):
    name = models.CharField(null=False, blank=True, max_length=80, unique=True, db_index=True, verbose_name="分类名")
    belong = models.ForeignKey('self', on_delete=models.CASCADE, to_field="name", null=True, blank=True, verbose_name="父级")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = verbose_name


# 文章
class Article(models.Model):
    title = models.CharField(null=True, blank=True, max_length=80, verbose_name="文章标题")
    describe = models.CharField(null=True, blank=True, max_length=200, verbose_name="文章描述")
    top = models.IntegerField(null=False, blank=True, default=0, verbose_name="是否置顶")
    content = models.TextField(verbose_name="文章内容")
    belong = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='article_user', verbose_name="作者")
    category_belong = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='article_category', verbose_name="分类")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="最后修改时间")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name


# 文章置顶中间表
class tmp(models.Model):
    belong = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name='top_article')

    def __int__(self):
        return self.belong

    class Meta:
        verbose_name = "置顶文章ID"
        verbose_name_plural = verbose_name


# 收藏
class Favorite(models.Model):
    belong_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='favor_user', verbose_name="谁收藏了")
    belong = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name='favor_article', verbose_name="文章")

    def __int__(self):
        return self.id


# 点赞
class Like(models.Model):
    belong_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='like_user', verbose_name="谁点赞了")
    belong = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name='like_article', verbose_name="文章")

    def __int__(self):
        return self.id


# 打赏
class PayOrder(models.Model):
    order = models.CharField(null=True, blank=True, max_length=80)
    price = models.CharField(null=True, blank=True, max_length=80)
    status = models.BooleanField(default=False, null=True, blank=True)
    belong_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='order_user', verbose_name="谁收藏了")
    belong = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name='order_article', verbose_name="收藏")

    def __int__(self):
        return self.id


# 评论
class Comments(models.Model):
    reply_user = models.CharField(null=True, blank=True, max_length=10, verbose_name="评论人")
    reply_email = models.CharField(null=True, blank=True, max_length=30, verbose_name="邮箱")
    reply_web = models.CharField(null=True, blank=True, max_length=80, verbose_name="网站")
    belong = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name='conmment_article', verbose_name="评论文章")
    reply_comment = models.CharField(null=True, blank=True, max_length=120)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")

    def __int__(self):
        return self.id

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name



# 链接
class Navigations(models.Model):
    logo = models.CharField(null=False, blank=True, max_length=255, verbose_name="logo")
    title = models.CharField(null=False, blank=True, max_length=80, verbose_name="网站标题")
    describes = models.CharField(null=False, blank=True, max_length=80, verbose_name="网站介绍")
    link = models.CharField(null=False, blank=True, max_length=255, verbose_name="链接")
    template = models.CharField(null=True, default=False, blank=True, max_length=1000, verbose_name="同意展示")

    def __int__(self):
        return self.id

    class Meta:
        verbose_name = "链接"
        verbose_name_plural = verbose_name


# 留言弹幕
class Barrage(models.Model):
    text = models.CharField(null=False, blank=True, max_length=20, verbose_name="弹幕")
    color = models.CharField(null=False, blank=True, max_length=7, verbose_name="颜色")
    x = models.CharField(null=False, blank=True, max_length=255, verbose_name="X")
    y = models.CharField(null=False, blank=True, max_length=255, verbose_name="Y")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")
    send_ip = models.CharField(null=False, blank=True, max_length=20, verbose_name="发送IP")

    def __int__(self):
        return self.text

    class Meta:
        verbose_name = "弹幕"
        verbose_name_plural = verbose_name
