# -*- coding: utf-8 -*-
"""Tests for lib/event_data.py."""

import unittest

from eccemotus.lib import event_data

# pylint: disable=protected-access

class EventDatumTest(unittest.TestCase):
  """Tests for event datum."""

  def test_init(self):
    """Tests datum initialization."""
    datum_value = u'10.20.30.40'
    datum = event_data.EventDatum(value=datum_value, source=True)

    self.assertEqual(datum.value, datum_value)
    self.assertTrue(datum.source)
    self.assertFalse(datum.target)

    with self.assertRaises(ValueError):
      _ = event_data.EventDatum(
          value=datum_value, source=True, target=True)

  def test_GetFullName(self):
    """Tests full name generation."""
    datum = event_data.Ip(source=True)
    name = datum.GetFullName()
    expected_name = (True, False, u'ip')
    self.assertEqual(expected_name, name)

    datum = event_data.StorageFileName(target=True)
    name = datum.GetFullName()
    expected_name = (False, True, u'plaso')
    self.assertEqual(expected_name, name)


class EventDataTest(unittest.TestCase):
  """Tests for event data."""

  DATUM_CLASSES = [
      event_data.Ip,
      event_data.MachineName,
      event_data.StorageFileName,
      event_data.UserId,
      event_data.UserName
  ]

  def test_init(self):
    """Tests data initialization."""
    value = u'value'
    data_collection = [
        datum(value=value) for datum in self.DATUM_CLASSES]
    event_data_type = u'syslog'
    event_id = 20
    timestamp = 10
    data = event_data.EventData(
        data=data_collection, event_data_type=event_data_type,
        event_id=event_id, timestamp=timestamp)
    self.assertTrue(data.event_id, event_id)
    self.assertTrue(data.event_data_type, event_data_type)
    self.assertTrue(data.timestamp, timestamp)

    for datum in data_collection:
      datum_name = datum.GetFullName()
      self.assertIn(datum_name, data._index)

  def test_Add(self):
    """Tests datum adding."""
    data = event_data.EventData()
    ip_address = u'10.20.30.40'
    ip_address2 = u'10.20.30.42'
    ip = event_data.Ip(value=ip_address)
    ip2 = event_data.Ip(value=ip_address2)
    data.Add(ip)
    self.assertEqual(len(data._index), 1)
    ip_expected = data._index[ip.GetFullName()]
    self.assertEqual(ip_expected.value, ip_address)

    data.Add(ip2)
    self.assertEqual(len(data._index), 1)
    ip_expected = data._index[ip.GetFullName()]
    self.assertEqual(ip_expected.value, ip_address2)

    data = event_data.EventData()
    blacklisted_ip = event_data.Ip(value=u'-')
    data.Add(blacklisted_ip)
    self.assertEqual(len(data._index), 0)

  def test_Items(self):
    """Tests data enumeration."""
    value = u'value'
    data_collection = [
        datum_class(value=value) for datum_class in self.DATUM_CLASSES]
    data = event_data.EventData(data=data_collection)

    for datum in data.Items():
      self.assertIn(datum, data_collection)

    items_len = len(list(data.Items()))
    expected_len = len(data_collection)
    self.assertEqual(expected_len, items_len)

  def test_Get(self):
    """Tests datum getting from data."""
    data = event_data.EventData()

    user1_id = u'123'
    user1 = event_data.UserId(value=user1_id)
    user2_id = u'124'
    user2 = event_data.UserId(value=user2_id)

    data.Add(user1)
    user = data.Get(user1)
    self.assertEqual(user.value, user1_id)
    user = data.Get(user2)
    self.assertEqual(user.value, user1_id)

    data.Add(user2)
    user = data.Get(user1)
    self.assertEqual(user.value, user2_id)
    user = data.Get(user2)
    self.assertEqual(user.value, user2_id)

    storage = event_data.StorageFileName()
    storage_datum = data.Get(storage)
    self.assertIsNone(storage_datum)
    default = u'default'
    storage_datum = data.Get(storage, default=default)
    self.assertEqual(storage_datum, default)

  def test_IsEmpty(self):
    """Tests test for emptiness."""
    data = event_data.EventData()
    is_empty = data.IsEmpty()
    self.assertTrue(is_empty)

    machine_name = u'Dean-pc'
    machine_datum = event_data.MachineName(value=machine_name)
    data.Add(machine_datum)
    is_empty = data.IsEmpty()
    self.assertFalse(is_empty)
