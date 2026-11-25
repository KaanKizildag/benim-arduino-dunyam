---
name: release-checklist
description: "Kid Arduino Studio projesinde yeni bir sürüm, refactor veya özellik tamamlandığında uygulanması zorunlu kalite, test, tip kontrolü ve derleme kontrol listesi."
---

# Kid Arduino Studio — Sürüm ve Commit Öncesi Kontrol Listesi

Bu liste, kod tabanına yeni bir özellik eklendiğinde veya refactor yapıldığında branch commitlenmeden önce adım adım uygulanmalıdır.

---

## 1. Kod Temizliği ve Statik Analiz
- [ ] **Ölü Kod:** Kullanılmayan Vue bileşenleri, geçici test scriptleri veya çağrılmayan importlar silindi mi?
- [ ] **Konsol Logları:** Hata ayıklama amaçlı eklenen geçici `console.log` veya `print` satırları temizlendi mi?
- [ ] **Sır / Gizli Anahtarlar:** Hiçbir API anahtarı (Gemini, OpenAI, Claude) koda veya `.env.example` içine yazılmadı mı?

---

## 2. Otomatik Testler
Aşağıdaki iki test paketi de terminalde sırayla çalıştırılmalı ve **0 hata** vermelidir:

```bash
# 1. Backend Python Unit Testleri (19+ test, 0.03s)
python -m unittest discover -s backend/tests -v

# 2. Frontend TypeScript Tip Kontrolü
npm.cmd --prefix frontend run typecheck

# 3. Frontend Üretim Paketi Derlemesi
npm.cmd --prefix frontend run build
```

---

## 3. Token ve Güvenlik Denetimi
- [ ] Dinamik katalog (`catalog.py`) kullanılarak prompt boyutu minimumda tutuldu mu?
- [ ] LiteLLM çağrısında `max_tokens=2500` sınırı tanımlı mı?
- [ ] Deterministik akış (`build_deterministic_flow_from_code`) ilk adım olarak çalışıyor mu?
- [ ] Yanıt önbelleği (`cache.py`) devrede mi?
- [ ] Çocuk koruma guardrailleri (`prompt_filter.py`) devrede mi?

---

## 4. Git İşlemleri
- [ ] Değişiklikler doğru branch üzerinde mi? (Kullanıcı onayı olmadan `master` branch'e doğrudan merge yapılmaz).
- [ ] `git status` çıktısında unutulmuş geçici dosya veya `.db` bulunmuyor mu?
