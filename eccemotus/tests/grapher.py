""" Tests for lib/grapher.py."""
import unittest
import eccemotus.lib.grapher as G

class GrapherTest(unittest.TestCase):
  """Test ParserManager """
  def test_init(self):
    """Test graph initialization."""
    graph = G.Graph()
    self.assertEqual(len(graph.edges), 0)
    self.assertEqual(len(graph.edges_ids), 0)
    self.assertEqual(len(graph.nodes), 0)
    self.assertEqual(len(graph.nodes_ids), 0)

  def test_get_add_node(self):
    """Test get_add_node method."""
    def node_tuple_to_dict(node_tuple, node_id):
      """Create dict node from tuple node """
      return {
          'id': node_id,
          'type': node_tuple[0],
          'value': node_tuple[1],
      }

    graph = G.Graph()
    node1 = ("node_type_1", "node_value_1")
    graph.get_add_node(node1[0], node1[1])
    self.assertEqual(len(graph.nodes), 1)
    self.assertEqual(graph.nodes[0], node_tuple_to_dict(node1, 0))
    self.assertEqual(len(graph.nodes_ids), 1)

    node2 = ("node_type_1", "node_value_2")
    graph.get_add_node(node2[0], node2[1])
    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(graph.nodes[1], node_tuple_to_dict(node2, 1))
    self.assertEqual(len(graph.nodes_ids), 2)

    graph.get_add_node(node1[0], node1[1])
    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(graph.nodes[0], node_tuple_to_dict(node1, 0))
    self.assertEqual(len(graph.nodes_ids), 2)

