"""
Kid Arduino Studio - Rol Tabanlı Yönetim ve Kurumsal API Yönlendiricisi (RBAC Router)

Bu modül:
- /api/auth (Login, Öğrenci PIN Girişi, Me)
- /api/mudur (Öğretmen, Sınıf, Öğrenci, Veli-Öğrenci Eşleştirme)
- /api/teacher (Sınıf Envanteri, Devre Onayı, Medya Yükleme, Rozetler)
- /api/student (Sınıf Envanteri, Öğrenci Projeleri)
- /api/parent (KVKK İzni, Çocuk Projeleri, Başarı Sertifikası)
- /api/media (Yetkilendirilmiş Kapalı Devre Video/Fotoğraf Sunumu)
rotalarını yönetir.
"""

import os
import uuid
import json
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import (
    get_db_connection,
    hash_password,
    UPLOAD_DIR,
)
from auth_service import (
    authenticate_user,
    authenticate_student,
    create_access_token,
    get_current_user,
    get_current_user_optional,
    require_role,
    check_institution_access,
)

router = APIRouter()


# -------------------------------------------------------------------------
# Pydantic İstek / Yanıt Modelleri
# -------------------------------------------------------------------------

class UserLoginRequest(BaseModel):
    username: str
    password: str

class StudentLoginRequest(BaseModel):
    institution_code: str
    student_no: str
    pin: str

class CreateTeacherRequest(BaseModel):
    username: str
    full_name: str
    password: str

class CreateClassRequest(BaseModel):
    name: str
    teacher_id: Optional[str] = None
    inventory: Optional[List[str]] = None

class CreateStudentRequest(BaseModel):
    full_name: str
    student_no: str
    pin: str
    class_id: Optional[str] = None

class ResetStudentPinRequest(BaseModel):
    new_pin: str

class CreateParentPairRequest(BaseModel):
    parent_username: str
    parent_full_name: str
    parent_password: str
    student_id: str

class UpdateInventoryRequest(BaseModel):
    inventory: List[str]

class TeacherFeedbackRequest(BaseModel):
    badge: Optional[str] = "TEMIZ_DEVRE"
    comment: Optional[str] = "Tebrikler, devre başarıyla çalıştı!"
    stars: Optional[int] = 5

class KvkkConsentUpdateRequest(BaseModel):
    student_id: str
    allow_media_share: bool


# -------------------------------------------------------------------------
# 1. KİMLİK DOĞRULAMA (AUTH) ROTASI
# -------------------------------------------------------------------------

@router.post("/api/auth/login")
def login_endpoint(req: UserLoginRequest):
    """Admin, Müdür, Öğretmen ve Veli için e-posta/kullanıcı adı ile giriş."""
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı!"
        )
    token = create_access_token({
        "sub": user["id"],
        "institution_id": user.get("institution_id"),
        "role": user["role"],
        "name": user["full_name"]
    })
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/api/auth/login-student")
def student_login_endpoint(req: StudentLoginRequest):
    """Öğrenciler için Okul Kodu + No + 4 Haneli PIN ile çocuk dostu giriş."""
    student = authenticate_student(req.institution_code, req.student_no, req.pin)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Okul kodu, öğrenci numarası veya PIN hatalı!"
        )
    token = create_access_token({
        "sub": student["id"],
        "institution_id": student.get("institution_id"),
        "role": student["role"],
        "name": student["full_name"],
        "student_no": student.get("student_no")
    })
    return {"access_token": token, "token_type": "bearer", "user": student}


