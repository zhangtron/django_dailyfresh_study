from django.shortcuts import render, redirect
from df_order.models import *
from django.db import transaction
import datetime
from decimal import Decimal
from df_cart.models import *
from df_user.user_decorator import login_judge
from django.db.models import Q
# Create your views here.


@login_judge
def order(request):
    gid = [int(x) for x in request.GET.getlist('id')]
    uid = request.session['user_id']
    carts = CartInfo.objects.filter(user_id=uid)
    # filter_fields = [Q(**{CartInfo.id: id}) for id in gid]
    print([e.id for e in carts])
    context = {
        'page_name': 1,
        'title': '提交订单',
        'carts': carts,
        'id_list': gid,
    }
    return render(request, 'df_order/order.html', context)


@transaction.atomic()
@login_judge
def order_handle(request):
    # 先保存一个点，未来可以回退到这个点
    tran_ids = transaction.savepoint()
    # 接收购物车编号
    cart_ids = request.GET.get('cart_ids')
    try:
        # 创建订单对象
        order = OrderInfo()
        now = datetime.datetime.now()
        uid = request.session['user_id']
        order.oid = '%s%d' % (now.strftime('%Y%m%d%H%S'), uid)
        order.user_id = uid
        order.odate = now
        order.ototal = Decimal(request.GET.get('total'))
        order.save()
        cart_ids1 = [int(item) for item in cart_ids]
        for id1 in cart_ids1:
            detail = OrderDetailInfo()
            detail.order = order
            # 查询购物车信息
            cart = CartInfo.objects.get(id=id1)
            # 判断商品库存
            goods = cart.goods
            if goods.ginventory >= cart.count:  # 如果库存大于购买数量
                # 减少商品库存
                goods.ginventory = cart.goods.ginventory - cart.count
                goods.save()

                # 保存详单
                detail.goods_id = goods.id
                detail.price = goods.gprice
                detail.count = cart.count
                detail.save()

                # 删除购物车数据
                cart.delete()
            else:
                # 回退到保存的点，所有数据库更改操作失效
                transaction.savepoint_rollback(tran_ids)
                return redirect('/cart/')

        # 保存提交
        transaction.savepoint_commit(tran_ids)
    except Exception as e:
        print('=' * 20 + str(e))
        transaction.savepoint_rollback(tran_ids)

    return redirect('/user/order/')


@login_judge
def pay(request, oid):
    order = OrderInfo.objects.get(oid=oid)
    order.oIsPay = True
    order.save()
    context = {'order': order}
    return render(request, 'df_order/pay.html', context)
