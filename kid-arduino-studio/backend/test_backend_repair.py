import json
from unittest.mock import patch, MagicMock
from schemas import CircuitNetlist, NetlistComponent, NetlistConnection
from ai_service import (
    generate_project_idea,
    validate_strict_raw_project_dict,
)
from flow_service import (
    legacy_akis_to_diyagram,
    validate_flow_diagram,
    build_deterministic_flow_from_code,
    generate_flow_from_code,
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
        "akis_diyagrami": {
            "dugumler": [
                {"id": "n1", "tip": "kurulum", "metin": "LED pinini çıkış yap", "parcalar": ["led1"]},
                {"id": "n2", "tip": "eylem", "metin": "Kırmızı LED'i yak", "parcalar": ["led1"]},
                {"id": "n3", "tip": "bekle", "metin": "500ms bekle", "parcalar": []}
            ],
            "baglantilar": [
                {"kaynak": "n1", "hedef": "n2", "etiket": None},
                {"kaynak": "n2", "hedef": "n3", "etiket": None},
                {"kaynak": "n3", "hedef": "n2", "etiket": "Tekrarla"}
            ]
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

    # 2. Repair çağrısında LLM düzeltilmiş JSON dönsün
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
        "akis_diyagrami": {
            "dugumler": [
                {"id": "n1", "tip": "kurulum", "metin": "D13 LED pinini ayarla", "parcalar": ["led1"]},
                {"id": "n2", "tip": "eylem", "metin": "Kırmızı LED'i yak", "parcalar": ["led1"]},
                {"id": "n3", "tip": "bekle", "metin": "500ms bekle", "parcalar": []},
                {"id": "n4", "tip": "eylem", "metin": "Kırmızı LED'i söndür", "parcalar": ["led1"]},
                {"id": "n5", "tip": "bekle", "metin": "500ms bekle", "parcalar": []}
            ],
            "baglantilar": [
                {"kaynak": "n1", "hedef": "n2", "etiket": None},
                {"kaynak": "n2", "hedef": "n3", "etiket": None},
                {"kaynak": "n3", "hedef": "n4", "etiket": None},
                {"kaynak": "n4", "hedef": "n5", "etiket": None},
                {"kaynak": "n5", "hedef": "n2", "etiket": "Tekrarla"}
            ]
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

    assert call_count["n"] == 2
    assert result.proje_adi == "Onarılmış Süper Lamba 💡"
    assert result.akis_diyagrami is not None
    assert len(result.akis_diyagrami.dugumler) == 5
    assert result.netlist is not None
    conns = [(c.from_pin, c.to_pin) for c in result.netlist.connections]
    assert ("uno.D13", "r1.1") in conns
    assert ("r1.2", "led1.A") in conns
    assert ("led1.C", "GND") in conns


def test_legacy_akis_adapter():
    legacy = {
        "gozlemle": "LDR ışık değerini okur",
        "karar_ver": "Hava karanlık mı?",
        "evet_sonucu": "Gece lambasını yak!",
        "hayir_sonucu": "Lambayı söndür."
    }
    comps = [
        {"id": "ldr1", "type": "wokwi-photoresistor", "label": "LDR"},
        {"id": "led1", "type": "wokwi-led", "label": "LED"},
    ]
    diagram = legacy_akis_to_diyagram(legacy, comps)
    assert len(diagram.dugumler) == 5
    assert any(n.tip == "karar" for n in diagram.dugumler)
    assert any(e.etiket == "Evet" for e in diagram.baglantilar)
    assert any(e.etiket == "Hayır" for e in diagram.baglantilar)
    assert any(e.etiket == "Tekrarla" for e in diagram.baglantilar)


def test_flow_validator_catches_errors_and_warnings():
    netlist = CircuitNetlist(
        board="arduino-uno",
        components=[
            NetlistComponent(id="led1", type="wokwi-led", label="Kırmızı LED"),
            NetlistComponent(id="r1", type="wokwi-resistor", label="220Ω Direnç"),
        ],
        connections=[
            NetlistConnection(**{"from": "uno.D13", "to": "r1.1"}),
            NetlistConnection(**{"from": "r1.2", "to": "led1.A"}),
            NetlistConnection(**{"from": "led1.C", "to": "GND"}),
        ],
    )
    # Karar düğümünün sadece 1 çıkışı var + geçersiz hedef id
    bad_flow = {
        "dugumler": [
            {"id": "n1", "tip": "kurulum", "metin": "Başla", "parcalar": ["led1", "hayali_parca"]},
            {"id": "n2", "tip": "karar", "metin": "Tek çıkışlı karar", "parcalar": []},
            {"id": "n3", "tip": "eylem", "metin": "Yak", "parcalar": ["led1"]},
        ],
        "baglantilar": [
            {"kaynak": "n1", "hedef": "n2", "etiket": None},
            {"kaynak": "n2", "hedef": "n3", "etiket": "Evet"},
            {"kaynak": "n3", "hedef": "n99", "etiket": "Tekrarla"},
        ],
    }
    errs, warns, model = validate_flow_diagram(bad_flow, netlist, "void setup(){} void loop(){ digitalWrite(13, HIGH); }")
    assert model is None
    assert any("en az 2 çıkış" in e for e in errs)
    assert any("n99" in e for e in errs)
    assert any("hayali_parca" in w for w in warns)


def test_deterministic_fallback_four_scenarios():
    # 1) Blink (karar yok!)
    blink_net = CircuitNetlist(
        board="arduino-uno",
        components=[
            NetlistComponent(id="r1", type="wokwi-resistor", label="220Ω"),
            NetlistComponent(id="led1", type="wokwi-led", label="Kırmızı LED"),
        ],
        connections=[
            NetlistConnection(**{"from": "uno.D13", "to": "r1.1"}),
            NetlistConnection(**{"from": "r1.2", "to": "led1.A"}),
            NetlistConnection(**{"from": "led1.C", "to": "GND"}),
        ],
    )
    blink_code = """
const int LED = 13;
void setup() { pinMode(LED, OUTPUT); }
void loop() {
  digitalWrite(LED, HIGH);
  delay(1000);
  digitalWrite(LED, LOW);
  delay(1000);
}
"""
    blink_flow = build_deterministic_flow_from_code(blink_net, blink_code)
    assert not any(n.tip == "karar" for n in blink_flow.dugumler), "Blink kodunda sahte karar olmamalı!"
    assert sum(1 for n in blink_flow.dugumler if n.tip == "bekle") == 2
    assert any(e.etiket == "Tekrarla" for e in blink_flow.baglantilar)

    # 2) Trafik ışığı (sıra + bekle, karar yok)
    traffic_net = CircuitNetlist(
        board="arduino-uno",
        components=[
            NetlistComponent(id="led1", type="wokwi-led", label="Kırmızı LED"),
            NetlistComponent(id="led2", type="wokwi-led", label="Sarı LED"),
            NetlistComponent(id="led3", type="wokwi-led", label="Yeşil LED"),
        ],
        connections=[
            NetlistConnection(**{"from": "uno.D12", "to": "led1.A"}),
            NetlistConnection(**{"from": "uno.D11", "to": "led2.A"}),
            NetlistConnection(**{"from": "uno.D10", "to": "led3.A"}),
        ],
    )
    traffic_code = """
void setup() { pinMode(12, OUTPUT); pinMode(11, OUTPUT); pinMode(10, OUTPUT); }
void loop() {
  digitalWrite(12, HIGH); delay(3000);
  digitalWrite(11, HIGH); delay(1000);
  digitalWrite(10, HIGH); delay(3000);
}
"""
    traffic_flow = build_deterministic_flow_from_code(traffic_net, traffic_code)
    assert not any(n.tip == "karar" for n in traffic_flow.dugumler)
    assert sum(1 for n in traffic_flow.dugumler if n.tip == "bekle") == 3

    # 3) Günebakan Servo (3 dal)
    servo_net = CircuitNetlist(
        board="arduino-uno",
        components=[
            NetlistComponent(id="ldr1", type="wokwi-photoresistor", label="Sol LDR"),
            NetlistComponent(id="ldr2", type="wokwi-photoresistor", label="Sağ LDR"),
            NetlistComponent(id="servo1", type="wokwi-servo", label="SG90 Servo"),
        ],
        connections=[
            NetlistConnection(**{"from": "ldr1.2", "to": "uno.A0"}),
            NetlistConnection(**{"from": "ldr2.2", "to": "uno.A1"}),
            NetlistConnection(**{"from": "uno.D9", "to": "servo1.PWM"}),
        ],
    )
    servo_code = """
void setup() { s.attach(9); }
void loop() {
  int l = analogRead(A0);
  int r = analogRead(A1);
  if (l > r + 30) { s.write(135); }
  else if (r > l + 30) { s.write(45); }
  else { s.write(90); }
  delay(100);
}
"""
    servo_flow = build_deterministic_flow_from_code(servo_net, servo_code)
    dec_nodes = [n for n in servo_flow.dugumler if n.tip == "karar"]
    assert len(dec_nodes) == 1
    out_edges = [e for e in servo_flow.baglantilar if e.kaynak == dec_nodes[0].id]
    assert len(out_edges) == 3, f"Günebakan servo 3 dallı olmalı, bulunan: {len(out_edges)}"

    # 4) Bluetooth araba (5 komutlu if/else-if)
    bt_net = CircuitNetlist(
        board="arduino-uno",
        components=[
            NetlistComponent(id="hc05", type="wokwi-hc-05", label="HC-05 Bluetooth"),
            NetlistComponent(id="l293d", type="wokwi-l293d", label="L293D Sürücü"),
            NetlistComponent(id="motor1", type="wokwi-dc-motor", label="Sol Motor"),
            NetlistComponent(id="motor2", type="wokwi-dc-motor", label="Sağ Motor"),
        ],
        connections=[
            NetlistConnection(**{"from": "hc05.TXD", "to": "uno.D10"}),
            NetlistConnection(**{"from": "l293d.IN1", "to": "uno.D2"}),
            NetlistConnection(**{"from": "l293d.IN2", "to": "uno.D3"}),
        ],
    )
    bt_code = """
void setup() { bt.begin(9600); pinMode(2, OUTPUT); pinMode(3, OUTPUT); }
void loop() {
  if (bt.available()) {
    char c = bt.read();
    if (c == 'F') { digitalWrite(2, HIGH); digitalWrite(3, LOW); }
    else if (c == 'B') { digitalWrite(2, LOW); digitalWrite(3, HIGH); }
    else if (c == 'L') { digitalWrite(2, LOW); digitalWrite(3, HIGH); }
    else if (c == 'R') { digitalWrite(2, HIGH); digitalWrite(3, LOW); }
    else { digitalWrite(2, LOW); digitalWrite(3, LOW); }
  }
}
"""
    bt_flow = build_deterministic_flow_from_code(bt_net, bt_code)
    bt_dec = [n for n in bt_flow.dugumler if n.tip == "karar"]
    assert len(bt_dec) == 1
    bt_out = [e for e in bt_flow.baglantilar if e.kaynak == bt_dec[0].id]
    assert len(bt_out) == 5, f"Bluetooth araba 5 dallı olmalı, bulunan: {len(bt_out)}"


def test_generate_flow_from_code_retry_and_fallback():
    netlist = CircuitNetlist(
        board="arduino-uno",
        components=[NetlistComponent(id="led1", type="wokwi-led", label="Kırmızı LED")],
        connections=[NetlistConnection(**{"from": "uno.D13", "to": "led1.A"})],
    )
    code = "void setup() { pinMode(13, OUTPUT); } void loop() { digitalWrite(13, HIGH); delay(500); digitalWrite(13, LOW); delay(500); }"

    # İki deneme de geçersiz dönerse deterministik fallback çalışmalı
    with patch("flow_service._call_llm_for_flow", return_value='{"dugumler":[],"baglantilar":[]}'):
        flow, warns, status = generate_flow_from_code(
            prompt="LED yak söndür",
            netlist=netlist,
            arduino_kodu=code,
            chosen_model="ollama/qwen2.5:1.5b",
            provider_used="ollama",
            ollama_url="http://127.0.0.1:11434",
            api_key=None,
            clean_json_fn=lambda s: s,
        )
        assert status == "DETERMINISTIC_FALLBACK"
        assert len(flow.dugumler) >= 3
        assert not any(n.tip == "karar" for n in flow.dugumler)


if __name__ == "__main__":
    test_repair_flow_with_broken_and_aliased_json()
    test_legacy_akis_adapter()
    test_flow_validator_catches_errors_and_warnings()
    test_deterministic_fallback_four_scenarios()
    test_generate_flow_from_code_retry_and_fallback()
    print("✅ TÜM BACKEND AKIŞ VE REPAIR TESTLERİ BAŞARILI!")
