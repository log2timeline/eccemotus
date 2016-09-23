""" Example usage of eccemotus.py library."""
from __future__ import print_function

import json
import sqlite3
from flask import Flask, g, jsonify, redirect, render_template, request, url_for

import eccemotus.eccemotus as E

app = Flask(__name__)

# Routines for managing database.

def get_db():
  """Returns database object."""
  db = getattr(g, 'database', None)
  if db is None:
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    g.database = db
  return db

@app.teardown_appcontext
def close_connection(_):
  """Closes database connection if it was opened."""
  db = getattr(g, 'database', None)
  if db is not None:
    db.close()

@app.route('/drop')
def drop():
  """Drops table with graphs.

  This can be used, if you want to "reset" your database.
  """
  db = get_db()
  c = db.cursor()
  c.execute('''DROP TABLE IF EXISTS graphs''')
  db.commit()
  return 'dropped'

@app.route('/prepare')
def prepare():
  """Creates table for graphs is database."""
  db = get_db()
  c = db.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS graphs
      (id INTEGER PRIMARY KEY, name TEXT, graph BLOB )''')
  db.commit()
  return 'prepared'

@app.route('/graph/<graph_id>')
def graph_viewer(graph_id):
  """Returns html for specific graph.

  Actual graph data is fetched with javascript and call to graph_geter.
  """
  db = get_db()
  c = db.cursor()
  c.execute('SELECT id, name from graphs where id = ?', (graph_id, ))
  graphs = c.fetchall()
  if len(graphs) != 1:
    return 'Database returned %d graphs. Expected 1.' % (len(graphs))

  return render_template('graph.html', graph=graphs[0])


@app.route('/api/graph/<graph_id>')
def graph_geter(graph_id):
  """Returns graph data for graph with graph_id. """
  db = get_db()
  c = db.cursor()
  c.execute('SELECT id, name, graph from graphs where id = ?', (graph_id, ))
  graph = c.fetchall()
  if len(graph) != 1:
    return None

  return jsonify(graph=json.loads(graph[0]['graph']))


def list_graphs():
  """Returns list of graphs in database."""
  db = get_db()
  c = db.cursor()
  c.execute('SELECT id, name from graphs')
  data = c.fetchall()
  return data

def add_graph(name, graph):
  """ Routine for adding graph data to database."""
  db = get_db()
  c = db.cursor()
  c.execute('INSERT INTO graphs (name, graph) VALUES (?,?)', (name, graph))
  db.commit()

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
      data_generator = E.file_data_generator(fname, verbose=True)
      graph = E.get_graph_json(data_generator, verbose=True)
      add_graph(graph_name, graph)
      return redirect(url_for('index'))

    elif request.form['submit'] == 'elastic':
      graph_name = request.form['name']
      ip = request.form['ip']
      port = int(request.form['port'])
      raw_indexes = request.form['indexes'].replace('\n', ' ')
      indexes = [el_index for el_index in raw_indexes.split() if el_index]
      client = E.get_client(ip, port)

      data_generator = E.elastic_data_generator(client, indexes, verbose=True)
      graph = E.get_graph_json(data_generator, verbose=True)
      add_graph(graph_name, graph)
      return redirect(url_for('index'))

  graphs = list_graphs()
  return render_template('index.html', graphs=graphs)


def run(host=u'127.0.0.1', port=5012, database='eccemotus.sql'):
  """Start flask app. """
  app.config['DATABASE'] = database
  with app.app_context():
    prepare()
  app.run(debug=True, host=host, port=port)

