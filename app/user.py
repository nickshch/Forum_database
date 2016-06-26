from flask import Blueprint, request
from extensions import mysql, responses_codes
from functions import get_user_entity, list_posts
import user_addons
import json

app = Blueprint('user', __name__)


@app.route('/create/', methods=['POST'])
def create_user():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        username = json_obj["username"]
        about = json_obj["about"]
        name = json_obj["name"]
        email = json_obj["email"]
        isanon = 0
        if username == "None" or username is None:
            username = ""
        if about == "None" or about is None:
            about = ""
        if name == "None" or name is None:
            name = ""
        if "isAnonymous" in json_obj:
            isanon = int(json_obj["isAnonymous"])
    except Exception:
        return json.dumps(responses_codes[2])

    try:
        cur.execute('''INSERT INTO User (username,about,name,email,isAnonymous) VALUES ('%s','%s','%s','%s','%s')''' % (
            username, about, name, email, isanon,))
        cur.execute('''SELECT id FROM User WHERE email='%s' ''' % email)
        id = cur.fetchone()
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": {
            "id": id[0],
            "name": name,
            "username": username,
            "about": about,
            "email": email,
            "isAnonymous": bool(isanon)
        }
    })
#######################################


@app.route('/details/', methods=['GET'])
def detail_forum():
    user_email = request.args.get("user")
    if not user_email:
        return json.dumps(responses_codes[2])
    response = get_user_entity(user_email)

    if response in responses_codes:
        return json.dumps(response)
    result = {
        "code": 0,
        "response": response
    }
    return json.dumps(result)
#######################################


@app.route('/follow/', methods=['POST'])
def follow_user():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        follower = json_obj["follower"]
        followee = json_obj["followee"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not follower or not followee:
        return json.dumps(responses_codes[1])
    # exist both users?
    cur.execute('''SELECT id FROM User WHERE email='%s' ''' % follower)
    if not cur.fetchone():
        return json.dumps(responses_codes[1])
    cur.execute('''SELECT id FROM User WHERE email='%s' ''' % followee)
    if not cur.fetchone():
        return json.dumps(responses_codes[1])
    # exist follow?
    cur.execute('''SELECT id FROM Follow WHERE follower = '%s' AND followee = '%s' ''' % (follower, followee,))
    if cur.fetchone():
        return json.dumps(responses_codes[5])

    try:
        cur.execute('''INSERT INTO Follow (follower, followee) VALUES ('%s','%s')''' % (follower, followee,))
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": get_user_entity(follower)
    }, sort_keys=True)
#######################################


@app.route('/listFollowers/', methods=['GET'])
def list_followers():
    return user_addons.list_follow("follower", "followee")
#######################################


@app.route('/listFollowing/', methods=['GET'])
def list_following():
    return user_addons.list_follow("followee", "follower")
#######################################


@app.route('/listPosts/', methods=['GET'])
def listPosts_forum():
    email = request.args.get("user")
    if email:
        entity = "user"
        var = email
    else:
        return json.dumps(responses_codes[2], sort_keys=True)
    related = request.args.getlist("related")
    since = request.args.get("since")
    limit = request.args.get("limit")
    order = request.args.get("order")
    results = {
        "code": 0,
        "response": list_posts(related, since, limit, order, entity, var)
    }
    return json.dumps(results, sort_keys=True)
#######################################


@app.route('/unfollow/', methods=['POST'])
def unfollow_user():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        follower = json_obj["follower"]
        followee = json_obj["followee"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not follower or not followee:
        return json.dumps(responses_codes[2])

    try:
        cur.execute('''DELETE FROM Follow WHERE follower = '%s' AND followee = '%s' ''' % (follower, followee,))
    except Exception:
        return json.dumps(responses_codes[1])

    return json.dumps({
        "code": 0,
        "response": get_user_entity(follower)
    }, sort_keys=True)
#######################################


@app.route('/updateProfile/', methods=['POST'])
def user_updateProfile():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        about = json_obj["about"]
        email = json_obj["user"]
        name = json_obj["name"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not about or not email or not name:
        return json.dumps(responses_codes[2])
    try:
        cur.execute('''UPDATE User SET about='%s',name='%s' WHERE email = '%s' ''' % (about, name, email,))
    except Exception:
        return json.dumps(responses_codes[1])
    return json.dumps({
        "code": 0,
        "response": get_user_entity(email)
    }, sort_keys=True)


if __name__ == '__main__':
    app.run(debug=True)
