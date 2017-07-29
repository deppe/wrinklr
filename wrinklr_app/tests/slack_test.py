
import unittest
from ..slack import parse_slash_command

class TestSlack(unittest.TestCase):
    def test_parse_slash_comand(self):
        parse = parse_slash_command
        self.assertEqual(parse('blah vs bloo'), ('blah', 'bloo'))
        self.assertEqual(parse('blah bloo vs blah bloo'), ('blah bloo', 'blah bloo'))
        self.assertEqual(parse('vs bloo'), (None, 'bloo'))
        self.assertEqual(parse('vs'), (None, None))
        self.assertEqual(parse(''), (None, None))

