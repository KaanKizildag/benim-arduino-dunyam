"""
Koddan Dinamik Akış Diyagramı Üretimi, Doğrulama, Geriye Uyumluluk Adaptörü ve Deterministik Fallback.
"""

import json
import os
import re
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import httpx

from schemas import (
    AkisBaglantisi,
    AkisDiyagrami,
    AkisDugumu,
    CircuitNetlist,
)

VALID_FLOW_NODE_TYPES: Set[str] = {
    "baslangic",
    "kurulum",
    "oku",
    "karar",
    "eylem",
    "bekle",
    "dongu",
    "bitis",
}

FLOW_FROM_CODE_SYSTEM_PROMPT = """Sen çocuklar için Arduino C++ kodunu görsel akış diyagramına çeviren bir eğitmensin.
Sana kullanıcının isteği, devredeki gerçek parçalar (id, type, label) ve son Arduino C++ kodu verilecek.
Görevin: Bu kodun `setup()` ve `loop()` mantığını, çocukların kolayca anlayacağı sade Türkçe ile, SADECE JSON formatında bir düğüm/kenar akış diyagramına (`dugumler`, `baglantilar`) dönüştürmek.

KESİN KURALLAR:
1. Çıktı şeması:
   {"dugumler":[{"id":"n1","tip":"baslangic|kurulum|oku|karar|eylem|bekle|dongu|bitis","metin":"...","parcalar":["led1"]}],"baglantilar":[{"kaynak":"n1","hedef":"n2","etiket":null}]}
2. Toplam 3 ile 12 arasında düğüm kullan.
3. Koddaki her `if / else if / else / switch-case` dalı, `delay(...)` ve `loop()` tekrarı gerçek düğümlerle gösterilmeli.
4. `karar` düğümünün EN AZ 2 çıkışı olmalı (`else if` veya `switch` için 3, 4, 5 çıkış serbest!). Her çıkışta açıklayıcı `etiket` yaz (örn. "Evet", "Hayır", "Sol > Sağ", "F (İleri)").
5. SENSÖRSÜZ / KARARSIZ PROJELERDE (blink, trafik ışığı, sırayla yanan LED'ler): Kodda `if` veya `switch` yoksa ASLA sahte `karar` düğümü ekleme! Düz sıra (`eylem` -> `bekle` -> `eylem` -> `bekle`) ve en sondan döngü başına geri dönen kenar kullan.
6. `parcalar` listesinde SADECE sana verilen bileşen listesinde bulunan gerçek `id`'leri yaz (örn. `["led1"]`, `["ldr1", "ldr2"]`). Dirençleri yazmana gerek yok; bilmediğin veya listede olmayan id ASLA yazma.
7. `loop()` döngüsünü, son düğümden (veya dalların birleştiği düğümden) döngünün ilk düğümüne geri giden bir kenarla ifade et (`etiket: "Tekrarla"`).
8. Kodda olmayan hiçbir sensör, koşul veya eylem uydurma!

ÖRNEK 1 (Sensörsüz Trafik Işığı - Karar yok, sıra + bekle + döngü):
{"dugumler":[{"id":"n1","tip":"kurulum","metin":"Kırmızı, Sarı ve Yeşil LED pinlerini çıkış olarak hazırla","parcalar":["led1","led2","led3"]},{"id":"n2","tip":"eylem","metin":"Kırmızı LED'i yak, diğerlerini söndür","parcalar":["led1"]},{"id":"n3","tip":"bekle","metin":"3 saniye bekle","parcalar":[]},{"id":"n4","tip":"eylem","metin":"Sarı LED'i yak","parcalar":["led2"]},{"id":"n5","tip":"bekle","metin":"1 saniye bekle","parcalar":[]},{"id":"n6","tip":"eylem","metin":"Yeşil LED'i yak","parcalar":["led3"]},{"id":"n7","tip":"bekle","metin":"3 saniye bekle","parcalar":[]}],"baglantilar":[{"kaynak":"n1","hedef":"n2","etiket":null},{"kaynak":"n2","hedef":"n3","etiket":null},{"kaynak":"n3","hedef":"n4","etiket":null},{"kaynak":"n4","hedef":"n5","etiket":null},{"kaynak":"n5","hedef":"n6","etiket":null},{"kaynak":"n6","hedef":"n7","etiket":null},{"kaynak":"n7","hedef":"n2","etiket":"Tekrarla"}]}

ÖRNEK 2 (Çift LDR Günebakan Servo - 3 dallı karar):
{"dugumler":[{"id":"n1","tip":"kurulum","metin":"Servo motoru 90° orta konuma getir","parcalar":["servo1"]},{"id":"n2","tip":"oku","metin":"Sol ve Sağ LDR sensörlerinden ışık değerlerini oku","parcalar":["ldr1","ldr2"]},{"id":"n3","tip":"karar","metin":"Hangi tarafta ışık daha güçlü?","parcalar":["ldr1","ldr2"]},{"id":"n4","tip":"eylem","metin":"Servo motoru sola (135°) döndür","parcalar":["servo1"]},{"id":"n5","tip":"eylem","metin":"Servo motoru sağa (45°) döndür","parcalar":["servo1"]},{"id":"n6","tip":"eylem","metin":"Servo motoru ortada (90°) tut","parcalar":["servo1"]},{"id":"n7","tip":"bekle","metin":"100 milisaniye bekle","parcalar":[]}],"baglantilar":[{"kaynak":"n1","hedef":"n2","etiket":null},{"kaynak":"n2","hedef":"n3","etiket":null},{"kaynak":"n3","hedef":"n4","etiket":"Sol daha parlak"},{"kaynak":"n3","hedef":"n5","etiket":"Sağ daha parlak"},{"kaynak":"n3","hedef":"n6","etiket":"Işık eşit"},{"kaynak":"n4","hedef":"n7","etiket":null},{"kaynak":"n5","hedef":"n7","etiket":null},{"kaynak":"n6","hedef":"n7","etiket":null},{"kaynak":"n7","hedef":"n2","etiket":"Tekrarla"}]}

ÖRNEK 3 (Bluetooth Araba - 5 komutlu dallanma):
{"dugumler":[{"id":"n1","tip":"kurulum","metin":"Bluetooth (HC-05) ve motor sürücü pinlerini başlat","parcalar":["hc05","l293d"]},{"id":"n2","tip":"oku","metin":"Telefondan gelen Bluetooth komutunu oku","parcalar":["hc05"]},{"id":"n3","tip":"karar","metin":"Hangi yön komutu geldi?","parcalar":["hc05"]},{"id":"n4","tip":"eylem","metin":"İki motoru ileri çalıştır","parcalar":["motor1","motor2"]},{"id":"n5","tip":"eylem","metin":"İki motoru geri çalıştır","parcalar":["motor1","motor2"]},{"id":"n6","tip":"eylem","metin":"Sola dön","parcalar":["motor1","motor2"]},{"id":"n7","tip":"eylem","metin":"Sağa dön","parcalar":["motor1","motor2"]},{"id":"n8","tip":"eylem","metin":"Her iki motoru durdur","parcalar":["motor1","motor2"]}],"baglantilar":[{"kaynak":"n1","hedef":"n2","etiket":null},{"kaynak":"n2","hedef":"n3","etiket":null},{"kaynak":"n3","hedef":"n4","etiket":"F (İleri)"},{"kaynak":"n3","hedef":"n5","etiket":"B (Geri)"},{"kaynak":"n3","hedef":"n6","etiket":"L (Sol)"},{"kaynak":"n3","hedef":"n7","etiket":"R (Sağ)"},{"kaynak":"n3","hedef":"n8","etiket":"S (Dur)"},{"kaynak":"n4","hedef":"n2","etiket":"Tekrarla"},{"kaynak":"n5","hedef":"n2","etiket":"Tekrarla"},{"kaynak":"n6","hedef":"n2","etiket":"Tekrarla"},{"kaynak":"n7","hedef":"n2","etiket":"Tekrarla"},{"kaynak":"n8","hedef":"n2","etiket":"Tekrarla"}]}
"""


