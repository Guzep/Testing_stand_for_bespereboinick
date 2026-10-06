"""Юнит-тесты без железа."""

import unittest
from unittest.mock import MagicMock, patch

from stand.config import DEFAULT_UPS_PROFILE, DEVICES
from stand.devices.power_unit import PowerUnit


class ConfigTests(unittest.TestCase):
    def test_three_required_devices(self):
        required = [d for d in DEVICES if d.required]
        self.assertEqual(len(required), 3)
        keys = {d.key for d in required}
        self.assertEqual(keys, {"multimeter", "power_unit", "stm32"})

    def test_ups_profile_shape(self):
        self.assertGreaterEqual(len(DEFAULT_UPS_PROFILE), 1)
        for voltage, pins, expected in DEFAULT_UPS_PROFILE:
            self.assertIsInstance(voltage, int)
            self.assertIsInstance(pins, str)
            self.assertIsInstance(expected, float)


class PowerUnitDecodeTests(unittest.TestCase):
    def test_decode_response(self):
        sample = (
            "$COMMON,SERIES,1,0,0,"
            "15.000,2.000,14.980,0.010,"
            "60.000,3.000,1,0,0,15.000,2.000,0.000,0.000,60.000,3.000,5124#"
        )
        # Не открываем реальный COM: подменяем connect
        with patch.object(PowerUnit, "connect", lambda self: None):
            psu = PowerUnit("COM_FAKE", 115200)
            psu.serial_ = MagicMock()
            decoded = psu.decode_response(sample)
        self.assertEqual(decoded["set_voltage"], "15.000")
        self.assertEqual(decoded["real_voltage"], "14.980")
        self.assertEqual(decoded["real_current"], "0.010")

    def test_voltage_range(self):
        with patch.object(PowerUnit, "connect", lambda self: None):
            psu = PowerUnit("COM_FAKE", 115200)
            psu.serial_ = MagicMock()
            with self.assertRaises(ValueError):
                psu.voltage_change(99)


if __name__ == "__main__":
    unittest.main()
