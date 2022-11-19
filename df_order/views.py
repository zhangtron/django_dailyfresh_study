from django.shortcuts import render,redirect
from df_order.models import *
from django.db import transaction
import datetime
from decimal import Decimal
from df_cart.models import *
# Create your views here.

def order(request):
   return render(request,'df_order/order.html')


@transaction.atomic()
def order_handle(request):
    # 先保存一个点，未来可以回退到这个点
    tran_ids = transaction.savepoint()
    # 接收购物车编号
    cart_ids = request.POST.get('cart_ids')
    try:
        # 创建订单对象
        order = OrderInfo()
        now = datetime.now()
        uid = request.session['user_id']
        order.oid = '%s%d'%(now.strftime('%Y%m%d%H%S'), uid)
        order.user_id = uid
        order.odate= now
        order.ototal = Decimal(request.POST.get('total'))
        order.save()
        cart_ids1 = [int(item) for item in cart_ids.split(',')]
        for id1 in cart_ids1:
            detail = OrderDetailInfo()
            detail.order = order
            # 查询购物车信息
            cart = CartInfo.objects.get(id=id1)
            # 判断商品库存
            goods = cart.goods
            if goods.gkucun >= cart.count: # 如果库存大于购买数量
                # 减少商品苦楚
                goods.gkucun = cart.goods.gkucun - cart.count
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
        print('='*20 + e)
        transaction.savepoint_rollback()

    return redirect('/user/order/')

def pay(request,oid):
    order = OrderInfo.objects.get(oid=oid)
    order.oIsPay = True
    order.save()
    context = {'order':order}
    return render(request, 'df_order/pay.html', context)