def legacy_akis_to_diyagram(
    raw_akis: Dict[str, Any],
    netlist_components: Optional[List[Dict[str, Any]]] = None,
) -> AkisDiyagrami:
    """Eski 4 alanlı akis_adimlari (gozlemle/karar_ver/evet_sonucu/hayir_sonucu) yapısını AkisDiyagrami'na çevirir."""
    gozlemle = str(raw_akis.get("gozlemle") or "").strip() or "Devreyi izle."
    karar_ver = str(raw_akis.get("karar_ver") or "").strip() or "Koşul sağlandı mı?"
    evet = str(raw_akis.get("evet_sonucu") or "").strip() or "Eylemi çalıştır."
    hayir = str(raw_akis.get("hayir_sonucu") or "").strip() or "Bekle."

    input_ids: List[str] = []
    output_ids: List[str] = []
    input_hints = ("sensor", "photoresistor", "hc-sr04", "pushbutton", "potentiometer", "dht", "pir", "joystick", "hc-05", "hc-06", "ir-receiver")
    output_hints = ("led", "buzzer", "servo", "motor", "relay", "lcd", "ssd1306", "l293d", "l298n")

    for c in (netlist_components or []):
        cid = c.get("id") if isinstance(c, dict) else getattr(c, "id", None)
        ctype = (c.get("type") if isinstance(c, dict) else getattr(c, "type", "")) or ""
        if not cid or ctype == "wokwi-resistor":
            continue
        if any(h in ctype for h in input_hints):
            input_ids.append(cid)
        elif any(h in ctype for h in output_hints):
            output_ids.append(cid)

    dugumler = [
        AkisDugumu(id="n1", tip="baslangic", metin="Arduino açılır ve devre başlar", parcalar=[]),
        AkisDugumu(id="n2", tip="oku", metin=gozlemle, parcalar=input_ids[:3]),
        AkisDugumu(id="n3", tip="karar", metin=karar_ver, parcalar=input_ids[:2]),
        AkisDugumu(id="n4", tip="eylem", metin=evet, parcalar=output_ids[:3]),
        AkisDugumu(id="n5", tip="eylem", metin=hayir, parcalar=output_ids[:3]),
    ]
    baglantilar = [
        AkisBaglantisi(kaynak="n1", hedef="n2", etiket=None),
        AkisBaglantisi(kaynak="n2", hedef="n3", etiket=None),
        AkisBaglantisi(kaynak="n3", hedef="n4", etiket="Evet"),
        AkisBaglantisi(kaynak="n3", hedef="n5", etiket="Hayır"),
        AkisBaglantisi(kaynak="n4", hedef="n2", etiket="Tekrarla"),
        AkisBaglantisi(kaynak="n5", hedef="n2", etiket="Tekrarla"),
    ]
    return AkisDiyagrami(dugumler=dugumler, baglantilar=baglantilar)


