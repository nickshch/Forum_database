from flask import Flask, jsonify, Blueprint
from extensions import mysql, responses_codes

app = Blueprint('clear', __name__)
    
@app.route('/', methods=['POST'])
def clear():
    cur = mysql.connection.cursor()
    tables = ['User', 'Forum', 'Thread', 'Post', 'Follow', 'Subscribe']
    for table in tables:
    	cur.execute('''TRUNCATE TABLE %s''' % table)
    return jsonify(responses_codes[0])

if __name__ == '__main__':
    app.run(debug=True)