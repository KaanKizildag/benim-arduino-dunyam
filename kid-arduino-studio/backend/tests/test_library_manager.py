import unittest
import sys
import os

# backend dizinini import yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from arduino_service import (
    HEADER_TO_LIBRARY_MAP,
    get_library_search_paths,
    auto_install_missing_libraries,
)


class TestLibraryManager(unittest.TestCase):
    def test_header_mappings_exist(self):
        self.assertIn("Adafruit_GFX.h", HEADER_TO_LIBRARY_MAP)
        self.assertEqual(HEADER_TO_LIBRARY_MAP["Adafruit_GFX.h"], "Adafruit GFX Library")
        self.assertIn("Adafruit_SSD1306.h", HEADER_TO_LIBRARY_MAP)
        self.assertEqual(HEADER_TO_LIBRARY_MAP["Adafruit_SSD1306.h"], "Adafruit SSD1306")
        self.assertIn("LiquidCrystal_I2C.h", HEADER_TO_LIBRARY_MAP)
        self.assertIn("DHT.h", HEADER_TO_LIBRARY_MAP)
        self.assertIn("IRremote.h", HEADER_TO_LIBRARY_MAP)

    def test_search_paths_format(self):
        paths = get_library_search_paths()
        self.assertIsInstance(paths, list)
        for p in paths:
            self.assertIsInstance(p, str)

    def test_auto_install_ignores_core_libraries(self):
        # Wire.h ve SPI.h dahili çekirdektir, lib install çağrılmamalıdır
        err_output = "KidSketch.ino:1:10: fatal error: Wire.h: No such file or directory"
        installed = auto_install_missing_libraries(cli_bin="", err_text=err_output)
        self.assertEqual(installed, [])


if __name__ == "__main__":
    unittest.main()
