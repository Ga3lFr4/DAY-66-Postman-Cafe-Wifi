from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route('/random')
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    all_cafes_dict = {}
    for cafe in all_cafes:
        all_cafes_dict[cafe.name] = cafe.to_dict()
    return jsonify(cafes=all_cafes_dict)


@app.route('/search')
def find_a_cafe():
    loc = request.args.get('loc').title()
    loc_cafes = Cafe.query.filter_by(location=loc)
    loc_cafes_dict = {}
    for cafe in loc_cafes:
        loc_cafes_dict[cafe.name] = cafe.to_dict()
    if loc_cafes_dict:
        return jsonify(cafes=loc_cafes_dict)
    else:
        return jsonify(error={
            "Not Found": "Sorry we have no cafe at that location."
        })


## HTTP POST - Create Record

@app.route('/add', methods=['POST'])
def add_cafe():
    new_cafe = Cafe(name=request.form.get('name'),
                    map_url=request.form.get('map_url'),
                    img_url=request.form.get('img_url'),
                    location=request.form.get('location'),
                    seats=request.form.get('seats'),
                    has_toilet=bool(request.form.get('has_toilet')),
                    has_wifi=bool(request.form.get('has_wifi')),
                    can_take_calls=bool(request.form.get('can_take_calls')),
                    has_sockets=bool(request.form.get('has_sockets')))
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify({"Success": "Successfully added line to db"})

## HTTP PUT/PATCH - Update Record
@app.route('/update-price/<cafe_id>')
def modify_coffee_price(cafe_id):
    cafe_to_update = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_to_update:
        new_price = request.args.get('new_price')
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify({"Success": f"Coffee price updated for {cafe_to_update.name}"})
    else:
        return jsonify({"Error": f"No cafe with that id found."}), 404


## HTTP DELETE - Delete Record
@app.route('/report-closed/<cafe_id>')
def delete_cafe(cafe_id):
    if request.args.get('api-key') and request.args.get('api-key') == 'TopSecretAPIKey':
        cafe_to_delete = Cafe.query.filter_by(id=cafe_id).first()
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify({"Success": "Cafe successfully deleted, still sad :("})
        else:
            return jsonify({'Error': 'No cafe found with that id'}), 404
    else:
        return jsonify({'Error': 'Unauthorized access'}), 403

if __name__ == '__main__':
    app.run(debug=True, port=8000)
