import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from arduino_code_utils import sanitize_arduino_identifiers

class TestArduinoCodeUtils(unittest.TestCase):
    def test_turkish_char_cleaning(self):
        sample_code = """
        // Bu bir Türkçe açıklamadır: Çocuklar için gece lambası
        const int IŞIK_EŞİĞİ = 450;
        int ölçümDeğeri = 0;
        void setup() {
            Serial.begin(9600);
            Serial.println("Çok karanlık!");
        }
        """
        cleaned = sanitize_arduino_identifiers(sample_code)
        self.assertIn("ISIK_ESIGI", cleaned)
        self.assertIn("olcumDegeri", cleaned)
        self.assertIn("Çocuklar için gece lambası", cleaned)
        self.assertIn('"Çok karanlık!"', cleaned)

if __name__ == "__main__":
    unittest.main()
