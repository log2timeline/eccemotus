# -*- coding: utf-8 -*-
"""Provides basic methods for storing lateral movement logs in property Graph.

For default use-case, call CreateGraph(data).MinimalSerialize().
This returns json representation of property graph. It can be directly send to
javascript visualization.
"""

from collections import defaultdict
from collections import namedtuple
import logging

from eccemotus.lib import event_data


class Graph(object):
  """Very light-weight implementation of property graph.

  This implementation is not meant to be a general property graph. It is meant
  for storing event data about lateral movement. Property graph is a set of
  nodes and edges, where each edge and each node can have any number of
  key/value properties associated with them.

  In our case, we have a very specific set of properties.
  nodes:
    id: Automatic generated unique id
    type: Type/name of the node. These correspond to EventDatum.NAME.
    value: Value that the node has.
  Pair (tuple) (type, value) is also unique identifier of a node.

  edge:
    source: Id of a source node
    target: Id of a target node
    type: Type of an edge
      Usual types are
        "has": Machine has an user
        "is": Machine is ip_address (this is not necessarily true for the whole
            time)
        "access": remote connection
    events:
      List of event ids and timestamps. Those events are responsible for
      creation of given edge. Events can be found by id in timesketch or
      filtered by timestamps.
  In fact, every edge in a graph represents multiple edges created by multiple
  events. Those events are specified in events property of this node.

  In theory, edges are directed. In practice, only place where it makes a
  difference is visualization.

  This dictionary (not class) based implementation has its meaning. It is
  easily extensible and prone to data integrity errors. It also has direct
  mapping to data, that can be used in javascript (d3) visualization.

  Attributes:
    edges (list): list of graph edges.
    edges_ids (defaultdict[tuple, int]): maps tuple serialized edges to their
        ids.
    nodes (list): list of graph nodes.
    nodes_ids (defaultdict[tuple, int]): maps tuple serialized nodes to their
        ids.
  """

  # Edge types.
  EDGE_HAS = u'has'
  EDGE_IS = u'is'
  EDGE_ACCESS = u'access'

  # Rules describing which pairs of event_data should create which type of
  # edge.
  Rule = namedtuple(u'Rule', [u'source', u'target', u'type'])
  RULES = (
      Rule(
          event_data.Ip(source=True), event_data.MachineName(source=True),
          EDGE_IS),
      Rule(
          event_data.UserName(source=True), event_data.UserId(source=True),
          EDGE_IS),
      Rule(
          event_data.MachineName(target=True), event_data.Ip(target=True),
          EDGE_IS),
      Rule(
          event_data.UserName(target=True), event_data.UserId(target=True),
          EDGE_IS),
      Rule(
          event_data.Ip(source=True), event_data.UserName(source=True),
          EDGE_HAS),
      Rule(
          event_data.Ip(source=True), event_data.UserId(source=True), EDGE_HAS),
      Rule(
          event_data.MachineName(source=True), event_data.UserName(source=True),
          EDGE_HAS),
      Rule(
          event_data.MachineName(source=True), event_data.UserId(source=True),
          EDGE_HAS),
      Rule(
          event_data.Ip(target=True), event_data.UserName(target=True),
          EDGE_HAS),
      Rule(
          event_data.Ip(target=True), event_data.UserId(target=True), EDGE_HAS),
      Rule(
          event_data.MachineName(target=True), event_data.UserName(target=True),
          EDGE_HAS),
      Rule(
          event_data.MachineName(target=True), event_data.UserId(target=True),
          EDGE_HAS)
  )

  # List of things that should be used as remote source/target in decreasing
  # priority.
  DATA_PRIORITY = (
      event_data.UserName, event_data.UserId, event_data.MachineName,
      event_data.Ip, event_data.StorageFileName)

  def __init__(self):
    """Initializes empty graph."""
    self.edges = []
    self.edges_ids = defaultdict(int)  # Provides fast index for edges.
    self.nodes = []
    self.nodes_ids = defaultdict(int)  # Provides fast index for nodes.

  def GetAddNode(self, node_type, node_value):
    """Gets node's id with given type and value.

    If the node does not exist, it is created.

    Args:
      node_type (str): type of node derived from event datum names.
      node_value (str): value of the node.

    Returns:
      int: identifier of node. This is a position of node in self.nodes.
    """
    node = Node(node_type, node_value)
    if node.ToTuple() not in self.nodes_ids:
      node.id = len(self.nodes)
      self.nodes_ids[node.ToTuple()] = node.id
      self.nodes.append(node.ToDict())

    return self.nodes_ids[node.ToTuple()]

  def AddEdge(self, source_id, target_id, edge_type, timestamp, event_id):
    """Adds new edge to graph or just adds new event to existing edge.

    Args:
      edge_type (str): type of the edge (currently "has", "is" or "access").
      event_id (int|str): identifier for event responsible for this edge.
      source_id (int): id of source node.
      target_id (int): id of target node.
      timestamp (int): timestamp when event happened.
    """
    edge = (source_id, target_id, edge_type)
    if edge in self.edges_ids:
      edge_id = self.edges_ids[edge]
      event = {
          u'id': event_id,
          u'timestamp': timestamp
      }
      self.edges[edge_id][u'events'].append(event)
    else:
      edge_id = len(self.edges)
      self.edges_ids[edge] = edge_id
      event = {
          u'id': event_id,
          u'timestamp': timestamp
      }
      self.edges.append({
          u'source': source_id,
          u'target': target_id,
          u'type': edge_type,
          u'events': [event],
      })

  @classmethod
  def GetRemote(cls, data, source=False, target=False):
    """Gets most specific remote source/target.

    Knowing that the remote connection was from user Dean is better than knowing
    only the ip address.
    Note that user name and user id is extended by machine identifier so the
    information about machine is not lost.

    Args:
      data (event_data.EventData): data about event.
      source (bool): whether to find source.
      target (bool): whether to find target.

    Returns:
      event_data.EventDatum|None: most specific event data about source/target.
          None if no event data were found.

    Exactly one of source, target arguments should be True. Otherwise the
    function do not raise an error, but it does not make sense.
    """
    for data_class in cls.DATA_PRIORITY:
      raw_datum = data_class(source=source, target=target)
      event_datum = data.Get(raw_datum)
      if event_datum:
        return event_datum
    return None


  def AddData(
      self, source_datum, target_datum, edge_type, event_time, event_id):
    """Adds edge with corresponding nodes to graph.

    This ensures that required nodes are in the graph and creates an edge
    between them.

    Args:
      edge_type (str): edge type.
      event_id (int|str): event identifier.
      event_time (str): timestamp for event.
      source_datum (event_data.EventDatum): event datum about source node.
      target_datum (event_data.EventDatum): event datum about target node.
    """
    source_id = self.GetAddNode(source_datum.NAME, source_datum.value)
    target_id = self.GetAddNode(target_datum.NAME, target_datum.value)
    self.AddEdge(source_id, target_id, edge_type, event_time, event_id)

  def AddEventData(self, parsed_event):
    """Processes one parsed event and encodes it to edges and nodes.

    Encoding is based on simple rules stored at RULES. If event contains
    event_data with key/name rule.source and rule.target, a new edge will be
    created with type rule.type.

    Args:
      parsed_event (event_data.EventData): event data about event to be
          translated to graph.
    """
    # Evaluate rules from RULES.
    for rule in self.__class__.RULES:
      source_datum = parsed_event.Get(rule.source)
      target_datum = parsed_event.Get(rule.target)
      if source_datum and target_datum:
        self.AddData(
            source_datum, target_datum, rule.type, parsed_event.timestamp,
            parsed_event.event_id)

    # Rules for access edges.
    remote_source = self.__class__.GetRemote(parsed_event, source=True)
    remote_target = self.__class__.GetRemote(parsed_event, target=True)
    if remote_source and remote_target:
      self.AddData(
          remote_source, remote_target, self.__class__.EDGE_ACCESS,
          parsed_event.timestamp, parsed_event.event_id)

  def MinimalSerialize(self):
    """Serializes only required data for visualization."""
    return {u'nodes': self.nodes, u'links': self.edges}

  def Finalize(self):
    """Assigns cluster identifier to each node.

    Cluster is subgraph of nodes connected by has/is edges and approximately
    represents one machine. Identifier is an node id from this cluster (cluster
    center), preferably machine name or machine ip address. This will override
    the old cluster assignments.
    """
    def PropagateClusterId(node_id, cluster_id, G):
      """Performs depth first search that propagates cluster_id to reachable
      nodes.

      This follows only "has" and "is" edges. It modifies Graph.nodes.

      Args:
        node_id (int): id of current node.
        cluster_id (int): cluster id I want to assign.
        G (list[list[int]]): adjacency graph.
      """
      if u'cluster' in self.nodes[node_id]:
        # This means the node has already been visited.
        return

      self.nodes[node_id][u'cluster'] = cluster_id

      for edge_id in G[node_id]:
        edge = self.edges[edge_id]
        if edge[u'type'] not in [self.EDGE_HAS, self.EDGE_IS]:
          continue

        PropagateClusterId(edge[u'source'], cluster_id, G)
        PropagateClusterId(edge[u'target'], cluster_id, G)


    def Priority(item):
      """Returns node's priority to be the center of the cluster.

      This function is used as a sort key (that is the reason for weird
      arguments). Node is a center of cluster if it is the node with the
      smallest Priority in the cluster.

      Args:
        item (tuple[int, tuple]): node's id and tuple serialized node.

      Returns:
        int: priority.
      """
      node = item[1]
      PRIORITY = {
          u'machine_name': 0,
          u'ip': 1,
          u'user_name':2,
          u'user_id': 3
      }
      if node[u'type'] in PRIORITY:
        return PRIORITY[node[u'type']]
      else:
        return 10**10



    for node in self.nodes:
      if u'cluster' in node:
        del node[u'cluster']

    G = [[] for node in self.nodes]
    for i, edge in enumerate(self.edges):
      G[edge[u'source']].append(i)
      G[edge[u'target']].append(i)

    nodes_with_ids = list(enumerate(self.nodes))

    sorted_nodes_with_ids = sorted(nodes_with_ids, key=Priority)
    for node_id, node in sorted_nodes_with_ids:
      PropagateClusterId(node_id, node_id, G)

