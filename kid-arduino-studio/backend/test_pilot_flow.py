import sys
import os
import json
import io

sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, get_db_connection
from auth_service import (
    authenticate_user,
    authenticate_student,
    create_access_token,
    decode_access_token
)
from rbac_api import (
    login_endpoint,
    student_login_endpoint,
    get_mudur_overview,
    get_teachers_endpoint,
    create_teacher_endpoint,
    get_classes_endpoint,
    create_class_endpoint,
    get_students_endpoint,
    create_student_endpoint,
    reset_student_pin_endpoint,
    create_parent_student_pair,
    get_teacher_classes,
    update_class_inventory,
    get_teacher_student_projects,
    approve_project_endpoint,
    add_project_feedback,
    upload_project_media,
    get_parent_children,
    update_parent_kvkk_consent,
    get_parent_projects_portfolio,
    stream_project_media,
    UserLoginRequest,
    StudentLoginRequest,
    CreateTeacherRequest,
    CreateClassRequest,
    CreateStudentRequest,
    ResetStudentPinRequest,
    CreateParentPairRequest,
    UpdateInventoryRequest,
    TeacherFeedbackRequest,
    KvkkConsentUpdateRequest
)
from fastapi import UploadFile

def run_pilot_flow_test():
    print("=" * 60)
    print("🚀 ÇOCUK ARDUİNO STÜDYOSU - PİLOT TEST AKIŞI TESTİ 🚀")
    print("=" * 60)

    init_db()

    # Önceki test kalıntılarını temizle (tekrarlanabilir test için)
    db_clean = get_db_connection()
    db_clean.execute("DELETE FROM users WHERE username IN ('fatma_ogrt', 'veli_efe') OR student_no = '205';")
    db_clean.execute("DELETE FROM projects WHERE id = 'pilot_proj_efe_001';")
    db_clean.commit()
    db_clean.close()

    # -----------------------------------------------------------------
    # ADIM 1: KURULUM (Okul Müdürü Yönetimi)
    # -----------------------------------------------------------------
    print("\n[Adım 1] Okul Müdürü Girişi & Kurum İçi Atamalar...")
    mudur_auth = authenticate_user("mudur1", "mudur123")
    assert mudur_auth is not None, "Müdür girişi başarısız!"
    print(f"  ✓ Müdür Girişi Başarılı: {mudur_auth['full_name']} ({mudur_auth['institution_name']})")

    # Müdür özet paneli
    overview = get_mudur_overview(mudur_auth)
    assert "teachers" in overview and "students" in overview
    print(f"  ✓ Kurum İstatistikleri: {overview['teachers']} Öğretmen, {overview['students']} Öğrenci, {overview['classes']} Sınıf")

    # Müdür yeni bir pilot öğretmen ekler
    new_t = create_teacher_endpoint(
        CreateTeacherRequest(
            username="fatma_ogrt",
            full_name="Fatma Hoca",
            password="fatma_pwd_123"
        ),
        user=mudur_auth
    )
    pilot_teacher_id = new_t["teacher_id"]
    print(f"  ✓ Yeni Öğretmen Eklendi: Fatma Hoca (@{new_t['username']})")

    # Müdür yeni bir sınıf oluşturur ve öğretmeni atar
    new_c = create_class_endpoint(
        CreateClassRequest(
            name="4-B Robotik",
            teacher_id=pilot_teacher_id
        ),
        user=mudur_auth
    )
    pilot_class_id = new_c["class_id"]
    print(f"  ✓ Yeni Sınıf Oluşturuldu: {new_c['name']} (ID: {pilot_class_id})")

    # Müdür yeni bir öğrenci ekler (No: 205, PIN: 5678)
    new_s = create_student_endpoint(
        CreateStudentRequest(
            full_name="Efe Demir",
            student_no="205",
            pin="5678",
            class_id=pilot_class_id
        ),
        user=mudur_auth
    )
    pilot_student_id = new_s["student_id"]
    print(f"  ✓ Yeni Öğrenci Eklendi: {new_s['full_name']} (No: {new_s['student_no']}, PIN: 5678)")

    # Müdür veli hesabı açar ve öğrenciyle eşleştirir
    new_p = create_parent_student_pair(
        CreateParentPairRequest(
            parent_username="veli_efe",
            parent_full_name="Ayşe Demir",
            parent_password="veli_pwd_123",
            student_id=pilot_student_id
        ),
        user=mudur_auth
    )
    assert new_p["success"] is True
    print(f"  ✓ Veli Hesabı Açıldı & Öğrenciyle Eşleştirildi (Veli ID: {new_p['parent_id']})")

    # -----------------------------------------------------------------
    # ADIM 2: ENVANTER HAZIRLIĞI (Öğretmen Sınıf Kiti)
    # -----------------------------------------------------------------
    print("\n[Adım 2] Öğretmen Sınıf Arduino Kiti Envanterini İşaretliyor...")
    teacher_auth = authenticate_user("fatma_ogrt", "fatma_pwd_123")
    assert teacher_auth is not None, "Öğretmen girişi başarısız!"
    
    t_classes = get_teacher_classes(user=teacher_auth)
    assert len(t_classes) > 0, "Öğretmene atanmış sınıf bulunamadı!"
    print(f"  ✓ Öğretmenin Atandığı Sınıf: {t_classes[0]['name']}")

    # Öğretmen sınıf envanterini belirler
    kit_components = [
        "ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220",
        "PUSH_BUTTON", "BUZZER", "ULTRASONIC_HC_SR04"
    ]
    inv_res = update_class_inventory(
        class_id=pilot_class_id,
        req=UpdateInventoryRequest(inventory=kit_components),
        user=teacher_auth
    )
    assert inv_res["success"] is True
    print(f"  ✓ Sınıf Envanteri Kaydedildi: {len(kit_components)} parça işaretlendi.")

    # -----------------------------------------------------------------
    # ADIM 3: PROJE ÜRETİMİ (Öğrenci PIN ile Giriş & Proje Kaydı)
    # -----------------------------------------------------------------
    print("\n[Adım 3] Öğrenci PIN ile Giriş Yapıyor & Projesini Kaydediyor...")
    std_login = student_login_endpoint(
        StudentLoginRequest(
            institution_code="KOD-01",
            student_no="205",
            pin="5678"
        )
    )
    student_auth = std_login["user"]
    print(f"  ✓ Öğrenci PIN Girişi Başarılı: {student_auth['full_name']} (No: {student_auth['student_no']})")

    # Öğrenci projesini tamamlar ve SQLite veritabanına kaydeder
    db = get_db_connection()
    project_id = "pilot_proj_efe_001"
    netlist_data = {
        "board": "arduino-uno",
        "components": [
            {"id": "uno1", "type": "ARDUINO_UNO"},
            {"id": "led1", "type": "LED_RED"},
            {"id": "r1", "type": "RESISTOR_220"}
        ],
        "connections": [
            {"from": "uno1:D13", "to": "r1:1", "color": "red"},
            {"from": "r1:2", "to": "led1:anode", "color": "red"},
            {"from": "led1:cathode", "to": "uno1:GND", "color": "black"}
        ]
    }
    db.execute(
        """
        INSERT OR REPLACE INTO projects (id, institution_id, student_id, proje_adi, prompt, netlist_json, arduino_kodu, status, is_shared_with_parent)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'beklemede', 1)
        """,
        (
            project_id,
            student_auth["institution_id"],
            student_auth["id"],
            "Akıllı Gece Lambası",
            "Butona basınca yanan güvenli devre",
            json.dumps(netlist_data),
            "void setup() { pinMode(13, OUTPUT); } void loop() { digitalWrite(13, HIGH); }"
        )
    )
    db.commit()
    db.close()
    print("  ✓ Öğrenci Projesi DB'ye Kaydedildi (ID: pilot_proj_efe_001)")

    # -----------------------------------------------------------------
    # ADIM 4: FİZİKSEL KONTROL & ANIN KAYDI (Öğretmen Onayı, Rozet, Medya)
    # -----------------------------------------------------------------
    print("\n[Adım 4] Öğretmen Fiziksel Kontrolü Yapıyor, Rozet Takıyor & Video Yüklüyor...")
    t_projects = get_teacher_student_projects(user=teacher_auth)
    matching_projects = [p for p in t_projects if p["id"] == project_id]
    assert len(matching_projects) > 0, "Öğrenci projesi öğretmene görünmedi!"
    print(f"  ✓ Öğretmen Öğrencinin Projesini Gördü: '{matching_projects[0]['proje_adi']}' (Öğrenci: {matching_projects[0]['student_name']})")

    # Öğretmen devreyi masada kontrol eder ve onaylar
    app_res = approve_project_endpoint(project_id=project_id, user=teacher_auth)
    assert app_res["success"] is True
    print("  ✓ Devre Fiziksel Kontrolü Öğretmen Tarafından Onaylandı: status='ogretmen_onayladi' ✅")

    # Öğretmen rozet verir
    fb_res = add_project_feedback(
        project_id=project_id,
        req=TeacherFeedbackRequest(
            badge="🚀 Usta Mucit",
            comment="Tebrikler Efe! İlk seferde devre harika çalıştı.",
            stars=5
        ),
        user=teacher_auth
    )
    assert fb_res["success"] is True
    print("  ✓ Öğretmen Başarı Rozeti Verdi: 🚀 Usta Mucit (5 Yıldız ⭐)")

    # Öğretmen çalışan devre videosu yükler (simüle dosya)
    dummy_video_bytes = b"MP4_SAMPLE_VIDEO_STREAM_DATA"
    upload_file = UploadFile(
        filename="calisan_lamba.mp4",
        file=io.BytesIO(dummy_video_bytes)
    )
    media_res = upload_project_media(
        project_id=project_id,
        file=upload_file,
        caption="Efe devresini başarıyla çalıştırdı!",
        user=teacher_auth
    )
    assert media_res["success"] is True
    media_id = media_res["media_id"]
    print(f"  ✓ Çalışan Devre Videosu Kapalı Devre Olarak Yüklendi (Media ID: {media_id})")

    # -----------------------------------------------------------------
    # ADIM 5: VELİ BİLGİLENDİRMESİ & PORTFOLYO (Kapalı Devre Görünüm)
    # -----------------------------------------------------------------
    print("\n[Adım 5] Veli Portfolyoyu İnceliyor & KVKK Açık Rıza Veriyor...")
    parent_auth = authenticate_user("veli_efe", "veli_pwd_123")
    assert parent_auth is not None, "Veli girişi başarısız!"
    print(f"  ✓ Veli Girişi Başarılı: {parent_auth['full_name']}")

    # Veli bağlı çocuğunu görür
    children = get_parent_children(user=parent_auth)
    assert len(children) > 0, "Veliye bağlı çocuk bulunamadı!"
    child = children[0]
    print(f"  ✓ Veli Çocuğunu Gördü: {child['student_name']} (Sınıf: {child['class_name']})")

    # Veli KVKK açık rızasını günceller
    consent_res = update_parent_kvkk_consent(
        req=KvkkConsentUpdateRequest(
            student_id=pilot_student_id,
            allow_media_share=True
        ),
        user=parent_auth
    )
    assert consent_res["success"] is True
    print("  ✓ Veli KVKK Açık Rıza Onayı Doğrulandı: media_share_allowed = True")

    # Veli çocuğun projeler portfolyosunu görüntüler
    portfolio_projects = get_parent_projects_portfolio(user=parent_auth)
    assert len(portfolio_projects) > 0
    proj_view = portfolio_projects[0]

    assert proj_view["id"] == project_id
    assert proj_view["status"] == "ogretmen_onayladi"
    assert proj_view["teacher_badge"] == "🚀 Usta Mucit"
    assert len(proj_view["media_list"]) > 0

    print("  ✓ Veli Çocuğunun Projesini, Onayını ve Çalışan Videosunu Gördü:")
    print(f"     - Proje Başlığı: {proj_view['proje_adi']}")
    print(f"     - Öğretmen Onayı: {proj_view['status']}")
    print(f"     - Öğretmen Rozeti: {proj_view['teacher_badge']} ({proj_view['teacher_stars']} Yıldız)")
    print(f"     - Öğretmen Yorumu: '{proj_view['teacher_comment']}'")
    print(f"     - Kapalı Devre Medya URL: {proj_view['media_list'][0]['url']}")

    # Medya akış testi (kapalı devre erişim)
    media_file_resp = stream_project_media(media_id=media_id, user=parent_auth)
    assert media_file_resp.status_code == 200
    print(f"  ✓ Kapalı Devre Medya Akışı Başarılı (Status: {media_file_resp.status_code})")

    print("\n" + "=" * 60)
    print("🎉 5 ADIMLI TÜM PİLOT AKIŞI EKSİKSİZ VE BAŞARIYLA GEÇTİ! 🎉")
    print("=" * 60)

if __name__ == "__main__":
    run_pilot_flow_test()