def count_code_decision_branches(code: str) -> int:
    """Arduino kodundaki if / else if / else / case dal sayısını kabaca tahmin eder."""
    loop_body = _extract_function_body(code, "loop") or code
    # Yorumları temizle
    cleaned = re.sub(r"//.*", "", loop_body)
    cleaned = re.sub(r"/\*[\s\S]*?\*/", "", cleaned)

    cases = len(re.findall(r"\bcase\b\s+[^:]+:", cleaned))
    defaults = len(re.findall(r"\bdefault\s*:", cleaned))
    if cases > 0:
        return cases + defaults

    ifs = len(re.findall(r"\bif\s*\(", cleaned))
    else_ifs = len(re.findall(r"\belse\s+if\s*\(", cleaned))
    elses = len(re.findall(r"\belse\s*\{", cleaned))
    if ifs == 0:
        return 0
    # Her if kendi başına en az 2 yol (doğru/yanlış) veya else/else-if dalları üretir
    return max(2, ifs + else_ifs + elses)


def validate_flow_diagram(
    flow_dict: Any,
    netlist: CircuitNetlist,
    code: str = "",
) -> Tuple[List[str], List[str], Optional[AkisDiyagrami]]:
    """
    Akış diyagramını şema, kenar bütünlüğü, karar dalı sayısı, parça id'leri ve kod uyumu açısından doğrular.
    Dönüş: (errors, warnings, validated_model_or_None)
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(flow_dict, dict):
        return ["Akış diyagramı geçerli bir JSON nesnesi değil."], warnings, None

    raw_nodes = flow_dict.get("dugumler")
    raw_edges = flow_dict.get("baglantilar")
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        return ["'dugumler' ve 'baglantilar' listeleri zorunludur."], warnings, None

    if len(raw_nodes) < 3 or len(raw_nodes) > 12:
        errors.append(f"Düğüm sayısı 3 ile 12 arasında olmalıdır (bulunan: {len(raw_nodes)}).")

    valid_comp_ids = {c.id for c in (netlist.components or [])}
    node_ids: Set[str] = set()
    cleaned_nodes: List[AkisDugumu] = []

    for idx, n in enumerate(raw_nodes):
        if not isinstance(n, dict):
            errors.append(f"{idx + 1}. düğüm geçerli bir nesne değil.")
            continue
        nid = str(n.get("id") or "").strip()
        ntip = str(n.get("tip") or "").strip().lower()
        nmetin = str(n.get("metin") or "").strip()
        nparcalar_raw = n.get("parcalar") if isinstance(n.get("parcalar"), list) else []

        if not nid:
            errors.append(f"{idx + 1}. düğümün 'id' alanı boş.")
            continue
        if nid in node_ids:
            errors.append(f"Tekrarlayan düğüm id'si: '{nid}'.")
            continue
        node_ids.add(nid)

        if ntip not in VALID_FLOW_NODE_TYPES:
            errors.append(f"Geçersiz düğüm tipi '{ntip}' (düğüm: '{nid}').")
            continue
        if not nmetin:
            errors.append(f"Düğüm '{nid}' metin alanı boş.")
            continue

        valid_parcalar: List[str] = []
        for p in nparcalar_raw:
            ps = str(p).strip()
            if ps in valid_comp_ids:
                if ps not in valid_parcalar:
                    valid_parcalar.append(ps)
            elif ps:
                warnings.append(f"Akış düğümü '{nid}' içindeki bilinmeyen parça '{ps}' temizlendi.")

        cleaned_nodes.append(
            AkisDugumu(id=nid, tip=ntip, metin=nmetin, parcalar=valid_parcalar)
        )

    out_degree: Dict[str, int] = {n.id: 0 for n in cleaned_nodes}
    cleaned_edges: List[AkisBaglantisi] = []

    for idx, e in enumerate(raw_edges):
        if not isinstance(e, dict):
            errors.append(f"{idx + 1}. bağlantı geçerli bir nesne değil.")
            continue
        src = str(e.get("kaynak") or "").strip()
        dst = str(e.get("hedef") or "").strip()
        etiket = e.get("etiket")
        etiket_str = str(etiket).strip() if etiket is not None and str(etiket).strip() else None

        if src not in node_ids:
            errors.append(f"Bağlantı kaynağı '{src}' düğüm listesinde yok.")
            continue
        if dst not in node_ids:
            errors.append(f"Bağlantı hedefi '{dst}' düğüm listesinde yok.")
            continue

        out_degree[src] = out_degree.get(src, 0) + 1
        cleaned_edges.append(AkisBaglantisi(kaynak=src, hedef=dst, etiket=etiket_str))

    if not cleaned_edges:
        errors.append("Akış diyagramında en az bir bağlantı olmalıdır.")

    decision_nodes = [n for n in cleaned_nodes if n.tip == "karar"]
    total_decision_branches = 0
    for dn in decision_nodes:
        deg = out_degree.get(dn.id, 0)
        total_decision_branches += deg
        if deg < 2:
            errors.append(f"Karar düğümü '{dn.id}' en az 2 çıkış bağlantısına sahip olmalıdır (bulunan: {deg}).")

    # Koddaki if/else if/case dallarıyla tutarlılık uyarısı (blocking değil, warning)
    if code.strip():
        code_branches = count_code_decision_branches(code)
        if code_branches == 0 and len(decision_nodes) > 0:
            warnings.append("Kodda koşullu dallanma (if/switch) yokken akışta karar düğümü üretildi.")
        elif code_branches >= 2 and len(decision_nodes) == 0:
            warnings.append(f"Kodda ~{code_branches} dallı karar yapısı var ancak akışta karar düğümü yok.")
        elif code_branches >= 3 and total_decision_branches < 3:
            warnings.append(
                f"Kodda {code_branches} dal bulunmasına rağmen akışta yalnızca {total_decision_branches} karar çıkışı var."
            )

    if errors:
        return errors, warnings, None

    return [], warnings, AkisDiyagrami(dugumler=cleaned_nodes, baglantilar=cleaned_edges)


# ---------------------------------------------------------------------------
# Deterministik Kod -> Akış Diyagramı Parser (Fallback)
# ---------------------------------------------------------------------------

def _extract_function_body(code: str, func_name: str) -> str:
    """Verilen C++ fonksiyonunun (örn. 'setup', 'loop') dış süslü parantez gövdesini döndürür."""
    m = re.search(rf"\bvoid\s+{re.escape(func_name)}\s*\([^)]*\)\s*\{{", code)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(code) and depth > 0:
        ch = code[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return code[start:i]
        i += 1
    return code[start:]


def _extract_braced_block(text: str, open_brace_idx: int) -> Tuple[str, int]:
    """open_brace_idx ('{' konumu) ile eşleşen '}' konumunu bulur ve iç metni döndürür."""
    depth = 1
    i = open_brace_idx + 1
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_idx + 1 : i], i + 1
        i += 1
    return text[open_brace_idx + 1 :], len(text)


def _format_delay_text(ms_str: str) -> str:
    try:
        ms = int(ms_str)
        if ms >= 1000 and ms % 1000 == 0:
            return f"{ms // 1000} saniye bekle"
        if ms >= 1000:
            return f"{ms / 1000:.1f} saniye bekle"
        return f"{ms} milisaniye bekle"
    except Exception:
        return "Kısa süre bekle"


def _summarize_code_snippet(
    snippet: str,
    comp_by_id: Dict[str, Tuple[str, str]],
    pin_to_comp_ids: Dict[str, List[str]],
    var_to_pin: Dict[str, str],
) -> Tuple[str, List[str]]:
    """Küçük bir C++ kod bloğundan çocuk dostu Türkçe özet ve kullanılan parça id'lerini çıkarır."""
    used_ids: List[str] = []

    def add_pin_comps(pin_expr: str) -> None:
        expr = pin_expr.strip()
        resolved = var_to_pin.get(expr, expr).upper()
        if resolved.isdigit():
            resolved = f"D{resolved}"
        for cid in pin_to_comp_ids.get(resolved, []):
            if cid not in used_ids:
                used_ids.append(cid)

    actions: List[str] = []

    # Servo write
    for m in re.finditer(r"(\w+)\.write\s*\(\s*([^)]+)\s*\)", snippet):
        angle = m.group(2).strip()
        for cid, (ctype, _) in comp_by_id.items():
            if "servo" in ctype and cid not in used_ids:
                used_ids.append(cid)
        actions.append(f"Servoyu {angle}° konumuna çevir")

    # digitalWrite
    high_labels: List[str] = []
    low_labels: List[str] = []
    for m in re.finditer(r"digitalWrite\s*\(\s*([^,]+)\s*,\s*(HIGH|LOW|1|0)\s*\)", snippet):
        pin_expr, val = m.group(1).strip(), m.group(2).strip()
        add_pin_comps(pin_expr)
        resolved = var_to_pin.get(pin_expr, pin_expr).upper()
        if resolved.isdigit():
            resolved = f"D{resolved}"
        cids = pin_to_comp_ids.get(resolved, [])
        lbl = comp_by_id[cids[0]][1] if cids and cids[0] in comp_by_id else pin_expr
        if val in ("HIGH", "1"):
            if lbl not in high_labels:
                high_labels.append(lbl)
        else:
            if lbl not in low_labels:
                low_labels.append(lbl)

    if high_labels and not low_labels:
        actions.append(f"{', '.join(high_labels[:2])} aç/yak")
    elif low_labels and not high_labels:
        actions.append(f"{', '.join(low_labels[:2])} kapat/durdur")
    elif high_labels and low_labels:
        actions.append(f"{', '.join(high_labels[:2])} çalıştır")

    # tone / noTone
    if re.search(r"\btone\s*\(", snippet):
        for cid, (ctype, _) in comp_by_id.items():
            if "buzzer" in ctype and cid not in used_ids:
                used_ids.append(cid)
        actions.append("Buzzer ile ses çal")
    elif re.search(r"\bnoTone\s*\(", snippet):
        for cid, (ctype, _) in comp_by_id.items():
            if "buzzer" in ctype and cid not in used_ids:
                used_ids.append(cid)
        actions.append("Buzzer sesini sustur")

    # lcd.print
    lcd_m = re.search(r"lcd\.print\s*\(\s*\"([^\"]+)\"\s*\)", snippet)
    if lcd_m:
        for cid, (ctype, _) in comp_by_id.items():
            if "lcd" in ctype and cid not in used_ids:
                used_ids.append(cid)
        actions.append(f"Ekrana '{lcd_m.group(1)[:18]}' yaz")

    if not actions:
        if used_ids:
            names = [comp_by_id[cid][1] for cid in used_ids[:2] if cid in comp_by_id]
            return f"{', '.join(names)} parçasını güncelle", used_ids
        return "Çıkış komutlarını uygula", used_ids

    return "; ".join(actions[:2]), used_ids


