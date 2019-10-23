from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
from . import login_manager
from . import db

class Permission:
	FOLLOW = 1
	COMMENT = 2
	WRITE = 4
	MODERATE = 8
	ADMIN = 16

# dynamic（不加载记录，但提供加载记录的查询,返回一个尚未执行的查询）
class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	# index表示只能有一类角色（User）的这个字段可以设为 True，其他角色都应该设为 False。
	# 为了提升搜索的速度。
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)
	users = db.relationship('User', backref='role', lazy='dynamic')

	def __init__(self, **kwargs):
		super(Role, self).__init__(**kwargs)
		if self.permissions is None:
			self.permissions = 0

	def __repr__(self):
		return '<Role %r>' % self.name

	def add_permission(self, perm):
		if not self.has_permission(perm):
			self.permissions += perm

	def remove_permission(self, perm):
		if self.has_permission(perm):
			self.permissions -= perm

	def reset_permissions(self):
		self.permissions = 0

	def has_permission(self, perm):
		# 位运算，self.permissions是权限数字相加是单数
		# perm是否1,2,4..二次幂，比如 7 & 4得到4，所以该用户包含了4的权限
		return self.permissions & perm == perm

	@staticmethod
	def insert_roles():
		roles = {
			'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
			'Moderator': [Permission.FOLLOW, Permission.COMMENT,Permission.WRITE, 
					Permission.MODERATE],
			'Administrator': [Permission.FOLLOW, Permission.COMMENT,
								Permission.WRITE, Permission.MODERATE,
		                        Permission.ADMIN],
		}
		default_role = 'User'
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.reset_permissions()
			for perm in roles[r]:
				role.add_permission(perm)
			role.default = (role.name == default_role)
			db.session.add(role)
		db.session.commit()

# 主要给current_user用的，因为未登陆的状态下current_user会默认为anonymous_user
class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False

login_manager.anonymous_user = AnonymousUser

class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id')	, primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id')	, primary_key=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	avatar = db.Column(db.String(64))
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	confirmed = db.Column(db.Boolean, default=False)

	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	
	# Follow.follower_id 是关注的一方,user.followed会返回Follow的查询， follower_id是主键
	# db.backref() 回引 Follow 模型, 
	# ascade 参数配置在父对象上执行的操作对相关对象的影响,比如在删除对象时，删除记录后正确的行为应该是把指向该记录的实体也删除，这样才能有效销毁连接。这就是层叠选项值 delete-orphan 的作用。
	followed = db.relationship('Follow',
		foreign_keys=[Follow.follower_id],
		backref=db.backref('follower', lazy='joined'),
		lazy='dynamic',
		cascade='all, delete-orphan')
		
	# Follow.followed_id 是被关注的一方
	followers = db.relationship('Follow',
		foreign_keys=[Follow.followed_id],
		backref=db.backref('followed', lazy='joined'),
		lazy='dynamic',
		cascade='all, delete-orphan')

	# dynamic（不加载记录，但提供加载记录的查询） user.posts返回查询语句
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	comments = db.relationship('Comment', backref='author', lazy='dynamic')

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['MAIL_SENDER']:
				self.role = Role.query.filter_by(name='Administrator').first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()

	def can(self, perm):
		return self.role is not None and self.role.has_permission(perm)

	def is_administrator(self):
		return self.can(Permission.ADMIN)

	def generate_confirmation_token(self, expiration=3600):
		# 方法生成一个令牌，有效期默认为一小时
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id}).decode('utf-8')

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

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id}).decode('utf-8')

	@property
	def password(self):
		raise AttributeError('paassword is not a redable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
	
	@staticmethod
	def reset_password(token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		# 从token中解析出id
		user = User.query.get(data.get('reset'))	
		if user is None:
			return False
		user.password = new_password
		db.session.add(user)
		return True	

	def generate_email_change_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps(
			 {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		if data.get('change_email') != self.id:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email = new_email
		db.session.add(self)
		return True

	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)
		db.session.commit()

	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)

	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)
	
	def is_following(self, user):
		if user.id is None:
			return False
		return self.followed.filter_by(
			followed_id=user.id
		).first() is not None
	
	def is_followed_by(self, user):
		if user.id is None:
			return False
		return self.followers.filter_by(
			follower_id=user.id).first() is not None

	@property
	def followed_posts(self):
		# 先找出所有被关注过的人的文章，再从文章中过滤出关注者是当前用户，注意该属性返回的是查询
		return Post.query.join(Follow, Follow.followed_id == Post.author_id) \
			.filter(Follow.follower_id == self.id)

	def __repr__(self):
		return '<User %r>' % self.username

# 该方法会获取已登录的用户，应该会把当前用户写入到session，写入到current_user
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	comments = db.relationship('Comment', backref='post', lazy="dynamic")

class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

	# 原本是要过滤markdown的方法的
	@staticmethod
	def on_changed_body(self, value, oldvalue, initiator):
		self.body_html = value

db.event.listen(Comment.body, 'set', Comment.on_changed_body)