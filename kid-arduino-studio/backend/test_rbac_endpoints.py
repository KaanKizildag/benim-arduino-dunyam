"""
RBAC ve Kurumsal API Doğrudan Fonksiyonel Testleri
"""

import os
os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

from rbac_api import (
    login_endpoint,
    student_login_endpoint,
    get_mudur_overview,
    get_teacher_classes,
    update_class_inventory,
    get_parent_children,
    update_parent_kvkk_consent,
    UserLoginRequest,
    StudentLoginRequest,
    UpdateInventoryRequest,
    KvkkConsentUpdateRequest,
)
from auth_service import decode_access_token

def test_rbac_functions():
    print("=" * 60)
    print(" 🏫 RBAC VE KURUMSAL API FONKSİYONEL TESTLERİ 🏫")
    print("=" * 60)

    # 1. Öğrenci PIN Girişi
    std_res = student_login_endpoint(StudentLoginRequest(
        institution_code="KOD-01",
        student_no="104",
        pin="1234"
    ))
    assert "access_token" in std_res
    std_user = std_res["user"]
    assert std_user["full_name"] == "Can Yıldız"
    assert std_user["role"] == "ogrenci"
    print(f"✅ Test 1 Başarılı: Öğrenci PIN girişi yapıldı ({std_user['full_name']})")

    # 2. Öğretmen Girişi
    tch_res = login_endpoint(UserLoginRequest(
        username="ogretmen1",
        password="ogretmen123"
    ))
    assert "access_token" in tch_res
    tch_user = tch_res["user"]
    assert tch_user["role"] == "ogretmen"
    print("✅ Test 2 Başarılı: Öğretmen girişi doğrulandı.")

    # 3. Öğretmenin Sınıf Envanterini Listelemesi & Güncellemesi
    classes = get_teacher_classes(tch_user)
    assert len(classes) > 0
    class_id = classes[0]["id"]

    new_inv = ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "BUZZER", "LDR_SENSOR"]
    upd_res = update_class_inventory(class_id, UpdateInventoryRequest(inventory=new_inv), tch_user)
    assert upd_res["success"] is True
    assert upd_res["inventory"] == new_inv
    print("✅ Test 3 Başarılı: Öğretmen sınıf envanterini güncelledi.")

    # 4. Müdür Girişi & İstatistikler
    mdr_res = login_endpoint(UserLoginRequest(
        username="mudur1",
        password="mudur123"
    ))
    mdr_user = mdr_res["user"]
    overview = get_mudur_overview(mdr_user)
    assert overview["students"] >= 1
    assert overview["classes"] >= 1
    print(f"✅ Test 4 Başarılı: Müdür paneli özet verileri okundu (Öğrenci: {overview['students']}, Sınıf: {overview['classes']})")

    # 5. Veli Girişi, Çocuk Listesi & KVKK Onayı
    prt_res = login_endpoint(UserLoginRequest(
        username="veli1",
        password="veli123"
    ))
    prt_user = prt_res["user"]
    children = get_parent_children(prt_user)
    assert len(children) >= 1
    assert children[0]["student_name"] == "Can Yıldız"
    print(f"✅ Test 5 Başarılı: Veli kendi çocuğuyla eşleşmeyi doğruladı ({children[0]['student_name']})")

    kvkk_res = update_parent_kvkk_consent(KvkkConsentUpdateRequest(
        student_id=children[0]["student_id"],
        allow_media_share=True
    ), prt_user)
    assert kvkk_res["success"] is True
    assert kvkk_res["media_share_allowed"] is True
    print("✅ Test 6 Başarılı: Veli KVKK açık rıza onayını güncelledi.")

    print("\n⭐ TÜM RBAC FONKSİYONEL API TESTLERİ BAŞARIYLA GEÇTİ! ⭐\n")

if __name__ == "__main__":
    test_rbac_functions()
