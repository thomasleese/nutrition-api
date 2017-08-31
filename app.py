import decimal
from json import JSONEncoder
import os

from flask import Flask, jsonify
from tesco import Tesco


class MyJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        else:
            return super().default(obj)


app = Flask(__name__)
app.json_encoder = MyJSONEncoder

tesco = Tesco(os.environ['TESCO_API_KEY'])


@app.route('/<gtin>')
def lookup(gtin):
    product = tesco.lookup(gtin=gtin)[0]
    return jsonify(product=product)
