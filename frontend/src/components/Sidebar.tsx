"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

type Role = 'admin' | 'technician' | 'guest';

type SubItem = { name: string; href: string; roles?: Role[] };

type MenuItem = {
  name: string;
  href?: string;
  icon?: React.ReactNode;
  roles?: Role[];
  submenu?: SubItem[];
};

export default function Sidebar({ userRole: propUserRole, onLogout }: { userRole?: Role | null; onLogout?: () => void }) {
  const pathname = usePathname();
  const [openSubmenu, setOpenSubmenu] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userRole, setUserRole] = useState<Role>('admin');
  const [username, setUsername] = useState('Usuario');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const roleFromStorage = (localStorage.getItem('role') as Role) || null;
      const initialRole = propUserRole || roleFromStorage || 'admin';
      setUserRole(initialRole as Role);
      setUsername(localStorage.getItem('username') || 'Usuario');
    }
  }, [propUserRole]);

  const isActive = (href?: string) => {
    if (!href) return false;
    return pathname === href || pathname?.startsWith(href + '/');
  };

  const toggleSub = (name: string) => setOpenSubmenu((s) => (s === name ? null : name));

  const handleLogout = async () => {
    if (onLogout) {
      onLogout();
      return;
    }

    if (typeof window === 'undefined') return;

    const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/$/, '');
    const refresh = localStorage.getItem('refresh_token');
    const access = localStorage.getItem('access_token');

    try {
      if (refresh) {
        await fetch(`${API_URL}/api/logout/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(access ? { Authorization: `Bearer ${access}` } : {}),
          },
          body: JSON.stringify({ refresh }),
        });
      }
    } catch (err) {
      // Ignore network errors; proceed to clear storage anyway
      console.warn('Logout request failed', err);
    }

    // Clear client storage and redirect to login
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    localStorage.removeItem('role');
    window.location.href = '/';
  };

  const menu: MenuItem[] = [
    { name: 'Dashboard', href: '/dashboard', roles: ['admin', 'technician'], icon: (
      <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 13h8V3H3v10zM3 21h8v-6H3v6zM13 21h8V11h-8v10zM13 3v6h8V3h-8z"/></svg>
    ) },
    { name: 'Equipos', href: '/equipment', roles: ['admin', 'technician'], icon: (
      <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M20 7H4v10h16V7zM8 3v4"/></svg>
    ), submenu: [
      { name: 'Lista de Equipos', href: '/equipment', roles: ['admin', 'technician'] },
      { name: 'Nuevo Equipo', href: '/equipment/new', roles: ['admin'] },
    ] },
    { name: 'Mantenimientos', href: '/maintenance', roles: ['admin', 'technician'], icon: (
      <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 1v4M12 19v4M4.2 4.2l2.8 2.8M17 17l2.8 2.8M1 12h4M19 12h4M4.2 19.8l2.8-2.8M17 7l2.8-2.8"/></svg>
    ), submenu: [
      { name: 'Lista Mantenimientos', href: '/maintenance', roles: ['admin', 'technician'] },
      { name: 'Nuevo Mantenimiento', href: '/maintenance/new', roles: ['admin', 'technician'] },
    ] },
    { name: 'Reportes', href: '/reports', roles: ['admin', 'technician'], icon: (
      <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 3h18v18H3V3zM7 7h10M7 11h10M7 15h6"/></svg>
    ), submenu: [
      { name: 'Plantillas', href: '/reports/templates', roles: ['admin', 'technician'] },
      { name: 'Generados', href: '/reports/list', roles: ['admin', 'technician'] },
    ] },
    { name: 'Ubicaciones', href: '/admin/locations', roles: ['admin'], icon: (
      <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 2C8 2 5 5 5 9c0 5 7 13 7 13s7-8 7-13c0-4-3-7-7-7z"/></svg>
    ), submenu: [
      { name: 'Sedes', href: '/admin/locations?tab=sedes', roles: ['admin'] },
      { name: 'Dependencias', href: '/admin/locations?tab=dependencias', roles: ['admin'] },
      { name: 'Subdependencias', href: '/admin/locations?tab=subdependencias', roles: ['admin'] },
    ] },
    { name: 'Usuarios', href: '/admin/users', roles: ['admin'], icon: (
      <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 12c2.7 0 5-2.3 5-5s-2.3-5-5-5-5 2.3-5 5 2.3 5 5 5zM4 20c0-4 4-6 8-6s8 2 8 6"/></svg>
    ) },
    { name: 'Configuración', href: '/admin', roles: ['admin'], icon: (
      <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 8a4 4 0 100 8 4 4 0 000-8zM19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09a1.65 1.65 0 00-1-1.51 1.65 1.65 0 00-1.82.33l-.06.06A2 2 0 012.28 18l.06-.06A1.65 1.65 0 012.67 16.2 1.65 1.65 0 013 14.4V12a2 2 0 110-4v-.09c0-.6.24-1.17.67-1.59l.06-.06A2 2 0 115.57 4.4l-.06.06A1.65 1.65 0 017.4 3.67 1.65 1.65 0 009.2 3h.09A2 2 0 0112 2h0a2 2 0 011.71 1.09c.2.36.57.61 1 .65h.09a1.65 1.65 0 011.58 1.45c.05.36.28.68.62.88z"/></svg>
    ), submenu: [
      { name: 'Ajustes', href: '/admin/settings', roles: ['admin'] },
      { name: 'Permisos', href: '/admin/permissions', roles: ['admin'] },
      { name: 'Backup', href: '/admin/backup', roles: ['admin'] },
    ] },
  ];

  const filtered = menu.filter((m) => (m.roles ? m.roles.includes(userRole) : true));

  return (
    <>
      {/* Mobile toggle */}
      <button onClick={() => setMobileOpen((s) => !s)} className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-blue-900 text-white">
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>

      <aside className={`fixed top-0 left-0 z-40 h-screen w-64 bg-gradient-to-b from-blue-900 to-blue-800 text-white shadow-lg transform ${mobileOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 transition-transform duration-200`}>
        <div className="p-4 border-b border-blue-800">
          <h1 className="text-lg font-bold">Sistema</h1>
          <div className="text-sm text-blue-200 mt-1">{username}</div>
        </div>

        <nav className="p-3 space-y-1 overflow-y-auto h-[calc(100vh-64px)]">
          {filtered.map((item) => (
            <div key={item.name}>
              {item.submenu ? (
                <div>
                  <button onClick={() => toggleSub(item.name)} className={`w-full flex items-center justify-between px-3 py-2 rounded hover:bg-blue-800 ${isActive(item.href) ? 'bg-blue-700' : ''}`}>
                    <div className="flex items-center">
                      {item.icon}
                      <span>{item.name}</span>
                    </div>
                    <span className={`transform transition-transform ${openSubmenu === item.name ? 'rotate-180' : 'rotate-0'}`}>▾</span>
                  </button>
                  {openSubmenu === item.name && (
                    <div className="pl-4 mt-1 space-y-1">
                      {item.submenu!.filter(si => !si.roles || si.roles.includes(userRole)).map((si) => (
                        <Link key={si.href} href={si.href} className={`block px-3 py-2 rounded hover:bg-blue-800 ${isActive(si.href) ? 'bg-blue-600' : ''}`}>{si.name}</Link>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <Link href={item.href || '#'} className={`block px-3 py-2 rounded hover:bg-blue-800 ${isActive(item.href) ? 'bg-blue-700' : ''}`}>
                  <div className="flex items-center">
                    {item.icon}
                    <span>{item.name}</span>
                  </div>
                </Link>
              )}
            </div>
          ))}
        </nav>

        <div className="p-3 border-t border-blue-800">
          <button onClick={handleLogout} className="w-full text-left px-3 py-2 rounded hover:bg-red-600 flex items-center">
            <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M16 17l5-5-5-5M21 12H9"/></svg>
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>
    </>
  );
}
