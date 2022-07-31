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
from models import db, User, Planets, Characters, Vehicles, Fav_planet, Fav_character, Fav_vehicle

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

app.config['JWT_SECRET_KEY'] = '4geeks_academy'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_user():

    user = User.query.all()
    user_serialized = list(map(lambda x: x.serialize(), user))

    response_body = {
        'results': user_serialized
    }
    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
def handle_planets():

    all_planets = Planets.query.all()
    planets_serialized = list(map(lambda x: x.serialize(), all_planets))

    response_body = {
        'results': planets_serialized
    }
    return jsonify(response_body), 200

@app.route('/planets/<int:planets_id>', methods=['GET'])
def handle_planets_id(planets_id):

    if planets_id < 1:
        raise APIException('Planet id is not valid', status_code=400)

    planet = Planets.query.get(planets_id)

    if planet == None:
        raise APIException('Planet does not exist', status_code=400)

    response_body = {
        'results': planet.serialize()
    }
    return jsonify(response_body), 200

@app.route('/characters', methods=['GET'])
def handle_characters():

    all_characters = Characters.query.all()
    characters_serialized = list(map(lambda x: x.serialize(), all_characters))

    response_body = {
        'results': characters_serialized
    }
    return jsonify(response_body), 200

@app.route('/characters/<int:characters_id>', methods=['GET'])
def handle_characters_id(characters_id):

    if characters_id < 1:
        raise APIException('Character id is not valid', status_code=400)

    character = Characters.query.get(characters_id)

    if character == None:
        raise APIException('Character does not exist', status_code=400)

    response_body = {
        'results': character.serialize()
    }
    return jsonify(response_body), 200

@app.route('/vehicles', methods=['GET'])
def handle_vehicles():

    all_vehicles = Vehicles.query.all()
    vehicles_serialized = list(map(lambda x: x.serialize(), all_vehicles))

    response_body = {
        'results': vehicles_serialized
    }
    return jsonify(response_body), 200

