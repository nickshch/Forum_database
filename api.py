from flask import Flask, jsonify, Blueprint
from extensions import mysql

from app.clear import app as clear
from app.status import app as status
from app.forum import app as forum
from app.post import app as post
from app.user import app as user
from app.thread import app as thread

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2112'
app.config['MYSQL_DB'] = 'forum_database_last'
app.config['MYSQL_CHARSET'] = 'utf8'
mysql.init_app(app)

app.register_blueprint(clear, url_prefix='/db/api/clear')
app.register_blueprint(status, url_prefix='/db/api/status')
app.register_blueprint(forum, url_prefix='/db/api/forum')
app.register_blueprint(post, url_prefix='/db/api/post')
app.register_blueprint(user, url_prefix='/db/api/user')
app.register_blueprint(thread, url_prefix='/db/api/thread')


@app.route('/')
def users():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT * FROM user''')
    result = cur.fetchall()
    for res in result:
        return str(result)


if __name__ == '__main__':
    app.run(debug=True)
