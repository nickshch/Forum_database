from flask import Flask, Blueprint, request
from extensions import mysql, responses_codes
from functions import get_forum_entity, list_posts, list_threads, list_users
import json


app = Blueprint('forum', __name__)


@app.route('/create/', methods=['POST'])
def create_forum():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        name = json_obj["name"]
        short_name = json_obj["short_name"]
        user = json_obj["user"]
    except Exception:
        return json.dumps(responses_codes[2], sort_keys=True)
    # try:
    #     cur.execute('''SELECT * FROM User WHERE email = '%s' ''' % user)
    #     check_user = cur.fetchone()
    #     if not check_user:
    #         return json.dumps(responses_codes[1], sort_keys=True)
    # except Exception:
    #     return json.dumps(responses_codes[1], sort_keys=True)

    try:
        cur.execute('''INSERT INTO Forum (name,short_name,user) VALUES ('%s','%s','%s')''' % (name, short_name, user,))
        cur.execute('''SELECT id FROM Forum WHERE name='%s' ''' % name)
        id = cur.fetchone()
    except Exception:
        return json.dumps(responses_codes[5], sort_keys=True)

    return json.dumps({
        "code": 0,
        "response": {
            "id": id[0],
            "name": name,
            "short_name": short_name,
            "user": user
        }
    }, sort_keys=True)
#######################################


@app.route('/details/', methods=['GET'])
def detail_forum():
    related = request.args.getlist("related")
    forum_short_name = request.args.get("forum")
    if not forum_short_name:
        return json.dumps(responses_codes[2], sort_keys=True)
    response = get_forum_entity(related, forum_short_name)
    if response in responses_codes:
        return json.dumps(response, sort_keys=True)
    result = {
        "code": 0,
        "response": response
    }
    return json.dumps(result, sort_keys=True)
#######################################


@app.route('/listPosts/', methods=['GET'])
def listPosts_forum():
    forum_short_name = request.args.get("forum")
    if forum_short_name:
        entity = "forum"
        var = forum_short_name
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


@app.route('/listThreads/', methods=['GET'])
def listThreads_forum():
    forum_short_name = request.args.get("forum")
    if forum_short_name:
        entity = "forum"
        var = forum_short_name
    else:
        return json.dumps(responses_codes[2], sort_keys=True)
    related = request.args.getlist("related")
    since = request.args.get("since")
    limit = request.args.get("limit")
    order = request.args.get("order")
    results = {
        "code": 0,
        "response": list_threads(related, since, limit, order, entity, var)
    }
    return json.dumps(results, sort_keys=True)
#######################################


@app.route('/listUsers/', methods=['GET'])
def listUsers_forum():
    forum_short_name = request.args.get("forum")
    if forum_short_name:
        entity = "forum"
        var = forum_short_name
    else:
        return json.dumps(responses_codes[2], sort_keys=True)
    since_id = request.args.get("since_id")
    limit = request.args.get("limit")
    order = request.args.get("order")
    results = {
        "code": 0,
        "response": list_users(since_id, limit, order, entity, var)
    }
    return json.dumps(results, sort_keys=True)
#######################################


if __name__ == '__main__':
    app.run(debug=True)