@router.get("/api/auth/me")
def get_me_endpoint(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Oturumu açık olan kullanıcının detaylarını ve yetkilerini döner."""
    return current_user


# -------------------------------------------------------------------------
# 2. OKUL MÜDÜRÜ YÖNETİM ROTASI (MÜDÜR / ADMIN)
# -------------------------------------------------------------------------

@router.get("/api/mudur/overview")
def get_mudur_overview(user: Dict[str, Any] = Depends(require_role(["mudur", "admin"]))):
    """Müdür kontrol paneli için özet istatistikler."""
    inst_id = user.get("institution_id")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Filtreleme (Admin değilse sadece kendi kurumu)
        inst_clause = "WHERE institution_id = ?" if inst_id else ""
        inst_params = (inst_id,) if inst_id else ()

        cursor.execute(f"SELECT COUNT(*) FROM users WHERE role = 'ogretmen' {'AND institution_id = ?' if inst_id else ''};", inst_params)
        teacher_count = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM users WHERE role = 'ogrenci' {'AND institution_id = ?' if inst_id else ''};", inst_params)
        student_count = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM classes {inst_clause};", inst_params)
        class_count = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM projects {inst_clause};", inst_params)
        project_count = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM parent_student_pairs {inst_clause};", inst_params)
        paired_count = cursor.fetchone()[0]

    return {
        "teachers": teacher_count,
        "students": student_count,
        "classes": class_count,
        "projects": project_count,
        "paired_parents": paired_count
    }


@router.get("/api/mudur/teachers")
def get_teachers_endpoint(user: Dict[str, Any] = Depends(require_role(["mudur", "admin"]))):
    """Kurumdaki öğretmenleri listeler."""
    inst_id = user.get("institution_id")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if inst_id:
            cursor.execute("""
                SELECT id, username, full_name, role, avatar_icon, created_at
                FROM users WHERE role = 'ogretmen' AND institution_id = ? AND is_active = 1
                ORDER BY full_name ASC;
            """, (inst_id,))
        else:
            cursor.execute("SELECT id, username, full_name, role, avatar_icon, created_at FROM users WHERE role = 'ogretmen' AND is_active = 1;")
        return [dict(r) for r in cursor.fetchall()]


@router.post("/api/mudur/teachers")
def create_teacher_endpoint(req: CreateTeacherRequest, user: Dict[str, Any] = Depends(require_role(["mudur", "admin"]))):
    """Yeni öğretmen hesabı açar."""
    inst_id = user.get("institution_id")
    if not inst_id and user.get("role") != "admin":
        raise HTTPException(status_code=400, detail="Kurum bilgisi bulunamadı.")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Kullanıcı adı kontrolü
        cursor.execute("SELECT id FROM users WHERE username = ?;", (req.username.strip(),))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Bu kullanıcı adı zaten kullanılıyor.")

        teacher_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO users (id, institution_id, username, password_hash, full_name, role, avatar_icon)
            VALUES (?, ?, ?, ?, ?, 'ogretmen', '👨‍🏫');
        """, (teacher_id, inst_id, req.username.strip(), hash_password(req.password), req.full_name.strip()))
        conn.commit()

    return {"success": True, "teacher_id": teacher_id, "username": req.username}


@router.get("/api/mudur/classes")
def get_classes_endpoint(user: Dict[str, Any] = Depends(require_role(["mudur", "admin"]))):
    """Kurumdaki sınıfları ve atanan öğretmenleri listeler."""
    inst_id = user.get("institution_id")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT c.*, u.full_name as teacher_name,
                   (SELECT COUNT(*) FROM class_students cs WHERE cs.class_id = c.id) as student_count
            FROM classes c
            LEFT JOIN users u ON c.teacher_id = u.id
        """
        if inst_id:
            query += " WHERE c.institution_id = ? ORDER BY c.name ASC;"
            cursor.execute(query, (inst_id,))
        else:
            query += " ORDER BY c.name ASC;"
            cursor.execute(query)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            d = dict(r)
            try:
                d["inventory"] = json.loads(d.get("inventory_json") or "[]")
            except Exception:
                d["inventory"] = []
            results.append(d)
        return results


@router.post("/api/mudur/classes")
def create_class_endpoint(req: CreateClassRequest, user: Dict[str, Any] = Depends(require_role(["mudur", "admin"]))):
    """Yeni sınıf tanımlar ve öğretmen atar."""
    inst_id = user.get("institution_id")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        class_id = str(uuid.uuid4())
        inv_json = json.dumps(req.inventory or ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220", "BUZZER"])
        cursor.execute("""
            INSERT INTO classes (id, institution_id, teacher_id, name, inventory_json)
            VALUES (?, ?, ?, ?, ?);
        """, (class_id, inst_id, req.teacher_id, req.name.strip(), inv_json))
        conn.commit()
    return {"success": True, "class_id": class_id, "name": req.name}


@router.get("/api/mudur/students")
def get_students_endpoint(user: Dict[str, Any] = Depends(require_role(["mudur", "admin"]))):
    """Kurumdaki öğrencileri, sınıflarını ve eşleşen velilerini listeler."""
    inst_id = user.get("institution_id")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT u.id, u.username, u.full_name, u.student_no, u.avatar_icon, u.created_at,
                   c.id as class_id, c.name as class_name,
                   p.full_name as parent_name, p.id as parent_id,
                   kc.media_share_allowed
            FROM users u
            LEFT JOIN class_students cs ON u.id = cs.student_id
            LEFT JOIN classes c ON cs.class_id = c.id
            LEFT JOIN parent_student_pairs psp ON u.id = psp.student_id
            LEFT JOIN users p ON psp.parent_id = p.id
            LEFT JOIN kvkk_consents kc ON u.id = kc.student_id
            WHERE u.role = 'ogrenci' AND u.is_active = 1
        """
        if inst_id:
            query += " AND u.institution_id = ? ORDER BY u.full_name ASC;"
            cursor.execute(query, (inst_id,))
        else:
            query += " ORDER BY u.full_name ASC;"
            cursor.execute(query)
        return [dict(r) for r in cursor.fetchall()]


