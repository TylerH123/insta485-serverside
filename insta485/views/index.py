"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
from insta485.model import *


@insta485.app.route("/uploads/<path:name>/")
def retrieveImage(name):
    """Send image link."""
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], name, as_attachment=True
    )


@insta485.app.route('/')
def show_index():
    """Display / route."""
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
        postData = getPostData(postid)
        context["posts"].append(postData)
    return flask.render_template("index.html", **context)


@insta485.app.route('/users/<path:username>/')
def show_user(username):
    """Display /users/<username> route."""
    context = {
        "logname": "awdeorio",
        "username": username,
    }

    userData = getUserData(username)
    context['fullname'] = userData['fullname']

    followers = getUserFollowers(username)
    context['logname_follows_username'] = context['logname'] in followers

    posts = getUserPosts(username)
    context['posts'] = posts
    context['total_posts'] = len(posts)
    context['followers'] = len(getUserFollowers(username))
    context['following'] = len(getUserFollowing(username))

    return flask.render_template("user.html", **context)


@insta485.app.route('/posts/<path:postid>/')
def show_posts(postid):
    """Display /posts/<postid>/ route."""
    post = getPostData(postid)
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
    context = {
        "logname": "awdeorio",
        "followers": []
    }

    logname_following_list = getUserFollowing(context["logname"])
    followers_list = getUserFollowers(username)

    # Get all users following username
    for follower in followers_list:
        user = {
            "username": follower,
            "logname_follows_username": follower in logname_following_list
        }
        user["user_img_url"] = getUserPhoto(follower)
        context["followers"].append(user)

    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<path:username>/following/')
def show_following(username):
    """Display /users/<userid>/following route."""
    context = {
        "logname": "awdeorio",
        "following": []
    }

    logname_following_list = getUserFollowing(context["logname"])
    following_list = getUserFollowing(username)

    # Get all users that username follows
    for following in following_list:
        user = {
            "username": following,
            "user_img_url": "",
            "logname_follows_username": following in logname_following_list
        }
        user["user_img_url"] = getUserPhoto(following)
        context["following"].append(user)

    return flask.render_template("following.html", **context)


@insta485.app.route('/explore/')
def show_explore():
    """Display /explore/ route."""
    context = {
        "logname": "awdeorio",
        "not_following": []
    }

    not_following_list = getUserNotFollowing(context["logname"])

    # Get all users that username follows
    for notfollowing in not_following_list:
        user = {
            "username": notfollowing,
            "user_img_url": "",
        }
        user["user_img_url"] = getUserPhoto(notfollowing)
        context["not_following"].append(user)

    return flask.render_template("explore.html", **context)
