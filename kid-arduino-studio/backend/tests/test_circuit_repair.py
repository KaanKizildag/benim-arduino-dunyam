import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_service import (
    build_token_safe_circuit_repair_prompt,
    repair_circuit_with_llm
)

class TestCircuitRepair(unittest.TestCase):
    def test_build_token_safe_repair_prompt(self):
        errors = [
            "Bileşen 'led1' yalnızca 1 pinle bağlanmış.",
            "Direnç 'r1' açıkta kalmış."
        ]
        long_output = '{"netlist": {"components": []}}' * 100
        prompt = build_token_safe_circuit_repair_prompt(
            errors=errors,
            current_output=long_output,
            user_prompt="Kırmızı LED yak",
            inventory=["ARDUINO_UNO", "LED_RED"]
        )
        self.assertIn("DİKKAT: Önceki ürettiğin devre ve kod çıktısında", prompt)
        self.assertIn("Bileşen 'led1'", prompt)
        self.assertIn("... [kalan JSON kırpıldı]", prompt)

    def test_repair_circuit_mock(self):
        # Mocking llm response by testing repair cycle logic with invalid JSON
        broken_json = '{"netlist": {"board": "arduino-uno", "components": [{"id": "led1", "type": "wokwi-led"}], "connections": [{"from": "uno.D13", "to": "led1.A"}]}}'
        attempts_recorded = []
        def progress_cb(attempt, max_attempts, errs):
            attempts_recorded.append((attempt, errs))

        # Test token safety limit with max_attempts=1
        norm_data, raw_code, errors, warnings, was_repaired = repair_circuit_with_llm(
            current_text=broken_json,
            prompt="Kırmızı LED yak",
            inventory=["ARDUINO_UNO", "LED_RED"],
            chosen_model="mock/test",
            provider_used="mock",
            max_attempts=1,
            progress_callback=progress_cb
        )
        # Verify it halted gracefully without crashing
        self.assertIsInstance(errors, list)
        self.assertTrue(len(errors) > 0)

if __name__ == "__main__":
    unittest.main()
