from django.shortcuts import render
from django.core.paginator import Paginator, Page
from df_goods.models import *
from django.http import request

# Create your views here.
def index(request):
    # 查询各分类的最新4条、最热4条数据
    typelist = TypeInfo.objects.all()
    type0 = typelist[0].goodsinfo_set.order_by('-id')[0:4]
    type01 = typelist[0].goodsinfo_set.order_by('-gclick')[0:4]
    type1 = typelist[1].goodsinfo_set.order_by('-id')[0:4]
    type11 = typelist[1].goodsinfo_set.order_by('-gclick')[0:4]
    type2 = typelist[2].goodsinfo_set.order_by('-id')[0:4]
    type21 = typelist[2].goodsinfo_set.order_by('-gclick')[0:4]
    type3 = typelist[3].goodsinfo_set.order_by('-id')[0:4]
    type31 = typelist[3].goodsinfo_set.order_by('-gclick')[0:4]
    type4 = typelist[4].goodsinfo_set.order_by('-id')[0:4]
    type41 = typelist[4].goodsinfo_set.order_by('-gclick')[0:4]
    type5 = typelist[5].goodsinfo_set.order_by('-id')[0:4]
    type51 = typelist[5].goodsinfo_set.order_by('-gclick')[0:4]
    context = {
        'title':'首页','guest_cart':1,
        'type0':type0, 'type01':type01,
        'type1':type1, 'type11':type11,
        'type2':type2, 'type02':type21,
        'type3':type3, 'type03':type31,
        'type4':type4, 'type04':type41,
        'type5':type5, 'type05':type51,
    }
    return render(request, 'df_goods/index.html', context)

def list(request,tid, pindex, sort):
    typeinfo = TypeInfo.objects.get(pk=int(tid))
    # 查询最新的两条，放新品推荐
    news = typeinfo.goodsinfo_set.order_by('-id')[0:2]
    if sort == '1': # 默认最新
        goods_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-id')
    elif sort == '2': # 按价格
        goods_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-gprice')
    elif sort == '3': # 按人气，点击量
        goods_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-gclick')
    paginator = Paginator(goods_list,10)
    page = paginator.page(int(pindex))

    context = {
        'guest_cart':1,
        'title': typeinfo.ttitle,
        'page':page,
        'paginator':paginator,
        'typeinfo':typeinfo,
        'sort':sort,
        'news':news,
    }
    return render(request, 'df_goods/list.html', context)

def detail(request, id):
    # 点击量加1
    goods = GoodsInfo.objects.get(pk=int(id))
    goods.gclick = goods.gclick + 1
    goods.save()

    # 新品推荐
    news = goods.gtype.goodsinfo_set.order_by('-id')[0:2]
    context = {
        'title': goods.gtype.ttitle,
        'guest_cart':1,
        'g':goods,
        'news':news,
        'id':id
    }
    response = render(request, 'df_goods/detail.html', context)

    # 最近浏览，在用户中心显示
    # 第一次没有cookie 默认为空字符串
    goods_ids = request.COOKIES.get('goods_ids', '')
    goods_id = '%d'%goods.id
    if goods_ids != '':
        goods_ids1 = goods_ids.split(',')

        # 如果已经记录就删除
        if goods_ids1.count(goods_id) >= 1:
            goods_ids1.remove(goods_id)

        # 将新浏览id插入cookie列表第一个
        goods_ids1.insert(0, goods_id)

        # 如果cookie列表大于6，就只取5个
        if len(goods_ids1) >= 6:
            del goods_ids1[5]

        # 拼接逗号
        goods_ids = ','.join(goods_ids1)
    else:
        goods_ids = goods_id

    # 写入cookie值
    response.set_cookie('goods_ids', goods_ids)


    return response