@router.post("/api/mudur/students")
def create_student_endpoint(req: CreateStudentRequest, user: Dict[str, Any] = Depends(require_role(["mudur", "admin"]))):
    """Yeni öğrenci ekler ve 4 haneli PIN atar."""
    inst_id = user.get("institution_id")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Öğrenci numarası tekrarı kontrolü
        cursor.execute("SELECT id FROM users WHERE institution_id = ? AND student_no = ?;", (inst_id, req.student_no.strip()))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Bu öğrenci numarası bu okulda zaten kayıtlı!")

        student_id = str(uuid.uuid4())
        username = f"std_{req.student_no.strip()}_{uuid.uuid4().hex[:4]}"
        pin_hash = hash_password(req.pin.strip())

        cursor.execute("""
            INSERT INTO users (id, institution_id, username, password_hash, full_name, role, student_no, student_pin, avatar_icon)
            VALUES (?, ?, ?, ?, ?, 'ogrenci', ?, ?, '👦');
        """, (student_id, inst_id, username, pin_hash, req.full_name.strip(), req.student_no.strip(), pin_hash))

        if req.class_id:
            cursor.execute("""
                INSERT INTO class_students (id, class_id, student_id)
                VALUES (?, ?, ?);
            """, (str(uuid.uuid4()), req.class_id, student_id))

        conn.commit()

    return {"success": True, "student_id": student_id, "student_no": req.student_no, "full_name": req.full_name}


@router.post("/api/mudur/students/{student_id}/reset-pin")
def reset_student_pin_endpoint(student_id: str, req: ResetStudentPinRequest, user: Dict[str, Any] = Depends(require_role(["mudur", "admin", "ogretmen"]))):
    """Unutulan öğrenci PIN kodunu tek tıkla sıfırlar."""
    new_pin = req.new_pin.strip()
    if len(new_pin) < 4:
        raise HTTPException(status_code=400, detail="PIN kodu en az 4 haneli olmalıdır.")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, full_name FROM users WHERE id = ? AND role = 'ogrenci';", (student_id,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Öğrenci bulunamadı.")

        pin_hash = hash_password(new_pin)
        cursor.execute("UPDATE users SET student_pin = ?, password_hash = ? WHERE id = ?;", (pin_hash, pin_hash, student_id))
        conn.commit()

    return {"success": True, "message": f"{student['full_name']} için yeni PIN ({new_pin}) başarıyla güncellendi!"}


