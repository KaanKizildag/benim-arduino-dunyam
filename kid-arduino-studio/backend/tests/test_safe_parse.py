import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_service import safe_parse_llm_json, validate_one_shot_topology_and_code
from schemas import CircuitNetlist


class TestSafeJsonAndValidation(unittest.TestCase):
    def test_unterminated_string_recovery(self):
        # Truncated string at the end
        raw = '{"proje_adi": "Rastgele Veri", "arduino_kodu": "void setup() { Serial.begin(9600);'
        res = safe_parse_llm_json(raw)
        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("proje_adi"), "Rastgele Veri")
        self.assertIn("Serial.begin", res.get("arduino_kodu", ""))

    def test_literal_newlines_in_strings(self):
        raw = '{\n  "proje_adi": "Test Proje",\n  "arduino_kodu": "void setup() {\n    Serial.begin(9600);\n  }"\n}'
        res = safe_parse_llm_json(raw)
        self.assertEqual(res.get("proje_adi"), "Test Proje")
        self.assertIn("Serial.begin", res.get("arduino_kodu", ""))

    def test_trailing_commas(self):
        raw = '{"proje_adi": "Test", "gerekli_parcalar": ["ARDUINO_UNO", ], }'
        res = safe_parse_llm_json(raw)
        self.assertEqual(res.get("proje_adi"), "Test")
        self.assertEqual(res.get("gerekli_parcalar"), ["ARDUINO_UNO"])

    def test_serial_only_project_validation(self):
        # Seri port veya dahili mantık projelerinde harici bileşen olmaması blocking error olmamalıdır
        netlist = CircuitNetlist(board="arduino-uno", components=[], connections=[])
        code = "void setup() { Serial.begin(9600); } void loop() { Serial.println(random(100)); delay(500); }"
        blocking, report = validate_one_shot_topology_and_code(netlist=netlist, akis=None, code=code)
        circuit_blocking = [e for e in blocking if "akış" not in e.lower()]
        self.assertEqual(circuit_blocking, [])
        self.assertTrue(any("dahili Arduino Uno" in c for c in report.checks))


if __name__ == "__main__":
    unittest.main()
