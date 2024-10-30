# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
#1. start the homepage / list all avalable routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API! <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )

#2. Convert the query results to a dictionary by using date as the key and prcp as the value.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # start a session:
    session = Session(engine)
    # query to return all date and precipitation data:
    results = session.query(Measurement.date, Measurement.prcp).all()

    # convert results to a dictionary with date as key and prcp as value
    prcp_data = {date:prcp for date, prcp in results}
    #close session:
    session.close()

    # Return to JSON representation of the dictionary
    return jsonify(prcp_data)

#3.Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():
    #satrt a session
    session =Session(engine)
    # select field from the station table
    select_fields = [Station.station, Station.name, Station.latitude, Station.longitude, station.elevation]

    #query all station data
    query_results = session.query(*select_fields).all()
    #close session
    session.close()

    #Covert results in to a Dictionary
    stations = [
        {
            "Station":station,
            "Name":name,
            "Lat":lat,
            "Lon":lon,
            "Elevation":el
        }
        for station, name, lat,lon,el in query_results
    ]
    #return JSON list of stations
    return jsonify(stations)

#4.Query the dates and temperature observations of the most-active station for the previous year of data.
#- Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # start a session
    session= Session(engine)
    #Query the dates and temperature observations of the most-active station for the previous year of data.
    results =session.query(Measurement.tobs).filter(Measurement.station=='USC00519281')\
    .filter(Measurement.date>='2016-08-23').all()
    #close session
    session.close()

    #convert query result to a list of dictionaries
    tob_result = [{"Date":date, "Tobs":tobs} for date, tobs in results]
    #Return a JSON list of temperature observations for the previous year.
    return jsonify(tob_result)

#5./api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def start_temps(start):
    #start a session
    session =Session(engine)
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    temperature= session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
    .filter(Measurement.date >=start).all()
    #close session
    session.close()

    #list of the minimum temperature, the average temperature, and the maximum temperature for a specified start
    temp_results = [{"Minimum Temperature":min_temp, "Average Temperature":avg_temp, "Maximum Temperature":max_temp}
                    for min_temp, avg_temp, max_temp in temperature]
    #Returen JSON list for a sopecified start
    return jsonify(temp_results)

@app.route("/api/v1.0/<start>/<end>")
def start_end_temps(start, end):
    #start a session
    session = Session(engine)
    ## For a specified start- end, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start end range.
    temperature= session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs))\
    .filter(Measurement.date >=start).filter(Measurement.date<=end).all()
    #close session
    session.close()

   #the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range 
    temp_results = [{"Minimum Temperature":min_temp, "Average Temperature":avg_temp, "Maximum Temperature":max_temp}
                    for min_temp, avg_temp, max_temp in temperature]
    #Returen JSON list for a sopecified start
    return jsonify(temp_results)
    
if __name__ == '__main__':
    app.run(debug=True)
