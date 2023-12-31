import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
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
    )


@app.route("/api/v1.0/precipitation") #Convert query results to a dictionary using `date` as the key and `tobs` as the value
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Measurement
    results = (session.query(Measurement.date, Measurement.tobs)
                      .order_by(Measurement.date))
    
    # Create a dictionary
    precipitation_date_tobs = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["tobs"] = each_row.tobs
        precipitation_date_tobs.append(dt_dict)

    return jsonify(precipitation_date_tobs)


@app.route("/api/v1.0/stations") #Return a JSON list of stations from the dataset
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    year_ago_date= dt.date(2017, 8, 23) - dt.timedelta(days=366)
    mas = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    return { date:tmp for date,tmp in session.query(Measurement.date,Measurement.tobs).filter((Measurement.station==mas) & (Measurement.date >= year_ago_date))}

@app.route('/api/v1.0/<startDate>')
@app.route('/api/v1.0/<startDate>/<endDate>')
def dateRange(startDate, endDate = '2017-08-23'):

    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).first()

    return {'min':result[0],'avg':result[1],'max':result[2]}

if __name__ == '__main__':
    app.run(debug=True)
