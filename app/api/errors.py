from flask import request, render_template, jsonify
from ..main import main
from ..exceptions import ValidationError
from . import api

@main.app_errorhandler(404)
def page_not_found(e):
    # 根据请求期望的响应格式返回不同的结果
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404

def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403  
    return response

def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response

# 全局有效,省去每个api接口去捕获错误, ValidationError是自定义的
@api.errorhandler(ValidationError)
def validation_error(e):
    # 只要ValidationError错误触发就执行bad_request
    return bad_request(e.args[0])