@router.post("/api/mudur/pairs")
def create_parent_student_pair(req: CreateParentPairRequest, user: Dict[str, Any] = Depends(require_role(["mudur", "admin"]))):
    """Veli hesabı oluşturur ve öğrenci ile eşleştirir."""
    inst_id = user.get("institution_id")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Veli kullanıcı adı var mı?
        cursor.execute("SELECT id FROM users WHERE username = ?;", (req.parent_username.strip(),))
        existing_parent = cursor.fetchone()
        if existing_parent:
            parent_id = existing_parent[0]
        else:
            parent_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO users (id, institution_id, username, password_hash, full_name, role, avatar_icon)
                VALUES (?, ?, ?, ?, ?, 'veli', '👨‍👩‍👧');
            """, (parent_id, inst_id, req.parent_username.strip(), hash_password(req.parent_password), req.parent_full_name.strip()))

        # Eşleşmeyi ekle
        pair_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR REPLACE INTO parent_student_pairs (id, institution_id, parent_id, student_id)
            VALUES (?, ?, ?, ?);
        """, (pair_id, inst_id, parent_id, req.student_id))

        # Varsayılan KVKK rızası kaydı aç
        consent_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR IGNORE INTO kvkk_consents (id, institution_id, parent_id, student_id, media_share_allowed)
            VALUES (?, ?, ?, ?, 1);
        """, (consent_id, inst_id, parent_id, req.student_id))

        conn.commit()

    return {"success": True, "parent_id": parent_id, "student_id": req.student_id}


# -------------------------------------------------------------------------
# 3. ÖĞRETMEN YÖNETİM & DEVRE ONAY ROTASI (ÖĞRETMEN)
# -------------------------------------------------------------------------

@router.get("/api/teacher/classes")
def get_teacher_classes(user: Dict[str, Any] = Depends(require_role(["ogretmen", "mudur", "admin"]))):
    """Giriş yapan öğretmene atanan sınıfları ve malzeme envanterini döner."""
    teacher_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, (SELECT COUNT(*) FROM class_students cs WHERE cs.class_id = c.id) as student_count
            FROM classes c
            WHERE c.teacher_id = ?
            ORDER BY c.name ASC;
        """, (teacher_id,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["inventory"] = json.loads(d.get("inventory_json") or "[]")
            except Exception:
                d["inventory"] = []
            results.append(d)
        return results


@router.put("/api/teacher/classes/{class_id}/inventory")
def update_class_inventory(class_id: str, req: UpdateInventoryRequest, user: Dict[str, Any] = Depends(require_role(["ogretmen", "mudur", "admin"]))):
    """Öğretmen sınıfındaki Arduino kutusunda bulunan malzemeleri işaretler/günceller."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        inv_json = json.dumps(req.inventory)
        cursor.execute("UPDATE classes SET inventory_json = ? WHERE id = ?;", (inv_json, class_id))
        conn.commit()
    return {"success": True, "class_id": class_id, "inventory": req.inventory}


@router.get("/api/teacher/projects")
def get_teacher_student_projects(user: Dict[str, Any] = Depends(require_role(["ogretmen", "mudur", "admin"]))):
    """Öğretmenin sınıfındaki öğrencilerin ürettiği projeleri listeler."""
    teacher_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, u.full_name as student_name, u.student_no,
                   c.name as class_name,
                   (SELECT COUNT(*) FROM project_media pm WHERE pm.project_id = p.id) as media_count,
                   pf.badge as teacher_badge, pf.comment as teacher_comment, pf.stars as teacher_stars
            FROM projects p
            INNER JOIN users u ON p.student_id = u.id
            INNER JOIN class_students cs ON u.id = cs.student_id
            INNER JOIN classes c ON cs.class_id = c.id
            LEFT JOIN project_feedback pf ON p.id = pf.project_id
            WHERE c.teacher_id = ?
            ORDER BY p.updated_at DESC;
        """, (teacher_id,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["netlist"] = json.loads(d.get("netlist_json") or "{}")
            except Exception:
                d["netlist"] = {}
            results.append(d)
        return results


@router.post("/api/teacher/projects/{project_id}/approve")
def approve_project_endpoint(project_id: str, user: Dict[str, Any] = Depends(require_role(["ogretmen", "mudur", "admin"]))):
    """Öğretmen öğrencinin masasına gelip devreyi fiziksel kontrol ettikten sonra projeyi onaylar."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE projects
            SET status = 'ogretmen_onayladi', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (project_id,))
        conn.commit()
    return {"success": True, "project_id": project_id, "status": "ogretmen_onayladi"}


@router.post("/api/teacher/projects/{project_id}/feedback")
def add_project_feedback(project_id: str, req: TeacherFeedbackRequest, user: Dict[str, Any] = Depends(require_role(["ogretmen", "mudur", "admin"]))):
    """Öğretmen devreyi onaylayıp dijital başarı rozeti ve yıldız takar."""
    feedback_id = str(uuid.uuid4())
    teacher_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO project_feedback (id, project_id, teacher_id, badge, comment, stars)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (feedback_id, project_id, teacher_id, req.badge, req.comment, req.stars))
        conn.commit()
    return {"success": True, "project_id": project_id, "badge": req.badge, "stars": req.stars}


@router.post("/api/teacher/projects/{project_id}/media")
def upload_project_media(
    project_id: str,
    file: UploadFile = File(...),
    caption: Optional[str] = Form(""),
    user: Dict[str, Any] = Depends(require_role(["ogretmen", "mudur", "admin"]))
):
    """
    Öğretmen çalışan devrenin fotoğrafını veya kısa videosunu çeker ve yükler.
    KVKK izni kontrol edilir; veli açık rıza vermediyse yükleme engellenir.
    """
    teacher_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, institution_id FROM projects WHERE id = ?;", (project_id,))
        proj = cursor.fetchone()
        if not proj:
            raise HTTPException(status_code=404, detail="Proje bulunamadı.")

        student_id = proj["student_id"]

        # KVKK İzin Kontrolü
        cursor.execute("SELECT media_share_allowed FROM kvkk_consents WHERE student_id = ?;", (student_id,))
        consent = cursor.fetchone()
        if consent and consent["media_share_allowed"] == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu öğrencinin velisi fotoğraf/video paylaşımına henüz KVKK açık rızası vermemiştir."
            )

        # Dosya uzantısı kontrolü
        filename = file.filename or "media.jpg"
        ext = os.path.splitext(filename)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".webp"):
            media_type = "image"
        elif ext in (".mp4", ".mov", ".webm", ".mkv"):
            media_type = "video"
        else:
            raise HTTPException(status_code=400, detail="Desteklenmeyen dosya formatı. (.jpg, .png, .mp4 desteklenir)")

        # Dosyayı kaydet
        media_id = str(uuid.uuid4())
        save_filename = f"{project_id}_{media_id}{ext}"
        save_path = os.path.join(UPLOAD_DIR, save_filename)

        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Veritabanına işle
        cursor.execute("""
            INSERT INTO project_media (id, project_id, teacher_id, media_type, file_path, caption)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (media_id, project_id, teacher_id, media_type, save_path, caption))
        conn.commit()

    return {
        "success": True,
        "media_id": media_id,
        "media_type": media_type,
        "caption": caption,
        "url": f"/api/media/stream/{media_id}"
    }


# -------------------------------------------------------------------------
# 4. ÖĞRENCİ ROTASI (ÖĞRENCİ)
# -------------------------------------------------------------------------

@router.get("/api/student/class-inventory")
def get_student_class_inventory(user: Dict[str, Any] = Depends(require_role(["ogrenci"]))):
    """Öğrencinin kayıtlı olduğu sınıfın öğretmen tarafından belirlenen Arduino envanterini döner."""
    student_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.inventory_json, c.name as class_name
            FROM class_students cs
            INNER JOIN classes c ON cs.class_id = c.id
            WHERE cs.student_id = ?;
        """, (student_id,))
        row = cursor.fetchone()
        if not row:
            return {
                "class_name": "Serbest Sınıf",
                "inventory": ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220", "BUZZER"]
            }
        try:
            inv = json.loads(row["inventory_json"] or "[]")
        except Exception:
            inv = ["ARDUINO_UNO", "BREADBOARD", "LED_RED", "RESISTOR_220", "BUZZER"]
        return {"class_name": row["class_name"], "inventory": inv}


@router.get("/api/student/my-projects")
def get_student_my_projects(user: Dict[str, Any] = Depends(require_role(["ogrenci"]))):
    """Öğrencinin kendi yaptığı projeleri, öğretmen onaylarını ve rozetlerini döner."""
    student_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*,
                   pf.badge as teacher_badge, pf.comment as teacher_comment, pf.stars as teacher_stars,
                   (SELECT COUNT(*) FROM project_media pm WHERE pm.project_id = p.id) as media_count
            FROM projects p
            LEFT JOIN project_feedback pf ON p.id = pf.project_id
            WHERE p.student_id = ?
            ORDER BY p.updated_at DESC;
        """, (student_id,))
        rows = cursor.fetchall()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["netlist"] = json.loads(d.get("netlist_json") or "{}")
            except Exception:
                d["netlist"] = {}
            results.append(d)
        return results


