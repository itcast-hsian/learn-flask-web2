## windows下安装虚拟环境

python3中已经原生支持venv虚拟环境，创建venv：

```js
python -m venv venv
```

激活虚拟环境：

```js
venv\Scripts\activate
```



## pip的使用

查看pip安装过哪些包：

```
pip freeze
```

生成需求文件

```
pip freeze >requirements.txt
```

安装命令

```
pip install -r requirements.txt
```



## 启动项目

·开发环境中启动debug：

```
set FLASK_APP=xxx.py
set FLASK_DEBUG=1
flask run
```



## Jinja2

变量过滤器

| 过滤器名     | 说明                                       |
| ------------ | ------------------------------------------ |
| `safe`       | 渲染值时不转义                             |
| `capitalize` | 把值的首字母转换成大写，其他字母转换成小写 |
| `lower`      | 把值转换成小写形式                         |
| `upper`      | 把值转换成大写形式                         |
| `title`      | 把值中每个单词的首字母都转换成大写         |
| `trim`       | 把值的首尾空格删掉                         |
| `striptags`  | 渲染之前把值中所有的 HTML 标签都删掉       |

条件判断语句：

```
{% if user %}
    Hello, {{ user }}!
{% else %}
    Hello, Stranger!
{% endif %}
```

 `for` 循环

```
<ul>
    {% for comment in comments %}
        <li>{{ comment }}</li>
    {% endfor %}
</ul>
```



## sqlalchemy数据库框架

**常见数据库配置URL：**

| 数据库引擎             | URL                                              |
| ---------------------- | ------------------------------------------------ |
| MySQL                  | mysql://username:password@hostname/database      |
| Postgres               | postgresql://username:password@hostname/database |
| SQLite（Linux，macOS） | sqlite:////absolute/path/to/database             |
| SQLite（Windows）      | sqlite:///c:/absolute/path/to/database           |

> 应用使用的数据库 URL 必须保存到 Flask 配置对象的 `SQLALCHEMY_DATABASE_URI` 键中。Flask-SQLAlchemy 文档还建议把 `SQLALCHEMY_TRACK_MODIFICATIONS` 键设为 `False`



**迁移数据库：**

初始化`flask db init`

(1) 对模型类做必要的修改。

(2) 执行 `flask db migrate -m "initial migration"` 命令，自动创建一个迁移脚本。(更改数据表结构后要执行)

(3) 检查自动生成的脚本，根据对模型的实际改动进行调整。

(4) 把迁移脚本纳入版本控制。

(5) 执行 `flask db upgrade` 命令，把迁移应用到数据库中。



> 对第一个迁移来说，其作用与调用 `db.create_all()` 方法一样。但在后续的迁移中，`flask db upgrade` 命令能把改动应用到数据库中，且不影响其中保存的数据。
>
> aaamwlfobbkcbvbgbe



**`lazy='dynamic`说明：**

指定了 `lazy='dynamic'` 参数，所以返回的查询可接受额外的过滤器。

```
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    classes = db.relationship('Class',
                              secondary=registrations,
                              backref=db.backref('students', lazy='dynamic'),
                              lazy='dynamic')
```

```
student.classes.all()
```

> 方法包含了all(), remove(), filter_by()等方法。



**多对多数据库查询**

```
class User(UserMixin, db.Model):
    # ...
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
```

在这段代码中，`followed` 和 `followers` 关系都定义为单独的一对多关系。注意，为了消除外键间的歧义，定义关系时必须使用可选参数 `foreign_keys` 指定外键。而且，**`db.backref()` 参数并不是指定这两个关系之间的引用关系，而是回引 `Follow` 模型。**

回引中的 `lazy` 参数指定为 `joined`。这种 `lazy` 模式可以实现立即从联结查询中加载相关对象。**例如，如果某个用户关注了 100 个用户，调用 `user.followed.all()` 后会返回一个列表，其中包含 100 个 `Follow` 实例，每一个实例的 `follower` 和 `followed` 回引属性都指向相应的用户。**设定为 `lazy='joined'` 模式，就可在一次数据库查询中完成这些操作。如果把 `lazy` 设为默认值 `select`，那么首次访问 `follower` 和 `followed` 属性时才会加载对应的用户，而且每个属性都需要一个单独的查询，这就意味着获取全部被关注用户时需要增加 100 次额外的数据库查询。



## `itsdangerous`生成确认令牌



1. 使用该类导入生成令牌的方法

   ```
   from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
   ```

2. `dumps()` 方法为指定的数据生成一个加密签名，然后再对数据和签名进行序列化，生成令牌字符串。`expires_in` 参数设置令牌的过期时间，单位为秒。
3. 为了解码令牌，序列化对象提供了 `loads()` 方法，其唯一的参数是令牌字符串。这个方法会检验签名和过期时间，如果都有效，则返回原始数据。如果提供给 `loads()` 方法的令牌无效或是过期了，则抛出异常。



案例：

```python
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db

class User(UserMixin, db.Model):
    # ...
    confirmed = db.Column(db.Boolean, default=False)

    # 生成token
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
	
    # 解密token 
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
```



> 注意加密和解密过程的字符串编码使用
>



## 权限管理

**应用中的各项权限**

| 操作                    | 权限名     | 权限值 |
| ----------------------- | ---------- | ------ |
| 关注用户                | `FOLLOW`   | `1`    |
| 在他人的文章中发表评论` | `COMMENT`  | `2`    |
| 写文章`                 | `WRITE`    | `4`    |
| 管理他人发表的评论`     | `MODERATE` | `8`    |
| 管理员权限`             | `ADMIN`    | `16`   |

> 使用 2 的幂表示权限值有个好处：每种不同的权限组合对应的值都是唯一的，



注意：应该把 Flask 的 `route` 装饰器放在首，比如

```python
@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"
```



## flask-login

**`current_user._get_current_object())`获取user对象:**

```python
current_user.name = form.name.data
current_user.location = form.location.data
current_user.about_me = form.about_me.data

db.session.add(current_user._get_current_object())
```



## 其他

**获取路由参数:**

`type=int` 确保参数在无法转换成整数时返回默认值。

```
request.args.get(参数名, 默认值, type=int)
```





