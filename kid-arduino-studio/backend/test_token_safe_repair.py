"""
Token Korumalı Devre ve Komponent Onarım Döngüsü Testi
"""
import sys
import os
import json

# backend dizinini sys.path'e ekle
sys.path.insert(0, os.path.dirname(__file__))

from ai_service import (
    repair_circuit_with_llm,
    build_token_safe_circuit_repair_prompt,
    validate_one_shot_topology_and_code
)
from schemas import CircuitNetlist

def test_token_safe_repair_prompt():
    print("\n--- TEST 1: Token Korumalı Repair Prompt Oluşturma ---")
    errors = [
        "'Kırmızı LED' (led1) bileşeninin yalnızca 1 ucu (A) bağlanmış, devresi tamamlanmamış.",
        "Kodda kullanılan [uno.D13] netlist'te yok."
    ]
    long_output = "{" + '"test": "data", ' * 200 + "}"
    prompt = build_token_safe_circuit_repair_prompt(
        errors=errors,
        current_output=long_output,
        user_prompt="Hava kararınca yanan gece lambası",
        inventory=["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"]
    )
    assert "DİKKAT: Önceki ürettiğin devre ve kod çıktısında aşağıdaki bağlantı/komponent hataları tespit edildi:" in prompt
    assert "led1" in prompt
    assert "uno.D13" in prompt
    assert len(prompt) < 3000, f"Prompt token tasarrufu için kısa olmalı (uzunluk: {len(prompt)})"
    print("  ✅ Token korumalı prompt başarıyla oluşturuldu ve kırpıldı.")

def test_successful_repair_loop():
    print("\n--- TEST 2: Başarılı AI Devre Onarım Döngüsü ---")
    # İlk hatalı çıktı: LED'in sadece Anot ucu bağlı (Katot boşta)
    faulty_output = json.dumps({
        "netlist": {
            "board": "arduino-uno",
            "components": [
                {"id": "r1", "type": "wokwi-resistor", "label": "220Ω Direnç"},
                {"id": "led1", "type": "wokwi-led", "label": "Kırmızı LED"}
            ],
            "connections": [
                {"from": "uno.D13", "to": "r1.1"},
                {"from": "r1.2", "to": "led1.A"}
                # HATA: led1.C GND'ye bağlanmamış!
            ]
        },
        "arduino_kodu": "void setup() { pinMode(13, OUTPUT); }\nvoid loop() { digitalWrite(13, HIGH); }"
    })

    # Düzeltilmiş çıktı (Mock AI'nin döndüreceği):
    fixed_output = json.dumps({
        "netlist": {
            "board": "arduino-uno",
            "components": [
                {"id": "r1", "type": "wokwi-resistor", "label": "220Ω Direnç"},
                {"id": "led1", "type": "wokwi-led", "label": "Kırmızı LED"}
            ],
            "connections": [
                {"from": "uno.D13", "to": "r1.1"},
                {"from": "r1.2", "to": "led1.A"},
                {"from": "led1.C", "to": "GND"}
            ]
        },
        "arduino_kodu": "void setup() { pinMode(13, OUTPUT); }\nvoid loop() { digitalWrite(13, HIGH); }"
    })

    # Mock Ollama çağrısı simülasyonu:
    original_post = None
    import httpx
    class MockResponse:
        status_code = 200
        def json(self):
            return {"response": fixed_output}

    def mock_httpx_post(url, **kwargs):
        return MockResponse()

    httpx.post = mock_httpx_post

    callback_calls = []
    def on_progress(attempt, max_att, errs):
        callback_calls.append((attempt, max_att, errs))

    norm_data, raw_code, blocking_errors, warnings, was_repaired = repair_circuit_with_llm(
        current_text=faulty_output,
        prompt="Kırmızı LED yak",
        inventory=["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220"],
        chosen_model="ollama/mock-model",
        provider_used="ollama",
        max_attempts=2,
        progress_callback=on_progress
    )

    assert was_repaired is True, "Onarım başarıyla gerçekleşmiş olmalıydı."
    assert len(blocking_errors) == 0, f"Hata kalmamalıydı: {blocking_errors}"
    assert len(callback_calls) == 1, f"Tam olarak 1 kez onarım denenmeliydi: {callback_calls}"
    assert norm_data["netlist"]["connections"][-1]["to"] == "GND"
    print("  ✅ Model bağlantı hatasını tespit edip tek denemede başarıyla düzeltti!")

def test_token_guarded_max_attempts():
    print("\n--- TEST 3: Token Koruma Sınırı (Maksimum Deneme Sayısı) ---")
    # Sürekli hatalı dönen model simülasyonu
    persistent_faulty_output = json.dumps({
        "netlist": {
            "board": "arduino-uno",
            "components": [{"id": "led1", "type": "wokwi-led", "label": "LED"}],
            "connections": [{"from": "uno.D13", "to": "led1.A"}] # Katot hep boşta
        },
        "arduino_kodu": "void setup() {} void loop() {}"
    })

    import httpx
    class MockResponse:
        status_code = 200
        def json(self):
            return {"response": persistent_faulty_output}

    httpx.post = lambda url, **kwargs: MockResponse()

    callback_calls = []
    norm_data, raw_code, blocking_errors, warnings, was_repaired = repair_circuit_with_llm(
        current_text=persistent_faulty_output,
        prompt="Sürekli bozuk devre",
        inventory=["LED_RED"],
        chosen_model="ollama/mock-model",
        provider_used="ollama",
        max_attempts=2,
        progress_callback=lambda a, m, e: callback_calls.append(a)
    )

    assert len(callback_calls) == 2, f"Maksimum 2 deneme yapılmalıydı, yapılan: {len(callback_calls)}"
    assert len(blocking_errors) > 0, "Düzeltilemeyen hata raporlanmalı."
    print("  ✅ Token koruması çalıştı: 2 deneme sonrası sonsuz döngü kesildi ve kontrol tamamlandı!")

if __name__ == "__main__":
    test_token_safe_repair_prompt()
    test_successful_repair_loop()
    test_token_guarded_max_attempts()
    print("\n========================================================")
    print(" ⭐ TÜM TOKEN KORUMALI DEVRE ONARIM TESTLERİ BAŞARILI! ⭐")
    print("========================================================")
