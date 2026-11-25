---
name: add-api-endpoint
description: "Kid Arduino Studio backendine yeni bir FastAPI uç noktası (endpoint) ekleme ve frontend api/client.ts ile bağlama standartları."
---

# Yeni API Uç Noktası (Endpoint) Ekleme Kılavuzu

Bu kılavuz, backend'e yeni bir REST veya SSE uç noktası eklerken ve frontend ile entegre ederken uyulması gereken mimari kuralları açıklar.

---

## 1. Mimari Prensipler
1. **İş Mantığını Endpoint İçine Yığmayın:** `main.py` sadece HTTP yönlendirme (routing), istek doğrulama ve hata yakalama yapmalıdır. Veri saklama `app/repositories/` içinde, servis mantığı `app/services/` içinde yer almalıdır.
2. **Pydantic Şemaları Kullanın:** Tüm istek ve yanıt gövdeleri `schemas.py` içindeki Pydantic modelleriyle tanımlanmalıdır.
3. **Frontend API İstemcisini Güncelleyin:** `App.vue` veya bileşenler doğrudan `fetch('/api/...')` çağrısı yapmamalı; daima `frontend/src/api/client.ts` içindeki `api` nesnesini kullanmalıdır.

---

## 2. Backend Endpoint Tanımı (`backend/main.py`)

```python
from fastapi import HTTPException
from pydantic import BaseModel
from schemas import CustomResponseModel
from app.services.my_service import process_custom_action

class CustomRequest(BaseModel):
    title: str
    sensor_id: str

@app.post("/api/custom-action", response_model=CustomResponseModel)
def custom_action_endpoint(req: CustomRequest):
    try:
        result = process_custom_action(req.title, req.sensor_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Beklenmeyen bir sunucu hatası oluştu.")
```

---

## 3. Frontend İstemci Tanımı (`frontend/src/api/client.ts`)

```typescript
export const api = {
  // ...
  async postCustomAction(title: string, sensorId: string): Promise<CustomResponseModel> {
    const res = await fetch('/api/custom-action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, sensor_id: sensorId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Hata: HTTP ${res.status}`);
    }
    return res.json();
  }
};
```

---

## 4. Doğrulama
```bash
python -m unittest discover -s backend/tests -v
npm.cmd --prefix frontend run typecheck
```
