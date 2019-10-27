from flask import jsonify, request, g
from . import api
from .authentication import auth
from ..models import Post
from .. import db

# 参数如果用@api.route('/post/<id>'),那么返回的链接就是 /post/动态参数，否则是问号
@api.route('/post/')
def get_post():
    return jsonify({
        'title': "abc"
    })

@api.route('/posts/')
def get_posts():
    return jsonify({
        'title': "abc"
    })

@api.route('/posts/', methods=['POST'])
@auth.login_required
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())