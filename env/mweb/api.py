import re
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from mweb.models import Article, Userinfo, Category, Comments, Favorite, Like, PayOrder, Navigations, tmp, Barrage
from django.contrib.auth.models import User, Group, Permission
from django.db.models.aggregates import Count
from django.db.models.functions import TruncYear
from mweb.verify import verifyCode
import os
import datetime
import json

hostUrl = 'http://127.0.0.1:9000/'

num1 = verifyCode()[0]
num2 = verifyCode()[1]
# 验证码


def refresh():
    global num1
    num1 = verifyCode()[0]
    global num2
    num2 = verifyCode()[1]
    return ([num1, num2])


@api_view(['GET'])
def get_verify(request):
    return Response(refresh())


# 鉴权
@api_view(['POST'])
def ylmty_checkperm(request):
    token = request.POST['token']
    content_type = request.POST['contentType']
    permissions = json.loads(request.POST['permissions'])
    user_token = Token.objects.filter(key=token)
    if user_token:
        user = user_token[0].user
        for p in permissions:
            app_str = content_type.split('_')[0]
            model_str = content_type.split('_')[1]
            perm_str = app_str + '.' + p + '_' + model_str
            # print(perm_str)
            check = user.has_perm(perm_str)
            # print(check)
        if check == False:
            return Response('noperm')
    else:
        return Response('nologin')
    return Response('ok')


# 登录
@api_view(['POST'])
def ylmty_login(request):
    username = request.POST['username']
    password = request.POST['password']
    # 登录逻辑
    user = User.objects.filter(username=username)[0]
    user_info = Userinfo.objects.filter(belong=user)
    if user:
        checkPwd = check_password(password, user.password)
        if checkPwd:
            userinfo = Userinfo.objects.get_or_create(belong=user)
            userinfo = Userinfo.objects.get(belong=user)
            token = Token.objects.get_or_create(user=user)
            token = Token.objects.get(user=user)
            isadmin = user.is_superuser
            user_info.update(last_login=datetime.datetime.now())
        else:
            return Response('pwderr')
    else:
        return Response('none')
    userinfo_data = {
        'token': token.key,
        'nickName': userinfo.nickName,
        'headImg': userinfo.headImg,
        'isadmin': isadmin
    }
    return Response(userinfo_data)


