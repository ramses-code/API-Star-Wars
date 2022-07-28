from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            'name': self.name,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    population = db.Column(db.Integer, unique=False, nullable=False)
    
    def __repr__(self):
        return '<Planets %r>' % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'population': self.population,
        }

class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    mass = db.Column(db.Integer, unique=False, nullable=False)

    def __repr__(self):
        return '<Characters %r>' % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'mass': self.mass,
        }

class Vehicles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(20), unique=False, nullable=False)

    def __repr__(self):
        return '<Vehicle %r>' % self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'model': self.model,
        }

class Fav_character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id', ondelete='CASCADE'))
    Characters = db.relationship('Characters', primaryjoin=character_id == Characters.id)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    User = db.relationship('User', primaryjoin=user_id == User.id)

    def __repr__(self):
        return '<Fav_character %r' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'character_id': self.character_id,
            'user_id': self.user_id
        }

class Fav_planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id', ondelete='CASCADE'))
    Planets = db.relationship('Planets', primaryjoin=planet_id == Planets.id)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    User = db.relationship('User', primaryjoin=user_id == User.id)

    def __repr__(self):
        return '<Fav_planet %r' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'planet_id': self.planet_id,
            'user_id': self.user_id
        }

class Fav_vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id', ondelete='CASCADE'))
    Vehicles = db.relationship('Vehicles', primaryjoin=vehicle_id == Vehicles.id)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    User = db.relationship('User', primaryjoin=user_id == User.id)

    def __repr__(self):
        return '<Fav_vehicle %r' % self.id

    def serialize(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'user_id': self.user_id,
        }