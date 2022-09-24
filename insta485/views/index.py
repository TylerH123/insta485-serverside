"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
from insta485 import model


@insta485.app.route('/uploads/<path:name>')
def retrieve_image(name):
    """Send image link."""
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], name, as_attachment=True
    )


@insta485.app.route('/')
def show_index():
    """Display / route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    username = flask.session['login']
    context = {
        'logname': username,
        'posts': []
    }
    # Get all posts
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT postid '
        'FROM posts '
    )
    post_id_list = cur.fetchall()
    # Get all relevant data for each post
    for item in post_id_list:
        postid = item['postid']
        post_data = model.get_post_data(postid)
        post_data['not_liked'] = model.user_like_post(username, postid)
        context['posts'].append(post_data)
    return flask.render_template('index.html', **context)


@insta485.app.route('/users/<path:username>/')
def show_user(username):
    """Display /users/<username> route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    username = flask.session['login']
    context = {
        'logname': username,
        'username': username,
    }
    user_data = model.get_user_data(username)
    context['fullname'] = user_data['fullname']

    followers = model.get_user_followers(username)
    context['logname_follows_username'] = context['logname'] in followers

    posts = model.get_user_posts(username)
    context['posts'] = posts
    context['total_posts'] = len(posts)
    context['followers'] = len(followers)
    context['following'] = len(model.get_user_following(username))

    return flask.render_template('user.html', **context)


@insta485.app.route('/posts/<path:postid>/')
def show_posts(postid):
    """Display /posts/<postid>/ route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    username = flask.session['login']
    post = model.get_post_data(postid)
    context = {
        'logname': username,
        'postid': postid
    }

    for entry in post:
        context[entry] = post[entry]
    context['not_liked'] = model.user_like_post(username, postid)
    return flask.render_template('post.html', **context)


@insta485.app.route('/users/<path:username>/followers/')
def show_followers(username):
    """Display /users/<username>/follower route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    username = flask.session['login']
    context = {
        'logname': username,
        'followers': []
    }

    logname_following_list = model.get_user_following(context['logname'])
    followers_list = model.get_user_followers(username)

    # Get all users following username
    for follower in followers_list:
        user = {
            'username': follower,
            'logname_follows_username': follower in logname_following_list
        }
        user['user_img_url'] = model.get_user_photo(follower)
        context['followers'].append(user)

    return flask.render_template('followers.html', **context)


