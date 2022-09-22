"""Insta485 model (database) API."""
import sqlite3
import flask
import insta485
import arrow


def dict_factory(cursor, row):
    """Convert database row objects to a dictionary keyed on column name.

    This is useful for building dictionaries which are then used to render a
    template.  Note that this would be inefficient for large queries.
    """
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_db():
    """Open a new database connection."""
    if 'sqlite_db' not in flask.g:
        db_filename = insta485.app.config['DATABASE_FILENAME']
        flask.g.sqlite_db = sqlite3.connect(str(db_filename))
        flask.g.sqlite_db.row_factory = dict_factory
        # Foreign keys have to be enabled per-connection.  This is an sqlite3
        # backwards compatibility thing.
        flask.g.sqlite_db.execute("PRAGMA foreign_keys = ON")
    return flask.g.sqlite_db


@insta485.app.teardown_appcontext
def close_db(error):
    """Close the database at the end of a request.

    Flask docs:
    https://flask.palletsprojects.com/en/1.0.x/appcontext/#storing-data
    """
    assert error or not error  # Needed to avoid superfluous style error
    sqlite_db = flask.g.pop('sqlite_db', None)
    if sqlite_db is not None:
        sqlite_db.commit()
        sqlite_db.close()


def getUserData(username):
    """Get user data from table."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    userData = cur.fetchone()
    return userData


def getUserPhoto(username):
    """Get user photo link from table."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT filename "
        "FROM users "
        "WHERE username = ?",
        (username, )
    )
    filename = "/uploads/" + cur.fetchone()["filename"] + "/"
    return filename


def getUserPosts(username):
    """Get user's post from table."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT postid "
        "FROM posts "
        "WHERE owner = ?",
        (username, )
    )
    postsData = cur.fetchall()
    posts = []
    for p in postsData:
        posts.append(getPostData(p["postid"]))
    return posts


def getPostData(postid):
    """Get post data from table."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * "
        "FROM posts "
        "WHERE postid = ?",
        (postid, )
    )

    post = cur.fetchone()
    post["filename"] = "/uploads/" + post["filename"] + "/"
    post["user_filename"] = getUserPhoto(post["owner"])
    post["comments"] = getPostComments(postid)
    post["likes"] = getPostLikeCount(postid)
    post["created"] = arrow.get(post['created']).humanize()
    return post


def getPostComments(postid):
    """Get comments for post."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT owner, text "
        "FROM comments "
        "WHERE postid = ?",
        (postid, )
    )
    comments = cur.fetchall()
    return comments


def getPostLikeCount(postid):
    """Get likes for post."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT likeid "
        "FROM likes "
        "WHERE postid = ?",
        (postid, )
    )
    likes = cur.fetchall()
    return len(likes)


def getUserFollowers(username):
    """Get all the followers for a user."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username1 "
        "FROM following "
        "WHERE username2 = ?",
        (username, )
    )
    followersData = cur.fetchall()

    followers = []
    for item in followersData:
        followers.append(item['username1'])

    return followers


def getUserFollowing(username):
    """Get all the people that the user is following."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ?",
        (username, )
    )
    followingData = cur.fetchall()

    following = []
    for item in followingData:
        following.append(item['username2'])

    return following


def getUserNotFollowing(username):
    """Get all the users that the user is not following."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username "
        "FROM users "
        "EXCEPT "
        "SELECT username2 "
        "FROM following "
        "WHERE username1 = ?",
        (username, )
    )
    notFollowingData = cur.fetchall()
    notFollowing = []

    for item in notFollowingData:
        notFollowing.append(item['username'])
    notFollowing.remove(username)

    return notFollowing
