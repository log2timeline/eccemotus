# -*- coding: utf-8 -*-
"""Web server interface for eccemotus.py library.

This code also serves as an example usage of eccemotus library. Be aware that it
lacks a lot of graceful error handling and recovery.
"""

import json
import sqlite3
from flask import Flask, g, jsonify, redirect, render_template, request, url_for

from eccemotus import eccemotus_lib as eccemotus

app = Flask(__name__)

# Routines for managing database.

def GetDatabase():
  """Connect to database or reuse existing connection for this session.

  Returns:
    sqlite3.Connection: access to database.
  """
  database = getattr(g, u'database', None)
  if database is None:
    database = sqlite3.connect(app.config[u'DATABASE'])
    database.row_factory = sqlite3.Row
    g.database = database
  return database

@app.teardown_appcontext
def CloseConnection(_):
  """Closes database connection if it was opened."""
  database = getattr(g, u'database', None)
  if database is not None:
    database.close()

@app.route(u'/drop')
def Drop():
  """Drops table with graphs.

  This can be used, if you want to "reset" your database.

  Return:
    str: u'dropped'.
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute(u'''DROP TABLE IF EXISTS graphs''')
  database.commit()
  return u'dropped'

@app.route(u'/prepare')
def Prepare():
  """Creates table for graphs in database.

  Returns:
    str: u'prepared'.
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute((u'''CREATE TABLE IF NOT EXISTS graphs'''
             u'''(id INTEGER PRIMARY KEY, name TEXT, graph BLOB )'''))
  database.commit()
  return u'prepared'

# Views.

@app.route(u'/graph/<graph_id>')
def ViewGraph(graph_id):
  """Returns view for specific graph.

  Actual graph data is fetched with javascript and call to GetGraph api.

  Args:
    graph_id (str|int): id of graph to retrieve from the database.

  Returns:
    str: rendered template with context.
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute(u'SELECT id, name from graphs where id = ?', (graph_id, ))
  graphs = c.fetchall()
  if len(graphs) != 1:
    return u'Database returned %d graphs. Expected 1.' % (len(graphs))

  return render_template(u'graph.html', graph=graphs[0])


@app.route(u'/api/graph/<graph_id>')
def GetGraph(graph_id):
  """Returns graph data for graph with graph_id.

  Args:
    graph_id (str|int): id of graph to retrieve from the database.

  Returns:
    str: jsonified graph data.
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute(u'SELECT id, name, graph from graphs where id = ?', (graph_id, ))
  graph = c.fetchall()
  if len(graph) != 1:
    return None

  # The string is not unicode because Row cursor can not be indexed with
  # unicode.
  return jsonify(graph=json.loads(graph[0]['graph']))

def ListGraphs():
  """Lists graphs in database

  Returns:
    list[dict]: graphs in database.
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute(u'SELECT id, name from graphs')
  data = c.fetchall()
  return data

def AddGraph(name, graph):
  """Adds graph to database.

  Args:
    name (str): graph name.
    graph (str): duped JSON representation of graph.
  """
  database = GetDatabase()
  c = database.cursor()
  c.execute(u'INSERT INTO graphs (name, graph) VALUES (?,?)', (name, graph))
  database.commit()

@app.route(u'/', methods=[u'GET', u'POST'])
def Index():
  """Initial html page.

  Contains forms for adding new graphs from elasticsearch or from file and list
  of already added graphs.
  Adding from file is possible only for files on the same machine as the server.
  This will not sent the file to server, it just provides the file name.
  Adding from elasticsearch is possible only for ip/port that does not require
  authentication and is accessible to server (preferably on the same machine).

  Returns:
    str: rendered template with context.
  """
  if request.method == u'POST':
    if request.form[u'submit'] == u'file':
      fname = request.form[u'filename']
      graph_name = request.form[u'name']
      data_generator = eccemotus.FileDataGenerator(fname, verbose=True)
      graph = eccemotus.GetGraph(data_generator, verbose=True)
      graph_JSON = json.dumps(graph.MinimalSerialize())
      AddGraph(graph_name, graph_JSON)
      return redirect(url_for(u'Index'))

    elif request.form[u'submit'] == u'elastic':
      graph_name = request.form[u'name']
      ip = request.form[u'ip']
      port = int(request.form[u'port'])
      raw_indexes = request.form[u'indexes'].replace('\n', ' ')
      indexes = [el_index for el_index in raw_indexes.split() if el_index]
      client = eccemotus.GetClient(ip, port)

      data_generator = eccemotus.ElasticDataGenerator(
          client, indexes, verbose=True)
      graph = eccemotus.GetGraph(data_generator, verbose=True)
      graph_JSON = json.dumps(graph.MinimalSerialize())
      AddGraph(graph_name, graph_JSON)
      return redirect(url_for(u'Index'))

  graphs = ListGraphs()
  return render_template(u'index.html', graphs=graphs)


def Run(host=u'127.0.0.1', port=5012, database=u'eccemotus.sql'):
  """Start flask app.

  Args:
    host (str): flask app ip address.
    port (int): port for the flask app.
    database (str): name for sqlite3 database you want to use. If it does not
        exist, if will be created.
  """
  app.config[u'DATABASE'] = database
  with app.app_context():
    Prepare()
  app.run(debug=True, host=host, port=port)

