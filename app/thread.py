from flask import Flask, Blueprint, request
from extensions import mysql, responses_codes
from functions import get_thread_entity, list_threads, get_post_entity, list_posts
import json
import re

app = Blueprint('thread', __name__)


@app.route('/open/', methods=['POST'])
def open_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        thread_id = json_obj["thread"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not thread_id:
        return json.dumps(responses_codes[2])
    try:
        cur.execute('''UPDATE Thread SET isClosed=false WHERE id = '%s' ''' % (thread_id,))
    except Exception:
        return json.dumps(responses_codes[1])
    return json.dumps({
        "code": 0,
        "response": {
            "thread": thread_id
        }
    })
#######################################


@app.route('/close/', methods=['POST'])
def close_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        thread_id = json_obj["thread"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not thread_id:
        return json.dumps(responses_codes[2])
    try:
        cur.execute('''UPDATE Thread SET isClosed=true WHERE id = '%s' ''' % (thread_id,))
    except Exception:
        return json.dumps(responses_codes[1])
    return json.dumps({
        "code": 0,
        "response": {
            "thread": thread_id
        }
    })
#######################################

@app.route('/create/', methods=['POST'])
def create_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        forum_short_name = json_obj["forum"]
        title = json_obj["title"]
        isClosed = int(json_obj["isClosed"])
        email = json_obj["user"]
        date = json_obj["date"]
        message = json_obj["message"]
        slug = json_obj["slug"]
    except Exception:
        return json.dumps(responses_codes[2])
    isDeleted = 0
    if "isDeleted" in json_obj:
        isDeleted = int(json_obj["isDeleted"])

    query = ''' INSERT INTO Thread (forum,title,isClosed,user,date,message,slug,isDeleted) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s') '''
    try:
        cur.execute(query % (forum_short_name, title, isClosed, email, date, message, slug, isDeleted,))
        cur.execute('''SELECT id FROM Thread WHERE forum='%s' AND title='%s' AND user='%s' AND slug='%s' ''' % (
            forum_short_name, title, email, slug,))
        id = cur.fetchone()
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": {
            "date": date,
            "forum": forum_short_name,
            "id": id[0],
            "isClosed": bool(isClosed),
            "isDeleted": bool(isDeleted),
            "message": message,
            "slug": slug,
            "title": title,
            "user": email,
        }
    }, sort_keys=True)
#######################################


@app.route('/remove/', methods=['POST'])
def remove_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        thread_id = json_obj["thread"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not thread_id:
        return json.dumps(responses_codes[1])

    try:
        cur.execute('''UPDATE Thread SET isDeleted=true WHERE id = '%s' ''' % thread_id)
        cur.execute('''UPDATE Post SET isDeleted=true WHERE thread = '%s' ''' % thread_id)
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": {
            "thread": thread_id
        }
    }, sort_keys=True)
#######################################


@app.route('/restore/', methods=['POST'])
def restore_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        thread_id = json_obj["thread"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not thread_id:
        return json.dumps(responses_codes[1])

    try:
        cur.execute('''UPDATE Thread SET isDeleted=false WHERE id = '%s' ''' % thread_id)
        cur.execute('''UPDATE Post SET isDeleted=false WHERE thread = '%s' ''' % thread_id)
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": {
            "thread": thread_id
        }
    }, sort_keys=True)
#######################################


@app.route('/details/', methods=['GET'])
def detail_thread():
    related = request.args.getlist("related")
    thread_id = int(request.args.get("thread"))
    if not thread_id:
        return json.dumps(responses_codes[2], sort_keys=True)
    for x in related:
        if x not in ["forum", "user"]:
            return json.dumps(responses_codes[3], sort_keys=True)

    response = get_thread_entity(related, thread_id)
    if response in responses_codes:
        return json.dumps(response, sort_keys=True)
    result = {
        "code": 0,
        "response": response
    }
    return json.dumps(result, sort_keys=True)
#######################################


@app.route('/list/', methods=['GET'])
def list_thread():
    forum_short_name = request.args.get("forum")
    user_email = request.args.get("user")
    if forum_short_name:
        entity = "forum"
        var = forum_short_name
    else:
        if user_email:
            entity = "user"
            var = user_email
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


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)


