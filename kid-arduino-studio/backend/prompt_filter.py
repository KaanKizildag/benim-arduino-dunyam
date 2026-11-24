"""
Kid Arduino Studio - Akıllı Prompt Filtreleme ve Güvenlik Modülü (Prompt Moderation & Classification)

Bu modül:
1. Zararlı, tehlikeli, patlayıcı ve şiddet içeren promptları (Örn: "Bomba yapmak istiyorum")
   anında tespit edip GÜVENLİK ENGELİ ile durdurur.
2. Proje niteliği taşımayan günlük sohbet, hava durumu veya sağlık sorularını
   (Örn: "bugün hava nasıl?", "Başım ağrıyor ne yapmam lazım?") tespit edip
   elektronik/Arduino proje fikri olmadığını nazikçe bildirir ve çocuk dostu öneriler sunar.
3. Token israfını ve gereksiz LLM çağrılarını sıfıra indirir.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PromptFilterResult:
    is_valid: bool
    filter_type: str  # "PASS", "SAFETY_VIOLATION", "OFF_TOPIC"
    reason: str
    user_message: str
    suggested_prompts: List[str] = field(default_factory=list)


# Çocukların ilham alabileceği güvenli, popüler Arduino proje fikirleri
DEFAULT_PROJECT_SUGGESTIONS = [
    "Odam için gece lambası (LDR ışık sensörü ve LED ile)",
    "Mesafe ölçen ultrasonik park sensörü (HC-SR04 ve Buzzer)",
    "Hırsız algılayan hareket alarmlı devre (PIR sensörü ve lamba)",
    "Sıcaklık ve nem gösteren mini hava istasyonu (DHT11 ve LCD)",
    "Butona basınca bip sesi çıkaran mini kapı zili"
]


def _normalize_text(text: str) -> str:
    """Türkçe karakterleri ve boşlukları normalize eden yardımcı fonksiyon."""
    if not text:
        return ""
    # Küçük harfe çevir (Türkçe İ / ı harfleri uyumlu)
    lowered = text.replace("İ", "i").replace("I", "ı").lower()
    # Fazla boşlukları temizle
    cleaned = re.sub(r"\s+", " ", lowered).strip()
    return cleaned


# =========================================================================
# 1. GÜVENLİK VE ZARARLI İÇERİK KALIPLARI (SAFETY FILTER)
# =========================================================================
SAFETY_PATTERNS = [
    # Bomba ve Patlayıcılar
    (
        r"\b(bomba|patlay[ıi]c[ıi]|dinamit|c-?4|molotof|f[uü]nye|barut|patlatmak|patlataca[gğ][ıi]m|patlat[ıi]c[ıi])\b",
        "Patlayıcı veya bomba yapımı içeren ifadeler tespit edildi."
    ),
    (
        r"\b(bomba\s+yap|patlay[ıi]c[ıi]\s+devresi|bomba\s+zamanlay[ıi]c[ıi]s[ıi]|patlatma\s+d[uü]zene[gğ]i)\b",
        "Bomba veya patlayıcı mekanizması oluşturma isteği."
    ),
    # Silah ve Fiziksel Saldırı
    (
        r"\b(ate[sş]li\s+silah|tabanca\s+yap|t[uü]fek\s+yap|mermi\s+atar|kur[sş]un\s+atar)\b",
        "Ateşli silah veya mermi atıcı mekanizma yapımı içeren ifadeler."
    ),
    # Canlılara Zarar Verme / Şok Cihazı ile İşkence
    (
        r"\b(insanlara?\s+zarar|canl[ıi]lara?\s+zarar|birini\s+[oö]ld[uü]r|[oö]ld[uü]rmek\s+i[cç]in|can[ıi]n[ıi]\s+yak)\b",
        "İnsanlara veya canlılara fiziksel zarar verme amacı içeren ifadeler."
    ),
    (
        r"\b(elektro[sş]ok\s+silah[ıi]|[sş]ok\s+tabancas[ıi]|insan[ıi]\s+[cç]arpan\s+devre|can\s+yakan\s+[sş]ok)\b",
        "Canlılara elektroşok verme veya saldırı amaçlı yüksek voltaj şok cihazı isteği."
    ),
    # Zehir ve Tehlikeli Kimyasallar
    (
        r"\b(zehir|zehirleme|zehirli|asit\s+sald[ıi]r[ıi]s[ıi]|kimyasal\s+silah|biyolojik\s+silah)\b",
        "Zehirli, kimyasal veya biyolojik zararlı madde içeren ifadeler."
    ),
    # İntihar veya Kendine Zarar Verme
    (
        r"\b(intihar|kendimi\s+[oö]ld[uü]r|kendine\s+zarar\s+ver)\b",
        "Kendine zarar verme veya intihar amaçlı ifadeler."
    ),
    # Siber Saldırı ve Kötü Amaçlı Sızma
    (
        r"\b(wifi\s+hackle|siber\s+sald[ıi]r[ıi]|kart\s+kopyalay[ıi]c[ıi]|hacker\s+cihaz[ıi]|[sş]ifre\s+[cç]al)\b",
        "Kötü niyetli siber saldırı veya veri hırsızlığı cihazı isteği."
    )
]


# =========================================================================
# 2. PROJE DIŞI / GÜNLÜK SOHBET / SAĞLIK / HAVA DURUMU KALIPLARI (OFF-TOPIC)
# =========================================================================

# Sağlık / Tıbbi tavsiye kalıpları (Örn: "Başım ağrıyor ne yapmam lazım?")
MEDICAL_PATTERNS = [
    r"\b(ba[sş][ıi]m|karn[ıi]m|di[sş]im|bo[gğ]az[ıi]m|kolum|baca[gğ][ıi]m|midem|belim|g[oö]z[uü]m)\s+(a[gğ]r[ıi]yor|s[ıi]zl[ıi]yor|bulan[ıi]yor|k[oö]t[uü]|[sş]i[sş]ti)\b",
    r"\b(ne\s+yapmam\s+laz[ıi]m|ne\s+yapmal[ıi]y[ıi]m|hangi\s+ilac[ıi]|doktora\s+gitmeli\s+miyim|hastay[ıi]m|ate[sş]im\s+var|grip\s+oldum|hastal[ıi]k|tedavi)\b",
    r"\b(ila[cç]\s+[oö]ner|ba[sş]\s+a[gğ]r[ıi]s[ıi]na\s+ne\s+iyi\s+gelir|karn[ıi]m\s+a[gğ]r[ıi]yor)\b"
]

# Günlük hava durumu sorusu kalıpları (Örn: "bugün hava nasıl?")
# Dikkat: "hava durumu istasyonu", "sıcaklık ölçer devresi" gibi elektronik projeleri hariç tutulur!
WEATHER_QUESTION_PATTERNS = [
    r"^\s*(bug[uü]n\s+|yar[ıi]n\s+)?hava(\s+durumu)?\s+(nas[ıi]l|nedir|ka[cç]\s+derece|g[uü]zel\s+mi|so[gğ]uk\s+mu|s[ıi]cak\s+m[ıi]|ya[gğ]murlu\s+mu)(\s*\?)?\s*$",
    r"^\s*(bug[uü]n\s+|yar[ıi]n\s+)?(ya[gğ]mur|kar|f[ıi]rt[ıi]na)\s+(ya[gğ]acak\s+m[ıi]|var\s+m[ıi]|olacak\s+m[ıi])(\s*\?)?\s*$",
    r"^\s*hava\s+nas[ıi]l(\s*\?)?\s*$"
]

# Günlük sohbet, selamlama ve hal-hatır kalıpları
GREETING_AND_CHITCHAT_PATTERNS = [
    r"\b(merhaba|selam(lar)?|naber|nasılsın|nassın|iyi\s+misin|günaydın|tünaydın|iyi\s+geceler|hey|alo|hi|hello)\b",
    r"\b(sen\s+kimsin|ad[ıi]n\s+ne|ka[cç]\s+ya[sş][ıi]ndas[ıi]n|nerelisin|yapay\s+zeka\s+m[ıi]s[ıi]n)\b",
    r"\b(f[ıi]kra\s+anlat|[sş]iir\s+yaz|[sş]ark[ıi]\s+s[oö]yle|beni\s+seviyor\s+musun|komik\s+bir\s+[sş]ey\s+s[oö]yle|masal\s+anlat)\b",
    r"\b(matematik\s+[oö]devimi\s+yap|t[uü]rkiye('?nin)?\s+ba[sş]kenti|en\s+b[uü]y[uü]k\s+gezegen|d[uü]nya\s+d[oö]n[uü]yor\s+mu)\b",
    r"\b(yemek\s+tarifi\s+ver|kek\s+nas[ıi]l\s+yap[ıi]l[ıi]r|ak[sş]am\s+ne\s+yesem)\b"
]


# =========================================================================
# 3. ELEKTRONİK VE ARDUINO PROJE ANLAMSAL ANAHTAR KELİMELERİ (HARDWARE CONTEXT)
# =========================================================================
# Bu kelimelerden biri geçiyorsa, hava/nem/ilaç kelimesi geçse bile bu bir PROJEDİR!
# Örnek: "hava durumu istasyonu", "akıllı ilaç kutusu hatırlatıcı", "sıcaklık sensörü"
HARDWARE_CONTEXT_KEYWORDS = {
    # Donanım / Komponentler
    "arduino", "uno", "nano", "mega", "breadboard", "devre", "pin", "pini", "pinleri",
    "led", "ledi", "lambas[ıi]", "lamba", "buzzer", "hoparl[oö]r", "potansiyometre",
    "buton", "d[uü][gğ]me", "diren[cç]", "sens[oö]r", "sens[oö]r[uü]", "motor", "servo",
    "ekran", "lcd", "oled", "r[oö]le", "l293d", "l298n", "hc-?sr04", "ultrasonik",
    "pir", "ldr", "dht", "dht11", "dht22", "joystick", "bluetooth", "hc-?05", "hc-?06",
    "transist[oö]r", "entegre", "kablo", "jumper", "pot",
    # Proje & Sistem Kalıpları
    "proje", "projesi", "sistem", "sistemi", "d[uü]zenek", "d[uü]zene[gğ]i",
    "robot", "araba", "radar", "alarm", "alarm[ıi]", "otomasyon", "istasyon", "istasyonu",
    "sayac", "saya[cç]", "kronometre", "termometre", "voltmetre", "takip", "cetvel",
    # Elektronik Eylem Fiilleri
    "devresi", "devresini", "kodunu", "kodu", "ba[gğ]lant[ıi]s[ıi]", "ba[gğ]lant[ıi]lar[ıi]",
    "yak", "s[oö]nd[uü]r", "yans[ıi]n", "s[oö]ns[uü]n", "d[oö]ns[uü]n", "[oö]ts[uü]n", "[cç]als[ıi]n",
    "[oö]l[cç]", "[oö]l[cç]en", "[oö]l[cç]s[uü]n", "alg[ıi]la", "alg[ıi]las[ıi]n", "alg[ıi]layan",
    "hareketli", "engelden", "[cç]izgi", "ak[ıi]ll[ıi]", "otomatik"
}


def validate_project_prompt(prompt: str) -> PromptFilterResult:
    """
    Kullanıcının girdiği proje promptunu güvenlik ve konu uygunluğu açısından denetler.

    Döndürdüğü PromptFilterResult:
    - is_valid: True ise işlem devam eder, False ise işlem kesinlikle durdurulur.
    - filter_type: "PASS", "SAFETY_VIOLATION", "OFF_TOPIC"
    - user_message: Ekranda çocuğa/kullanıcıya gösterilecek tatlı ve açıklayıcı mesaj.
    """
    if not prompt or not prompt.strip():
        return PromptFilterResult(
            is_valid=False,
            filter_type="OFF_TOPIC",
            reason="Boş veya anlamsız istek.",
            user_message="💡 Lütfen yapmak istediğin Arduino devresi veya proje fikrini birkaç kelimeyle yaz! Örneğin: 'Gece lambası devresi' veya 'Mesafe ölçen radar'.",
            suggested_prompts=DEFAULT_PROJECT_SUGGESTIONS
        )

    clean_text = _normalize_text(prompt)

    # ---------------------------------------------------------------------
    # ADIM 1: GÜVENLİK VE ZARARLI İÇERİK KONTROLÜ (SAFETY FILTER - ÖNCELİK 1)
    # ---------------------------------------------------------------------
    for pattern, desc in SAFETY_PATTERNS:
        if re.search(pattern, clean_text):
            return PromptFilterResult(
                is_valid=False,
                filter_type="SAFETY_VIOLATION",
                reason=desc,
                user_message=(
                    "🛡️ Güvenlik Filtresi Uyarısı:\n\n"
                    "Kid Arduino Studio'da güvenli, eğitici ve bilimsel maker projeleri tasarlıyoruz. "
                    "Patlayıcı, bomba, silah veya canlılara zarar verebilecek tehlikeli devre istekleri "
                    "güvenlik kuralları gereği kesinlikle oluşturulamaz.\n\n"
                    "Lütfen lamba, park sensörü, mini robot veya akıllı ev gibi güvenli bir proje fikri deneyin!"
                ),
                suggested_prompts=DEFAULT_PROJECT_SUGGESTIONS
            )

    # ---------------------------------------------------------------------
    # ADIM 2: DONANIM BAĞLAMI TESPİTİ (HARDWARE CONTEXT CHECK)
    # ---------------------------------------------------------------------
    # Eğer metinde açıkça bir donanım, sensör, devre veya Arduino terimi varsa
    # bu bir elektronik projesidir. (Örn: "hava durumu istasyonu", "ilaç kutusu alarmı")
    has_hardware_context = False
    for kw in HARDWARE_CONTEXT_KEYWORDS:
        if re.search(r"\b" + kw + r"\b", clean_text):
            has_hardware_context = True
            break

    # ---------------------------------------------------------------------
    # ADIM 3: TIBBİ / SAĞLIK DANIŞMA SORULARI ("Başım ağrıyor ne yapmam lazım?")
    # ---------------------------------------------------------------------
    # Donanım içermeyen sağlık/ilaç soruları kesinlikle proje değildir!
    if not has_hardware_context:
        for med_pat in MEDICAL_PATTERNS:
            if re.search(med_pat, clean_text):
                return PromptFilterResult(
                    is_valid=False,
                    filter_type="OFF_TOPIC",
                    reason="Tıbbi tavsiye / sağlık sorusu tespit edildi.",
                    user_message=(
                        "💡 Sağlık Sorusu Tespit Edildi:\n\n"
                        "Geçmiş olsun! Ancak ben bir tıbbi danışman değil, Arduino ve Elektronik Tasarım Asistanıyım. "
                        "Sağlığınla ilgili konularda lütfen bir büyüğüne, doktora veya sağlık kuruluşuna danış.\n\n"
                        "Eğer elektronikle ilgili bir proje yapmak istersen (örneğin 'Akıllı İlaç Hatırlatıcı Kutu' gibi), "
                        "bana seve seve yardımcı olabilirim!"
                    ),
                    suggested_prompts=[
                        "Saat başı öten akıllı ilaç hatırlatıcı kutu alarmı",
                        "Oda sıcaklığını ölçen mini termometre devresi",
                        "El değmeden açılan otomatik çöp kutusu (Servo motor ile)"
                    ]
                )

    # ---------------------------------------------------------------------
    # ADIM 4: GÜNLÜK HAVA DURUMU SORULARI ("bugün hava nasıl?")
    # ---------------------------------------------------------------------
    # Donanım içermeyen hava durumu soruları (hava istasyonu projesi değilse)
    if not has_hardware_context:
        for w_pat in WEATHER_QUESTION_PATTERNS:
            if re.search(w_pat, clean_text):
                return PromptFilterResult(
                    is_valid=False,
                    filter_type="OFF_TOPIC",
                    reason="Genel hava durumu sorusu tespit edildi.",
                    user_message=(
                        "🌤️ Proje Fikri Gerekli:\n\n"
                        "Ben canlı hava durumu tahmini yapamıyorum çünkü ben bir Arduino ve Elektronik Mucit Asistanıyım! "
                        "Fakat istersen kendi odanın hava durumunu, sıcaklığını ve nemini ölçen harika bir "
                        "**'Hava Durumu İstasyonu'** devresi tasarlayabiliriz!\n\n"
                        "Bunu denemek ister misin?"
                    ),
                    suggested_prompts=[
                        "LCD ekranda sıcaklık ve nem gösteren hava istasyonu devresi",
                        "Yağmur yağınca buzzer ile ses çıkaran yağmur alarmı",
                        "Hava çok sıcak olunca otomatik çalışan mini serinletici fan"
                    ]
                )

    # ---------------------------------------------------------------------
    # ADIM 5: GÜNLÜK SOHBET, SELAMLAŞMA VEYA ALAKASIZ SORULAR ("naber", "sen kimsin", "fıkra anlat")
    # ---------------------------------------------------------------------
    if not has_hardware_context:
        for ch_pat in GREETING_AND_CHITCHAT_PATTERNS:
            if re.search(ch_pat, clean_text):
                return PromptFilterResult(
                    is_valid=False,
                    filter_type="OFF_TOPIC",
                    reason="Genel sohbet veya proje dışı soru.",
                    user_message=(
                        "🤖 Merhaba Genç Mucit!\n\n"
                        "Ben Kid Arduino Studio'nun Yapay Zeka Tasarım Asistanıyım. "
                        "Benimle sohbet etmek yerine, bana yapmak istediğin bir elektronik devre fikrini yazarsan "
                        "senin için Arduino kodunu ve kablo bağlantılarını anında çizebilirim!\n\n"
                        "Örneğin aşağıdaki popüler projelerden birini deneyebilirsin:"
                    ),
                    suggested_prompts=DEFAULT_PROJECT_SUGGESTIONS
                )

    # ---------------------------------------------------------------------
    # ADIM 6: DONANIMSIZ VE EYLEMSİZ ÇOK KISA / ANLAMSIZ SORU KALIPLARI
    # ---------------------------------------------------------------------
    # Eğer metinde hiçbir donanım/proje eylemi yoksa VE bir soru eki (mı, mi, mu, nasıl, nedir, ne vb.) içeriyorsa:
    if not has_hardware_context:
        # Soru kalıbı analizi
        is_generic_question = bool(re.search(r"(\?|nas[ıi]l|nedir|ne\s+zaman|nerede|kimdir|ka[cç]|m[ıi]s[ıi]n|m[ıi]y[ıi]m|m[ıi]\b|mi\b|mu\b|m[uü]\b)", clean_text))
        words = clean_text.split()
        
        # Eğer soru soruluyorsa ve tek bir elektronik kelime bile geçmiyorsa proje dışıdır
        if is_generic_question and len(words) <= 12:
            return PromptFilterResult(
                is_valid=False,
                filter_type="OFF_TOPIC",
                reason="Donanım veya devre içermeyen genel soru.",
                user_message=(
                    "💡 Bir Arduino Proje Fikri Yazmalısın!\n\n"
                    "Girdiğin soru bir elektronik veya devre tasarım isteği içermiyor. "
                    "Burası robotlar, ışıklar, sensörler ve alarmlar tasarladığımız bir laboratuvardır!\n\n"
                    "Bana örneğin: 'Karanlıkta yanan lamba yap' veya 'Park sensörü devresi kur' gibi bir fikir verebilirsin."
                ),
                suggested_prompts=DEFAULT_PROJECT_SUGGESTIONS
            )

        # 1-2 kelimelik çok kısa ve anlamsız girdiler (Örn: "elma", "merhaba", "asdfg")
        if len(words) <= 2 and len(clean_text) < 15:
            return PromptFilterResult(
                is_valid=False,
                filter_type="OFF_TOPIC",
                reason="Çok kısa veya donanımsız istek.",
                user_message=(
                    "💡 Proje fikrini biraz daha detaylandırabilir misin?\n\n"
                    "Örneğin: 'Butona basınca kırmızı ışık yansın' veya 'Mesafe yaklaşınca ses çıkaran devre' "
                    "gibi ne yapmak istediğini yazarsan devreni hemen tasarlayabilirim!"
                ),
                suggested_prompts=DEFAULT_PROJECT_SUGGESTIONS
            )

    # Başarıyla onaylandı!
    return PromptFilterResult(
        is_valid=True,
        filter_type="PASS",
        reason="Geçerli Arduino proje isteği.",
        user_message=""
    )
