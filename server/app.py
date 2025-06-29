from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from server.config import app, db, api
from models import User, Note
from flask_restful import Resource

app = Flask(__name__)
class Register(Resource):
    def post(self):
        data = request.get_json()
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Username already exists'}, 400
        user = User(username=data['username'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return {'message': 'User created'}, 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            token = create_access_token(identity=user.id)
            return {'access_token': token , 'username': user.username}, 200
        return {'message': 'Invalid credentials'}, 401
class Notes(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        notes = Note.query.filter_by(user_id=user_id).all()
        return [n.to_dict() for n in notes], 200

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        note = Note(title=data['title'], content=data['content'], tags=data.get('tags', ''), user_id=user_id)
        db.session.add(note)
        db.session.commit()
        return note.to_dict(), 201

class NoteById(Resource):
    @jwt_required()
    def put(self, id):
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=id, user_id=user_id).first_or_404()
        data = request.get_json()
        note.title = data['title']
        note.content = data['content']
        note.tags = data.get('tags', '')
        db.session.commit()
        return note.to_dict(), 200
    @jwt_required()
    def delete(self, id):
        user_id = get_jwt_identity()
        note = Note.query.filter_by(id=id, user_id=user_id).first_or_404()
        db.session.delete(note)
        db.session.commit()
        return {}, 204
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Notes, '/notes')
api.add_resource(NoteById, '/notes/<int:id>')

@app.route('/')
def index():
    return '<h1>JotSpot Flask API Running</h1>'

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
