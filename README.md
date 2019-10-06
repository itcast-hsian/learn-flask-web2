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

常见数据库配置URL：

| 数据库引擎             | URL                                              |
| ---------------------- | ------------------------------------------------ |
| MySQL                  | mysql://username:password@hostname/database      |
| Postgres               | postgresql://username:password@hostname/database |
| SQLite（Linux，macOS） | sqlite:////absolute/path/to/database             |
| SQLite（Windows）      | sqlite:///c:/absolute/path/to/database           |

> 应用使用的数据库 URL 必须保存到 Flask 配置对象的 `SQLALCHEMY_DATABASE_URI` 键中。Flask-SQLAlchemy 文档还建议把 `SQLALCHEMY_TRACK_MODIFICATIONS` 键设为 `False`



**迁移数据库：**

(1) 对模型类做必要的修改。

(2) 执行 `flask db migrate -m "initial migration"` 命令，自动创建一个迁移脚本。

(3) 检查自动生成的脚本，根据对模型的实际改动进行调整。

(4) 把迁移脚本纳入版本控制。

(5) 执行 `flask db upgrade` 命令，把迁移应用到数据库中。



> 对第一个迁移来说，其作用与调用 `db.create_all()` 方法一样。但在后续的迁移中，`flask db upgrade` 命令能把改动应用到数据库中，且不影响其中保存的数据。
>
> hhhhbxiwktqemkcbdd













