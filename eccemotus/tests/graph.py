# -*- coding: utf-8 -*-
"""Tests for lib/graph.py."""
import unittest
import eccemotus.lib.graph as G
import eccemotus.lib.parsers as P

class GrapherTest(unittest.TestCase):
  """Test ParserManager."""
  def test_init(self):
    """Test graph initialization."""
    graph = G.Graph()
    self.assertEqual(len(graph.edges), 0)
    self.assertEqual(len(graph.edges_ids), 0)
    self.assertEqual(len(graph.nodes), 0)
    self.assertEqual(len(graph.nodes_ids), 0)

  def test_GetAddNode(self):
    """Test GetAddNode method."""

    graph = G.Graph()
    node1 = G.Node(u'node_type_1', u'node_value_1', 0)
    graph.GetAddNode(node1.type, node1.value)
    self.assertEqual(len(graph.nodes), 1)
    self.assertEqual(graph.nodes[0], node1.ToDict())
    self.assertEqual(len(graph.nodes_ids), 1)

    node2 = G.Node(u'node_type_1', u'node_value_2', 1)
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
    graph = G.Graph()
    event = {
        P.EVENT_ID: 1,
        P.SOURCE_MACHINE_IP: u'192.168.1.11',
        P.SOURCE_MACHINE_NAME: u'192.168.1.11',
        P.TARGET_USER_NAME: u'dean@acserver',
        P.TARGET_MACHINE_NAME: u'acserver',
        P.TARGET_PLASO:
        u'acserver.dd/images/work/vlejd/home/google/local/usr/',
        P.TIMESTAMP: 1441559606244560}

    graph.AddEvent(event)

    self.assertEqual(len(graph.nodes), 4)
    self.assertEqual(len(graph.edges), 3)

  def test_CreateGraph(self):
    """Test CreateGraph."""
    event = {
        P.EVENT_ID: 1,
        P.SOURCE_MACHINE_IP: u'192.168.1.11',
        P.SOURCE_MACHINE_NAME: u'192.168.1.11',
        P.TARGET_USER_NAME: u'dean@acserver',
        P.TARGET_MACHINE_NAME: u'acserver',
        P.TARGET_PLASO:
        u'acserver.dd/images/work/vlejd/home/google/local/usr/',
        P.TIMESTAMP: 1441559606244560}
    events = [event]
    graph = G.CreateGraph(events)
    self.assertEqual(len(graph.nodes), 4)
    self.assertEqual(len(graph.edges), 3)
