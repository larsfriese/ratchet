from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from PyDictionary import PyDictionary
dictionary=PyDictionary()
import pronouncing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'anykeyforsecurity' #random keys can be generated with this: os.urandom(24)
socketio = SocketIO(app)

@app.route('/')
def home_page():
    return render_template('index.html')

@socketio.on('desc')
def handle_my_custom_event(word):
    word=word['data']
    dict = dictionary.meaning(word, disable_errors=True)
    dictList = []
    if dict==None:
        emit('desc', { 'data' : ['ERR', word] })
        return
    for key, value in dict.items():
        temp = [key,value]
        dictList.append(temp)
    description=[word ,dictList[0][0], dictList[0][1][0]]
    emit('desc', { 'data' : description })

@socketio.on('search')
def handleSearch(word):
    word=word['data']
    l = pronouncing.rhymes(str(word))
    l = list(dict.fromkeys(l)) #remove duplicate objects
    i = 1
    while i < len(l):
        l.insert(i, 5)
        i += 2
    l.append(5)
    if len(l)==1:
        emit('search', { 'data' : 'Word not found.' })
        return
    else:
        emit('search', { 'data' : l })
        return

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80)
