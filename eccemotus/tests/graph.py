# -*- coding: utf-8 -*-
"""Tests for lib/graph.py."""

import unittest

from eccemotus.lib import graph as graph_lib
from eccemotus.lib.parsers import utils

class GraphTest(unittest.TestCase):
  """Test Graph."""

  def test_init(self):
    """Test Graph initialization."""
    graph = graph_lib.Graph()
    self.assertEqual(len(graph.edges), 0)
    self.assertEqual(len(graph.edges_ids), 0)
    self.assertEqual(len(graph.nodes), 0)
    self.assertEqual(len(graph.nodes_ids), 0)

  def test_GetAddNode(self):
    """Test GetAddNode method."""
    graph = graph_lib.Graph()
    node1 = graph_lib.Node(u'node_type_1', u'node_value_1', 0)
    graph.GetAddNode(node1.type, node1.value)
    self.assertEqual(len(graph.nodes), 1)
    self.assertEqual(graph.nodes[0], node1.ToDict())
    self.assertEqual(len(graph.nodes_ids), 1)

    node2 = graph_lib.Node(u'node_type_1', u'node_value_2', 1)
    graph.GetAddNode(node2.type, node2.value)
    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(graph.nodes[1], node2.ToDict())
    self.assertEqual(len(graph.nodes_ids), 2)

    graph.GetAddNode(node1.type, node1.value)
    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(graph.nodes[0], node1.ToDict())
    self.assertEqual(len(graph.nodes_ids), 2)

  def test_AddEvent(self):
    """Test AddEvent."""
    graph = graph_lib.Graph()
    event = {
        utils.EVENT_ID: 1,
        utils.SOURCE_MACHINE_IP: u'192.168.1.11',
        utils.SOURCE_MACHINE_NAME: u'192.168.1.11',
        utils.TARGET_USER_NAME: u'dean@acserver',
        utils.TARGET_MACHINE_NAME: u'acserver',
        utils.TARGET_PLASO:
        u'acserver.dd/images/work/vlejd/home/google/local/usr/',
        utils.TIMESTAMP: 1441559606244560}

    graph.AddEvent(event)

    self.assertEqual(len(graph.nodes), 4)
    self.assertEqual(len(graph.edges), 3)

  def test_AddEdge(self):
    """Test AddEdge."""
    graph = graph_lib.Graph()
    node1 = graph_lib.Node(u'node_type_1', u'node_value_1')
    node1_id = graph.GetAddNode(node1.type, node1.value)
    node2 = graph_lib.Node(u'node_type_2', u'node_value_2')
    node2_id = graph.GetAddNode(node2.type, node2.value)

    graph.AddEdge(node1_id, node2_id, u'is', 10, 20)
    self.assertEqual(len(graph.edges), 1)
    edge = graph.edges[0]
    self.assertEqual(len(edge[u'events']), 1)

    graph.AddEdge(node1_id, node2_id, u'is', 20, 30)
    self.assertEqual(len(graph.edges), 1)
    edge = graph.edges[0]
    self.assertEqual(len(edge[u'events']), 2)

  def test_GetRemoteSource(self):
    """Test GetRemoteSource."""
    source_types = [utils.SOURCE_USER_NAME, utils.SOURCE_USER_ID,
                    utils.SOURCE_MACHINE_NAME, utils.SOURCE_MACHINE_IP,
                    utils.SOURCE_PLASO, u'random_type1', u'random_type2']
    source_values = [u'value_{0:s}'.format(source) for source in source_types]

    for i in range(5):  # 5 is number of real types.
      expected_type = source_types[i]
      expected_value = source_values[i]
      event = dict(zip(source_types[i:], source_values[i:]))
      source = graph_lib.Graph.GetRemoteSource(event)
      self.assertEqual(source, (expected_type, expected_value))

    event = dict(zip(source_types[-2:], source_values[-2:]))
    expecetd_source = (None, None)
    source = graph_lib.Graph.GetRemoteSource(event)
    self.assertEqual(source, expecetd_source)

  def test_GetRemoteTarget(self):
    """Test GetRemoteTarget."""
    target_types = [utils.TARGET_USER_NAME, utils.TARGET_USER_ID,
                    utils.TARGET_MACHINE_NAME, utils.TARGET_MACHINE_IP,
                    utils.TARGET_PLASO, u'random_type1', u'random_type2']
    target_values = [u'value_{0:s}'.format(source) for source in target_types]

    for i in range(5):  # 5 is number of real types.
      expected_type = target_types[i]
      expected_value = target_values[i]
      event = dict(zip(target_types[i:], target_values[i:]))
      source = graph_lib.Graph.GetRemoteTarget(event)
      self.assertEqual(source, (expected_type, expected_value))

    event = dict(zip(target_types[-2:], target_values[-2:]))
    expecetd_source = (None, None)
    source = graph_lib.Graph.GetRemoteTarget(event)
    self.assertEqual(source, expecetd_source)

  def test_AddData(self):
    """Test AddData."""
    graph = graph_lib.Graph()

    graph.AddData(utils.SOURCE_MACHINE_NAME, u'machine1',
                  utils.TARGET_MACHINE_NAME, u'machine2', u'access', 10, 20)

    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(len(graph.edges), 1)

  def test_MinimalSerialize(self):
    """Test MinimalSerialize."""
    graph = graph_lib.Graph()
    graph.AddData(utils.SOURCE_MACHINE_NAME, u'machine1',
                  utils.TARGET_MACHINE_NAME, u'machine2', u'access', 10, 20)

    serialized = graph.MinimalSerialize()
    expected_serialized = {
        u'nodes': [
            {
                u'type': u'machine_name',
                u'id': 0,
                u'value': u'machine1'
            },
            {
                u'type':
                u'machine_name',
                u'id': 1,
                u'value': u'machine2'
            }],
        u'links': [
            {
                u'source': 0,
                u'type': 'access',
                u'events': [
                    {
                        u'timestamp': 10,
                        u'id': 20
                    }],
                u'target': 1
            }]
    }

    self.assertEqual(serialized, expected_serialized)


