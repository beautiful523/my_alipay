import os

import time

from alipay import AliPay
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# 这是两个秘钥的路径
app.config["app_private_key_path"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "keys/app_private_key.pem")
app.config["alipay_public_key_path"] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "keys/alipay_public_key.pem")


@app.route('/', methods=["GET"])
def pay():
    return render_template("pay.html")


@app.route('/order_pay/', methods=["GET"])
def order_pay():
    # 实例化Alipay，并加上alipay需要的一些参数
    alipay = AliPay(
        appid="2016090800465324",
        app_notify_url='http://39.106.96.112',
        app_private_key_path=app.config["app_private_key_path"],
        alipay_public_key_path=app.config["alipay_public_key_path"],
        sign_type="RSA2",
        debug=True,
    )

    # 加上订单的参数
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no="12345678123",  # 订单id
        total_amount="99",  # 实付款
        subject='水杯',  # 订单标题
        return_url='https://www.baidu.com',
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 发送地址
    pay_url = "https://openapi.alipaydev.com/gateway.do" + '?' + order_string
    return jsonify({'pay_url': pay_url, 'message': 'OK'})


@app.route('/check_pay/', methods=["GET"])
def check_pay():
    order_id = "12345678123"
    alipay = AliPay(
        appid="2016090800465324",  # 应用appid
        app_notify_url='http://39.106.96.112',  # 默
        app_private_key_path=app.config["app_private_key_path"],
        alipay_public_key_path=app.config["alipay_public_key_path"],
        sign_type="RSA2",  # RSA或者 RSA2
        debug=True  # 默认False
    )

    while True:
        result = alipay.api_alipay_trade_query(order_id)
        # 接口是否调用成功
        code = result.get('code')
        print(code)
        print(result.get('trade_status'))

        if code == '10000' and result.get('trade_status') == "TRADE_SUCCESS":
            # 用户支付成功
            # 更新订单支付状态
            # order.status = 2  # 待发货
            # 填写支付宝交易号
            # order.trade_id = result.get('trade_no')
            # order.save()
            # 返回结果
            return jsonify({'res': 3, 'message': '支付成功'})
        elif (code == '10000' and result.get('trade_status') == 'WAIT_BUYER_PAY') or code == '40004':
            # 继续查询交易结果
            # 1.等待用户进行支付
            # 2.支付交易订单还未生成
            time.sleep(5)
            continue
        else:
            # 支付出错
            return jsonify({'res': 4, 'errmsg': '支付失败'})
app.run()