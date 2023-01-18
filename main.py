from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)


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

    def cafe_jsonify(self):
        data = jsonify(
            id=self.id,
            name=self.name,
            map_url=self.map_url,
            img_url=self.img_url,
            location=self.location,
            seats=self.seats,
            has_toilet=self.has_toilet,
            has_wifi=self.has_wifi,
            has_sockets=self.has_sockets,
            can_take_calls=self.can_take_calls,
            coffee_price=self.coffee_price,
        )
        return data

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def random():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = choice(all_cafes)
    # print(random_cafe)
    return random_cafe.cafe_jsonify()


@app.route("/all")
def all():
    all_cafes = db.session.query(Cafe).all()
    all_cafes_dic = [cafe.to_dict() for cafe in all_cafes]

    return jsonify(total=len(all_cafes_dic), cafes=all_cafes_dic)


@app.route("/search")
def search():
    # giv error if no parameter passed
    location = request.args['loc']
    cafes_at_loc = db.session.query(Cafe).filter(Cafe.location.like(location + '%'))
    cafes_dic = [cafe.to_dict() for cafe in cafes_at_loc]
    if not cafes_dic:
        return jsonify(error={'not found': f"sorry no cafe found in {location}"})

    return jsonify(total=len(cafes_dic), cafes=cafes_dic)


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<id_>", methods=["PATCH"])
def update_price(id_):
    new_price = request.args['new_price']
    cafe_to_update = Cafe.query.get(id_)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(response={"Not Found": "Not found cafe with this id"})


## HTTP DELETE - Delete Record
## HTTP PUT/PATCH - Update Record
@app.route("/report-close/<id_>", methods=["DELETE"])
def close(id_):
    api_key = request.args['api-key']
    if api_key != "TopSecretAPIKey":
        return jsonify(response={"Not Allowed": "Please enter a correct API key"})
    cafe_to_delete = Cafe.query.get(id_)
    if cafe_to_delete:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(response={"success": "Successfully deleted"})
    else:
        return jsonify(response={"Not Found": "Not found cafe with this id"})

if __name__ == '__main__':
    app.run(debug=True)
