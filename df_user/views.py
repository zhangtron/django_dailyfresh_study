from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from df_user.models import *
from df_goods.models import *
from hashlib import sha1
from .user_decorator import login_judge
from df_order.models import *
from django.core.paginator import Paginator, Page
# Create your views here.


def register(request):
    return render(request, 'df_user/register.html')


def register_handle(request):

    # 接收用户输入
    post = request.POST
    unamme = post.get('user_name')
    upwd = post.get('pwd')
    cpwd = post.get('cpwd')
    uemail = post.get('email')

    # 判断两次密码
    if upwd != cpwd:
        return redirect('/user/register')

    # 密码加密
    s1 = sha1()
    s1.update(upwd.encode('utf8'))
    upwd3 = s1.hexdigest()

    # 创建对象
    user = UserInfo()
    user.uname = unamme
    user.upwd = upwd3
    user.uemail = uemail
    user.save()
    # 注册成功，转到登录页面
    return redirect('/user/login/')

# 验证用户是否存在


def register_exist(request):
    uname = request.GET.get('uname')
    print(uname)
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count': count})

# 登录页面


def login(request):
    uname = request.COOKIES.get('uname')
    # 后面js有判断，如果为空就报错
    context = {'titel': '用户登录', 'erro_name': 0, 'error_pwd': 0, 'uname': uname}
    return render(request, 'df_user/login.html', context)


def login_handle(request):
    # 接收请求信息
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu = post.get('jizhu', 0)  # 勾选了1，默认不勾选0
    # 根据用户名查询对象
    # 用get查不到会报异常，用try处理
    # 用filter查不到返回[]
    users = UserInfo.objects.filter(uname=uname)
    print(uname)
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd.encode('utf8'))
        # 查出来是列表
        if s1.hexdigest() == users[0].upwd:
            red = HttpResponseRedirect('/user/info/')
            if jizhu != 0:
                red.set_cookie('uname', uname)
            else:
                # unme设为空，立马过期
                red.set_cookie('uname', '', max_age=-1)
            # 根据id查数据，name用的多，显示频度高，不希望每次都查，所以存起来
            print(users[0].id)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:  # 串过去的原因是让他们再显示
            context = {
                'title': '用户登录',
                'error_name': 0,
                'error_pwd': 1,
                'uname': uname,
                'upwd': upwd}
            return render(request, 'df_user/login.html', context)
    else:  # 用户名错误，密码没错
        context = {
            'title': '用户登录',
            'error_name': 1,
            'error_pwd': 0,
            'uname': uname,
            'upwd': upwd}
        return render(request, 'df_user/login.html', context)


def logout(request):
    request.session.flush()
    return redirect('/user/login/')
# 用户信息页面


@login_judge
def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail
    user_addr = UserInfo.objects.get(id=request.session['user_id']).uaddr

    # 获取最近浏览信息
    goods_ids = request.COOKIES.get('goods_ids', '')
    good_list = []
    if goods_ids != '':
        goods_ids1 = goods_ids.split(',')
        # GoodsInfo.objects.filter(id_in=goods_ids1) # 这么查是按照id排序

        # 和数据库交互了5次，上个只交互了1次
        for good_id in goods_ids1:
            good_list.append(GoodsInfo.objects.get(id=int(good_id)))

    context = {
        'title': '用户中心',
        'user_email': user_email,
        'user_name': request.session['user_name'],
        'user_addr': user_addr,
        'page': 'info',
        'page_name': 1,
        'goods_list': good_list,
    }
    return render(request, 'df_user/user_center_info.html', context)


@login_judge
def order(request):
    uid = request.session['user_id']
    orders = OrderInfo.objects.filter(user_id=uid)
    # 通过orderinfo表的用户名，查detail表的数据
    list_detail = OrderDetailInfo.objects.filter(order__user_id=uid)
    print(list_detail)
    paginator = Paginator(orders, 2)
    # 返回第几页，先填个1吧
    split_page = paginator.page(1)
    context = {
        'title': '用户中心',
        'page': 'order',
        'page_name': 1,
        'orders': orders,
        'split_page':split_page,
        'paginator':paginator,
        'list_detail':list_detail,

    }
    return render(request, 'df_user/user_center_order.html', context)


@login_judge
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.unickname = post.get('unickname')
        user.uaddr = post.get('uaddr')
        user.upostal = post.get('upostal')
        user.uphone = post.get('uphone')
        user.save()
    context = {'title': '用户中心', 'user': user, 'page': 'site', 'page_name': 1}
    return render(request, 'df_user/user_center_site.html', context)
