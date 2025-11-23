'use client';

import { ReactNode } from 'react';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: ReactNode;
  userRole: 'admin' | 'technician' | null;
  onLogout: () => void;
}

export default function Layout({ children, userRole, onLogout }: LayoutProps) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar userRole={userRole} onLogout={onLogout} />
      <main className="flex-1 lg:ml-64 p-4 sm:p-6 lg:p-8">
        {children}
      </main>
    </div>
  );
}
