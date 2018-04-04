import os
import random

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
    n = random.randint(0, 1000000)
    # create an order
    print(n)
    result = alipay.api_alipay_trade_precreate(
        subject="水杯",
        out_trade_no=str(n),
        total_amount=100,
        timeout_express="10m"
    )
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(result["qr_code"])
    qr.make(fit=True)
    img = qr.make_image()
    img.save(str(n)+'.png')
    print(img)
    # check order status
    paid = False
    for i in range(10):
        # check every 3s, and 10 times in all
        print("now sleep 3s")
        time.sleep(5)
        result = alipay.api_alipay_trade_query(out_trade_no=str(n))
        print(result)
        if result.get("trade_status", "") == "TRADE_SUCCESS":
            paid = True
            print("success")
            break
        print("not paid...")

    # order is not paid in 30s , cancel this order
    if paid is False:
        alipay.api_alipay_trade_cancel(out_trade_no=str(n))


order_pay()
