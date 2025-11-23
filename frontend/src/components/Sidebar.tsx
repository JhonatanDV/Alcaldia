'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  userRole: 'admin' | 'technician' | null;
  onLogout: () => void;
}

export default function Sidebar({ userRole, onLogout }: SidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [openSubmenu, setOpenSubmenu] = useState<string | null>(null);
  const [username, setUsername] = useState('Usuario');
  const pathname = usePathname();


  useEffect(() => {
    const storedUsername = localStorage.getItem('username') || 'Usuario';
    setUsername(storedUsername);
  }, []);

  useEffect(() => {
    console.log('Sidebar userRole:', userRole);
    console.log('Sidebar username:', username);
  }, [userRole, username]);

  const isActive = (path: string) => {
    return pathname === path || pathname?.startsWith(path + '/');
  };

  const toggleSubmenu = (name: string) => {
    setOpenSubmenu(openSubmenu === name ? null : name);
  };

  const menuItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
        </svg>
      ),
      roles: ['admin', 'technician'],
    },
    {
      name: 'Equipos',
      href: '/equipment',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
      roles: ['admin', 'technician'],
      submenu: [
        { name: 'Lista de Equipos', href: '/equipment', roles: ['admin', 'technician'] },
        { name: 'Nuevo Equipo', href: '/equipment/new', roles: ['admin'] },
      ],
    },
    {
      name: 'Mantenimientos',
      href: '/maintenance',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      roles: ['admin', 'technician'],
      submenu: [
        { name: 'Lista Mantenimientos', href: '/maintenance', roles: ['admin', 'technician'] },
        { name: 'Nuevo Mantenimiento', href: '/maintenance/new', roles: ['admin', 'technician'] },
      ],
    },
    {
      name: 'Reportes',
      href: '/reports',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      roles: ['admin', 'technician'],
    },
    {
      name: 'Ubicaciones',
      href: '/admin/locations',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      roles: ['admin'],
      submenu: [
        { name: 'Sedes', href: '/admin/locations?tab=sedes', roles: ['admin'] },
        { name: 'Dependencias', href: '/admin/locations?tab=dependencias', roles: ['admin'] },
        { name: 'Subdependencias', href: '/admin/locations?tab=subdependencias', roles: ['admin'] },
      ],
    },
    {
      name: 'Usuarios',
      href: '/admin/users',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
      roles: ['admin'],
    },
    {
      name: 'Configuración',
      href: '/admin',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
      roles: ['admin'],
      submenu: [
        { name: 'Ajustes', href: '/admin/settings', roles: ['admin'] },
        { name: 'Permisos', href: '/admin/permissions', roles: ['admin'] },
        { name: 'Backup', href: '/admin/backup', roles: ['admin'] },
      ],
    },
  ];

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(userRole as string)
  );

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-md bg-blue-900 text-white hover:bg-blue-800 transition-colors"
        aria-label="Toggle menu"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {isOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-40 h-screen w-64
          bg-gradient-to-b from-blue-900 to-blue-800
          text-gray-100 shadow-2xl
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header con nombre de usuario */}
          <div className="p-4 bg-blue-950 bg-opacity-50">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white font-bold text-lg">
                {username.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-white truncate">{username}</p>
                <p className="text-xs text-gray-300 capitalize">{userRole || 'Usuario'}</p>
              </div>
            </div>
          </div>

          {/* Navigation Menu */}
          <nav className="flex-1 overflow-y-auto py-4 px-2">
            {filteredMenuItems.map((item) => (
              <div key={item.name} className="mb-1">
                {item.submenu ? (
                  <>
                    <button
                      onClick={() => toggleSubmenu(item.name)}
                      className={`
                        w-full flex items-center justify-between px-3 py-2.5
                        text-sm font-medium rounded-lg
                        transition-all duration-200
                        ${isActive(item.href) || openSubmenu === item.name
                          ? 'bg-blue-700 text-white shadow-lg'
                          : 'text-gray-200 hover:bg-blue-800 hover:text-white'
                        }
                      `}
                    >
                      <div className="flex items-center space-x-3">
                        <span className="flex-shrink-0">{item.icon}</span>
                        <span>{item.name}</span>
                      </div>
                      <svg
                        className={`w-4 h-4 transition-transform duration-200 ${
                          openSubmenu === item.name ? 'transform rotate-180' : ''
                        }`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {openSubmenu === item.name && (
                      <div className="mt-1 ml-8 space-y-1">
                        {item.submenu
                          .filter(subitem => subitem.roles.includes(userRole as string))
                          .map((subitem) => (
                            <Link
                              key={subitem.href}
                              href={subitem.href}
                              onClick={() => setIsOpen(false)}
                              className={`
                                block px-3 py-2 text-sm rounded-lg
                                transition-all duration-200
                                ${isActive(subitem.href)
                                  ? 'bg-blue-600 text-white font-medium'
                                  : 'text-gray-300 hover:bg-blue-800 hover:text-white'
                                }
                              `}
                            >
                              <div className="flex items-center space-x-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                                <span>{subitem.name}</span>
                              </div>
                            </Link>
                          ))}
                      </div>
                    )}
                  </>
                ) : (
                  <Link
                    href={item.href}
                    onClick={() => setIsOpen(false)}
                    className={`
                      flex items-center space-x-3 px-3 py-2.5
                      text-sm font-medium rounded-lg
                      transition-all duration-200
                      ${isActive(item.href)
                        ? 'bg-blue-700 text-white shadow-lg'
                        : 'text-gray-200 hover:bg-blue-800 hover:text-white'
                      }
                    `}
                  >
                    <span className="flex-shrink-0">{item.icon}</span>
                    <span>{item.name}</span>
                  </Link>
                )}
              </div>
            ))}
          </nav>

          {/* Quick Actions Section */}
          <div className="border-t border-blue-700 px-2 py-4 bg-blue-950 bg-opacity-30">
            <p className="px-3 mb-2 text-xs font-semibold text-yellow-400 uppercase tracking-wider">
              Acciones Rápidas
            </p>
            <button
              onClick={onLogout}
              className="
                w-full flex items-center space-x-3 px-3 py-2.5
                text-sm font-medium text-gray-200
                hover:bg-red-600 hover:text-white
                rounded-lg transition-all duration-200
              "
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              <span>Cerrar Sesión</span>
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
