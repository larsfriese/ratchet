from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy
from PyDictionary import PyDictionary
dictionary=PyDictionary()
import pronouncing

app = Flask(__name__)
app.config['SECRET_KEY'] = 'anykeyforsecurity' #random keys can be generated with this: os.urandom(24)
socketio = SocketIO(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

class Wobject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(50))
    group = db.Column(db.String(50))
    level = db.Column(db.Integer, default=5)
    explicit = db.Column(db.Boolean)
    date_created = db.Column(db.DateTime, default=datetime.now)

class Relation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group1 = db.Column(db.String(50))
    group2 = db.Column(db.String(50))
    level = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.now)

@app.route('/')
def hello_world():
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
    wordobj = Wobject.query.filter_by(word=str(word)).first()
    try:
        syn = Wobject.query.filter_by(group=wordobj.group)
        synl=[]
        for i in syn:
            synl.append(i)
        syn=synl
        syn.remove(wordobj)
        #syn.sort(key=lambda x: x.level, reverse=True)
        temp=[]
        for i in syn:
            temp.append(i.word)
            temp.append(str(i.level))
        emit('search', { 'data' : temp })
    except:
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
        emit('search', { 'data' : l })
        return

@app.route('/<word>')
def get_word(word):
    wordobj = Wobject.query.filter_by(word=word).first()
    syn = Wobject.query.filter_by(group=wordobj.group)
    synl=[]
    for i in syn:
        synl.append(i)
    syn=synl
    syn.remove(wordobj)
    syn.sort(key=lambda x: x.level, reverse=True)
    return render_template('layout.html', syn=syn, word=word)

#@app.route('/make/<word>_<group>_<explicit>')
#def make_word(word, group, level, explicit):
#    explicit=True if explicit=="t" else False
#    newword = Wobject(word=str(word), group=str(group), explicit=explicit)
#    db.session.add(newword)
#    db.session.commit()
#    return f"Word {newword} has been added to the Database!"

if __name__ == '__main__':
    db.create_all()
    socketio.run(app, host='0.0.0.0', port=80)