def build_deterministic_flow_from_code(
    netlist: CircuitNetlist,
    code: str,
) -> AkisDiyagrami:
    """
    LLM akış üretimi başarısız olduğunda Arduino kodundan (setup/loop) deterministik olarak
    gerçek dalları, bekleme sürelerini ve bileşenleri yansıtan bir AkisDiyagrami üretir.
    """
    comp_by_id: Dict[str, Tuple[str, str]] = {
        c.id: (c.type, c.label) for c in (netlist.components or []) if c.type != "wokwi-resistor"
    }

    # Basit pin -> bileşen id eşlemesi (doğrudan veya direnç üzerinden)
    pin_to_comp_ids: Dict[str, List[str]] = {}
    resistor_ids = {c.id for c in (netlist.components or []) if c.type == "wokwi-resistor"}
    # Direnç -> diğer bağlı bileşen
    res_neighbors: Dict[str, Set[str]] = {}
    for conn in (netlist.connections or []):
        f_part = conn.from_pin.split(".")[0]
        t_part = conn.to_pin.split(".")[0]
        if f_part in resistor_ids and t_part in comp_by_id:
            res_neighbors.setdefault(f_part, set()).add(t_part)
        elif t_part in resistor_ids and f_part in comp_by_id:
            res_neighbors.setdefault(t_part, set()).add(f_part)

    for conn in (netlist.connections or []):
        for a, b in ((conn.from_pin, conn.to_pin), (conn.to_pin, conn.from_pin)):
            if a.lower().startswith("uno."):
                uno_pin = a.split(".", 1)[1].upper()
                other_part = b.split(".")[0]
                if other_part in comp_by_id:
                    pin_to_comp_ids.setdefault(uno_pin, [])
                    if other_part not in pin_to_comp_ids[uno_pin]:
                        pin_to_comp_ids[uno_pin].append(other_part)
                elif other_part in res_neighbors:
                    for nb in res_neighbors[other_part]:
                        pin_to_comp_ids.setdefault(uno_pin, [])
                        if nb not in pin_to_comp_ids[uno_pin]:
                            pin_to_comp_ids[uno_pin].append(nb)

    # Koddaki const int / #define sabitlerini pin'e çöz
    var_to_pin: Dict[str, str] = {}
    for m in re.finditer(r"(?:const\s+)?int\s+(\w+)\s*=\s*(A?\d+)\s*;", code):
        var_to_pin[m.group(1)] = m.group(2)
    for m in re.finditer(r"#define\s+(\w+)\s+(A?\d+)\b", code):
        var_to_pin[m.group(1)] = m.group(2)

    nodes: List[AkisDugumu] = []
    edges: List[AkisBaglantisi] = []
    nid_counter = 1

    def add_node(tip: str, metin: str, parcalar: Optional[List[str]] = None) -> str:
        nonlocal nid_counter
        nid = f"n{nid_counter}"
        nid_counter += 1
        nodes.append(AkisDugumu(id=nid, tip=tip, metin=metin, parcalar=(parcalar or [])[:3]))
        return nid

    setup_body = _extract_function_body(code, "setup")
    loop_body = _extract_function_body(code, "loop") or code
    # Yorumları temizle
    loop_clean = re.sub(r"//.*", "", loop_body)
    loop_clean = re.sub(r"/\*[\s\S]*?\*/", "", loop_clean)

    # 1) Kurulum düğümü
    all_non_res_ids = list(comp_by_id.keys())
    if setup_body.strip():
        setup_id = add_node(
            "kurulum",
            "Pinleri ve bağlı bileşenleri başlat",
            all_non_res_ids[:3],
        )
    else:
        setup_id = add_node("baslangic", "Arduino çalışmaya başlar", [])

    prev_id = setup_id
    loop_entry_id: Optional[str] = None

    # 2) Loop başındaki sensör / giriş okumaları
    read_comp_ids: List[str] = []
    read_descriptions: List[str] = []
    for m in re.finditer(r"(analogRead|digitalRead)\s*\(\s*([^)]+)\s*\)", loop_clean):
        pin_expr = m.group(2).strip()
        resolved = var_to_pin.get(pin_expr, pin_expr).upper()
        if resolved.isdigit():
            resolved = f"D{resolved}"
        for cid in pin_to_comp_ids.get(resolved, []):
            if cid not in read_comp_ids:
                read_comp_ids.append(cid)
                read_descriptions.append(comp_by_id[cid][1])

    if re.search(r"\b(bt|Serial|bluetooth)\w*\.read\s*\(", loop_clean):
        for cid, (ctype, lbl) in comp_by_id.items():
            if ("hc-05" in ctype or "hc-06" in ctype) and cid not in read_comp_ids:
                read_comp_ids.append(cid)
                read_descriptions.append(lbl)
        if not read_descriptions:
            read_descriptions.append("Bluetooth/Seri veri")

    if re.search(r"\bpulseIn\s*\(", loop_clean):
        for cid, (ctype, lbl) in comp_by_id.items():
            if "hc-sr04" in ctype and cid not in read_comp_ids:
                read_comp_ids.append(cid)
                read_descriptions.append(lbl)

    if read_descriptions:
        read_id = add_node(
            "oku",
            f"{', '.join(read_descriptions[:2])} değerini oku",
            read_comp_ids[:3],
        )
        edges.append(AkisBaglantisi(kaynak=prev_id, hedef=read_id, etiket=None))
        prev_id = read_id
        loop_entry_id = read_id

    # 3) switch/case veya if/else if/else dallarını yakala
    branches: List[Tuple[str, str]] = []  # (etiket, snippet)
    decision_text = ""

    switch_m = re.search(r"\bswitch\s*\(([^)]+)\)\s*\{", loop_clean)
    if switch_m:
        decision_text = f"'{switch_m.group(1).strip()}' komutunu kontrol et"
        sw_body, _ = _extract_braced_block(loop_clean, switch_m.end() - 1)
        case_matches = list(re.finditer(r"\b(?:case\s+([^:]+)|default)\s*:", sw_body))
        for idx, cm in enumerate(case_matches):
            lbl = cm.group(1).strip().strip("'\"") if cm.group(1) else "Diğer"
            seg_start = cm.end()
            seg_end = case_matches[idx + 1].start() if idx + 1 < len(case_matches) else len(sw_body)
            branches.append((lbl, sw_body[seg_start:seg_end]))
    else:
        # En içteki anlamlı if/else-if/else zincirini (ör. bt.available() içindeki if zincirini) bul
        search_area = loop_clean
        avail_m = re.search(r"\bif\s*\([^)]*available\s*\(\s*\)[^)]*\)\s*\{", loop_clean)
        if avail_m:
            inner, _ = _extract_braced_block(loop_clean, avail_m.end() - 1)
            if re.search(r"\bif\s*\(", inner):
                search_area = inner

        if_m = re.search(r"\bif\s*\(([^)]+)\)\s*\{", search_area)
        if if_m:
            cond1 = if_m.group(1).strip()
            decision_text = f"Koşulu kontrol et: {cond1[:36]}?"
            blk1, cursor = _extract_braced_block(search_area, if_m.end() - 1)
            branches.append((cond1[:22] if "==" in cond1 or ">" in cond1 or "<" in cond1 else "Evet", blk1))

            while cursor < len(search_area) and len(branches) < 6:
                rest = search_area[cursor:]
                elif_m = re.match(r"\s*else\s+if\s*\(([^)]+)\)\s*\{", rest)
                if elif_m:
                    cond_i = elif_m.group(1).strip()
                    blk_i, next_rel = _extract_braced_block(rest, elif_m.end() - 1)
                    branches.append((cond_i[:22], blk_i))
                    cursor += next_rel
                    continue
                else_m = re.match(r"\s*else\s*\{", rest)
                if else_m:
                    blk_e, next_rel = _extract_braced_block(rest, else_m.end() - 1)
                    branches.append(("Diğer / Hayır", blk_e))
                    cursor += next_rel
                break

            if len(branches) == 1:
                branches.append(("Hayır", ""))

    # 4) Dallanma varsa karar + dal düğümleri oluştur; yoksa sıralı eylem/bekle düğümleri oluştur
    if branches:
        dec_id = add_node("karar", decision_text or "Koşulu kontrol et?", read_comp_ids[:2])
        edges.append(AkisBaglantisi(kaynak=prev_id, hedef=dec_id, etiket=None))
        if loop_entry_id is None:
            loop_entry_id = dec_id

        branch_end_ids: List[str] = []
        # En fazla 6 dal (toplam <= 12 düğüm sınırını korumak için)
        for lbl, snippet in branches[:6]:
            if snippet.strip():
                summary, used = _summarize_code_snippet(snippet, comp_by_id, pin_to_comp_ids, var_to_pin)
            else:
                summary, used = "Bekle / işlem yapma", []
            b_id = add_node("eylem", summary, used)
            edges.append(AkisBaglantisi(kaynak=dec_id, hedef=b_id, etiket=lbl))
            branch_end_ids.append(b_id)

        # Loop sonunda ortak delay varsa bekle düğümü ekle
        tail_delay = re.search(r"delay\s*\(\s*(\d+)\s*\)", loop_clean[-120:])
        if tail_delay and len(nodes) < 12:
            wait_id = add_node("bekle", _format_delay_text(tail_delay.group(1)), [])
            for bid in branch_end_ids:
                edges.append(AkisBaglantisi(kaynak=bid, hedef=wait_id, etiket=None))
            edges.append(AkisBaglantisi(kaynak=wait_id, hedef=loop_entry_id, etiket="Tekrarla"))
        else:
            for bid in branch_end_ids:
                edges.append(AkisBaglantisi(kaynak=bid, hedef=loop_entry_id, etiket="Tekrarla"))
    else:
        # Sensörsüz / sıralı kod (blink, trafik ışığı vb.) — delay(...) noktalarından böl
        parts = re.split(r"(delay\s*\(\s*\d+\s*\)\s*;?)", loop_clean)
        step_ids: List[str] = []
        for part in parts:
            if len(nodes) >= 11:
                break
            p_str = part.strip()
            if not p_str:
                continue
            dm = re.match(r"delay\s*\(\s*(\d+)\s*\)", p_str)
            if dm:
                w_id = add_node("bekle", _format_delay_text(dm.group(1)), [])
                edges.append(AkisBaglantisi(kaynak=prev_id, hedef=w_id, etiket=None))
                prev_id = w_id
                step_ids.append(w_id)
                if loop_entry_id is None:
                    loop_entry_id = w_id
            elif re.search(r"(digitalWrite|analogWrite|\.write|tone|noTone|lcd\.print)", p_str):
                summary, used = _summarize_code_snippet(p_str, comp_by_id, pin_to_comp_ids, var_to_pin)
                a_id = add_node("eylem", summary, used)
                edges.append(AkisBaglantisi(kaynak=prev_id, hedef=a_id, etiket=None))
                prev_id = a_id
                step_ids.append(a_id)
                if loop_entry_id is None:
                    loop_entry_id = a_id

        if not step_ids:
            a_id = add_node("eylem", "Devre adımını çalıştır", all_non_res_ids[:2])
            edges.append(AkisBaglantisi(kaynak=prev_id, hedef=a_id, etiket=None))
            prev_id = a_id
            loop_entry_id = a_id

        # En az 3 düğüm garantisi
        if len(nodes) < 3:
            w_id = add_node("bekle", "Kısa süre bekle", [])
            edges.append(AkisBaglantisi(kaynak=prev_id, hedef=w_id, etiket=None))
            prev_id = w_id

        edges.append(AkisBaglantisi(kaynak=prev_id, hedef=loop_entry_id or setup_id, etiket="Tekrarla"))

    return AkisDiyagrami(dugumler=nodes, baglantilar=edges)


