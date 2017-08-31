import decimal
from json import JSONEncoder
import os

from flask import Flask, jsonify
from tesco import Tesco
import tesco.data


class MyJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        else:
            return super().default(obj)


app = Flask(__name__)
app.json_encoder = MyJSONEncoder

tesco = Tesco(os.environ['TESCO_API_KEY'])


def jsonify_product(product):
    def jsonify_serving(serving):
        return {
            'description': serving.description,
            'nutrients': {
                key: {'units': nutrient.units, 'value': nutrient.value}
                for key, nutrient in serving.nutrients.items()
            },
        }

    return {
        'gtin': product.gtin,
        'description': product.description,
        'nutrition': {
            'per_100': jsonify_serving(product.nutrition.per_100),
            'per_serving': jsonify_serving(product.nutrition.per_serving),
        }
    }

@app.route('/product/<gtin>')
def lookup(gtin):
    product = tesco.lookup(gtin=gtin)[0]

    return jsonify(product=jsonify_product(product))
