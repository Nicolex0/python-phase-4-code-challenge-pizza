#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantsResources(Resource):
    def get(self):
        response = [restaurant.to_dict(only=("id", "name", "address")) for restaurant in Restaurant.query.all()]
        return make_response(jsonify(response), 200)
    
class RestaurantResource(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            response = restaurant.to_dict()
            return make_response(jsonify(response), 200)
        else:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response = make_response(jsonify({"message": "Restaurant deleted"}), 204)
        else:
            response = make_response(jsonify({"error": "Restaurant not found"}), 404)
        
        return response
    
class PizzasResource(Resource):
    def get(self):
        response = [pizza.to_dict(only=("id", "name", "ingredients")) for pizza in Pizza.query.all()]
        return make_response(jsonify(response), 200)
    
class RestaurantPizzasResource(Resource):
    def post(self):
        data = request.get_json()

        try:
            restaurant_id = data['restaurant_id']
            pizza_id = data['pizza_id']
            price = data['price']

            if price < 1 or price > 30:
                return make_response(jsonify({"errors": ["validation errors"]}), 400)
            
            # Create a new Restaurant pizza object
            new_restaurant_pizza = RestaurantPizza(restaurant_id=restaurant_id, pizza_id=pizza_id, price=price)

            db.session.add(new_restaurant_pizza)
            db.session.commit()

            response = new_restaurant_pizza.to_dict()
            return make_response(jsonify(response), 201)
            
        # Handle errors
        except KeyError as e:
            return make_response(jsonify({"errors": [f"Missing key: {str(e)}"]}), 400)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)
        finally:
            db.session.close()

api.add_resource(RestaurantsResources, "/restaurants")
api.add_resource(RestaurantResource, "/restaurants/<int:id>")
api.add_resource(PizzasResource, "/pizzas")
api.add_resource(RestaurantPizzasResource, "/restaurant_pizzas")
if __name__ == "main":
    app.run(port=5555, debug=True)

# @app.route('/restaurants', methods=['GET'])
# def get_restaurants():
#     restaurants = Restaurant.query.all()
#     return jsonify([restaurant.to_dict() for restaurant in restaurants])

# @app.route('/restaurants/<int:id>', methods=['GET'])
# def get_restaurant(id):
#     restaurant = Restaurant.query.get(id)
#     if restaurant:
#         return jsonify(restaurant.to_dict())
#     else:
#         return jsonify({"error": "Restaurant not found"}), 404

# @app.route('/restaurants/<int:id>', methods=['DELETE'])
# def delete_restaurant(id):
#     restaurant = Restaurant.query.get(id)
#     if restaurant:
#         db.session.delete(restaurant)
#         db.session.commit()
#         return '', 204
#     else:
#         return jsonify({"error": "Restaurant not found"}), 404

# @app.route('/pizzas', methods=['GET'])
# def get_pizzas():
#     pizzas = Pizza.query.all()
#     return jsonify([pizza.to_dict() for pizza in pizzas])

# @app.route('/restaurant_pizzas', methods=['POST'])
# def create_restaurant_pizza():
#     data = request.get_json()
#     try:
#         restaurant_pizza = RestaurantPizza(
#             price=data['price'],
#             pizza_id=data['pizza_id'],
#             restaurant_id=data['restaurant_id']
#         )
#         db.session.add(restaurant_pizza)
#         db.session.commit()
#         return jsonify(restaurant_pizza.to_dict()), 201
#     except ValueError as e:
#         return jsonify({"errors": [str(e)]}), 400

# if __name__ == '__main__':
#     app.run(port=5555, debug=True)