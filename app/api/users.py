from .authentication import auth
from . import api

@api.route('/user/')
@auth.login_required
def get_user():
    pass

@api.route('/user_posts/')
def get_user_posts():
    pass

@api.route('/user_followed_posts/')
def get_user_followed_posts():
    pass