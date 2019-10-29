import unittest
import json
from app import create_app, db
from app.models import User, Role
from base64 import b64encode


class APITestCase(unittest.TestCase):
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

    def get_api_headers(self, username, password):

        response = self.client.post(
            '/api/v1/tokens/',
            headers = {'Content-Type': 'application/json'},
            data = json.dumps({
                'email': username,
                'password': password
            })
        )
        #json_response = json.loads(response.data.decode('utf-8'))
        #token = json_response.get('token')

        # son.dumps() 编码 、 json.loads 解码
        json_response = json.loads(response.get_data(as_text=True))
        token = json_response['token']

        self.assertIsNotNone(token)

        return {
            # 'Authorization': 'Bearer ' + b64encode(
            #         (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_no_auth(self):
        response = self.client.post('/api/v1/posts/', content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_posts(self):
        # 添加一个用户
        r = Role.query.filter_by(name='User').first()
        self.assertIsNotNone(r)

        u = User(email='test@qq.com', password='123', confirmed=True, role=r)
        db.session.add(u)
        db.session.commit()

        # 写一篇文章
        response = self.client.post(
            '/api/v1/posts/',
            headers = self.get_api_headers('test@qq.com', '123'),
            data = json.dumps({'body': 'test post body'})
        )
        self.assertEqual(response.status_code, 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)

        # 获取刚发布的文章
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual('http://localhost' + json_response['url'], url)
        self.assertEqual(json_response['body'], 'test post body')