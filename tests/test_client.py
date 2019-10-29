import unittest
from app import create_app, db
from app.models import User, Role
import re

class FlaskClientTestCase(unittest.TestCase):
    # 测试设置
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    ## 测试卸载
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # 默认情况下 get_data() 返回的响应主体是一个字节数组，传入参数 as_text=True 后得到的是一个更易于处理的字符串。
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        response = self.client.post('/auth/register', data={
            'email': 'test@qq.com',
            'username': 'test',
            'password': '123',
            'password2': '123'
        })
        # 因为注册成功后重定向，redirect(url_for('main.index'))，状态码是302
        self.assertEqual(response.status_code, 302)
        
        # 使用新注册的账户登录
        response = self.client.post('/auth/login', data={
            'email': 'test@qq.com',
            'password': '123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # 避免空格影响测试结果，我们使用正则表达式。
        self.assertTrue(re.search('test', response.get_data(as_text=True)))
        
        
        # 退出， follow_redirects=True，让测试客户端自动向重定向的 URL 发起 GET 请求
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('You have been logged out' in response.get_data(as_text=True))

    