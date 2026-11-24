"""
Auth ve RBAC Servis Testi
"""

from auth_service import (
    authenticate_user,
    authenticate_student,
    create_access_token,
    decode_access_token,
    check_institution_access,
)

def test_auth():
    print("=" * 60)
    print(" 🔐 AUTH VE RBAC SERVİSİ BİRİM TESTLERİ 🔐")
    print("=" * 60)

    # 1. Admin Girişi
    admin = authenticate_user("admin", "admin123")
    assert admin is not None, "Admin girişi başarısız!"
    assert admin["role"] == "admin"
    print("✅ Test 1 Başarılı: Admin girişi doğrulandı.")

    # 2. Yanlış şifre denemesi
    fail = authenticate_user("admin", "yanlis_sifre")
    assert fail is None
    print("✅ Test 2 Başarılı: Yanlış şifre reddedildi.")

    # 3. Öğrenci PIN Girişi (KOD-01, No: 104, PIN: 1234)
    student = authenticate_student("KOD-01", "104", "1234")
    assert student is not None, "Öğrenci girişi başarısız!"
    assert student["role"] == "ogrenci"
    assert student["full_name"] == "Can Yıldız"
    print("✅ Test 3 Başarılı: Öğrenci No + PIN girişi doğrulandı.")

    # 4. Öğrenci yanlış PIN denemesi
    fail_pin = authenticate_student("KOD-01", "104", "9999")
    assert fail_pin is None
    print("✅ Test 4 Başarılı: Yanlış PIN reddedildi.")

    # 5. JWT Token Üretimi ve Çözümü
    token = create_access_token({"sub": student["id"], "role": student["role"], "name": student["full_name"]})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == student["id"]
    assert payload["role"] == "ogrenci"
    print("✅ Test 5 Başarılı: JWT Token üretildi ve başarıyla deşifre edildi.")

    # 6. Kurum İzolasyonu Denetimi
    inst_id = student["institution_id"]
    assert check_institution_access(student, inst_id) is True
    assert check_institution_access(student, "farkli_kurum_id") is False
    assert check_institution_access(admin, "herhangi_bir_kurum_id") is True
    print("✅ Test 6 Başarılı: Kurum izolasyonu (Multi-Tenancy) doğrulandı.")

    print("\n⭐ TÜM AUTH & GÜVENLİK TESTLERİ BAŞARIYLA GEÇTİ! ⭐\n")

if __name__ == "__main__":
    test_auth()
