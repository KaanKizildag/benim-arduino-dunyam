---
name: add-electronic-part
description: "Kid Arduino Studio projesine yeni bir elektronik sensör, modül veya Wokwi bileşeni ekleme prosedürü. Wokwi elementleri, katalog tanımları, pin takma adları, elektriksel kurallar ve envanter entegrasyonunu kapsar."
---

# Yeni Elektronik Parça / Sensör Ekleme Kılavuzu

Kid Arduino Studio'ya yeni bir elektronik parça (örneğin titreşim sensörü, BMP280, renk sensörü) eklerken sistemin tüm katmanlarının güncellenmesi gerekir.

---

## 1. Katmanlar ve Değiştirilecek Dosyalar

| Sıra | Katman | Dosya | Yapılacak İşlem |
|---|---|---|---|
| **1** | **Backend Katalog** | `backend/app/llm/catalog.py` | `SUPPORTED_TYPES_AND_PINS`, `TYPE_ALIASES`, `COMPONENT_PROMPT_DOCS`, `get_component_meta`, `keyword_map` güncellenir. |
| **2** | **Elektriksel Kurallar** | `backend/ai_service.py` | Gerekirse `auto_complete_electrical_topology` içine pull-up/pull-down direnç veya sürücü kuralı eklenir. |
| **3** | **Frontend Tipleri** | `frontend/src/types/project.ts` | Parça tipi ve pin sözlüğü tanımlanır. |
| **4** | **Wokwi Render** | `frontend/src/components/WokwiCircuitStage.vue` | İlgili `@wokwi/elements` bileşeni sahneye bağlanır veya SVG ikonu tanımlanır. |
| **5** | **Çanta / Envanter** | `frontend/src/components/InventoryModal.vue` | Çocukların çantadan parçayı seçebilmesi için parça rozeti ve ikonu eklenir. |

---

## 2. Katalog Tanımlama Örneği (`catalog.py`)

```python
# 1. Desteklenen pinler
SUPPORTED_TYPES_AND_PINS["wokwi-vibration-sensor"] = {"VCC", "GND", "DO"}

# 2. Takma adlar (AI'ın farklı adlandırmaları için)
TYPE_ALIASES["vibration"] = "wokwi-vibration-sensor"
TYPE_ALIASES["titresim"] = "wokwi-vibration-sensor"

# 3. Kompakt Prompt Dökümü (Token tasarrufu için)
COMPONENT_PROMPT_DOCS["wokwi-vibration-sensor"] = (
    "- wokwi-vibration-sensor: vib1.VCC, vib1.GND, vib1.DO (Dijital pin)"
)

# 4. Meta Bilgi (Çocuk dostu etiket ve emoji)
# "wokwi-vibration-sensor": ("Titreşim / Sarsıntı Sensörü", "📳")

# 5. Dinamik Filtreleme Anahtar Kelimeleri
# "titreşim": ["wokwi-vibration-sensor"],
# "deprem": ["wokwi-vibration-sensor"],
```

---

## 3. Doğrulama Testi
Eklemeyi yaptıktan sonra backend testlerini çalıştırın:
```bash
python -m unittest discover -s backend/tests -v
```
Testlerde parça çözümleme ve katalog çıktısının hatasız çalıştığını teyit edin.
