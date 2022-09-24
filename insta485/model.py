"""Insta485 model (database) API."""
import sqlite3
import uuid
import pathlib
import hashlib
import flask
import arrow
import insta485


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
        flask.g.sqlite_db.execute('PRAGMA foreign_keys = ON')
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


# ===== LOGIN =====
def put_new_user(user_data):
    """Insert new user into table."""
    connection = insta485.model.get_db()
    connection.execute(
        'INSERT INTO '
        'users (username, fullname, email, filename, password) '
        'VALUES (?, ?, ?, ?, ?)',
        (*user_data, )
    )


def upload_file(fileobj):
    """Upload a file."""
    filename = fileobj.filename
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix
    uuid_basename = f'{stem}{suffix}'
    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename


def hash_password(password, salt=None):
    """Hashes password."""
    algorithm = 'sha512'
    user_salt = salt if salt is not None else uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = user_salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = '$'.join([algorithm, user_salt, password_hash])
    return password_db_string


# ===== USER =====
def get_user_data(username):
    """Get user data from table."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT * '
        'FROM users '
        'WHERE username = ?',
        (username, )
    )
    user_data = cur.fetchone()
    return user_data


def get_user_photo(username):
    """Get user photo link from table."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT filename '
        'FROM users '
        'WHERE username = ?',
        (username, )
    )
    filename = '/uploads/' + cur.fetchone()['filename'] + '/'
    return filename


def get_user_posts(username):
    """Get user's post from table."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT postid '
        'FROM posts '
        'WHERE owner = ?',
        (username, )
    )
    posts_data = cur.fetchall()
    posts = []
    for entry in posts_data:
        posts.append(get_post_data(entry['postid']))
    return posts


def get_user_followers(username):
    """Get all the followers for a user."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT username1 '
        'FROM following '
        'WHERE username2 = ?',
        (username, )
    )
    followers_data = cur.fetchall()
    followers = []
    for item in followers_data:
        followers.append(item['username1'])
    return followers


def get_user_following(username):
    """Get all the people that the user is following."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT username2 '
        'FROM following '
        'WHERE username1 = ?',
        (username, )
    )
    following_data = cur.fetchall()
    following = []
    for item in following_data:
        following.append(item['username2'])
    return following


def get_user_not_following(username):
    """Get all the users that the user is not following."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT username '
        'FROM users '
        'EXCEPT '
        'SELECT username2 '
        'FROM following '
        'WHERE username1 = ?',
        (username, )
    )
    not_following_data = cur.fetchall()
    not_following = []
    for item in not_following_data:
        not_following.append(item['username'])
    not_following.remove(username)
    return not_following

def edit_user_profile(data):
    """Update Fullname, Email, Profile Picture."""
    username = data[0]
    fullname = data[1]
    email = data[2]
    filename = data[3]
    connection = insta485.model.get_db()
    connection.execute(
        'UPDATE users '
        'SET fullname = ?, email = ?, filename = ? '
        'WHERE username = ?',
        (fullname, email, filename, username )
    )

# ===== POSTS =====
def get_post_data(postid):
    """Get post data from table."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT * '
        'FROM posts '
        'WHERE postid = ?',
        (postid, )
    )
    post = cur.fetchone()
    post['filename'] = '/uploads/' + post['filename'] + '/'
    post['user_filename'] = get_user_photo(post['owner'])
    post['comments'] = get_post_comments(postid)
    post['likes'] = get_post_like_count(postid)
    post['created'] = arrow.get(post['created']).humanize()
    return post


def get_post_comments(postid):
    """Get comments for post."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT * '
        'FROM comments '
        'WHERE postid = ?',
        (postid, )
    )
    comments = cur.fetchall()
    return comments


def get_post_like_count(postid):
    """Get likes for post."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT likeid '
        'FROM likes '
        'WHERE postid = ?',
        (postid, )
    )
    likes = cur.fetchall()
    return len(likes)


def user_like_post(username, postid):
    """Return true if user has liked post."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT * '
        'FROM likes '
        'WHERE postid = ? AND owner = ?',
        (postid, username)
    )
    data = cur.fetchall()
    return len(data) == 0


def update_likes(like, username, postid):
    """Update likes for post."""
    if like:
        connection = insta485.model.get_db()
        cur = connection.execute(
            'INSERT INTO '
            'likes (owner, postid) '
            'VALUES (?, ?)',
            (username, postid)
        )
    else:
        connection = insta485.model.get_db()
        cur = connection.execute(
            'SELECT * FROM likes '
            'WHERE owner = ? AND postid = ?',
            (username, postid)
        )
        print(cur.fetchall())
        cur = connection.execute(
            'DELETE FROM likes '
            'WHERE owner = ? AND postid = ?',
            (username, postid)
        )

def create_comments(username, postid, text):
    """Update comments for post."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'INSERT INTO '
        'comments (owner, postid, text) '
        'VALUES (?, ?, ?)',
        (username, postid, text)
    )


def delete_comments(commentid):
    """Update comments for post."""
    connection = insta485.model.get_db()
    cur = connection.execute(
        'DELETE FROM comments '
        'WHERE commentid = ?',
        (commentid, )
    )


# ===== Comments =====
def get_comment_owner(commentid):
    connection = insta485.model.get_db()
    cur = connection.execute(
        'SELECT owner '
        'FROM comments '
        'WHERE commentid = ?',
        (commentid, )
    )
    return cur.fetchone() 
