from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy_serializer import SerializerMixin

# ------------------------
# App setup
# ------------------------
app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ------------------------
# Model
# ------------------------
class Message(db.Model, SerializerMixin):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)

    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now())

    serialize_rules = ("-updated_at",)  # optional for tests

# ------------------------
# Routes
# ------------------------

@app.route("/")
def index():
    return {"message": "Chatterbox API running"}

# GET all messages
@app.route("/messages", methods=["GET"])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages]), 200

# POST a new message
@app.route("/messages", methods=["POST"])
def create_message():
    data = request.get_json()
    if not data or not data.get("body") or not data.get("username"):
        return jsonify({"error": "Missing body or username"}), 400

    message = Message(body=data["body"], username=data["username"])
    db.session.add(message)
    db.session.commit()
    return jsonify(message.to_dict()), 201

# PATCH an existing message
@app.route("/messages/<int:id>", methods=["PATCH"])
def update_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()
    message.body = data.get("body", message.body)
    db.session.commit()
    return jsonify(message.to_dict()), 200

# DELETE a message
@app.route("/messages/<int:id>", methods=["DELETE"])
def delete_message(id):
    message = Message.query.get(id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()
    return jsonify({}), 204

# ------------------------
# Run server
# ------------------------
if __name__ == "__main__":
    app.run(port=5555, debug=True)

