from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
auth = HTTPBasicAuth() # HTTPTokenAuth
from flask import jsonify, g, request

from .errors import unauthorized, forbidden
from ..models import User
from . import api

# auth必须要实现的装饰器，return True表示验证通过, nestjs也有这玩意
# 问题参数从头信息获取的，头信息用什么格式传呢?
@auth.verify_password
def verify_password(email_or_token, password):
    print(email_or_token)
    if email_or_token == '':
        return False
    
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None

    user = User.query.filter_by(email = email).first()
    if not user:
        return False
    # 写入上下文
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

# 全部都要验证
# @api.before_request
# @auth.login_required
# def before_request():
#     pass

@api.route('/tokens/', methods=['POST'])
def get_token():
    try:
        email, password = request.form['email'], request.form['password']
        user = User.query.filter_by(email = email).first()
        if not user:
            return unauthorized('Invalid email')
        if user.verify_password(password):
            g.current_user = user
        else:
            return unauthorized('Invalid password')
        
        # 这里是必须通过flask-login登录后的用户才能生成，不是通过rest传递过来用户名密码
        # if g.current_user.is_anonymous or g.token_used:
        #     return unauthorized('Invalid credentials')
        return jsonify({
            'token': g.current_user.generate_auth_token(expiration=3600), 
            'expiration': 3600})
    except Exception as e:
        print(e)
        return unauthorized('Invalid credentials')