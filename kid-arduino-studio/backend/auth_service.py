"""
Kid Arduino Studio - Kimlik Doğrulama ve Rol Güvenlik Servisi (Auth & RBAC)

Bu modül:
- JWT token üretimi ve doğrulaması yapar.
- Normal kullanıcı (şifre) ve öğrenci (Okul Kodu + No + PIN) oturum açma mantığını yönetir.
- FastAPI dependency fonksiyonları ile rol ve kurum izolasyonu güvenliğini sağlar.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import (
    get_db_connection,
    verify_password,
    hash_password,
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "kid_arduino_super_secret_jwt_key_2026")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

security_bearer = HTTPBearer(auto_error=False)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Kullanıcı bilgileri ile imzalı JWT token üretir."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """JWT token'ı çözer ve geçerliliğini doğrular."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Kullanıcı adı / E-posta ve şifre ile giriş (Admin, Müdür, Öğretmen, Veli).
    """
    clean_username = username.strip().lower()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, i.name as institution_name, i.code as institution_code
            FROM users u
            LEFT JOIN institutions i ON u.institution_id = i.id
            WHERE LOWER(u.username) = ? AND u.is_active = 1
        """, (clean_username,))
        row = cursor.fetchone()
        if not row:
            return None

        user = dict(row)
        if verify_password(password, user["password_hash"]):
            # Hassas alanları temizle
            del user["password_hash"]
            if "student_pin" in user:
                del user["student_pin"]
            return user
        return None


EMOJI_DIGIT_MAP = {
    "1": "🚀", "2": "⭐", "3": "🤖", "4": "⚡",
    "5": "🐱", "6": "🎈", "7": "🍕", "8": "🦁"
}
DIGIT_EMOJI_MAP = {v: k for k, v in EMOJI_DIGIT_MAP.items()}

def to_digit_pin(pin_str: str) -> str:
    """Emoji dizisini karşılık gelen rakamlara çevirir."""
    res = []
    i = 0
    while i < len(pin_str):
        matched = False
        for emoji, digit in DIGIT_EMOJI_MAP.items():
            if pin_str.startswith(emoji, i):
                res.append(digit)
                i += len(emoji)
                matched = True
                break
        if not matched:
            res.append(pin_str[i])
            i += 1
    return "".join(res)

def to_emoji_pin(pin_str: str) -> str:
    """Rakam dizisini çocuk dostu emojilere çevirir."""
    return "".join(EMOJI_DIGIT_MAP.get(ch, ch) for ch in pin_str)

def authenticate_student(institution_code: str, student_no: str, pin: str) -> Optional[Dict[str, Any]]:
    """
    Öğrenci Girişi: Kurum Kodu + Öğrenci No + 4 Haneli Emoji Şifre (veya PIN).
    Çocuklar renkli emoji tuş takımından 4 emoji seçer (örn: 🚀 ⭐ 🤖 ⚡).
    """
    clean_code = institution_code.strip().upper()
    clean_no = student_no.strip()
    clean_pin = pin.strip()

    # Kontrol edilecek alternatif varyantlar (doğrudan emoji, rakam eşdeğeri veya emoji eşdeğeri)
    candidates = [clean_pin, to_digit_pin(clean_pin), to_emoji_pin(clean_pin)]
    # Tekrarları temizle
    candidates = list(dict.fromkeys(candidates))

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, i.name as institution_name, i.code as institution_code
            FROM users u
            INNER JOIN institutions i ON u.institution_id = i.id
            WHERE UPPER(i.code) = ? AND u.student_no = ? AND u.role = 'ogrenci' AND u.is_active = 1
        """, (clean_code, clean_no))
        row = cursor.fetchone()
        if not row:
            return None

        user = dict(row)
        stored_pin_hash = user.get("student_pin")
        if not stored_pin_hash:
            return None

        is_valid = any(verify_password(c, stored_pin_hash) for c in candidates)
        if is_valid:
            del user["password_hash"]
            del user["student_pin"]
            return user
        return None


# -------------------------------------------------------------------------
# FastAPI Rol ve Güvenlik Bağımlılıkları (Dependencies)
# -------------------------------------------------------------------------

def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Optional[Dict[str, Any]]:
    """
    Opsiyonel kullanıcı doğrulayıcı: Token varsa kullanıcıyı döner, yoksa None döner.
    Serbest maker / misafir isteklerinde kullanılır.
    """
    if not auth or not auth.credentials:
        return None

    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        return None

    user_id = payload["sub"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.institution_id, u.username, u.full_name, u.role, u.student_no, u.avatar_icon,
                   i.name as institution_name, i.code as institution_code
            FROM users u
            LEFT JOIN institutions i ON u.institution_id = i.id
            WHERE u.id = ? AND u.is_active = 1
        """, (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)


def get_current_user(
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Zorunlu kullanıcı doğrulayıcı: Token yoksa veya geçersizse HTTP 401 fırlatır.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bu işlem için oturum açmanız gerekmektedir.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user


def require_role(allowed_roles: List[str]):
    """
    Belirli rollere sahip kullanıcıların erişimine izin veren Dependency Factory.
    Örn: Depends(require_role(["admin", "mudur"]))
    """
    def role_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_role = user.get("role")
        if user_role not in allowed_roles:
            role_labels = {
                "admin": "Sistem Yöneticisi (Admin)",
                "mudur": "Okul Müdürü",
                "ogretmen": "Öğretmen",
                "ogrenci": "Öğrenci",
                "veli": "Veli"
            }
            allowed_labels = [role_labels.get(r, r) for r in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yetkisiz erişim! Bu alana yalnızca şu roller erişebilir: {', '.join(allowed_labels)}."
            )
        return user
    return role_checker


def check_institution_access(user: Dict[str, Any], target_institution_id: Optional[str]) -> bool:
    """
    Kurum izolasyonu denetimi: Super admin herkesi görebilir; diğerleri sadece kendi kurumunu görür.
    """
    if user.get("role") == "admin":
        return True
    user_inst = user.get("institution_id")
    if not user_inst or not target_institution_id:
        return False
    return user_inst == target_institution_id
