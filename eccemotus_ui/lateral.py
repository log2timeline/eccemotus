""" Web server interface for eccemotus.py library.

This code also serves as an example usage of this library. Be aware that it
lacks a lot of graceful error handling.
"""

from __future__ import print_function

import json
import sqlite3
from flask import Flask, g, jsonify, redirect, render_template, request, url_for

import eccemotus.eccemotus as E

app = Flask(__name__)

# Routines for managing database.

def GetDatabase():
  """Connect to database or reuse existing connection for this session.

  Returns:
    sqlite3.Connection: access to database.

  Returns database object."""
  database = getattr(g, 'database', None)
  if database is None:
    database = sqlite3.connect(app.config['DATABASE'])
    database.row_factory = sqlite3.Row
    g.database = database
  return database

@app.teardown_appcontext
def CloseConnection(_):
  """Closes database connection if it was opened."""
  database = getattr(g, 'database', None)
  if database is not None:
    database.close()

@app.route('/drop')
def Drop():
  """Drops table with graphs.

  This can be used, if you want to "reset" your database.
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute('''DROP TABLE IF EXISTS graphs''')
  database.commit()
  return 'dropped'

@app.route('/prepare')
def Prepare():
  """Creates table for graphs in database."""
  database = GetDatabase()
  c = database.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS graphs
      (id INTEGER PRIMARY KEY, name TEXT, graph BLOB )''')
  database.commit()
  return 'prepared'

@app.route('/graph/<graph_id>')
def ViewGraph(graph_id):
  """Returns view for specific graph.

  Actual graph data is fetched with javascript and call to GetGraph.
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute('SELECT id, name from graphs where id = ?', (graph_id, ))
  graphs = c.fetchall()
  if len(graphs) != 1:
    return 'Database returned %d graphs. Expected 1.' % (len(graphs))

  return render_template('graph.html', graph=graphs[0])


@app.route('/api/graph/<graph_id>')
def GetGraph(graph_id):
  """Returns graph data for graph with graph_id. """
  database = GetDatabase()
  c = database.cursor()
  c.execute('SELECT id, name, graph from graphs where id = ?', (graph_id, ))
  graph = c.fetchall()
  if len(graph) != 1:
    return None

  return jsonify(graph=json.loads(graph[0]['graph']))

def ListGraphs():
  """Returns list of graphs in database."""
  database = GetDatabase()
  c = database.cursor()
  c.execute('SELECT id, name from graphs')
  data = c.fetchall()
  return data

def AddGraph(name, graph):
  """ Routine for adding graph data to database.

  Args:
    name (str): graph name.
    graph (str): duped json representation of graph.

  Returns:
    None
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute('INSERT INTO graphs (name, graph) VALUES (?,?)', (name, graph))
  database.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
  """Initial html page.

  Contains forms for adding new graphs from elasticsearch or from file and list
  of already added graphs.
  Adding from file is possible only for files on the same machine as the server.
  This will not sent the file to server, it just provides the file name.
  Adding from elasticsearch is possible only for ip/port that does not require
  authentication and is accessible to server (preferably on the same machine).
  """
  if request.method == 'POST':
    if request.form['submit'] == 'file':
      fname = request.form['filename']
      graph_name = request.form['name']
      data_generator = E.FileDataGenerator(fname, verbose=True)
      graph = E.GetGraph(data_generator, verbose=True)
      graph_json = json.dumps(graph.MinimalSerialize())
      add_graph(graph_name, graph_json)
      return redirect(url_for('index'))

    elif request.form['submit'] == 'elastic':
      graph_name = request.form['name']
      ip = request.form['ip']
      port = int(request.form['port'])
      raw_indexes = request.form['indexes'].replace('\n', ' ')
      indexes = [el_index for el_index in raw_indexes.split() if el_index]
      client = E.GetClient(ip, port)

      data_generator = E.ElasticDataGenerator(client, indexes, verbose=True)
      graph = E.GetGraph(data_generator, verbose=True)
      graph_json = json.dumps(graph.MinimalSerialize())
      add_graph(graph_name, graph_json)
      return redirect(url_for('index'))

  graphs = ListGraphs()
  return render_template('index.html', graphs=graphs)


def run(host='127.0.0.1', port=5012, database='eccemotus.sql'):
  """Start flask app.

  Args:
    host (str): flask app ip address.
    port (int): port for the flask app.
    database (str): name for sqlite3 database you want to use. If it does not
        exist, if will be created.

  Returns:
    None

  """
  app.config['DATABASE'] = database
  with app.app_context():
    Prepare()
  app.run(debug=True, host=host, port=port)

