from flask import Flask, Blueprint, request
from extensions import mysql, responses_codes
from functions import get_post_entity, list_posts
import json

app = Blueprint('post', __name__)


@app.route('/create/', methods=['POST'])
def create_post():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        date = json_obj["date"]
        thread_id = json_obj["thread"]
        message = json_obj["message"]
        email = json_obj["user"]
        forum_short_name = json_obj["forum"]
    except Exception:
        return json.dumps(responses_codes[2])
    isDeleted = 0
    if "isDeleted" in json_obj:
        isDeleted = int(json_obj["isDeleted"])

    isSpam = 0
    if "isSpam" in json_obj:
        isSpam = int(json_obj["isSpam"])

    isEdited = 0
    if "isEdited" in json_obj:
        isEdited = int(json_obj["isEdited"])

    isHighlighted = 0
    if "isHighlighted" in json_obj:
        isHighlighted = int(json_obj["isHighlighted"])

    isApproved = 0
    if "isApproved" in json_obj:
        isApproved = int(json_obj["isApproved"])

    parent = None
    try:
        if "parent" in json_obj:
            parent = int(json_obj["parent"])
    except Exception:
        parent = None

    if parent is None:
        query = ''' INSERT INTO Post (date,thread,message,user,forum,isDeleted,isSpam,isEdited,isHighlighted,isApproved,parent) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',NULL) '''
        query_params = (date,thread_id,message,email,forum_short_name,isDeleted,isSpam,isEdited,isHighlighted,isApproved,)

    else:
        query = ''' INSERT INTO Post (date,thread,message,user,forum,isDeleted,isSpam,isEdited,isHighlighted,isApproved,parent) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s') '''
        query_params = (date,thread_id,message,email,forum_short_name,isDeleted,isSpam,isEdited,isHighlighted,isApproved,parent,)

    #try:
    cur.execute(query % query_params)
    cur.execute('''SELECT id FROM Post WHERE forum='%s' AND thread='%s' AND user='%s' AND message='%s' ''' % (forum_short_name, thread_id, email, message))
    post_id = cur.fetchone()
    cur.execute('''UPDATE Thread SET posts = posts + 1 WHERE id = '%s' ''' % thread_id)
    #except Exception:
    #    return json.dumps(responses_codes[5])

    #set path for each post
    if parent:
        cur.execute('''SELECT path FROM Post WHERE id = '%s' ''' % parent)
        path = cur.fetchone()
        if path:
            path = path[0]
        else:
            path = ''
        path += '.' + str(post_id[0])
        cur.execute('''UPDATE Post SET path = '%s' WHERE id = '%s' ''' % (path, post_id[0],))
    else:
        path = str(post_id[0])
        cur.execute('''UPDATE Post SET path = '%s' WHERE id = '%s' ''' % (path, post_id[0],))

    return json.dumps({
        "code": 0,
        "response": {
            "date": date,
            "forum": forum_short_name,
            "id": post_id[0],
            "isApproved": bool(isApproved),
            "isDeleted": bool(isDeleted),
            "isEdited": bool(isEdited),
            "isHighlighted": bool(isHighlighted),
            "isSpam": bool(isSpam),
            "message": message,
            "parent": parent,
            "thread": thread_id,
            "user": email
        }
    }, sort_keys=True)
#######################################


@app.route('/details/', methods=['GET'])
def detail_post():
    related = request.args.getlist("related")
    post_id = int(request.args.get("post"))
    if not post_id:
        return json.dumps(responses_codes[2], sort_keys=True)
    response = get_post_entity(related, post_id)
    if response in responses_codes:
        return json.dumps(response, sort_keys=True)
    result = {
        "code": 0,
        "response": response
    }
    return json.dumps(result, sort_keys=True)
#######################################


@app.route('/list/', methods=['GET'])
def list_post():
    forum_short_name = request.args.get("forum")
    thread_id = request.args.get("thread")
    if forum_short_name:
        entity = "forum"
        var = forum_short_name
    else:
        if thread_id:
            entity = "thread"
            var = thread_id
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


@app.route('/remove/', methods=['POST'])
def remove_post():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        post_id = json_obj["post"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not post_id:
        return json.dumps(responses_codes[1])

    try:
        cur.execute('''UPDATE Post SET isDeleted=true WHERE id = '%s' ''' % post_id)
        cur.execute('''SELECT thread FROM Post WHERE id = '%s' ''' % post_id)
        thread_id = cur.fetchone()
        cur.execute('''UPDATE Thread SET posts = posts - 1 WHERE id = '%s' ''' % thread_id[0])
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": {
            "post": post_id
        }
    }, sort_keys=True)
#######################################


@app.route('/restore/', methods=['POST'])
def restore_post():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        post_id = json_obj["post"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not post_id:
        return json.dumps(responses_codes[1])

    try:
        cur.execute('''UPDATE Post SET isDeleted=false WHERE id = '%s' ''' %  post_id)
        cur.execute('''SELECT thread FROM Post WHERE id = '%s' ''' % post_id)
        thread_id = cur.fetchone()
        cur.execute('''UPDATE Thread SET posts = posts + 1 WHERE id = '%s' ''' % thread_id[0])
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": {
            "post": post_id
        }
    }, sort_keys=True)
#######################################


@app.route('/update/', methods=['POST'])
def update_post():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        post_id = json_obj["post"]
        message = json_obj["message"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not post_id or not message:
        return json.dumps(responses_codes[1])
    try:
        cur.execute('''SELECT message, isEdited FROM Post WHERE id = '%s' ''' % post_id)
        res = cur.fetchone()
        isEdited = int(res[1])
        if res[0] != message:
            isEdited = 1

        cur.execute('''UPDATE Post SET message='%s', isEdited='%s' WHERE id = '%s' ''' % (message, isEdited, post_id,))
    except Exception:
        return json.dumps(responses_codes[5])
    response = get_post_entity([], post_id)
    if response in responses_codes:
        return json.dumps(response, sort_keys=True)
    result = {
        "code": 0,
        "response": response
    }
    return json.dumps(result, sort_keys=True)
#######################################


@app.route('/vote/', methods=['POST'])
def vote_post():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        post_id = json_obj["post"]
        vote = str(json_obj["vote"])
    except Exception:
        return json.dumps(responses_codes[2])
    if not post_id or not vote:
        return json.dumps(responses_codes[1])
    if vote not in {'1', '-1'}:
        return json.dumps(responses_codes[2])
    try:
        if vote == '1':
            cur.execute('''UPDATE Post SET points = points + 1, likes = likes + 1 WHERE id = '%s' ''' % post_id)
        else:
            cur.execute('''UPDATE Post SET points = points - 1, dislikes = dislikes + 1 WHERE id = '%s' ''' % post_id)
    except Exception:
        return json.dumps(responses_codes[5])
    response = get_post_entity([], post_id)
    if response in responses_codes:
        return json.dumps(response, sort_keys=True)
    result = {
        "code": 0,
        "response": response
    }
    return json.dumps(result, sort_keys=True)
#######################################

if __name__ == '__main__':
    app.run(debug=True)