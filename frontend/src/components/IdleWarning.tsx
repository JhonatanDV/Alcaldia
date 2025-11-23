"use client";

import { useEffect, useState } from 'react';

interface Props {
  remainingMs: number;
  onExtend: () => void;
  onLogout: () => void;
}

export default function IdleWarning({ remainingMs, onExtend, onLogout }: Props) {
  const [secs, setSecs] = useState(Math.ceil(remainingMs / 1000));

  useEffect(() => {
    setSecs(Math.max(0, Math.ceil(remainingMs / 1000)));
    const iv = setInterval(() => {
      setSecs((s) => Math.max(0, s - 1));
    }, 1000);
    return () => clearInterval(iv);
  }, [remainingMs]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black opacity-40" />
      <div className="relative bg-white rounded-lg shadow-lg p-6 w-full max-w-md z-60">
        <h3 className="text-lg font-semibold mb-2">Sesión a punto de expirar</h3>
        <p className="text-sm text-gray-600 mb-4">Por inactividad, tu sesión se cerrará en <strong>{secs}</strong> segundos.</p>
        <div className="flex justify-end space-x-3">
          <button onClick={onLogout} className="px-3 py-2 bg-red-600 text-white rounded">Cerrar sesión ahora</button>
          <button onClick={onExtend} className="px-3 py-2 bg-green-600 text-white rounded">Mantener sesión</button>
        </div>
      </div>
    </div>
  );
}
