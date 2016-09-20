""" Provides basic methods for storing lateral movement logs in property Graph.

For Default use-case, call create_graph(data).minimal_serialize().
This returns json representation of property graph. This can be directly send to
javascript visualization.
"""

from __future__ import print_function
from collections import defaultdict as dfd
import sys

import eccemotus.lib.parsers as P


class Graph(object):
  """Very light-weighed implementation of property graph.

    This implementation is not meant to be a general property graph.
    It is meant for storing information about lateral movement.

    Property graph is a set of nodes and edges, where each edge and each node
    can have any number of key/value properties associated with them.

    In our case, we have a very specific set of properties.
    nodes:
      id: Automatic generated unique id
      type: Type/name of the node
            These correspond to information names in parsers.parsers module
      value: Value that the node has.
    Pair (tuple) (type, value) is also unique identifier of a node.

    edge:
      source: Id of a source node
      target: Id of a target node
      type: Type of an edge
        Usual types are
          has: Machine has an user
          is: Machine is ip_address (this is not necessarily true for the whole
              time)
          access: ssh connection
      events:
        List of event ids and timestamps. Those events are responsible for
        creation of given edge. Events can be found by id in timesketch or
        filtered by timestamps.
    In fact, every edge is a graph represents multiple edges created by multiple
    events. Those events are specified in events property of this node.

    In theory, edges are directed. In practice, only place where it makes a
    difference is visualization.

    This dictionary (not class) based implementation has its meaning. It is
    easily extensible and prone to data integrity errors. It also has direct
    mapping to data, that can be used in javascript (d3) visualization.

    """

  def __init__(self):
    """Initialize empty graph."""
    self.edges = []
    self.edges_ids = dfd(int)  # Provides fast index for edges
    self.nodes = []
    self.nodes_ids = dfd(int)  # Provides fast index for nodes

  def get_add_node(self, node_type, node_value):
    """Return node's id or create a new one if it does not exist."""

    node = (node_type, node_value)
    if node not in self.nodes_ids:
      self.nodes_ids[node] = len(self.nodes_ids)
      self.nodes.append({
          "id": self.nodes_ids[node],
          "value": node_value,
          "type": node_type
      })

    return self.nodes_ids[node]

  def add_edge(self,
               source_id,
               target_id,
               edge_type,
               timestamp=None,
               event_id=None):
    """Add new edge to graph or just add new event to existing edge."""

    edge = (source_id, target_id, edge_type)
    if edge in self.edges_ids:
      edge_id = self.edges_ids[edge]
      self.edges[edge_id]["events"].append({"id": event_id,
                                            "timestamp": timestamp})

    else:
      edge_id = len(self.edges)
      self.edges_ids[edge] = edge_id
      self.edges.append({
          "source": source_id,
          "target": target_id,
          "type": edge_type,
          "events": [({"id": event_id,
                       "timestamp": timestamp})],
      })

  EDGE_HAS = "has"
  EDGE_IS = "is"
  EDGE_ACCEESS = "access"
  SIMPLE_RULES = [
      (P.SOURCE_MACHINE_IP, P.SOURCE_MACHINE_NAME, EDGE_IS),
      (P.SOURCE_USER_NAME, P.SOURCE_USER_ID, EDGE_IS),
      (P.TARGET_MACHINE_NAME, P.TARGET_MACHINE_IP, EDGE_IS),
      (P.TARGET_USER_NAME, P.TARGET_USER_ID, EDGE_IS),
      (P.SOURCE_MACHINE_IP, P.SOURCE_USER_NAME, EDGE_HAS),
      (P.SOURCE_MACHINE_IP, P.SOURCE_USER_ID, EDGE_HAS),
      (P.SOURCE_MACHINE_NAME, P.SOURCE_USER_NAME, EDGE_HAS),
      (P.SOURCE_MACHINE_NAME, P.SOURCE_USER_ID, EDGE_HAS),
      (P.TARGET_MACHINE_IP, P.TARGET_USER_NAME, EDGE_HAS),
      (P.TARGET_MACHINE_IP, P.TARGET_USER_ID, EDGE_HAS),
      (P.TARGET_MACHINE_NAME, P.TARGET_USER_NAME, EDGE_HAS),
      (P.TARGET_MACHINE_NAME, P.TARGET_USER_ID, EDGE_HAS),

      #(P.TARGET_PLASO, P.TARGET_MACHINE_NAME, EDGE_IS),
  ]

  def get_ssh_source(self, event):
    """ Return best most specific ssh_source."""

    # List of things that should be used as ssh source in decreasing priority.
    SSH_SOURCE = [P.SOURCE_USER_NAME, P.SOURCE_USER_ID, P.SOURCE_MACHINE_NAME,
                  P.SOURCE_MACHINE_IP, P.SOURCE_PLASO]
    for key in SSH_SOURCE:
      if key in event:
        return key, event[key]
    return None, None

  def get_ssh_target(self, event):
    """ Return best most specific ssh_target."""

    # List of things that should be used as ssh target in decreasing priority.
    SSH_TARGET = [P.TARGET_USER_NAME, P.TARGET_USER_ID, P.TARGET_MACHINE_NAME,
                  P.TARGET_MACHINE_IP, P.TARGET_PLASO]
    for key in SSH_TARGET:
      if key in event:
        return key, event[key]
    return None, None

  def add_data(self, source_type, source_value, target_type, target_value,
               edge_type, event_time, event_id):
    """Add edge with corresponding nodes to graph."""

    source_id = self.get_add_node(P.get_type(source_type), source_value)
    target_id = self.get_add_node(P.get_type(target_type), target_value)
    self.add_edge(source_id, target_id, edge_type, event_time, event_id)

  def add_event(self, event):
    """ Processes one parsed event and encodes it to edges and nodes.

        Encoding is based on simple rules. (source, target, edge_type).
        source and target are almost (prefix "source:"/"target:" must be
        removed) types of new nodes. They are also keys to event dictionary
        which provides value for a given node.
        """

    #Simple rules for ownership and identity
    for rule in self.__class__.SIMPLE_RULES:
      # Removing target:/source: prefix
      source_value = event.get(rule[0])

      target_value = event.get(rule[1])
      if not (source_value and target_value):
        continue

      self.add_data(rule[0], source_value, rule[1], target_value, rule[2],
                    event[P.TIMESTAMP], event[P.EVENT_ID])

    #Rules for access edge

    ssh_source_type, ssh_source_value = self.get_ssh_source(event)
    ssh_target_type, ssh_target_value = self.get_ssh_target(event)
    if ssh_source_value and ssh_target_value:
      self.add_data(ssh_source_type, ssh_source_value, ssh_target_type,
                    ssh_target_value, self.__class__.EDGE_ACCEESS,
                    event[P.TIMESTAMP], event[P.EVENT_ID])

  def minimal_serialize(self):
    """Serialized only required information for visualization."""
    return {"nodes": self.nodes, "links": self.edges}


def create_graph(data, verbose=False):
  """Creates graph from data.

  Args:
    data (iterable): parsed plaso events.

  Returns:
    Graph: property graph for events.

  data can be any iterable (list), but preferably generator, because of memory
  optimization.
  """
  graph = Graph()
  for i, event in enumerate(data):
    graph.add_event(event)
    if not i % 1000 and verbose:
      print(
          "Nodes:%d Edges: %d" % (len(graph.nodes), len(graph.edges)),
          file=sys.stderr)

  return graph


