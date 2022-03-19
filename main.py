import os
from flask import Flask, render_template
import sqlalchemy

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')
host = os.environ.get('CLOUD_SQL_HOST')

# When deployed to App Engine, the `GAE_ENV` environment variable will be
# set to `standard`
if os.environ.get('GAE_ENV') == 'standard':
    # If deployed, use the local socket interface for accessing Cloud SQL
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    engine_url = 'mysql+pymysql://{}:{}@/{}?unix_socket={}'.format(
        db_user, db_password, db_name, unix_socket)
else:
    # If running locally, use the TCP connections instead
    # Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
    # so that your application can use 127.0.0.1:3306 to connect to your
    # Cloud SQL instance

    engine_url = 'mysql+pymysql://{}:{}@{}/{}'.format(
        db_user, db_password, host, db_name)

# The Engine object returned by create_engine() has a QueuePool integrated
# See https://docs.sqlalchemy.org/en/latest/core/pooling.html for more
# information
engine = sqlalchemy.create_engine(engine_url, pool_size=3)

app = Flask(__name__)


@app.route('/')
def main():
    cnx = engine.connect()
    cursor = cnx.execute('SELECT NOW() as now;')
    result = cursor.fetchall()
    current_time = result[0][0]
    # If the connection comes from a pool, close() will send the connection
    # back to the pool instead of closing it
    cnx.close()

    return render_template('index.html', time=current_time)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