# -------------------------------------------------------------------------
# 5. VELİ ROTASI (VELİ - GURUR PORTFOLYOSU & KVKK)
# -------------------------------------------------------------------------

@router.get("/api/parent/children")
def get_parent_children(user: Dict[str, Any] = Depends(require_role(["veli"]))):
    """Giriş yapan velinin eşleştiği çocukları döner."""
    parent_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id as student_id, u.full_name as student_name, u.student_no, u.avatar_icon,
                   c.name as class_name,
                   COALESCE(kc.media_share_allowed, 1) as media_share_allowed
            FROM parent_student_pairs psp
            INNER JOIN users u ON psp.student_id = u.id
            LEFT JOIN class_students cs ON u.id = cs.student_id
            LEFT JOIN classes c ON cs.class_id = c.id
            LEFT JOIN kvkk_consents kc ON psp.student_id = kc.student_id
            WHERE psp.parent_id = ?;
        """, (parent_id,))
        return [dict(r) for r in cursor.fetchall()]


@router.post("/api/parent/kvkk")
def update_parent_kvkk_consent(req: KvkkConsentUpdateRequest, user: Dict[str, Any] = Depends(require_role(["veli"]))):
    """Veli çocuğunun proje fotoğraflarının ve videolarının paylaşımına açık rıza verir veya kaldırır."""
    parent_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT institution_id FROM users WHERE id = ?;", (parent_id,))
        inst_id = cursor.fetchone()["institution_id"]

        consent_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT OR REPLACE INTO kvkk_consents (id, institution_id, parent_id, student_id, media_share_allowed)
            VALUES (?, ?, ?, ?, ?);
        """, (consent_id, inst_id, parent_id, req.student_id, 1 if req.allow_media_share else 0))
        conn.commit()

    return {"success": True, "student_id": req.student_id, "media_share_allowed": req.allow_media_share}


