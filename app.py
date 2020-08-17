import datetime as dt
from datetime import date as date
from datetime import timedelta
import numpy as np

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, and_

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# engine = create_engine("sqlite:///Resources/hawaii.sqlite")
enginge = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables, reflect Database into ORM classes
Base.prepare(engine, reflect=True)

# Save references to the tables as 'Measurement' and as 'Station'
# Assign measurement and station classes to the variables Measurement and Station
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Create our session (link) from Python to the DB
#################################################
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Creating an object of the class, called Flask
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

#Reference: https://github.com/pallets/flask/issues/974
app.config["JSON_SORT_KEYS"] = False

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- List of prior year rain totals from all stations.<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- List of Station numbers and names.<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- List of prior year temperatures from all stations.<br/>"
        f"<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"- Given a start date (YYYY-MM-DD), (i.e., /api/v1.0/temp/2016-01-01), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date.<br/>"
        f"- Start date as early as 2010-01-01, end date as late as 2017-08-23.<br/>"
        f"<br/>"
        f"/api/v1.0/temp/<start>/<end><br/>"
        f"- Given a start and an end date (YYYY-MM-DD), (i.e., /api/v1.0/temp/2016-01-01/2016-01-07), calculates the MIN/AVG/MAX temperature for dates between the start and end date inclusive.<br/>"
        f"- Start date as early as 2010-01-01, end date as late as 2017-08-23.<br/>"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns a list of the data sets last year's precipitation"""

    # Query current or latest date in dataset, obtain last year's precip data from current date.
    last_year= dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query to retrieve the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= last_year).\
            order_by(Measurement.date).all()
    
    # Convert query results to Dictionary using `date` as the key and `prcp` as the value.
    # Create a dictionary from each row of data, and append to precip_list, ceating list of dictionaries.
    precip_list = []
    for row in results:
        precip_dict = {}
        precip_dict['date'] = row.date
        precip_dict['prcp'] = row.prcp
        precip_list.append(precip_dict)
    # Return the JSON representation.
    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    """Returns a JSON list of stations from the dataset"""

    results = session.query(Measurement.station, Station.name).\
            filter(Measurement.station == Station.station).\
            group_by(Station.name).all()
    
    station_list = []
    for row in results:
        station_dict = {}
        station_dict['station'] = row.station
        station_dict['name'] = row.name
        station_list.append(station_dict)
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a JSON list of Temperature Observations (tobs) for the previous year"""

    #Query latest date (last data point) in dataset, obtain last year's precip data from latest date.
    latest_date = session.query(func.max(Measurement.date)).all()
    latest_date_ls = [list(item) for item in latest_date][0]
    latest_date_ls = latest_date_ls[0]
    last_year= dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Query for the dates and temperature observations from a year from the last data point
    results = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.date >= last_year).\
            filter(Measurement.date <= latest_date_ls).\
            order_by(Measurement.date).all()
    
    #Return a JSON list of Temperature Observations (tobs) for the previous year
    tobs_list = []
    for row in results:
        tobs_dict = {}
        tobs_dict['date']= row.date
        tobs_dict['tobs'] = row.tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs_list)

@app.route("/api/v1.0/temp/<start>")
def temp_start(start=None):
    """Returns a JSON list of 'Tmin', 'Tavg' and 'Tmax' for all dates greater than & equal to a given start range."""

    # Query calculate Tmin, Tavg, Tmax for all dates greater than and equal to the start date.
    results = session.query(func.min(Measurement.tobs).label('min'),\
         func.avg(Measurement.tobs).label('avg'),\
         func.max(Measurement.tobs).label('max')).\
         filter(Measurement.date >= start).all()
    
    start_temp_list= []
    for row in results:
        start_dict = {}
        start_dict['Start Date']= start
        start_dict['Min Temp'] = row.min
        start_dict['Averge Temp'] = row.avg
        start_dict['Max Temp'] = row.max
        start_temp_list.append(start_dict)
    
    return jsonify(start_temp_list)

@app.route("/api/v1.0/temp/<start>/<end>")
def temp_start_end(start=None, end=None):
    """Return a json list of the minimum temperature, the average temperature, 
    and the max temperature for a given start-end date range."""
    
    # Query for the Tmin, Tavg, Tmax for dates between the start and end date inclusive.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    # Create a dictionary from the row data and append to a list.
    temp_end = []
    for Tmin, Tmax, Tavg in results:
        temp_end_dict = {}
        temp_end_dict['Start Date']= start
        temp_end_dict['End Date']= end
        temp_end_dict["Min Temp"] = Tmin
        temp_end_dict["Average Temp"] = Tavg
        temp_end_dict["Max Temp"] = Tmax
        temp_end.append(temp_end_dict)
    
    return jsonify(temp_end)

if __name__ == '__main__':
    app.run(debug=True)


    