@app.route('/vehicles/<int:vehicles_id>', methods=['GET'])
def handle_vehicles_id(vehicles_id):

    if vehicles_id < 1:
        raise APIException('Vehicle id is not valid', status_code=400)
    
    vehicle = Vehicles.query.get(vehicles_id)

    if vehicle == None:
        raise APIException('Vehicle does not exist', status_code=400)

    response_body = {
        'results': vehicle.serialize()
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/planets/<int:user_id>', methods=['GET'])
@jwt_required()
def handle_fav_planets(user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_all_planets = Planets.query.join\
    (Fav_planet, Fav_planet.planet_id == Planets.id)\
    .filter(Fav_planet.user_id == user_id)

    all_planets = list(map(lambda x: x.serialize(), fav_all_planets))

    response_body = {
        'results': all_planets
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/characters/<int:user_id>', methods=['GET'])
@jwt_required()
def handle_fav_characters(user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_all_characters = Characters.query.join\
    (Fav_character, Fav_character.character_id == Characters.id)\
    .filter(Fav_character.user_id == user_id)

    all_characters = list(map(lambda x: x.serialize(), fav_all_characters))

    response_body = {
        'results': all_characters
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/vehicles/<int:user_id>', methods=['GET'])
@jwt_required()
def handle_fav_vehicles(user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_all_vehicles = Vehicles.query.join\
    (Fav_vehicle, Fav_vehicle.vehicle_id == Vehicles.id)\
    .filter(Fav_vehicle.user_id == user_id)

    all_vehicles = list(map(lambda x: x.serialize(), fav_all_vehicles))

    response_body = {
        'results': all_vehicles
    }
    return jsonify(response_body), 200

@app.route('/user', methods=['POST'])
def create_user():
    body = request.get_json()

    if body is None:
        raise APIException('You need to specify the request body as a json object',\
                                                                    status_code=400)
    if 'name' not in body:
        raise APIException('Name field can not be empty', status_code=400)
    if 'email' not in body:
        raise APIException('Email field can not be empty', status_code=400)
    if 'password' not in body:
        raise APIException('Password field can not be empty', status_code=400)

    user_email = User.query.filter_by(email= body['email']).first()
    if user_email != None:
        raise APIException('Email not available', status_code=400)

    pw_hash = bcrypt.generate_password_hash(body['password'])

    new_user = User(name = body['name'], email = body['email'],\
                    password = pw_hash, is_active = True)
    db.session.add(new_user)
    db.session.commit()

    response_body = {
        'results': new_user.serialize()
    }
    return jsonify(response_body), 200

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()
    if user is None:
        raise APIException('User does not exist', status_code=400)
    if password is None:
        raise APIException('Password required', status_code=400)
    
    is_correct = bcrypt.check_password_hash(user.password, password)
    if not is_correct:
        return jsonify({'msg': 'Bad email or password'}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)

@app.route('/user/favorites/planets', methods=['POST'])
@jwt_required()
def post_fav_planet():
    body = request.get_json()
    user = User.query.get(body['user_id'])
    current_user = get_jwt_identity()

    if user == None:
        raise APIException('User does not exist', status_code=400)
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_field = Fav_planet.query.filter_by\
    (planet_id = body['planet_id']).filter_by(user_id = body['user_id']).all()
    if len(fav_field) > 0:
        raise APIException('User already liked this planet', status_code=400)

    planet_id = Planets.query.get(body['planet_id'])
    if planet_id == None:
        raise APIException('Planet does not exist', status_code=400)

    create_fav = Fav_planet(planet_id = body['planet_id'], user_id = body['user_id'])
    db.session.add(create_fav)
    db.session.commit()

    response_body = {
        'results': create_fav.serialize()
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/characters', methods=['POST'])
@jwt_required()
def post_fav_character():
    body = request.get_json() 
    user = User.query.get(body['user_id'])
    current_user = get_jwt_identity()

    if user == None:
        raise APIException('User does not exist', status_code=400)
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_field = Fav_character.query.filter_by\
    (character_id = body['character_id']).filter_by(user_id = body['user_id']).all()
    if len(fav_field) > 0:
        raise APIException('User already liked this character', status_code=400)

    character_id = Characters.query.get(body['character_id'])
    if character_id == None:
        raise APIException('Character does not exist', status_code=400)

    create_fav = Fav_character(character_id = body['character_id'], user_id = body['user_id'])
    db.session.add(create_fav)
    db.session.commit()

    response_body = {
        'results': create_fav.serialize()
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/vehicles', methods=['POST'])
@jwt_required()
def post_fav_vehicle():
    body = request.get_json()
    user = User.query.get(body['user_id'])
    current_user = get_jwt_identity()

    if user == None:
        raise APIException('User does not exist', status_code=400)
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_field = Fav_vehicle.query.filter_by\
    (vehicle_id = body['vehicle_id']).filter_by(user_id = body['user_id']).all()
    if len(fav_field) > 0:
        raise APIException('User already liked this vehicle', status_code=400)

    vehicle_id = Vehicles.query.get(body['vehicle_id'])
    if vehicle_id == None:
        raise APIException('Vehicle does not exist', status_code=400)

    create_fav = Fav_vehicle(vehicle_id = body['vehicle_id'], user_id = body['user_id'])
    db.session.add(create_fav)
    db.session.commit()

    response_body = {
        'results': create_fav.serialize()
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/planets/<int:fav_id>/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_fav_planets(fav_id, user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_p = Fav_planet.query.get(fav_id)
    if fav_p == None:
        raise APIException('Favorite does not exist', status_code=400)

    if fav_p.user_id != user_id:
        raise APIException('User do not have this favorite', status_code=400)
    db.session.delete(fav_p)
    db.session.commit()

    response_body = {
        'results': 'ok'
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/characters/<int:fav_id>/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_fav_character(fav_id, user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_c = Fav_character.query.get(fav_id)
    if fav_c == None:
        raise APIException('Favorite does not exist', status_code=400)

    if fav_c.user_id != user_id:
        raise APIException('User do not have this favorite', status_code=400)
    db.session.delete(fav_c)
    db.session.commit()

    response_body = {
        'results': 'ok'
    }
    return jsonify(response_body), 200

@app.route('/user/favorites/vehicles/<int:fav_id>/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_fav_vehicles(fav_id, user_id):
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if current_user != user.email:
        raise APIException('Not access allowed!', status_code=401)

    fav_v = Fav_vehicle.query.get(fav_id)
    if fav_v == None:
        raise APIException('Favorite does not exist', status_code=400)
    
    if fav_v.user_id != user_id:
        raise APIException('User do not have this favorite', status_code=400)
    db.session.delete(fav_v)
    db.session.commit()

    response_body = {
        'results': 'ok'
    }
    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
