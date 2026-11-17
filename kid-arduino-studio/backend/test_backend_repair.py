import json
from unittest.mock import patch, MagicMock
from ai_service import (
    generate_project_idea,
    extract_arduino_code_pins,
    check_code_netlist_pin_consistency,
    validate_strict_raw_project_dict,
)


def test_repair_flow_with_broken_and_aliased_json():
    print("=== BACKEND REPAIR VE KOD-NETLIST UYUM TESTİ ===")

    # 1. İlk çağrıda LLM bozuk/alias'lı ve kod-pin uyumsuz bir JSON dönsün
    broken_first_json = json.dumps({
        "proje_adi": "Test Lambası",
        "karsilama_mesaji": "Merhaba!",
        "gerekli_parcalar": ["ARDUINO_UNO", "LED_RED", "RESISTOR_220"],
        "netlist": {
            "board": "arduino-uno",
            "components": [
                {"id": "r1", "type": "resistor", "props": {"value": "220"}, "label": "220Ω Direnç"},
                {"id": "led1", "type": "led", "props": {"color": "red"}, "label": "Kırmızı LED"}
            ],
            "connections": [
                {"from": "uno.13", "to": "r1.A", "color": "orange"},
                {"from": "r1.B", "to": "led1.anode", "color": "red"},
                {"from": "GND", "to": "led1.cathode", "color": "black"}
            ]
        },
        "akis_adimlari": {
            "gozlemle": "Sürekli izle",
            "karar_ver": "Süre doldu mu?",
            "evet_sonucu": "Yak",
            "hayir_sonucu": "Söndür"
        },
        "arduino_kodu": """
const int LED_PIN = 12; // Netlist'te D13 ama kodda 12!
void setup() { pinMode(LED_PIN, OUTPUT); }
void loop() { digitalWrite(LED_PIN, HIGH); delay(500); }
"""
    })

    # Katı doğrulamanın hataları yakaladığını kontrol et
    strict_errs = validate_strict_raw_project_dict(json.loads(broken_first_json))
    print("Yakalanan ilk çıktı hataları:", strict_errs)
    assert len(strict_errs) >= 4, "Alias, ters GND ve kod-pin uyuşmazlığı yakalanmalıydı!"

    # 2. Repair çağrısında LLM düzeltilmiş (veya hala ufak alias içeren) JSON dönsün
    repaired_second_json = json.dumps({
        "proje_adi": "Onarılmış Süper Lamba 💡",
        "karsilama_mesaji": "Onarıldı!",
        "gerekli_parcalar": ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"],
        "netlist": {
            "board": "arduino-uno",
            "components": [
                {"id": "r1", "type": "wokwi-resistor", "props": {"value": "220"}, "label": "220Ω Direnç"},
                {"id": "led1", "type": "wokwi-led", "props": {"color": "red"}, "label": "Kırmızı LED"}
            ],
            "connections": [
                {"from": "uno.13", "to": "r1.1", "color": "orange"},
                {"from": "r1.2", "to": "led1.anode", "color": "red"},
                {"from": "GND", "to": "led1.C", "color": "black"}
            ]
        },
        "akis_adimlari": {
            "gozlemle": "Sayacı izle",
            "karar_ver": "1 saniye geçti mi?",
            "evet_sonucu": "Lambayı yak!",
            "hayir_sonucu": "Lambayı söndür!"
        },
        "arduino_kodu": """
const int LED_PIN = 13;
void setup() { pinMode(LED_PIN, OUTPUT); }
void loop() { digitalWrite(LED_PIN, HIGH); delay(500); digitalWrite(LED_PIN, LOW); delay(500); }
"""
    })

    call_count = {"n": 0}

    def fake_ollama_post(url, json=None, timeout=45.0):
        call_count["n"] += 1
        mock_res = MagicMock()
        mock_res.status_code = 200
        if call_count["n"] == 1:
            mock_res.json.return_value = {"response": broken_first_json}
        else:
            # Repair promptunun içinde hata mesajlarının yer aldığını doğrula
            assert "Önceki ürettiğin JSON çıktısında" in json["prompt"]
            mock_res.json.return_value = {"response": repaired_second_json}
        return mock_res

    with patch("ai_service.get_installed_ollama_models", return_value=[{
        "id": "ollama/qwen2.5-coder:1.5b",
        "name": "qwen2.5-coder:1.5b",
        "raw_name": "qwen2.5-coder:1.5b",
        "provider": "local",
        "category": "Yerel",
        "badge": "Yerel"
    }]), patch("ai_service.httpx.post", side_effect=fake_ollama_post):
        result = generate_project_idea(
            prompt="Kırmızı LED yakıp söndürmek istiyorum",
            inventory=["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"],
            model="ollama/qwen2.5-coder:1.5b"
        )

    assert call_count["n"] == 2, f"LLM tam 2 kez (1 ilk + 1 repair) çağrılmalıydı, çağrı sayısı: {call_count['n']}"
    assert result.proje_adi == "Onarılmış Süper Lamba 💡"
    assert result.netlist is not None
    conns = [(c.from_pin, c.to_pin) for c in result.netlist.connections]
    print("Repair sonrası normalize edilmiş bağlantılar:", conns)
    assert ("uno.D13", "r1.1") in conns
    assert ("r1.2", "led1.A") in conns
    assert ("led1.C", "GND") in conns
    print("Uyarılar:", result.uyarilar)
    print("✅ Backend Repair ve Normalizasyon Testi BAŞARILI!")


if __name__ == "__main__":
    test_repair_flow_with_broken_and_aliased_json()
