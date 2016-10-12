# -*- coding: utf-8 -*-
"""Tests for lib/graph.py."""

import unittest

from eccemotus.lib import event_data
from eccemotus.lib import graph as graph_lib

class GraphTest(unittest.TestCase):
  """Tests for graph library."""

  def test_init(self):
    """Tests graph initialization."""
    graph = graph_lib.Graph()
    self.assertEqual(len(graph.edges), 0)
    self.assertEqual(len(graph.edges_ids), 0)
    self.assertEqual(len(graph.nodes), 0)
    self.assertEqual(len(graph.nodes_ids), 0)

  def test_GetAddNode(self):
    """Tests node adding."""
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

  def test_AddEventData(self):
    """Tests event adding."""
    graph = graph_lib.Graph()
    informations_list = [
        event_data.Ip(source=True, value=u'192.168.1.11'),
        event_data.MachineName(source=True, value=u'192.168.1.11'),
        event_data.UserName(target=True, value=u'dean@acserver'),
        event_data.MachineName(target=True, value=u'acserver'),
        event_data.StorageFileName(
            target=True, value=u'acserver.dd/images/user/usr/'),
    ]
    informations = event_data.EventData(
        data=informations_list, event_id=1, timestamp=1441559606244560)
    graph.AddEventData(informations)

    self.assertEqual(len(graph.nodes), 4)
    self.assertEqual(len(graph.edges), 3)

  def test_AddEdge(self):
    """Tests edge adding."""
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

  def test_AddData(self):
    """Tests data adding."""
    graph = graph_lib.Graph()

    source_machine = event_data.MachineName(source=True, value=u'machine1')
    target_machine = event_data.MachineName(source=True, value=u'machine2')
    graph.AddData(source_machine, target_machine, u'access', 10, 20)

    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(len(graph.edges), 1)

    self.assertEqual(graph.nodes[0][u'type'], source_machine.NAME)
    self.assertEqual(graph.nodes[0][u'value'], source_machine.value)

    self.assertEqual(graph.nodes[1][u'type'], target_machine.NAME)
    self.assertEqual(graph.nodes[1][u'value'], target_machine.value)

  def test_Finalize(self):
    """Tests graph finalization."""
    graph = graph_lib.Graph()
    graph.AddData(
        event_data.MachineName(source=True, value=u'machine1'),
        event_data.MachineName(target=True, value=u'machine2'), u'access', 10,
        20)

    graph.AddData(
        event_data.MachineName(source=True, value=u'machine1'),
        event_data.UserName(source=True, value=u'user1'), u'has', 10,
        20)

    graph.AddData(
        event_data.UserName(source=True, value=u'user1'),
        event_data.UserId(source=True, value=u'userid1'), u'is', 10,
        20)

    graph.AddData(
        event_data.MachineName(target=True, value=u'machine2'),
        event_data.UserName(target=True, value=u'user2'), u'has', 10,
        20)

    graph.AddData(
        event_data.UserName(target=True, value=u'user2'),
        event_data.UserId(target=True, value=u'userid2'), u'is', 10,
        20)

    graph.Finalize()
    clusters = [node[u'cluster'] for node in graph.nodes]
    expected_clusters = [0, 1, 0, 0, 1, 1]
    self.assertEqual(clusters, expected_clusters)



  def test_MinimalSerialize(self):
    """Tests serialization."""
    graph = graph_lib.Graph()
    graph.AddData(event_data.MachineName(source=True, value=u'machine1'),
                  event_data.MachineName(source=True, value=u'machine2'),
                  u'access', 10, 20)

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
  """Test node class."""

  def test_init(self):
    """Tests node initialization."""
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
    """Tests converting to tuple."""
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
    """Tests converting to dict."""
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
  """Tests graph creation routine."""

  def test_CreateGraph(self):
    """Tests graph creation."""
    informations_list = [
        event_data.Ip(source=True, value=u'192.168.1.11'),
        event_data.MachineName(source=True, value=u'192.168.1.11'),
        event_data.UserName(target=True, value=u'dean@acserver'),
        event_data.MachineName(target=True, value=u'acserver'),
        event_data.StorageFileName(
            target=True, value=u'acserver.dd/images/user/usr/'),
    ]
    informations = event_data.EventData(
        data=informations_list, event_id=1, timestamp=1441559606244560)
    informations_list = [informations]
    graph = graph_lib.CreateGraph(informations_list)
    self.assertEqual(len(graph.nodes), 4)
    self.assertEqual(len(graph.edges), 3)
