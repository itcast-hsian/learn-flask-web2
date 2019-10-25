from flask import jsonify
from . import api
from .authentication import auth

@api.route('/posts/')
@auth.login_required
def get_posts():
    return jsonify({
        'title': "abc"
    })