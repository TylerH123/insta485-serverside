"""
Insta485 index (main) view.
URLs include:
/
"""
import flask
import insta485
import pprint
from insta485.model import *

# pp = pprint.PrettyPrinter(indent=4)

@insta485.app.route("/uploads/<path:name>")
def retrieveImage(name):
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
        "SELECT * "
        "FROM posts "
    )
    posts = cur.fetchall()

    # Get all relevant data for each post
    for p in posts:
        postData = getPostData(p["postid"])
        postData['user_filename'] = getUserPhoto(p["owner"])
        context["posts"].append(postData)

    # pp.pprint(context)

    return flask.render_template("index.html", context=context)