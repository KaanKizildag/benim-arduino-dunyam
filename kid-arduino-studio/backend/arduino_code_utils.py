"""
Arduino C++ kodu için yardımcılar.

Arduino Uno derleyicisi (avr-gcc 7.3) değişken, sabit ve fonksiyon adlarında Türkçe harf
kabul etmez. Örneğin yapay zekanın ürettiği `const int ESİK_DEGER = 500;` satırı şu hatayı verir:
    error: 'ES' was not declared in this scope

`sanitize_arduino_identifiers` bu harfleri SADECE kod kısmında ASCII karşılıklarına çevirir
(İ->I, ş->s, ğ->g, ü->u, ö->o, ç->c, ı->i). Yorumlara ve tırnak içindeki metinlere
(örn. Serial.print("Işık değeri")) dokunmaz; onlar derlemeyi bozmaz ve çocuğa Türkçe görünmeye devam eder.
"""

import unicodedata

_TURKISH_TO_ASCII = str.maketrans({
    "ç": "c", "Ç": "C",
    "ğ": "g", "Ğ": "G",
    "ı": "i", "İ": "I",
    "ö": "o", "Ö": "O",
    "ş": "s", "Ş": "S",
    "ü": "u", "Ü": "U",
})


def _to_ascii_letter(ch: str) -> str:
    """Tek bir ASCII dışı karakteri mümkünse ASCII harfe çevirir, çeviremezse olduğu gibi bırakır."""
    mapped = ch.translate(_TURKISH_TO_ASCII)
    if mapped != ch:
        return mapped
    # â, î, û gibi şapkalı harfler: aksan işaretini at
    stripped = "".join(
        c for c in unicodedata.normalize("NFKD", ch) if not unicodedata.combining(c)
    )
    if stripped and stripped.isascii():
        return stripped
    return ch


def sanitize_arduino_identifiers(code: str) -> str:
    """Koddaki Türkçe harfleri yorumlar ve tırnak içindeki metinler dışında ASCII'ye çevirir."""
    if not code or code.isascii():
        return code

    out = []
    i = 0
    n = len(code)
    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""

        # Tek satırlık yorum: // ... satır sonuna kadar
        if ch == "/" and nxt == "/":
            end = code.find("\n", i)
            end = n if end == -1 else end
            out.append(code[i:end])
            i = end
            continue

        # Çok satırlı yorum: /* ... */
        if ch == "/" and nxt == "*":
            end = code.find("*/", i + 2)
            end = n if end == -1 else end + 2
            out.append(code[i:end])
            i = end
            continue

        # Metin ("...") veya karakter ('...') sabiti; kaçış karakterlerini (\" \\) atla
        if ch in ('"', "'"):
            j = i + 1
            while j < n and code[j] != ch and code[j] != "\n":
                j += 2 if code[j] == "\\" else 1
            j = min(j + 1, n)
            out.append(code[i:j])
            i = j
            continue

        out.append(_to_ascii_letter(ch) if not ch.isascii() else ch)
        i += 1

    return "".join(out)
