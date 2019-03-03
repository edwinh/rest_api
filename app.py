from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from datetime import datetime

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Initialize db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# To create db:
# from app import db
# db.create_all()

# Measurement Class
class ElectricityMeasurement(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  dt = db.Column(db.DateTime)
  kwh_c1 = db.Column(db.Float)
  kwh_c2 = db.Column(db.Float)

  def __init__(self, dt, kwh_c1, kwh_c2):
    self.dt = dt
    self.kwh_c1 = kwh_c1
    self.kwh_c2 = kwh_c2

# Measurement schema
class ElectricityMeasurementSchema(ma.Schema):
  class Meta:
    fields = ('id', 'dt', 'kwh_c1', 'kwh_c2')

# Init schema
electricity_measurement_schema = ElectricityMeasurementSchema(strict=True)
electricity_measurements_schema = ElectricityMeasurementSchema(many=True, strict=True)

# Create a measurement
@app.route('/electricity', methods=['POST'])
def add_electricity():
  print(request)
  dt = datetime.strptime(request.json['dt'], '%Y-%m-%dT%H:%M:%S.%fZ')
  kwh_c1 = request.json['kwh_c1']
  kwh_c2 = request.json['kwh_c2']

  new_electricity = ElectricityMeasurement(dt, kwh_c1, kwh_c2)

  db.session.add(new_electricity)
  db.session.commit()

  return electricity_measurement_schema.jsonify(new_electricity)

# Get all elec measurements
@app.route('/electricity', methods=['GET'])
def get_elecmeasurements():
  all_measurements = ElectricityMeasurement.query.all()
  result = electricity_measurements_schema.dump(all_measurements)
  return jsonify(result.data)

# Get single measurement
@app.route('/electricity/<id>', methods=['GET'])
def get_elecmeasurement(id):
  measurement = ElectricityMeasurement.query.get(id)
  return electricity_measurement_schema.jsonify(measurement)

# Update a measurement
@app.route('/electricity/<id>', methods=['PUT'])
def update_measurement(id):
  measurement = ElectricityMeasurement.query.get(id)

  dt = datetime(request.json['dt'])
  kwh_c1 = request.json['kwh_c1']
  kwh_c2 = request.json['kwh_c2']

  measurement.dt = dt
  measurement.kwh_c1 = kwh_c1
  measurement.kwh_c2 = kwh_c2

  db.session.commit()

  return electricity_measurement_schema.jsonify(measurement)

# Delete measurement
@app.route('/electricity/<id>', methods=['DELETE'])
def delete_measurement(id):
  measurement = ElectricityMeasurement.query.get(id)
  db.session.delete(measurement)
  db.session.commit()
  return electricity_measurement_schema.jsonify(measurement)

if __name__ == '__main__':
  app.run(debug=True)