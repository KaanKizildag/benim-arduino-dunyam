import { ref, computed } from 'vue';

export interface AuthUser {
  id: string;
  institution_id?: string | null;
  username: string;
  full_name: string;
  role: 'admin' | 'mudur' | 'ogretmen' | 'ogrenci' | 'veli' | 'guest';
  student_no?: string;
  avatar_icon?: string;
  institution_name?: string;
  institution_code?: string;
}

const TOKEN_KEY = 'kid_arduino_auth_token';
const USER_KEY = 'kid_arduino_current_user';

const token = ref<string | null>(localStorage.getItem(TOKEN_KEY));
const currentUser = ref<AuthUser | null>(() => {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
});

export function useAuth() {
  const isAuthenticated = computed(() => Boolean(currentUser.value && token.value));
  const userRole = computed(() => currentUser.value?.role || 'guest');

  const isAdmin = computed(() => userRole.value === 'admin');
  const isMudur = computed(() => userRole.value === 'mudur');
  const isTeacher = computed(() => userRole.value === 'ogretmen');
  const isStudent = computed(() => userRole.value === 'ogrenci');
  const isParent = computed(() => userRole.value === 'veli');
  const isGuest = computed(() => !currentUser.value || userRole.value === 'guest');

  const roleLabel = computed(() => {
    switch (userRole.value) {
      case 'admin':
        return 'Sistem Yöneticisi';
      case 'mudur':
        return 'Okul Müdürü';
      case 'ogretmen':
        return 'Öğretmen';
      case 'ogrenci':
        return 'Öğrenci';
      case 'veli':
        return 'Veli';
      default:
        return 'Serbest Maker (Misafir)';
    }
  });

  const roleBadgeIcon = computed(() => {
    switch (userRole.value) {
      case 'admin':
        return '👑';
      case 'mudur':
        return '🏫';
      case 'ogretmen':
        return '👩‍🏫';
      case 'ogrenci':
        return '👦';
      case 'veli':
        return '👨‍👩‍👧';
      default:
        return '🌟';
    }
  });

  function getAuthHeaders(): Record<string, string> {
    if (token.value) {
      return { Authorization: `Bearer ${token.value}` };
    }
    return {};
  }

  function setSession(newToken: string, user: AuthUser) {
    token.value = newToken;
    currentUser.value = user;
    localStorage.setItem(TOKEN_KEY, newToken);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  function logout() {
    token.value = null;
    currentUser.value = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }

  async function loginCorporate(username: string, password: str): Promise<boolean> {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Kullanıcı adı veya şifre hatalı!');
      }
      const data = await res.json();
      setSession(data.access_token, data.user);
      return true;
    } catch (e: any) {
      throw new Error(e.message || 'Giriş yapılamadı.');
    }
  }

  async function loginStudent(institutionCode: string, studentNo: string, pin: string): Promise<boolean> {
    try {
      const res = await fetch('/api/auth/login-student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          institution_code: institutionCode,
          student_no: studentNo,
          pin
        })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Öğrenci numarası veya PIN hatalı!');
      }
      const data = await res.json();
      setSession(data.access_token, data.user);
      return true;
    } catch (e: any) {
      throw new Error(e.message || 'Öğrenci girişi yapılamadı.');
    }
  }

  return {
    token,
    currentUser,
    isAuthenticated,
    userRole,
    isAdmin,
    isMudur,
    isTeacher,
    isStudent,
    isParent,
    isGuest,
    roleLabel,
    roleBadgeIcon,
    getAuthHeaders,
    setSession,
    logout,
    loginCorporate,
    loginStudent
  };
}