# 注册
@api_view(['POST'])
def ylmty_register(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    password2 = request.POST['password2']
    # 注册逻辑
    user = User.objects.filter(username=username)
    if user:
        return Response('repeat')
    else:
        new_password = make_password(password, username)
        newUser = User(username=username, password=new_password, email=email)
        newUser.save()

    token = Token.objects.get_or_create(user=newUser)
    token = Token.objects.get(user=newUser)
    userinfo = Userinfo.objects.get_or_create(belong=newUser)
    userinfo = Userinfo.objects.get(belong=newUser)
    userinfo.save()
    return Response({"token": token.key})


# 自动登录
@api_view(['POST'])
def ylmty_autologin(request):
    token = request.POST['token']
    user_token = Token.objects.filter(key=token)
    if user_token:
        userinfo = Userinfo.objects.get(belong=user_token[0].user)
        user = User.objects.filter(id=userinfo.belong.id)
        isadmin = user[0].is_superuser
        userinfo_data = {
            'token': token,
            'nickName': userinfo.nickName,
            'headImg': userinfo.headImg,
            'isadmin': isadmin
        }
        return Response(userinfo_data)
    else:
        return Response('tokenTimeout')


# 登出
@api_view(['POST'])
def ylmty_logout(request):
    token = request.POST['token']
    user_token = Token.objects.get(key=token)
    user_token.delete()
    return Response('logout')


# 文章内容获取
@api_view(['GET'])
def article_data(request):
    article_id = request.GET['article_id']
    article = Article.objects.get(id=article_id)

    article_data = {
        "title": article.title,
        "describe": article.describe,
        "content": article.content,
        "nickName": article.belong.username,
        "time": article.update_time.strftime("%Y-%m-%d"),
        "category": "",
        "next_id": 0,
        "next_title": "",
        "pre_id": 0,
        "pre_title": "",

    }

    per_data = Article.objects.filter(id__lt=article_id)
    if per_data:
        article_data['pre_id'] = per_data.last().id
        article_data['pre_title'] = per_data.last().title

    next_data = Article.objects.filter(id__gt=article_id)
    if next_data:
        article_data['next_id'] = next_data.first().id
        article_data['next_title'] = next_data.first().title

    if article.category_belong:
        article_data["category"] = article.category_belong.name
    return Response(article_data)


# 发布文章
@api_view(['POST', 'PUT'])
def add_article(request):
    if request.method == "POST":
        token = request.POST['token']
        permList = [
            'mweb.add_article',
        ]
        checkUser = userLoginAndPerm(token, permList)
        if checkUser != 'perm_pass':
            print(checkUser)
            return Response(checkUser)
        title = request.POST['title']
        describe = request.POST['describe']
        content = request.POST['content']
        category = request.POST['category']
        create_time = request.POST['time']
        create_time = datetime.datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
        # print(create_time)
        category_item = Category.objects.filter(name=category)[0]
        user_token = Token.objects.filter(key=token)
        if len(user_token) == 0:
            return Response('nologin')
        # 保存文章
        try:
            new_article = Article(title=title)
            new_article.content = content
            new_article.describe = describe
            new_article.belong = user_token[0].user
            if category_item:
                new_article.category_belong = category_item
            else:
                new_article.category_belong = None
            new_article.create_time = create_time
            new_article.save()
            print(new_article.create_time)
            # print(src,new_src)
            return Response('ok')
        except:
            return Response('save article error')


# 图片上传
@api_view(['POST', 'FILES'])
def upload_image(request):
    imgForm = request.FILES.getlist('file')
    for i in imgForm:
        # 文件重命名
        image_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.' + i.name.split('.')[1]
        print(image_name)
        # 保存
        image_url = os.path.join('upload', image_name).replace('\\', '/')
        with open(image_url, 'wb') as f:
            f.write(i.read())
        # url拼接
        new_url = hostUrl + image_url
        return Response(new_url)


# 文章分页列表
@api_view(['GET'])
def article_list(request):
    page = request.GET['page']
    pageSize = request.GET['pageSize']
    category = request.GET['category']
    if category == 'all':
        articles = Article.objects.filter(top=0).order_by('-create_time')
    elif category == 'nobelong':
        articles = Article.objects.filter(category_belong__name=None).order_by('-create_time')
    else:
        articles = Article.objects.filter(category_belong__name=category).order_by('-create_time')
    total = len(articles)
    paginator = Paginator(articles, pageSize)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    articles_data = []
    for a in articles:
        a_item = {
            'title': a.title,
            'id': a.id,
            'category': '',
            'describe': a.describe,
            'create_time': a.create_time.strftime("%Y-%m-%d"),
            'update_time': a.update_time.strftime("%Y-%m-%d"),
        }
        if a.category_belong == None:
            a_item['category'] = '未分类'
        else:
            a_item['category'] = str(a.category_belong)
        articles_data.append(a_item)
    return Response({'data': articles_data, 'total': total + len(tmp.objects.all())-1})
    # return Response('ok')


# 文章归档
@api_view(['GET'])
def article_archives(request):
    articles = Article.objects.annotate(year=TruncYear("create_time")).values(
        "create_time__year").annotate(cout_num=Count("pk"))
    a = 0
    for i in articles:
        titles = Article.objects.filter(create_time__year=i["create_time__year"])
        item = []
        for i_title in titles:
            temp = {
                "id": i_title.id,
                "title": i_title.title,
                "time": i_title.create_time.strftime("%m-%d")
            }
            item.append(temp)
        articles[a].update({"data": item})
        a += 1
    articles = sorted(articles, key=lambda create_time__year: create_time__year["create_time__year"], reverse=True)
    return Response(articles)


# 文章置顶
@api_view(['POST', 'GET'])
def article_top(request):
    if request.method == 'POST':
        token = request.POST['token']
        permList = [
            'mweb.change_article',
        ]
        checkUser = userLoginAndPerm(token, permList)
        if checkUser != 'perm_pass':
            print(checkUser)
            return Response(checkUser)
        top_id = request.POST['id']
        article = Article.objects.filter(id=top_id)[0]
        top_tmp = tmp.objects.filter(belong=article)
        if top_tmp:
            article.top -= 1
            article.save()
            top_tmp[0].delete()
            return Response('cancel')
        else:
            article.top += 1
            article.save()
            in_top = tmp(belong=article)
            in_top.save()
            return Response('top')
    if request.method == 'GET':
        all_top = tmp.objects.all()
        top = []
        for t in all_top:
            t_item = {
                'title': t.belong.title,
                'id': t.belong.id,
                'category': '',
                'describe': t.belong.describe,
                'create_time': t.belong.create_time.strftime("%Y-%m-%d"),
                'update_time': t.belong.create_time.strftime("%Y-%m-%d"),

            }
            if t.belong.category_belong == None:
                t_item['category'] = '未分类'
            else:
                t_item['category'] = str(t.belong.category_belong)
            top.append(t_item)
        return Response(top)
    return Response('ok')


# 删除文章
@api_view(['DELETE'])
def delete_article(request):
    article_id = request.POST['id']
    token = request.POST['token']
    permList = [
        'mweb.add_article',
    ]
    checkUser = userLoginAndPerm(token, permList)
    if checkUser != 'perm_pass':
        print(checkUser)
        return Response(checkUser)
    article = Article.objects.filter(id=article_id)
    if article:
        article.delete()
        return Response('ok')
    else:
        return Response('Not found')


# 用户列表
@api_view(['GET', 'POST'])
def ylmty_userlist(request):
    if request.method == 'GET':
        user_list = Userinfo.objects.all()
        user_list_data = []
        for user in user_list:
            user_item = {
                "id": user.belong.id,
                "account": user.belong.username,
                "nickname": user.nickName,
                "email": user.belong.email,
                "date_joined": user.belong.date_joined.strftime("%Y-%m-%d %H:%M"),
                "last_login": user.last_login.strftime("%Y-%m-%d %H:%M")
            }
            user_list_data.append(user_item)
        return Response(user_list_data)
    if request.method == 'POST':
        token = request.POST['token']
        permList = [
            'auth.change_user',
        ]
        checkUser = userLoginAndPerm(token, permList)
        if checkUser != 'perm_pass':
            return Response(checkUser)
        edit_id = request.POST['id']
        edit_new_account = request.POST['edit_new_account']
        edit_new_nickname = request.POST['edit_new_nickname']
        edit_new_email = request.POST['edit_new_email']
        # edit_new_password = request.POST['edit_new_password']
        editToUser = User.objects.filter(id=edit_id)
        if not editToUser:
            return Response("not found")
        else:
            return Response(editToUser[0].username)


# 检查用户登录与权限
def userLoginAndPerm(token, permlist):
    user_token = Token.objects.filter(key=token)
    if user_token:
        user = user_token[0].user
        for perm_str in permlist:
            perm_user = user.has_perm(perm_str)
            if perm_user:
                return 'perm_pass'
            else:
                return 'noperm'
    else:
        return 'nologin'


# 获取分类
@api_view(['GET'])
def get_category(request):
    allarticle = Article.objects.all()
    allcategory_of_num = Category.objects.values().annotate(category_num=Count('article_category')).order_by("id")
    return Response({"allcategory_of_num": allcategory_of_num, "all": len(allarticle), "no_belong": len(Article.objects.filter(category_belong=None))})
    # return Response('ok')


# 提交分类
@api_view(['POST'])
def post_category(request):
    category_name = request.POST['category']
    category_belong = request.POST['category_belong']
    is_category = Category.objects.filter(name=category_name)
    is_belong = Category.objects.filter(name=category_belong)
    if is_category and is_belong:
        return Response("repeat")
    elif is_belong:
        new_category = Category(name=category_name, belong=is_belong[0])
        new_category.save()
    else:
        return Response("Not found")
    return Response('ok')


# 删除分类
@api_view(['POST'])
def delete_category(request):
    category_name = request.POST['category']
    token = request.POST['token']
    permList = [
        'mweb.delte_category',
    ]
    checkUser = userLoginAndPerm(token, permList)
    if checkUser != 'perm_pass':
        print(checkUser)
        return Response(checkUser)
    is_category = Category.objects.filter(name=category_name)
    if is_category:
        is_category.delete()
    else:
        return Response("Not found")
    return Response('ok')


# 文章用户互动
@api_view(['GET', 'POST'])
def ylmty_comments(request):
    if request.method == 'GET':
        articleId = request.GET['article_id']
        print(articleId)
        article = Article.objects.get(id=articleId)
        comments = Comments.objects.filter(belong=article)[::-1]
        Allcomments = Comments.objects.filter(belong=article).all()[:5]

        comments_data = []
        for comment in comments:
            comment_item = {
                "reply_user": comment.reply_user,
                "reply_content": comment.reply_comment,
                "reply_time": comment.create_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            comments_data.append(comment_item)

        # for Newcomment in Allcomments:
        #     Newcomment_item = {
        #         "New_nickName": Newcomment.belong_user.username,
        #         "New_comment": Newcomment.comment
        #     }
        #     comments_data.append(Newcomment_item)

        return Response(comments_data)

    if request.method == 'POST':
        replyUser = request.POST['replyUser']
        replyEmail = request.POST['replyEmail']
        replyWeb = request.POST['replyWeb']
        replyContent = request.POST['replyContent']
        articleId = request.POST['articleId']

        article = Article.objects.get(id=articleId)

        new_comments = Comments(reply_user=replyUser, reply_email=replyEmail, reply_web=replyWeb, belong=article, reply_comment=replyContent)
        new_comments.save()
        return Response('ok')


# 获取点赞 收藏 打赏
@api_view(['POST'])
def user_article_info(request):
    token = request.POST['token']

    user_token = Token.objects.filter(key=token)
    if len(user_token) == 0:
        Response('nologin')

    article_id = request.POST['article_id']
    article = Article.objects.get(id=article_id)
    user = user_token[0].user

    user_article_info = {
        "like": False,
        "favor": False,
        "dashang": False
    }

    liked = Like.objects.filter(belong=article, belong_user=user)
    if liked:
        user_article_info['like'] = True

    Favored = Favorite.objects.filter(belong=article, belong_user=user)
    if Favored:
        user_article_info['favor'] = True

    Payed = PayOrder.objects.filter(belong=article, belong_user=user, status=True)
    if Payed:
        user_article_info['dashang'] = True

    return Response(user_article_info)


# 执行点赞 收藏 打赏
@api_view(['POST'])
def article_like(request):
    token = request.POST['token']

    user_token = Token.objects.filter(key=token)
    if len(user_token) == 0:
        return Response('nologin')

    article_id = request.POST['article_id']
    article = Article.objects.get(id=article_id)

    liked = Like.objects.filter(belong=article, belong_user=user_token[0].user)

    if liked:
        liked[0].delete()
        return Response('ok')
    else:
        new_like = Like(belong=article, belong_user=user_token[0].user)
        new_like.save()
        return Response('ok')


@api_view(['POST', 'GET'])
def add_navigation(request):
    if request.method == 'POST':
        title = request.POST['title']
        logo = request.POST['logo']
        describes = request.POST['describes']
        type = request.POST['type']
        link = request.POST['link']
        links = Navigations(title=title)
        links.logo = logo
        links.describes = describes
        links.link = link
        links.save()
        print(type)
        # return Response({"friends": friends, "navigations": navigations, "tools": tools})
    return Response('ok')


@api_view(['POST'])
def add_barrage(request):
    v = int(request.POST['v'])
    if num1+num2 != v:
        return Response("CodeError")
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    text = request.POST['text']
    color = request.POST['color']
    x = request.POST['x']
    y = request.POST['y']

    regular = re.compile(r'^#([a-fA-F\d]{6}|[a-fA-F\d]{3})$')
    if re.findall(regular, color):
        new_barrage = Barrage(text=text, color=color, x=x, y=y, send_ip=ip)
        new_barrage.save()
        lastBarrage = Barrage.objects.last()
        bar = {
            "text": lastBarrage.text,
            "color": lastBarrage.color,
            "ip": lastBarrage.send_ip
        }
        return Response(bar)
    else:
        return Response('Not a hex color')


@api_view(['GET'])
def get_barrage(request):
    allBarrage = Barrage.objects.all().order_by('-id')
    barrageList = []
    for i in allBarrage:
        item = {
            "text": i.text,
            "color": i.color,
            "x": i.x,
            "y": i.y,
            "ip": i.send_ip
        }
        barrageList.append(item)
    return Response(barrageList)
