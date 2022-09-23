"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
from insta485 import model


@insta485.app.route("/uploads/<path:name>/")
def retrieve_image(name):
    """Send image link."""
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], name, as_attachment=True
    )


@insta485.app.route('/')
def show_index():
    """Display / route."""
    flask.session['username'] = 'awdeorio'
    if 'username' not in flask.session: 
        return flask.redirect(flask.url_for(show_login)) 
    context = {
        "logname": "awdeorio",
        "posts": []
    }

    # Get all posts
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT postid "
        "FROM posts "
    )
    post_id_list = cur.fetchall()
    # Get all relevant data for each post
    for item in post_id_list:
        postid = item['postid']
        post_data = model.get_post_data(postid)
        context["posts"].append(post_data)
    return flask.render_template("index.html", **context)


@insta485.app.route('/users/<path:username>/')
def show_user(username):
    """Display /users/<username> route."""
    if 'username' not in flask.session: 
        return flask.redirect(flask.url_for(show_login)) 
    context = {
        "logname": "awdeorio",
        "username": username,
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

    return flask.render_template("user.html", **context)


@insta485.app.route('/posts/<path:postid>/')
def show_posts(postid):
    """Display /posts/<postid>/ route."""
    if 'username' not in flask.session: 
        return flask.redirect(flask.url_for(show_login)) 
    post = model.get_post_data(postid)
    context = {
        "logname": "awdeorio",
        "postid": postid
    }

    for entry in post:
        context[entry] = post[entry]

    return flask.render_template("post.html", **context)


@insta485.app.route('/users/<path:username>/followers/')
def show_followers(username):
    """Display /users/<username>/follower route."""
    if 'username' not in flask.session: 
        return flask.redirect(flask.url_for(show_login)) 
    context = {
        "logname": "awdeorio",
        "followers": []
    }

    logname_following_list = model.get_user_following(context["logname"])
    followers_list = model.get_user_followers(username)

    # Get all users following username
    for follower in followers_list:
        user = {
            "username": follower,
            "logname_follows_username": follower in logname_following_list
        }
        user["user_img_url"] = model.get_user_photo(follower)
        context["followers"].append(user)

    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<path:username>/following/')
def show_following(username):
    """Display /users/<userid>/following route."""
    if 'username' not in flask.session: 
        return flask.redirect(flask.url_for(show_login)) 
    context = {
        "logname": "awdeorio",
        "following": []
    }

    logname_following_list = model.get_user_following(context["logname"])
    following_list = model.get_user_following(username)

    # Get all users that username follows
    for following in following_list:
        user = {
            "username": following,
            "user_img_url": "",
            "logname_follows_username": following in logname_following_list
        }
        user["user_img_url"] = model.get_user_photo(following)
        context["following"].append(user)

    return flask.render_template("following.html", **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    if 'username' not in flask.session: 
        return flask.redirect(flask.url_for(show_login)) 
    context = {
        "logname": "awdeorio",
        "not_following": []
    }

    not_following_list = model.get_user_not_following(context["logname"])

    # Get all users that username follows
    for notfollowing in not_following_list:
        user = {
            "username": notfollowing,
            "user_img_url": "",
        }
        user["user_img_url"] = model.get_user_photo(notfollowing)
        context["not_following"].append(user)

    return flask.render_template("explore.html", **context)

@insta485.app.route('/accounts/login/')
def show_login(): 
    """Display login route."""
    if 'username' in flask.session:
        return flask.redirect(flask.url_for(show_index))
    flask.session['username'] = flask.request.form['username']
    return flask.render_template("explore.html")