@insta485.app.route('/users/<path:username>/following/')
def show_following(username):
    """Display /users/<userid>/following route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    username = flask.session['login']
    context = {
        'logname': username,
        'following': []
    }
    logname_following_list = model.get_user_following(context['logname'])
    following_list = model.get_user_following(username)
    # Get all users that username follows
    for following in following_list:
        user = {
            'username': following,
            'user_img_url': '',
            'logname_follows_username': following in logname_following_list
        }
        user['user_img_url'] = model.get_user_photo(following)
        context['following'].append(user)

    return flask.render_template('following.html', **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    username = flask.session['login']
    context = {
        'logname': username,
        'not_following': []
    }
    not_following_list = model.get_user_not_following(context['logname'])
    # Get all users that username follows
    for notfollowing in not_following_list:
        user = {
            'username': notfollowing,
            'user_img_url': '',
        }
        user['user_img_url'] = model.get_user_photo(notfollowing)
        context['not_following'].append(user)

    return flask.render_template('explore.html', **context)


@insta485.app.route('/accounts/login/')
def show_login():
    """Display login route."""
    if 'login' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    context = {
        'login': True
    }
    return flask.render_template('login.html', **context)


@insta485.app.route('/accounts/logout/', methods=["POST"])
def show_logout():
    """Display logout route."""
    flask.session.pop('login')
    return flask.redirect(flask.url_for("show_login"))


@insta485.app.route('/accounts/create/')
def show_create():
    """Display create account route."""
    if 'login' in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    context = {
        'login': True
    }
    return flask.render_template('create.html', **context)


@insta485.app.route('/accounts/edit/')
def show_edit():
    """Display edit account route."""
    if 'login' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))
    username = flask.session['login']
    context = {
        'logname': username,
        'user_filename': model.get_user_photo(username),
        **model.get_user_data(username),
    }
    return flask.render_template('edit.html', **context)


@insta485.app.route('/accounts/', methods=['POST'])
def update_accounts():
    """Display login route."""
    operation = flask.request.form['operation']
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    else:
        redirect = flask.url_for('show_index')
    if operation == 'login':
        if 'password' not in flask.request.form or \
           'username' not in flask.request.form: 
            return flask.abort(400)
        password = flask.request.form['password']
        username = flask.request.form['username']
        if username =='' or password == '':
            return flask.abort(400)
        data = model.get_user_data(username)
        if data is None:
            return flask.abort(403)
        hashed_pass = model.hash_password(password,
                                          data['password'].split('$')[1])
        if data['password'] != hashed_pass:
            return flask.abort(403)
        flask.session['login'] = username
        return flask.redirect(redirect)
    if operation == 'create':
        data = []
        fields = ['username', 'fullname', 'email', 'file', 'password']
        for field in fields:
            if field == 'file':
                fileobj = flask.request.files['file']
                data_field = model.upload_file(fileobj)
            elif field == 'password':
                password = flask.request.form['password']
                data_field = model.hash_password(password)
            else:
                data_field = flask.request.form[field]
                if data_field == '':
                    flask.abort(400)
            data.append(data_field)
        existing_username = model.get_user_data(data[0])
        if existing_username is not None:
            flask.abort(409)
        model.put_new_user(data)
        flask.session['login'] = data[0]
        return flask.redirect(redirect)
    if operation == 'edit_account':
        data = []
        fields = ['username', 'fullname', 'email', 'file']
        for field in fields:
            if field == 'file':
                fileobj = flask.request.files['file']
                data_field = model.upload_file(fileobj)
            else:
                data_field = flask.request.form[field]
                if data_field == '':
                    flask.abort(400)
            data.append(data_field)
        model.edit_user_profile(data)
        return flask.redirect(redirect)


@insta485.app.route('/likes/', methods=['POST'])
def update_likes():
    """Display likes route."""
    operation = flask.request.form['operation']
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    else:
        redirect = flask.url_for('show_index')
    if operation == 'like':
        username = flask.session['login']
        postid = flask.request.form['postid']
        if model.user_like_post(username, postid):
            model.update_likes(True, username, postid)
        else:
            flask.abort(409)
        return flask.redirect(redirect)
    if operation == 'unlike':
        username = flask.session['login']
        postid = flask.request.form['postid']
        if not model.user_like_post(username, postid):
            model.update_likes(False, username, postid)
        else:
            flask.abort(409)
        return flask.redirect(redirect)


@insta485.app.route('/comments/', methods=['POST'])
def update_comments():
    """Display comments route."""
    operation = flask.request.form['operation']
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    else:
        redirect = flask.url_for('show_index')
    if operation == 'create':
        username = flask.session['login']
        postid = flask.request.form['postid']
        text = flask.request.form['text']
        if text is None or text == "":
            flask.abort(400)
        model.create_comments(True, username, postid, text)
        return flask.redirect(redirect)
    if operation == 'delete':
        username = flask.session['login']
        commentid = flask.request.form['commentid']
        comment_owner = model.get_comment_owner(commentid)['owner']
        if username == comment_owner:
            model.delete_comment(commentid)
        else:
            flask.abort(403)
        return flask.redirect(redirect)


@insta485.app.route('/posts/', methods=['POST'])
def update_posts():
    """Display posts route."""
    operation = flask.request.form['operation']
    if 'target' in flask.request.args:
        redirect = flask.request.args['target']
    else:
        redirect = flask.url_for('show_index')
    if operation == 'create':
        return flask.redirect(redirect)
    if operation == 'delete':
        username = flask.session['login']
        postid = flask.request.form['postid']
        data = model.get_post_data(postid)
        filename = model.get_post_filename(postid)
        post_owner = data['owner']
        if username == post_owner:
            model.delete_post(postid, filename)
        else:
            flask.abort(403)
        return flask.redirect(redirect)
    