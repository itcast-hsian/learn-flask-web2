from flask import render_template, redirect, url_for, current_app, request, flash, make_response
from flask_login import login_required, current_user
from .. import db
from . import post
from .forms import PostForm, CommentForm
from ..models import Permission, Post, Comment
from ..main import main
from ..decorators import permission_required

@post.route('/', methods=['get', 'post'])
def index():
    form = PostForm()
    # type=int 确保参数在无法转换成整数时返回默认值。
    page = request.args.get('page', 1, type=int)

    # 判断是否只显示关注的用户文章
    show_followed = False
    if current_user.is_authenticated:
        # request.cookies是字典
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query

    # page是页数
    # per_page 是数量
    pagination = query.order_by(Post.timestamp.desc()).paginate(
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

@post.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60) # 30天, 不指定浏览器关闭后 cookie 就会过期
    return resp
    
@post.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60) # 30天
    return resp

@post.route('/detail/<int:id>', methods=['GET', 'POST'])
def detail(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                        post=post,
                        author=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been published.")
        return redirect(url_for('.detail', id=post.id, page=-1))
        
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = post.comments.count() // current_app.config['PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config['PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post/detail.html', post=post, form=form, comments=comments, pagination=pagination)

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

@post.route('/moderate', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post/moderate.html', comments=comments, pagination=pagination, page=page)

@post.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))

@post.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))