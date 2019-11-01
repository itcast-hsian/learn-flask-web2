import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

	MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
	MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '407775611@qq.com')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	MAIL_SENDER = '407775611@qq.com'
	MAIL_SUBJECT_PREFIX = 'Learn Flask'

	SQLALCHEMY_TRACK_MODIFICATIONS = False

	PER_PAGE = 2

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
		'sqlite://'
	# 禁用表单 CSRF 保护机制
	WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'data.sqlite')

	@classmethod
	def init_app(cls, app):
		Config.init_app(app)

		# 出错时邮件通知管理员
		import logging
		from logging.handlers import SMTPHandler
		credentials = None
		secure = None

		if getattr(cls, 'MAIL_USERNAME', None) is not None:
			credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
			if getattr(cls, 'MAIL_USE_TLS', None):
				secure = ()
		mail_handler = SMTPHandler(
			mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
			fromaddr=cls.MAIL_SENDER,
			toaddrs=[cls.MAIL_USERNAME],
			subject=cls.MAIL_SUBJECT_PREFIX + ' Application Error',
			credentials=credentials,
			secure=secure
		)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)

config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,

	'default': DevelopmentConfig
}