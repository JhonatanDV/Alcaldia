export type CanonicalRole = 'admin' | 'technician';

export function normalizeRole(raw?: string | null): CanonicalRole | null {
  if (!raw) return null;
  const r = String(raw).trim().toLowerCase();
  if (r === 'admin' || r === 'administrador' || r === 'administrador' || r === 'administrator') return 'admin';
  if (r === 'technician' || r === 'technico' || r === 'técnico' || r === 'tecnico') return 'technician';
  return null;
}

export function getStoredUserRole(): CanonicalRole | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem('user_role');
  return normalizeRole(raw);
}
