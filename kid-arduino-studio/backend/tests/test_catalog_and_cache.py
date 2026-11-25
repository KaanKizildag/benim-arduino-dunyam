"""
Unit tests for component catalog filtering and response caching.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.llm.catalog import (
    get_filtered_component_docs,
    build_one_shot_system_prompt,
    resolve_component_type,
    get_component_meta,
)
from app.llm.cache import (
    get_cached_project,
    set_cached_project,
    clear_cache,
    make_cache_key,
)


class TestCatalogAndCache(unittest.TestCase):
    def setUp(self):
        clear_cache()

    def test_component_resolution(self):
        self.assertEqual(resolve_component_type("led"), "wokwi-led")
        self.assertEqual(resolve_component_type("servo_sg90"), "wokwi-servo")
        self.assertEqual(resolve_component_type("ldr"), "wokwi-photoresistor")
        self.assertEqual(resolve_component_type("unknown-part"), "unknown-part")

    def test_component_meta(self):
        label, icon = get_component_meta("led")
        self.assertEqual(label, "LED Işık Lambası")
        self.assertEqual(icon, "💡")

        label, icon = get_component_meta("wokwi-servo")
        self.assertIn("Servo", label)
        self.assertEqual(icon, "🦾")

    def test_filtered_component_docs_token_saving(self):
        # A simple LED project should NOT include bluetooth, LCD, or DC motor docs
        docs_led = get_filtered_component_docs(
            inventory=["LED_RED", "RESISTOR_220"],
            user_prompt="Kırmızı ledi 1 saniye aralıklarla yakıp söndür"
        )
        self.assertIn("wokwi-led", docs_led)
        self.assertIn("wokwi-resistor", docs_led)
        self.assertNotIn("wokwi-hc-05", docs_led)
        self.assertNotIn("wokwi-lcd1602", docs_led)
        self.assertNotIn("wokwi-dc-motor", docs_led)

        # An ultrasonic car project SHOULD include ultrasonic and dc-motor/l293d
        docs_car = get_filtered_component_docs(
            inventory=[],
            user_prompt="Engelden kaçan akıllı araba mesafesi"
        )
        self.assertIn("wokwi-hc-sr04", docs_car)
        self.assertIn("wokwi-l293d", docs_car)
        self.assertIn("wokwi-dc-motor", docs_car)

    def test_dynamic_system_prompt_builder(self):
        prompt = build_one_shot_system_prompt("park sensörü buzzer ve mesafe", [])
        self.assertIn("wokwi-hc-sr04", prompt)
        self.assertIn("wokwi-buzzer", prompt)
        self.assertNotIn("wokwi-lcd1602", prompt)
        # Much smaller than 9,000 characters
        self.assertLess(len(prompt), 3500)

    def test_response_cache(self):
        # Cache miss initially
        cached = get_cached_project("Blink LED", ["LED_RED"], "gpt-4o")
        self.assertIsNone(cached)

        # Cache set
        mock_data = {"proje_adi": "Blink Test", "arduino_kodu": "void setup(){}"}
        set_cached_project("Blink LED", ["LED_RED"], "gpt-4o", mock_data)

        # Cache hit with identical inputs
        cached = get_cached_project("Blink LED", ["LED_RED"], "gpt-4o")
        self.assertIsNotNone(cached)
        self.assertEqual(cached["proje_adi"], "Blink Test")

        # Cache hit with different case and whitespace
        cached_case_insensitive = get_cached_project("  blink  led  ", ["LED_RED"], "gpt-4o")
        self.assertIsNotNone(cached_case_insensitive)

        # Different prompt should miss
        self.assertIsNone(get_cached_project("Other Project", ["LED_RED"], "gpt-4o"))


if __name__ == "__main__":
    unittest.main()
