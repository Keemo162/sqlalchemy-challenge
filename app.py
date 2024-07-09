# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import timedelta
# Given date
from datetime import datetime
import json
#################################################
# Database Setup
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
# View all of the classes that automap found
Base.classes.keys()
['station', 'measurement']
# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2017-01-04<br/>"
        f"/api/v1.0/2017-01-04/2017-01-05<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value."""
    """Return the JSON representation of your dictionary."""
    given_date = datetime(2017, 8, 23)

    # Calculate the date 12 months ago
    last_12_months_date = given_date - timedelta(days=365)

    

    last_12_mnths_of_prcp = session.query(measurement.date,measurement.prcp).\
    filter (measurement.date >= last_12_months_date.date()).all()
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    last_12_months_precipitation = {date: prcp for date, prcp in last_12_mnths_of_prcp}

    # Convert the dictionary to JSON format.
    json_data = json.dumps(last_12_months_precipitation)
    return jsonify(json_data)

@app.route("/api/v1.0/stations")
def station():
    """Return a JSON list of stations from the dataset."""

    # Design a query to find the most active stations (i.e. which stations have the most rows?)
    # List the stations and their counts in descending order.
    sel = [measurement.station, func.count(measurement.station)]
    query = session.query(*sel).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc())
    mylist=[]

    for row in query.all():
        mylist .append ({row[0]: row[1]})
    json_data = json.dumps(mylist)
    return jsonify(json_data)
         
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    # Identify the most active station
    sel = [measurement.station, func.count(measurement.station)]
    query = session.query(*sel).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc())
    most_active_station = query.first()[0]

    # Calculate the date one year ago from the last date in data set
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    one_year_ago = (datetime.strptime(latest_date, '%Y-%m-%d') - timedelta(days=365)).strftime('%Y-%m-%d')

    # Query the last 12 months of temperature observation data for this station
    sel = [measurement.date,measurement.tobs]
    query = session.query(*sel).\
    filter(measurement.station == most_active_station).\
    filter(measurement.date >= one_year_ago)
    temperature_observations = [{row[0]: row[1]} for row in query.all()]
    return jsonify(temperature_observations)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature(start=None,end=None):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    #start="2017-01-04"
    sel = [func.min(measurement.tobs),
       func.max(measurement.tobs),
       func.avg(measurement.tobs)]

    query = session.query(*sel).\
    filter(measurement.date >= start)
    min_max_avg = [{"min":row[0],"max":row[1],"avg":row[2]} for row in query.all()]

    sel = [func.min(measurement.tobs),
           func.max(measurement.tobs),
           func.avg(measurement.tobs)]

    if end:  # If end date is provided
        query = session.query(*sel).\
                filter(measurement.date >= start).\
                filter(measurement.date <= end)
    else:  # If only start date is provided
        query = session.query(*sel).\
                filter(measurement.date >= start)

    min_max_avg = [{"min": row[0], "max": row[1], "avg": row[2]} for row in query.all()]

    return jsonify(min_max_avg)
   

if __name__ == "__main__":
    app.run(debug=True)


