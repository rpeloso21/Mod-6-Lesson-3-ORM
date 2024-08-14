from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Tsrost007!@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class MemberSchema(ma.Schema):
    id = fields.String(required=True)
    name = fields.String(required=True)
    age = fields.String(required=True)

class SessionSchema(ma.Schema):
    session_id = fields.String(required=True)
    member_id = fields.String(required=True)
    session_date = fields.Date(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

session_schema = SessionSchema()
sessions_schema = SessionSchema(many=True)

class Member(db.Model):
    __tablename__ = "Members"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable = False)
    age = db.Column(db.Integer)




class WorkoutSession(db.Model):
    __tablename__ = "workoutsessions"
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.id'))
    session_date = db.Column(db.Date)
    session_time = db.Column(db.String(255))
    activity = db.Column(db.String(255))


@app.route('/members', methods=['GET'])
def get_all_members():
    members = Member.query.all()
    return members_schema.jsonify(members)


@app.route('/members', methods=['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Member(id = member_data['id'], name = member_data['name'], age = member_data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({"message": "New member added successfully"}), 201


@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.id = member_data['id']
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member updated successfully"}), 200


@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200


@app.route('/sessions/<int:member_id>', methods=['GET'])
def get_session_by_customer_id(member_id):
    sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
    if sessions:
        return sessions_schema.jsonify(sessions)
    else:
        return jsonify({"message": "No sessions found for that member."}), 404
    

@app.route('/sessions', methods=['POST'])
def add_session():
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_session = WorkoutSession(session_id = session_data['session_id'], member_id = session_data['member_id'], session_date = session_data['session_date'], session_time = session_data['session_time'], activity = session_data['activity'])
    db.session.add(new_session)
    db.session.commit()
    return jsonify({"message": "New session added successfully"}), 201


@app.route('/sessions/<int:session_id>', methods=['PUT'])
def update_session(session_id):
    session = WorkoutSession.query.get_or_404(session_id)
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    session.session_id = session_data['session_id']
    session.member_id = session_data['member_id']
    session.session_date = session_data['session_date']
    session.session_time = session_data['session_time']
    session.activity = session_data['activity']
    db.session.commit()
    return jsonify({"message": "Session updated successfully"}), 200

    

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)