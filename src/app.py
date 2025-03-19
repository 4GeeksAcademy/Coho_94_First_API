"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Post
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Obtener todos los usuarios:
@app.route('/users', methods=['GET'])
def get_all_users():

    users = User.query.all()
    users_serialized = [user.serialize() for user in users]

    return jsonify({
        "msg": "Users retrieved succesfully",
        "users": users_serialized
    }), 200

# Obtener un usuario:
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    return jsonify({
        "msg": "User found succesfully",
        "user" : user.serialize_is_active()
    }), 200

# Crear un nuevo usuario
@app.route('/user', methods=['POST'])
def create_user():

    # Guarda en request_data lo que viene del frontend
    request_data = request.get_json()

    # Comprobamos que los campos no estén vacíos
    if not request_data.get('email') or not request_data.get('password'):
        return jsonify({"msg": "Email and password are required"}), 400

    # Comprobamos que el email de este usuario no existe ya:
    existing_user = User.query.filter_by(email = request_data.get('email')).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 403

    # Creamos ese nuevo usuario
    new_user = User(
        email = request_data["email"],
        password = request_data["password"],
        is_active = True
    )

    # Guardamos el nuevo usuario en la base datos
    db.session.add(new_user)
    db.session.commit()

    # Devolvemos mensaje de éxito
    return jsonify({
        "msg" : "User created succesfully",
        "user" : new_user.serialize()
    }), 201

@app.route('/user/posts/<int:user_id>', methods=['GET'])
def get_user_posts(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg":"No se encontro el usuario"}), 404

    return jsonify({
        "msg": "User found succesfully",
        "user" : user.serialize_posts()
    }), 200

@app.route('/user/post', methods=['POST'])
def create_post():

    request_data = request.get_json()

    if not request_data or not request_data.get("title") or not request_data.get("content") or not request_data.get("user_id"):
        return jsonify({"msg" : "Petición incompleta"}), 400

    user = User.query.get(request_data.get("user_id"))

    if not user:
        return jsonify({"msg" : "El usuario no existe"}), 404

    new_post = Post(
        title = request_data.get("title"),
        content = request_data.get("content"),
        user_id = request_data.get("user_id")
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({
        "msg" : "Post creado con exito",
        "post" : new_post.serialize()
    }), 201

@app.route('user/post/<int:post_id>', methods = ['DELETE'])
def delete_post(post_id):

    post = Post.query.get(post_id)

    if not post:
        return jsonify({"msg" : "Post no encontrado"}), 404

    db.session.delete(post)
    db.session.commit()

    return jsonify({"msg": "Post borrado con éxito"}), 200






# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
