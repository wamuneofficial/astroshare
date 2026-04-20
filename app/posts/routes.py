from flask import render_template, redirect, url_for, flash, abort, request, jsonify
from flask_login import login_required, current_user
from flask_babel import gettext as _
from . import posts
from .forms import PostForm, CommentForm
from ..extensions import db
from ..models import Post, Comment, Like


@posts.route('/posts/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            user_id=current_user.id,
            title=form.title.data,
            content=form.content.data,
            post_type=form.post_type.data,
        )
        db.session.add(post)
        db.session.commit()
        flash(_('flash_post_created'), 'success')
        return redirect(url_for('posts.post_detail', post_id=post.id))
    return render_template('posts/create.html', form=form)


@posts.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if post.is_hidden and not (
        current_user.is_authenticated and
        (current_user.id == post.user_id or current_user.is_admin)
    ):
        abort(404)

    comment_form = CommentForm()
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None)\
                            .order_by(Comment.created_at.asc()).all()

    liked = False
    if current_user.is_authenticated:
        liked = Like.query.filter_by(
            user_id=current_user.id, post_id=post_id
        ).first() is not None

    return render_template('posts/post.html',
                           post=post,
                           comment_form=comment_form,
                           comments=comments,
                           liked=liked)


@posts.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        parent_id = request.form.get('parent_id', type=int)
        comment = Comment(
            post_id=post_id,
            user_id=current_user.id,
            text=form.text.data,
            parent_id=parent_id,
        )
        db.session.add(comment)
        db.session.commit()
        flash(_('flash_comment_added'), 'success')
    return redirect(url_for('posts.post_detail', post_id=post_id))


@posts.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(
        user_id=current_user.id, post_id=post_id
    ).first()

    if existing:
        db.session.delete(existing)
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        post.likes_count += 1
        liked = True

    db.session.commit()
    return jsonify({'liked': liked, 'likes_count': post.likes_count})


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash(_('flash_post_deleted'), 'info')
    return redirect(url_for('main.index'))
