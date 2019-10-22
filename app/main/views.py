from flask import render_template, session, redirect, url_for, current_app, flash, request
from flask_login import login_required, current_user
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role, Permission
from ..email import send_email
from ..decorators import admin_required, permission_required

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

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.location = form.location.data
		current_user.about_me = form.about_me.data

		db.session.add(current_user._get_current_object())
		db.session.commit()

		flash('Your profile has been updated.')
		return redirect(url_for('.user', username=current_user.username))
	form.name.data = current_user.name
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user = User.query.get_or_404(id)
	form = EditProfileAdminForm(user=user)
	if form.validate_on_submit():
		user.email = form.email.data
		user.username = form.username.data
		user.confirmed = form.confirmed.data
		user.role = Role.query.get(form.role.data)
		user.name = form.name.data
		user.location = form.location.data
		user.about_me = form.about_me.data
		db.session.add(user)
		db.session.commit()
		flash('The profile has been updated.')
		return redirect(url_for('.user', username=user.username))
	form.email.data = user.email
	form.username.data = user.username
	form.confirmed.data = user.confirmed
	form.role.data = user.role_id
	form.name.data = user.name
	form.location.data = user.location
	form.about_me.data = user.about_me
	return render_template('edit_profile.html', form=form, user=user)
	
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	
	if current_user.is_following(user):
		flash('You are already following this user.')
		return redirect(url_for('.user', username=username))
	
	current_user.follow(user)
	db.session.commit()
	flash('You are now following %s.' % username)
	return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))

	if current_user.is_following(user):
		current_user.unfollow(user)
		db.session.commit()
		flash('You are now unfollowing %s.' % username)
	return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
def followers(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.paginate(
		page, per_page=current_app.config['PER_PAGE'],
		error_out=False)
	follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
	return render_template('followers.html', 
						user=user, 								
						title="谁关注了 %s." % user.username,
                        endpoint='.followers', pagination=pagination,
                        follows=follows)

@main.route('/followed_by/<username>')
def followed_by(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid user.')
		return redirect(url_for('.index'))
	
	page = request.args.get('page', 1, type=int)
	pagination = user.followed.paginate(
		page, per_page=current_app.config['PER_PAGE'],
		error_out=False)
	follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
	return render_template('followers.html', 
						user=user, 								
						title="%s 关注了谁" % user.username,
                        endpoint='.followed_by', 
						pagination=pagination,
                        follows=follows)