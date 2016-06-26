from flask import Flask, jsonify, Blueprint
from extensions import mysql

app = Blueprint('status', __name__)
    
@app.route('', methods=['GET'])
def status():
    cur = mysql.connection.cursor()
    tables = ['user', 'thread', 'forum', 'post']
    result = []
    for table in tables:
    	cur.execute('''SELECT COUNT(*) FROM %s''' % table)
    	result.append(cur.fetchone())

    return jsonify({"code": 0, 
    	"response":{ "user": result[0][0], "thread": result[1][0], "forum": result[2][0], "post": result[3][0]}})

if __name__ == '__main__':
    app.run(debug=True)