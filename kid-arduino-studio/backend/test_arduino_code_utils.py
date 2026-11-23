from arduino_code_utils import sanitize_arduino_identifiers


def test_turkish_identifiers_become_ascii():
    # Gemini'nin gerçekten ürettiği ve avr-gcc'nin derleyemediği satırlar
    assert sanitize_arduino_identifiers("const int ESİK_DEGER = 500;") == "const int ESIK_DEGER = 500;"
    assert sanitize_arduino_identifiers("if (isikDegeri < ESİK_DEGER) {") == "if (isikDegeri < ESIK_DEGER) {"
    # Tüm Türkçe harfler (büyük/küçük)
    assert sanitize_arduino_identifiers("int ışıkŞiddeti, güç, ÖÇÜĞ;") == "int isikSiddeti, guc, OCUG;"
    # #define ve şapkalı harfler
    assert sanitize_arduino_identifiers("#define EŞİK 500\nint kâr = 1;") == "#define ESIK 500\nint kar = 1;"


def test_comments_and_strings_are_untouched():
    code = (
        '// Işık değeri ölçülüyor\n'
        '/* çok satırlı\n   yorum: şeker */\n'
        'Serial.print("Işık değeri: ");\n'
        'Serial.println("\\"Güneş\\" doğdu");\n'
        "char harf = 'ş';\n"
        'int ölçüm = 0; // ölçüm sonucu\n'
    )
    expected = (
        '// Işık değeri ölçülüyor\n'
        '/* çok satırlı\n   yorum: şeker */\n'
        'Serial.print("Işık değeri: ");\n'
        'Serial.println("\\"Güneş\\" doğdu");\n'
        "char harf = 'ş';\n"
        'int olcum = 0; // ölçüm sonucu\n'
    )
    assert sanitize_arduino_identifiers(code) == expected


def test_comment_markers_inside_strings_do_not_confuse():
    code = 'Serial.println("http://ışık.com"); int ölç = 1;'
    assert sanitize_arduino_identifiers(code) == 'Serial.println("http://ışık.com"); int olc = 1;'
    code = '// "tırnak" içeren yorum\nint şimdi = 2;'
    assert sanitize_arduino_identifiers(code) == '// "tırnak" içeren yorum\nint simdi = 2;'


def test_ascii_code_is_unchanged():
    code = "#include <Servo.h>\nvoid setup() {\n  pinMode(13, OUTPUT);\n}\nvoid loop() {}\n"
    assert sanitize_arduino_identifiers(code) == code
    assert sanitize_arduino_identifiers("") == ""


if __name__ == "__main__":
    test_turkish_identifiers_become_ascii()
    test_comments_and_strings_are_untouched()
    test_comment_markers_inside_strings_do_not_confuse()
    test_ascii_code_is_unchanged()
    print("✅ Arduino kod temizleyici testleri BAŞARILI!")