def _call_llm_for_flow(
    system_prompt: str,
    user_prompt: str,
    chosen_model: str,
    provider_used: str,
    ollama_url: str,
    api_key: Optional[str],
) -> Optional[str]:
    if provider_used == "ollama":
        clean_model = chosen_model.replace("ollama/", "")
        is_reasoning = any(k in clean_model.lower() for k in ("deepseek-r1", "qwq", "r1"))
        payload: Dict[str, Any] = {
            "model": clean_model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.15,
                "num_predict": 1400 if is_reasoning else 750,
            },
        }
        if not is_reasoning:
            payload["format"] = "json"
        try:
            res = httpx.post(f"{ollama_url}/api/generate", json=payload, timeout=90.0)
            if res.status_code == 200:
                return res.json().get("response", "")
        except Exception as e:
            print(f"[Flow AI] Ollama hatası: {e}")
            return None
    else:
        key = api_key
        if not key:
            if "gemini" in chosen_model:
                key = os.getenv("GEMINI_API_KEY")
            elif "gpt" in chosen_model:
                key = os.getenv("OPENAI_API_KEY")
            elif "claude" in chosen_model:
                key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            return None
        try:
            from litellm import completion

            response = completion(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                api_key=key,
                temperature=0.15,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[Flow AI] Bulut AI hatası: {e}")
            return None
    return None


def generate_flow_from_code(
    prompt: str,
    netlist: CircuitNetlist,
    arduino_kodu: str,
    chosen_model: str,
    provider_used: str,
    ollama_url: str,
    api_key: Optional[str],
    clean_json_fn: Callable[[str], str],
) -> Tuple[AkisDiyagrami, List[str], str]:
    """
    Kesinleşmiş netlist ve Arduino kodundan LLM ile akış diyagramı üretir.
    Doğrulama başarısız olursa hata listesiyle 1 kez retry yapar; yine başarısız olursa
    koddan deterministik olarak (build_deterministic_flow_from_code) akış üretir.
    Dönüş: (akis_diyagrami, warnings, status_label)
    """
    comp_summary = [
        {"id": c.id, "type": c.type, "label": c.label}
        for c in (netlist.components or [])
        if c.type != "wokwi-resistor"
    ]
    base_user_prompt = (
        f'KULLANICI İSTEĞİ: "{prompt}"\n'
        f"DEVREDEKİ PARÇALAR: {json.dumps(comp_summary, ensure_ascii=False)}\n"
        f"SON ARDUINO KODU:\n```cpp\n{arduino_kodu}\n```\n"
        "Bu koddaki setup() ve loop() mantığını birebir yansıtan `dugumler` ve `baglantilar` JSON nesnesini üret. Sadece JSON döndür."
    )

    last_errors: List[str] = []
    for attempt in range(2):
        uprompt = base_user_prompt
        if attempt == 1 and last_errors:
            uprompt = (
                base_user_prompt
                + "\n\nÖNCEKİ ÇIKTIDA ŞU HATALAR BULUNDU, DÜZELTEREK TEKRAR ÜRET:\n- "
                + "\n- ".join(last_errors)
            )

        raw = _call_llm_for_flow(
            system_prompt=FLOW_FROM_CODE_SYSTEM_PROMPT,
            user_prompt=uprompt,
            chosen_model=chosen_model,
            provider_used=provider_used,
            ollama_url=ollama_url,
            api_key=api_key,
        )
        if not raw or not raw.strip():
            last_errors = ["Modelden akış diyagramı yanıtı alınamadı."]
            continue

        try:
            parsed = json.loads(clean_json_fn(raw))
        except Exception as e:
            last_errors = [f"JSON parse hatası: {e}"]
            continue

        errs, warns, model_obj = validate_flow_diagram(parsed, netlist, arduino_kodu)
        if not errs and model_obj is not None:
            status = "REPAIRED" if attempt == 1 else "SUCCESS"
            return model_obj, warns, status
        last_errors = errs

    # 2 deneme de başarısızsa koddan deterministik akış üret (asla generic sabit metin yok!)
    det_flow = build_deterministic_flow_from_code(netlist, arduino_kodu)
    fallback_note = (
        "Akış diyagramı LLM yanıtı doğrulanamadığı için Arduino kodundan deterministik olarak türetildi."
    )
    return det_flow, [fallback_note], "DETERMINISTIC_FALLBACK"
