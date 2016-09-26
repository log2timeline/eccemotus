""" Tests for lib/grapher.py."""
import unittest
import eccemotus.lib.grapher as G
import eccemotus.lib.parsers as P

#TODO(vlejd) add more tests after lib/graph.py is reviewed.
class GrapherTest(unittest.TestCase):
  """Test ParserManager """
  def test_init(self):
    """Test graph initialization."""
    graph = G.Graph()
    self.assertEqual(len(graph.edges), 0)
    self.assertEqual(len(graph.edges_ids), 0)
    self.assertEqual(len(graph.nodes), 0)
    self.assertEqual(len(graph.nodes_ids), 0)

  def test_GetAddNode(self):
    """Test GetAddNode method."""
    def NodeTuplteToDict(node_tuple, node_id):
      """Create dict node from tuple node """
      return {
          'id': node_id,
          'type': node_tuple[0],
          'value': node_tuple[1],
      }

    graph = G.Graph()
    node1 = ("node_type_1", "node_value_1")
    graph.GetAddNode(node1[0], node1[1])
    self.assertEqual(len(graph.nodes), 1)
    self.assertEqual(graph.nodes[0], NodeTuplteToDict(node1, 0))
    self.assertEqual(len(graph.nodes_ids), 1)

    node2 = ("node_type_1", "node_value_2")
    graph.GetAddNode(node2[0], node2[1])
    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(graph.nodes[1], NodeTuplteToDict(node2, 1))
    self.assertEqual(len(graph.nodes_ids), 2)

    graph.GetAddNode(node1[0], node1[1])
    self.assertEqual(len(graph.nodes), 2)
    self.assertEqual(graph.nodes[0], NodeTuplteToDict(node1, 0))
    self.assertEqual(len(graph.nodes_ids), 2)

  def test_AddEvent(self):
    graph = G.Graph()
    event = {
        P.EVENT_ID: 1,
        P.SOURCE_MACHINE_IP: '192.168.1.11',
        P.SOURCE_MACHINE_NAME: '192.168.1.11',
        P.TARGET_USER_NAME: 'dean@acserver',
        P.TARGET_MACHINE_NAME: 'acserver',
        P.TARGET_PLASO:
        'acserver.dd/images/work/vlejd/home/google/local/usr/',
        P.TIMESTAMP: 1441559606244560}

    graph.AddEvent(event)

    self.assertEqual(len(graph.nodes), 4)
    self.assertEqual(len(graph.edges), 3)

