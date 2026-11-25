---
name: circuit-debugging
description: "Kid Arduino Studio devre şeması, Wokwi netlisti, pin eşleşmeleri ve bağlantı adımlarındaki hataları tespit etme ve giderme rehberi."
---

# Devre ve Netlist Hata Ayıklama Kılavuzu

Kid Arduino Studio'da yapay zekanın ürettiği devre şeması (`CircuitNetlist`) ile Arduino C++ kodu arasında tam uyum olması zorunludur.

---

## 1. Sık Karşılaşılan Hatalar ve Çözümleri

### A. Pin Numarası Uyuşmazlığı (Netlist vs. C++ Kodu)
- **Belirti:** Devrede LED `uno.D13` pinine bağlıyken C++ kodunda `const int LED_PIN = 9;` yazması.
- **Mekanizma:** `backend/ai_service.py` içindeki `verify_logic_against_wiring` fonksiyonu bu uyuşmazlığı tespit eder ve otomatik onarım döngüsünü tetikler.
- **Çözüm:** Pin algılayıcı `arduino_code_utils.extract_code_pins` fonksiyonunun koddaki `pinMode`, `digitalWrite`, `analogRead` ve kütüphane nesnelerini doğru tespit ettiğinden emin olun.

### B. Eksik Gerilim Bölücü (LDR 2 Bacaklı)
- **Belirti:** 2 bacaklı LDR'nin doğrudan 5V ve A0'a bağlanması ve GND'ye 10kΩ direnç bağlanmaması.
- **Otomatik Düzeltme:** `backend/ai_service.py` -> `auto_complete_electrical_topology` fonksiyonu bu eksikliği algılar ve şemaya otomatik bir 10kΩ direnç (`r_ldr1`) ekler.

### C. LED Seri Koruma Direnci Eksikliği
- **Belirti:** LED'in doğrudan `uno.D*` ve `GND` arasına bağlanması.
- **Otomatik Düzeltme:** `auto_complete_electrical_topology` araya 220Ω koruma direnci (`r_led1`) ekler.

---

## 2. Devre Doğrulama Testi Çalıştırma
```bash
python -m unittest backend.tests.test_circuit_repair -v
```
Bu test, hasarlı netlistlerin elektriksel onarımdan başarıyla geçip geçmediğini doğrular.