class Node(object):
  """Graph node.

  Attributes:
    id (int): node id.
    type (str): node type.
    value (str): node value.
  """

  def __init__(self, node_type, node_value, node_id=None):
    """Initializes Node.

    Args:
      type (str): node's type.
      value (str): node's value.
      id (int|None): Node id. None if node does not have id yet.
    """
    self.type = node_type
    self.value = node_value
    self.id = node_id

  def ToDict(self):
    """Creates dictionary representation of node.

    Returns:
      dict: representation of node.
    """
    return {
        u'id': self.id,
        u'type': self.type,
        u'value': self.value
    }

  def ToTuple(self):
    """Creates tuple representation of node.

    Used as a unique identifier for the node. Nodes with the same ToTuple
    representation should have have same ids, in other words, there should not
    be two nodes with the same ToTuple values.

    Returns:
      tuple [str,str]: tuple representation of node.
    """
    return (self.type, self.value)

def CreateGraph(events_data, verbose=False):
  """Creates graph from events_data.

  Args:
    events_data (iterable[event_data.EventData]): data can be any iterable
        (list), preferably generator, because of memory optimization.

  Returns:
    Graph: property graph for events.
  """
  logger = logging.getLogger(__name__)
  graph = Graph()
  VERBOSE_INTERVAL = 1000
  for i, event in enumerate(events_data):
    graph.AddEventData(event)
    if not i % VERBOSE_INTERVAL and verbose:
      log_message = u'Nodes:{0:d} Edges: {1:d}'
      logger.info(log_message.format(len(graph.nodes), len(graph.edges)))

  graph.Finalize()
  return graph
