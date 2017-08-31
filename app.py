import decimal
from json import JSONEncoder
import os

import bson
from flask import Flask, jsonify
from flask_pymongo import PyMongo
import pymongo
from tesco import Tesco
import tesco.data


class MyJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        elif isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
        else:
            return super().default(obj)


app = Flask(__name__)
app.json_encoder = MyJSONEncoder

tesco = Tesco(os.environ['TESCO_API_KEY'])

mongo = PyMongo(app)

with app.app_context():
    mongo.db.products.create_index('gtin', unique=True)


def jsonify_product(product):
    def jsonify_serving(serving):
        return {
            'description': serving.description,
            'nutrients': {
                key: {'units': nutrient.units, 'value': str(nutrient.value)}
                for key, nutrient in serving.nutrients.items()
            },
        }

    return {
        'gtin': str(int(product.gtin)),
        'description': product.description,
        'nutrition': {
            'per_100': jsonify_serving(product.nutrition.per_100),
            'per_serving': jsonify_serving(product.nutrition.per_serving),
        }
    }

@app.route('/product/<int:gtin>')
def lookup(gtin):
    saved_product = mongo.db.products.find_one({'gtin': str(gtin)})
    if saved_product:
        return jsonify(product=saved_product)

    tesco_product = tesco.lookup(gtin=gtin)[0]
    saved_product = jsonify_product(tesco_product)

    mongo.db.products.insert(saved_product)

    return jsonify(product=saved_product)
