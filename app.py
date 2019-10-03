import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from datetime import datetime

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve the last 12 months of precipitation data."""
    # Query to retrieve the last 12 months of precipitation data.
    query_date = dt.date(2017,8,23)- dt.timedelta(days=365)
    results = session.query(Measurement.id,Measurement.station, Measurement.date,Measurement.prcp,Measurement.tobs).\
    filter(Measurement.date >= query_date).all()
       
    session.close()
    
    # Create a dictionary from the row data and append to a list 
    prcp_data = []
    for id, station,date, prcp,tobs in results:
        prcp_dict = {}
        prcp_dict["id"] = id
        prcp_dict["station"] = station
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_dict["tobs"] = tobs
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def stn():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve list of stations from the dataset"""
    # Query to list of stations from the dataset
    results=session.query(Measurement.station).distinct().all()
  
    session.close()
      
    stn_data = list(np.ravel(results))


    return jsonify(stn_data)
    #return (f"List of stations:<br/>")

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """query for the dates and temperature observations from a year from the last data point.
      * Return a JSON list of Temperature Observations (tobs) for the previous year."""
    query_date = dt.date(2017,8,23)- dt.timedelta(days=365)
    results = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >= query_date).all()
  
    session.close()
    
    # Create a dictionary from the row data and append to a list 
    tobs_list=[]
    tobs_dict={}
    for date , tobs in results:
        tobs_dict["date"]=date
        tobs_dict["tobs"]=tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")

def calc_temps(start):
    """TMIN, TAVG, and TMAX for for all dates greater than and equal to the start date..
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
       
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()

    session.close()
    
    strt_data = list(np.ravel(results))

    return jsonify(strt_data)

@app.route("/api/v1.0/<start>/<end>")

def calc(start,end):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)
    
    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()
    
    end_data = list(np.ravel(results))

    return jsonify(end_data)


if __name__ == '__main__':
    app.run(debug=True)
