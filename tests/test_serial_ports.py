"""Discover configured GPSD ports without accumulating or inventing entries."""

import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from openplotterSerial.serialPorts import SerialPorts


class SerialPortsTest(unittest.TestCase):
    def scan(self, text, count=1):
        ports = SerialPorts(None)
        with patch('builtins.open', side_effect=lambda *a, **kw: io.StringIO(text)):
            for _ in range(count):
                result = ports.usedSerialPorts()
        return [row['device'] for row in result]

    def test_repeated_scan_is_a_snapshot(self):
        self.assertEqual(self.scan('DEVICES="/dev/ttyUSB0"\n', 2), ['/dev/ttyUSB0'])

    def test_comments_do_not_replace_active_devices(self):
        text = 'DEVICES="/dev/ttyUSB0"\n# DEVICES="/dev/obsolete"\n'
        self.assertEqual(self.scan(text), ['/dev/ttyUSB0'])

    def test_single_quotes_and_whitespace(self):
        self.assertEqual(self.scan("DEVICES='/dev/a\t/dev/b'\n"), ['/dev/a', '/dev/b'])

    def test_assignment_uses_first_equal_sign(self):
        self.assertEqual(self.scan('DEVICES="/dev/serial=one" # note\n'), ['/dev/serial=one'])

    def test_other_variable_does_not_match(self):
        self.assertEqual(self.scan('OTHER_DEVICES="/dev/unused"\n'), [])


if __name__ == '__main__':
    unittest.main()
