import os
import sys
import click

from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate

# COV = None
# if os.environ.get('FLASK_COVERAGE'):
# 	import coverage
# 	COV = coverage.coverage(branch=True, include='app/*')
# 	COV.start()

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
	return dict(db=db, User=User, Role=Role)

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
			help='Run tests under code coverage.')
def test(coverage):
	COV = None
	
	"""Run the unit tests."""
	if coverage:
		os.environ['FLASK_COVERAGE'] = '1'
		# 设定完环境变量 FLASK_COVERAGE 后，脚本会重启自身,貌似不支持windows
		# os.execvp(sys.executable, [sys.executable] + sys.argv)
		import coverage
		COV = coverage.coverage(branch=True, include='app/*')
		COV.start()
		
	import unittest
	tests =  unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)
	
	if COV:
		COV.stop()
		COV.save()
		print('Coverage Summary:')
		COV.report()
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print('HTML version: file://%s/index.html' % covdir)
		COV.erase()
