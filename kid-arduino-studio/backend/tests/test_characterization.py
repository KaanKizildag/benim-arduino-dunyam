import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_service import (
    extract_arduino_code_pins,
    extract_netlist_uno_pins,
    check_code_netlist_pin_consistency,
    auto_complete_electrical_topology,
    clean_llm_json_response
)
from flow_service import build_deterministic_flow_from_code
from schemas import CircuitNetlist, NetlistComponent, NetlistConnection

class TestCharacterization(unittest.TestCase):
    def test_extract_code_pins(self):
        code = """
        const int LED_PIN = 13;
        int sensorPin = A0;
        void setup() {
            pinMode(LED_PIN, OUTPUT);
            pinMode(8, INPUT);
        }
        void loop() {
            analogRead(sensorPin);
        }
        """
        pins = extract_arduino_code_pins(code)
        self.assertIn("uno.D13", pins)
        self.assertIn("uno.A0", pins)
        self.assertIn("uno.D8", pins)

    def test_netlist_pins_extraction(self):
        netlist = CircuitNetlist(
            board="arduino-uno",
            components=[
                NetlistComponent(id="led1", type="wokwi-led", label="LED"),
                NetlistComponent(id="r1", type="wokwi-resistor", label="Direnç")
            ],
            connections=[
                NetlistConnection(**{"from": "uno.D13", "to": "r1.1"}),
                NetlistConnection(**{"from": "r1.2", "to": "led1.A"}),
                NetlistConnection(**{"from": "led1.C", "to": "GND"})
            ]
        )
        uno_pins = extract_netlist_uno_pins(netlist)
        self.assertIn("uno.D13", uno_pins)

    def test_pin_consistency_check(self):
        code = "void setup() { pinMode(12, OUTPUT); }"
        netlist = CircuitNetlist(
            board="arduino-uno",
            components=[NetlistComponent(id="led1", type="wokwi-led", label="LED")],
            connections=[NetlistConnection(**{"from": "uno.D13", "to": "led1.A"})]
        )
        errors = check_code_netlist_pin_consistency(code, netlist)
        self.assertTrue(any("uno.D12" in e for e in errors))
        self.assertTrue(any("uno.D13" in e for e in errors))

    def test_clean_llm_json_response(self):
        markdown_json = '```json\n{"proje_adi": "Test Projesi"}\n```'
        cleaned = clean_llm_json_response(markdown_json)
        self.assertEqual(cleaned.strip(), '{"proje_adi": "Test Projesi"}')

    def test_deterministic_flow_from_code(self):
        netlist = CircuitNetlist(
            board="arduino-uno",
            components=[
                NetlistComponent(id="led1", type="wokwi-led", label="Kırmızı LED"),
                NetlistComponent(id="r1", type="wokwi-resistor", label="220Ω Direnç")
            ],
            connections=[
                NetlistConnection(**{"from": "uno.D13", "to": "r1.1"}),
                NetlistConnection(**{"from": "r1.2", "to": "led1.A"}),
                NetlistConnection(**{"from": "led1.C", "to": "GND"})
            ]
        )
        code = """
        void setup() {
            pinMode(13, OUTPUT);
        }
        void loop() {
            digitalWrite(13, HIGH);
            delay(1000);
            digitalWrite(13, LOW);
            delay(1000);
        }
        """
        flow = build_deterministic_flow_from_code(netlist, code)
        self.assertIsNotNone(flow)
        self.assertTrue(len(flow.dugumler) >= 3)
        self.assertTrue(len(flow.baglantilar) >= 2)
        # Check node types
        types = [n.tip for n in flow.dugumler]
        self.assertIn("kurulum", types)
        self.assertIn("eylem", types)

    def test_auto_complete_electrical_topology(self):
        # 2-pin LDR without resistor: auto_complete_electrical_topology must add 10k resistor
        raw_netlist = {
            "board": "arduino-uno",
            "components": [
                {"id": "ldr1", "type": "wokwi-photoresistor", "label": "LDR"}
            ],
            "connections": [
                {"from": "ldr1.1", "to": "5V"},
                {"from": "ldr1.2", "to": "uno.A0"}
            ]
        }
        completed, notes = auto_complete_electrical_topology(raw_netlist)
        comp_types = [c["type"] for c in completed["components"]]
        self.assertIn("wokwi-resistor", comp_types)

if __name__ == "__main__":
    unittest.main()
