---
name: llm-prompt-change
description: "Yapay zeka sistem promptlarını, filtreleme kurallarını ve tamir döngülerini güvenle değiştirme, token maliyetini koruma ve regresyonları önleme rehberi."
---

# LLM Prompt ve Filtreleme Değişiklik Kılavuzu

Kid Arduino Studio, çocukların yazdığı doğal dil isteklerinden devre ve C++ kodu üretir. Promptlarda yapılacak dikkatsiz değişiklikler devasa token tüketimine, pin uyumsuzluklarına veya derleme hatalarına yol açabilir.

---

## 1. Altın Kurallar

1. **Promptu Şişirmeyin (Token Tasarrufu):**
   - Asla sistem promptuna statik olarak tüm parçaları ve uzun JSON örneklerini yığmayın.
   - Parça pin belgelerini daima `backend/app/llm/catalog.py` içindeki `get_filtered_component_docs(inventory, prompt)` ile dinamik olarak ekleyin.
2. **Türkçe Karakter Kuralı (Kritik):**
   - Arduino IDE derleyicisi C++ değişken ve fonksiyon adlarında Türkçe harfleri (ç, ğ, ı, ö, ş, ü) derleyemez.
   - Sistem promptunda "arduino_kodu içindeki değişken ve fonksiyon adlarında SADECE İngilizce ASCII karakterler kullan" uyarısı mutlaka korunmalıdır.
3. **Akış Diyagramını LLM'den İstemeyin:**
   - Akış diyagramı (flowchart) LLM'den istenmez; `flow_service.py` içindeki deterministik C++ analizörü tarafından üretilir (0 token).
4. **Token Sınırını Koruyun:**
   - LiteLLM çağrılarında `max_tokens=2500` sınırını kaldırmayın veya aşmayın.
5. **Önbellek Entegrasyonu:**
   - Tekrarlanan istekleri önlemek için `app.llm.cache.get_cached_project` ve `set_cached_project` döngüsünü koruyun.

---

## 2. Prompt Değişikliğini Doğrulama
Prompt veya prompt_filter üzerinde bir değişiklik yapıldığında mutlaka aşağıdaki testleri çalıştırın:
```bash
python -m unittest discover -s backend/tests -v
```
Özellikle şu test dosyalarının geçtiğinden emin olun:
- `test_prompt_filter.py` (Güvenlik ihlali, konu dışı ve geçerli prompt filtreleri)
- `test_catalog_and_cache.py` (Dinamik filtreleme ve önbellek)
- `test_characterization.py` (One-shot prompt yapısı ve akış)
