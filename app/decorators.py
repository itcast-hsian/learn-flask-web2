from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):
    def decorator(f):
         
        # 装饰器函数
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                # 报错403
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 如何调用上面的装饰器
def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
                 