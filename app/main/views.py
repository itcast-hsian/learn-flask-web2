from flask import render_template, session, redirect, url_for, current_app
from . import main
from .forms import NameForm
from .. import db
from ..models import User
from ..email import send_email

@main.route('/', methods=['GET', 'POST'])
def index():
	name = None
	form = NameForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()

		if current_app.config['MAIL_PASSWORD']:
			send_email('541510140@qq.com', 
				'New User',
				'mail/new_user', 
				user=user)
		
		if user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			db.session.commit()
			session['known'] = False
		else:
			session['known'] = True
		session['name'] = form.name.data
		form.name.data = ''
		# flash(session['name'])
		return redirect(url_for('.index'))
	return render_template('index.html', 
		form=form, 
		name=session.get('name'),
		known=session.get('known', False))