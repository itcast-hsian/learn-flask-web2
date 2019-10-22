from flask import render_template, redirect, url_for, current_app, request, flash
from flask_login import login_required, current_user
from .. import db
from . import post
from .forms import PostForm
from ..models import Permission, Post
from ..main import main

@post.route('/', methods=['get', 'post'])
def index():
    form = PostForm()
    # type=int 确保参数在无法转换成整数时返回默认值。
    page = request.args.get('page', 1, type=int)
    # page是页数
    # per_page 是数量
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['PER_PAGE'],
        error_out=False)
    posts = pagination.items

    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
            author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    return render_template(
        'post/index.html', 
        form=form, 
        posts=posts, 
        pagination=pagination)

@post.route('/post/<int:id>')
def detail(id):
    post = Post.query.get_or_404(id)
    return render_template('post/detail.html', post=post)

@post.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated.')
        return redirect(url_for('.detail', id=post.id))
    form.body.data = post.body
    return render_template('post/edit.html', form=form)