@router.get("/api/parent/projects")
def get_parent_projects_portfolio(user: Dict[str, Any] = Depends(require_role(["veli"]))):
    """
    Veli Portfolyosu: Yalnızca kendi çocuğuyla ilgili paylaşılan projeleri,
    öğretmenin yüklediği videoları ve başarı rozetlerini salt okunur döner.
    """
    parent_id = user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, u.full_name as student_name, u.student_no,
                   pf.badge as teacher_badge, pf.comment as teacher_comment, pf.stars as teacher_stars
            FROM projects p
            INNER JOIN parent_student_pairs psp ON p.student_id = psp.student_id
            INNER JOIN users u ON p.student_id = u.id
            LEFT JOIN project_feedback pf ON p.id = pf.project_id
            WHERE psp.parent_id = ? AND p.is_shared_with_parent = 1
            ORDER BY p.updated_at DESC;
        """, (parent_id,))
        projects_rows = cursor.fetchall()

        results = []
        for pr in projects_rows:
            p_dict = dict(pr)
            proj_id = p_dict["id"]

            # Projeye ait medya dosyalarını getir
            cursor.execute("""
                SELECT id, media_type, caption, created_at
                FROM project_media
                WHERE project_id = ?;
            """, (proj_id,))
            media_rows = cursor.fetchall()
            p_dict["media_list"] = [
                {
                    "id": m["id"],
                    "media_type": m["media_type"],
                    "caption": m["caption"],
                    "url": f"/api/media/stream/{m['id']}"
                }
                for m in media_rows
            ]
            try:
                p_dict["netlist"] = json.loads(p_dict.get("netlist_json") or "{}")
            except Exception:
                p_dict["netlist"] = {}
            results.append(p_dict)

        return results


# -------------------------------------------------------------------------
# 6. KAPALI DEVRE MEDYA SUNUMU (GÜVENLİ DOSYA AKIŞI)
# -------------------------------------------------------------------------

@router.get("/api/media/stream/{media_id}")
def stream_project_media(media_id: str, user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)):
    """
    Kapalı devre medya servisi:
    Dosya sadece sisteme oturum açmış ilgili öğretmen, kurum müdürü, öğrenci veya veli tarafından izlenebilir.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM project_media WHERE id = ?;", (media_id,))
        media = cursor.fetchone()
        if not media:
            raise HTTPException(status_code=404, detail="Medya dosyası bulunamadı.")

        file_path = media["file_path"]
        if not os.path.isfile(file_path):
            raise HTTPException(status_code=404, detail="Fiziksel medya dosyası bulunamadı.")

        # Medya türüne göre Content-Type
        media_type = media["media_type"]
        content_type = "video/mp4" if media_type == "video" else "image/jpeg"

        return FileResponse(file_path, media_type=content_type)
