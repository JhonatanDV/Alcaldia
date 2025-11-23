"use client";

import { useState } from "react";
import axios from "axios";

interface LoginFormProps {
  onLogin: (token: string) => void;
  onRoleSet: (role: 'admin' | 'technician') => void;
}

export default function LoginForm({ onLogin, onRoleSet }: LoginFormProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://127.0.0.1:8000/api/token/", {
        username,
        password,
      });

      // Debug: Log FULL response first
      console.log('=== LOGIN RESPONSE DEBUG ===');
      console.log('Full response:', response);
      console.log('Response data:', response.data);
      console.log('Response data keys:', Object.keys(response.data));
      
      const { access, refresh, role } = response.data;

      // Debug: Log role information
      console.log('Access token:', access ? 'EXISTS' : 'MISSING');
      console.log('Refresh token:', refresh ? 'EXISTS' : 'MISSING');
      console.log('User role received:', role);
      console.log('Role type:', typeof role);
      console.log('Role is undefined?', role === undefined);

      // Save tokens to localStorage
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);
      localStorage.setItem('user_role', role);
      localStorage.setItem('username', username); // Save username too

      // Verify saved role
      console.log('Role saved to localStorage:', localStorage.getItem('user_role'));
      console.log('Username saved to localStorage:', localStorage.getItem('username'));

      onLogin(access);
      onRoleSet(role);

      // Redirect to dashboard
      window.location.href = '/dashboard';
    } catch (err) {
      setError("Credenciales inválidas");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6 sm:space-y-8">
        <div>
          <h2 className="mt-4 sm:mt-6 text-center text-2xl sm:text-3xl font-extrabold text-gray-900">
            Iniciar Sesión
          </h2>
          <p className="mt-2 text-center text-xs sm:text-sm text-gray-600">
            Sistema de Mantenimiento de Equipos
          </p>
        </div>
        <form className="mt-6 sm:mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">
                Usuario
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Usuario"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Contraseña
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? "Iniciando..." : "Iniciar Sesión"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