class NodeTest(unittest.TestCase):
  """Test Node."""

  def test_init(self):
    """Test Node initialization."""
    node_type = u'type'
    node_value = u'value'
    node_id = 10

    node = graph_lib.Node(node_type, node_value)
    self.assertEqual(node.type, node_type)
    self.assertEqual(node.value, node_value)
    self.assertIs(node.id, None)

    node = graph_lib.Node(node_type, node_value, node_id)
    self.assertEqual(node.type, node_type)
    self.assertEqual(node.value, node_value)
    self.assertIs(node.id, node_id)

  def test_ToTuple(self):
    """Test ToTuple."""
    node1_type = u'type'
    node1_value = u'value'
    node1_id = 10
    node1 = graph_lib.Node(node1_type, node1_value, node1_id)

    node1_tuple = node1.ToTuple()
    expected_tuple = (node1_type, node1_value)
    self.assertEqual(node1_tuple, expected_tuple)

    node1_with_id_none = graph_lib.Node(node1_type, node1_value)
    node1_with_id_none_tuple = node1_with_id_none.ToTuple()
    self.assertEqual(node1_tuple, node1_with_id_none_tuple)

  def test_ToDict(self):
    """Test ToDict."""
    node1_type = u'type'
    node1_value = u'value'
    node1_id = 10
    node1 = graph_lib.Node(node1_type, node1_value, node1_id)

    node1_dict = node1.ToDict()
    expected_dict = {
        u'id': node1_id,
        u'type': node1_type,
        u'value': node1_value
    }
    self.assertEqual(node1_dict, expected_dict)


class CreateGraphTest(unittest.TestCase):
  """Test CreateGraph."""

  def test_CreateGraph(self):
    """Test CreateGraph."""
    event = {
        utils.EVENT_ID: 1,
        utils.SOURCE_MACHINE_IP: u'192.168.1.11',
        utils.SOURCE_MACHINE_NAME: u'192.168.1.11',
        utils.TARGET_USER_NAME: u'dean@acserver',
        utils.TARGET_MACHINE_NAME: u'acserver',
        utils.TARGET_PLASO:
        u'acserver.dd/images/work/vlejd/home/google/local/usr/',
        utils.TIMESTAMP: 1441559606244560}
    events = [event]
    graph = graph_lib.CreateGraph(events)
    self.assertEqual(len(graph.nodes), 4)
    self.assertEqual(len(graph.edges), 3)