@app.route('/listPosts/', methods=['GET'])
def listPosts_thread():
    tree_posts_list = []
    cur = mysql.connection.cursor()

    thread_id = request.args.get("thread")
    if not thread_id:
        return json.dumps(responses_codes[2], sort_keys=True)
    sort = request.args.get("sort")
    since = request.args.get("since")
    limit = request.args.get("limit")
    order = request.args.get("order")

    if sort is None or sort == 'flat':
        results = {
            "code": 0,
            "response": list_posts([], since, limit, order, "thread", thread_id)
        }
        return json.dumps(results, sort_keys=True)

    if sort not in ['flat', 'tree', 'parent_tree']:
        return json.dumps(responses_codes[2], sort_keys=True)

    query = '''SELECT path FROM Post WHERE thread = '%s' '''
    query_params = (thread_id,)
    if since:
        query += "AND date >= '%s' "
        query_params += (since,)

    cur.execute(query % query_params)
    for x in cur.fetchall():
        tree_posts_list.append(x[0])

    tree_posts_list = natural_sort(tree_posts_list)

    if order is None or order == 'desc':
        tree_posts_list = sorted(tree_posts_list, key=lambda k: int(k.split('.')[0]), reverse=True)

    if limit and int(limit) <= len(tree_posts_list):
        n = int(limit)
    else:
        n = len(tree_posts_list)

    x = 0
    result_set = []
    if sort == 'tree':
        while x < n:
            split_list = tree_posts_list[x].split('.')
            result_set.append(get_post_entity([], int(split_list[len(split_list)-1])))
            x += 1
    else:
        if tree_posts_list != []:
            i = 0
            prev_firs_id = tree_posts_list[0].split('.')[0]
            while x < n and i < len(tree_posts_list):
                split_list = tree_posts_list[i].split('.')
                if split_list[0] != prev_firs_id:
                    x+=1
                if x < n:
                    result_set.append(get_post_entity([], int(split_list[len(split_list)-1])))
                prev_firs_id = tree_posts_list[i].split('.')[0]
                i+=1

    results = {
        "code": 0,
        "response": result_set
    }
    return json.dumps(results, sort_keys=True)
#######################################



@app.route('/subscribe/', methods=['POST'])
def subscribe_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        thread = json_obj["thread"]
        email = json_obj["user"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not thread or not email:
        return json.dumps(responses_codes[1])
    # exist thread?
    cur.execute('''SELECT title FROM Thread WHERE id='%s' ''' % thread)
    if not cur.fetchone():
        return json.dumps(responses_codes[1])
    # exist user?
    cur.execute('''SELECT id FROM User WHERE email='%s' ''' % email)
    if not cur.fetchone():
        return json.dumps(responses_codes[1])
    # exist subscription?
    cur.execute('''SELECT id FROM Subscribe WHERE user = '%s' AND thread = '%s' ''' % (email, thread,))
    if cur.fetchone():
        return json.dumps(responses_codes[5])

    try:
        cur.execute('''INSERT INTO Subscribe (user, thread) VALUES ('%s','%s')''' % (email, thread,))
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": {
            "thread": thread,
            "user": email
        }
    }, sort_keys=True)
#######################################


@app.route('/unsubscribe/', methods=['POST'])
def unsubscribe_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        thread = json_obj["thread"]
        email = json_obj["user"]
    except Exception:
        return json.dumps(responses_codes[2])
    if not thread or not email:
        return json.dumps(responses_codes[1])
    # exist thread?
    cur.execute('''SELECT title FROM Thread WHERE id='%s' ''' % thread)
    if not cur.fetchone():
        return json.dumps(responses_codes[1])
    # exist user?
    cur.execute('''SELECT id FROM User WHERE email='%s' ''' % email)
    if not cur.fetchone():
        return json.dumps(responses_codes[1])
    # exist subscription?
    cur.execute('''SELECT id FROM Subscribe WHERE user = '%s' AND thread = '%s' ''' % (email, thread,))
    if not cur.fetchone():
        return json.dumps(responses_codes[5])

    try:
        cur.execute('''DELETE FROM Subscribe WHERE user='%s' AND thread='%s' ''' % (email, thread,))
    except Exception:
        return json.dumps(responses_codes[5])

    return json.dumps({
        "code": 0,
        "response": {
            "thread": thread,
            "user": email
        }
    }, sort_keys=True)
#######################################


@app.route('/update/', methods=['POST'])
def update_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        thread_id = json_obj["thread"]
        message = json_obj["message"]
        slug = json_obj["slug"]
    except Exception:
        return json.dumps(responses_codes[2])

    if not thread_id or not message or not slug:
        return json.dumps(responses_codes[1])

    try:
        cur.execute('''UPDATE Thread SET message='%s', slug='%s' WHERE id = '%s' ''' % (message, slug, thread_id,))
    except Exception:
        return json.dumps(responses_codes[5])
    response = get_thread_entity([], thread_id)
    if response in responses_codes:
        return json.dumps(response, sort_keys=True)
    result = {
        "code": 0,
        "response": response
    }
    return json.dumps(result, sort_keys=True)
#######################################


@app.route('/vote/', methods=['POST'])
def vote_thread():
    cur = mysql.connection.cursor()
    try:
        json_obj = json.loads(json.dumps(request.json))
        thread_id = json_obj["thread"]
        vote = str(json_obj["vote"])
    except Exception:
        return json.dumps(responses_codes[2])
    if not thread_id or not vote:
        return json.dumps(responses_codes[1])
    if vote not in {'1', '-1'}:
        return json.dumps(responses_codes[2])
    try:
        if vote == '1':
            cur.execute('''UPDATE Thread SET points = points + 1, likes = likes + 1 WHERE id = '%s' ''' % thread_id)
        else:
            cur.execute('''UPDATE Thread SET points = points - 1, dislikes = dislikes + 1 WHERE id = '%s' ''' % thread_id)
    except Exception:
        return json.dumps(responses_codes[5])
    response = get_thread_entity([], thread_id)
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
