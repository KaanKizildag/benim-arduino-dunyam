"""
Kid Arduino Studio - Veritabanı ve Şema Yönetimi (SQLite)

Bu modül:
- SQLite veritabanı bağlantılarını yönetir.
- Kurum izolasyonu (Multi-Tenancy) ve RBAC ilişkisel şemalarını oluşturur.
- İlk çalıştırmada örnek kurum, roller ve kullanıcıları otomatik seed eder.
"""

import os
import sqlite3
import hashlib
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "kid_arduino.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads", "projects")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db_connection() -> sqlite3.Connection:
    """SQLite veritabanı bağlantısı açar ve Row nesnesi döner."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """PBKDF2-HMAC-SHA256 ile şifre veya PIN hashler."""
    if not salt:
        salt = uuid.uuid4().hex[:16]
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Hashlenmiş şifreyi doğrular."""
    try:
        salt, key_hex = stored_hash.split("$", 1)
        expected = hash_password(plain_password, salt)
        return expected == stored_hash
    except Exception:
        return False


def init_db():
    """Tüm tabloları oluşturur ve varsayılan seed verilerini yükler."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Okullar / Kurumlar Tablosu (Multi-Tenancy İzolasyonu)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS institutions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            daily_token_quota INTEGER DEFAULT 500,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Kullanıcılar Tablosu (RBAC: admin, mudur, ogretmen, ogrenci, veli)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            institution_id TEXT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            student_no TEXT,
            student_pin TEXT,
            phone_or_email TEXT,
            avatar_icon TEXT DEFAULT '👦',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE
        );
        """)

        # 3. Sınıflar / Gruplar Tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id TEXT PRIMARY KEY,
            institution_id TEXT NOT NULL,
            teacher_id TEXT,
            name TEXT NOT NULL,
            inventory_json TEXT DEFAULT '["ARDUINO_UNO","BREADBOARD","LED_RED","RESISTOR_220","BUZZER"]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE SET NULL
        );
        """)

        # 4. Sınıf - Öğrenci Atamaları
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS class_students (
            id TEXT PRIMARY KEY,
            class_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(class_id, student_id)
        );
        """)

        # 5. Veli - Öğrenci Eşleşmeleri
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS parent_student_pairs (
            id TEXT PRIMARY KEY,
            institution_id TEXT NOT NULL,
            parent_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(parent_id, student_id)
        );
        """)

        # 6. KVKK Açık Rıza Tablosu (Veli İzni)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS kvkk_consents (
            id TEXT PRIMARY KEY,
            institution_id TEXT NOT NULL,
            parent_id TEXT NOT NULL,
            student_id TEXT NOT NULL,
            media_share_allowed INTEGER DEFAULT 0,
            consented_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(parent_id, student_id)
        );
        """)

        # 7. Projeler Tablosu (İlişkisel Proje Saklama)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            institution_id TEXT,
            student_id TEXT NOT NULL,
            proje_adi TEXT NOT NULL,
            prompt TEXT,
            badge TEXT DEFAULT 'AI Tasarımım ✨',
            netlist_json TEXT,
            arduino_kodu TEXT,
            akis_diyagrami_json TEXT,
            status TEXT DEFAULT 'taslak',
            is_shared_with_parent INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (institution_id) REFERENCES institutions(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 8. Medya Dosyaları (Fotoğraf / Video - Kapalı Devre)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_media (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            media_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            caption TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 9. Öğretmen Değerlendirme & Rozet Tablosu
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_feedback (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            teacher_id TEXT NOT NULL,
            badge TEXT,
            comment TEXT,
            stars INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 10. Öğrenci Günlük AI Kullanım Kotaları
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_usage_quotas (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            usage_date TEXT NOT NULL,
            request_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, usage_date)
        );
        """)

        conn.commit()

        # Seed verilerini kontrol et
        _seed_initial_data(conn)


def _seed_initial_data(conn: sqlite3.Connection):
    """Sistemde hiç kullanıcı yoksa ilk varsayılan kullanıcıları oluşturur."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]
    if count > 0:
        return

    # 1. Super Admin
    admin_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO users (id, institution_id, username, password_hash, full_name, role, avatar_icon)
    VALUES (?, NULL, 'admin', ?, 'Sistem Yöneticisi', 'admin', '👑');
    """, (admin_id, hash_password("admin123")))

    # 2. Örnek Kurum
    inst_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO institutions (id, name, code, daily_token_quota)
    VALUES (?, 'Atatürk Bilim & Robotik Ortaokulu', 'KOD-01', 1000);
    """, (inst_id,))

    # 3. Okul Müdürü
    mudur_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO users (id, institution_id, username, password_hash, full_name, role, avatar_icon)
    VALUES (?, ?, 'mudur1', ?, 'Kemal Bey (Müdür)', 'mudur', '🏫');
    """, (mudur_id, inst_id, hash_password("mudur123")))

    # 4. Öğretmen
    teacher_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO users (id, institution_id, username, password_hash, full_name, role, avatar_icon)
    VALUES (?, ?, 'ogretmen1', ?, 'Zeynep Öğretmen', 'ogretmen', '👩‍🏫');
    """, (teacher_id, inst_id, hash_password("ogretmen123")))

    # 5. Sınıf
    class_id = str(uuid.uuid4())
    default_inv = json.dumps(["ARDUINO_UNO", "BREADBOARD", "LED_RED", "LED_GREEN", "RESISTOR_220", "BUZZER", "HCSR04", "LDR_SENSOR"])
    cursor.execute("""
    INSERT INTO classes (id, institution_id, teacher_id, name, inventory_json)
    VALUES (?, ?, ?, '5-A Robotik Grubu', ?);
    """, (class_id, inst_id, teacher_id, default_inv))

    # 6. Öğrenci (Okul No: 104, PIN: 1234)
    student_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO users (id, institution_id, username, password_hash, full_name, role, student_no, student_pin, avatar_icon)
    VALUES (?, ?, 'can104', ?, 'Can Yıldız', 'ogrenci', '104', ?, '👦');
    """, (student_id, inst_id, hash_password("1234"), hash_password("1234")))

    # Sınıfa öğrenciyi ata
    cursor.execute("""
    INSERT INTO class_students (id, class_id, student_id)
    VALUES (?, ?, ?);
    """, (str(uuid.uuid4()), class_id, student_id))

    # 7. Veli
    parent_id = str(uuid.uuid4())
    cursor.execute("""
    INSERT INTO users (id, institution_id, username, password_hash, full_name, role, phone_or_email, avatar_icon)
    VALUES (?, ?, 'veli1', ?, 'Mehmet Yıldız (Veli)', 'veli', 'veli@example.com', '👨‍👩‍👧');
    """, (parent_id, inst_id, hash_password("veli123")))

    # Veli - Öğrenci Eşleşmesi
    cursor.execute("""
    INSERT INTO parent_student_pairs (id, institution_id, parent_id, student_id)
    VALUES (?, ?, ?, ?);
    """, (str(uuid.uuid4()), inst_id, parent_id, student_id))

    # Veli KVKK Rızası (Varsayılan: Onaylı)
    cursor.execute("""
    INSERT INTO kvkk_consents (id, institution_id, parent_id, student_id, media_share_allowed)
    VALUES (?, ?, ?, ?, 1);
    """, (str(uuid.uuid4()), inst_id, parent_id, student_id))

    conn.commit()
    print("[Database] İlk veritabanı şeması ve test seed verileri başarıyla oluşturuldu.")


if __name__ == "__main__":
    init_db()
    print("Veritabanı oluşturma testi tamamlandı.")
