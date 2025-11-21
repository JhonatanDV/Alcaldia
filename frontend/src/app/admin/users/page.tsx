'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Group {
  id: number;
  name: string;
  user_count: number;
}

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  groups: Group[];
}

export default function UsersAdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>(null);

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    is_active: true,
    is_staff: false,
    is_superuser: false,
    group_ids: [] as number[],
  });

  const [passwordData, setPasswordData] = useState({
    password: '',
    confirmPassword: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    window.location.href = '/';
  };

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;
      
      if (!token) {
        window.location.href = '/';
        return;
      }

      setUserRole(role);

      if (!token) {
        setError('No está autenticado');
        return;
      }

      const headers = { Authorization: `Bearer ${token}` };

      const [usersRes, groupsRes] = await Promise.all([
        axios.get(`${API_URL}/api/admin/users/`, { headers }),
        axios.get(`${API_URL}/api/admin/groups/`, { headers }),
      ]);

      setUsers(usersRes.data);
      setGroups(groupsRes.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching data:', err);
      setError(err.response?.data?.detail || 'Error al cargar datos');
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.post(`${API_URL}/api/admin/users/`, formData, { headers });

      setShowCreateModal(false);
      resetForm();
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al crear usuario');
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingUser) return;

    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      const updateData: any = { ...formData };
      if (!updateData.password) {
        delete updateData.password;
      }

      await axios.put(`${API_URL}/api/admin/users/${editingUser.id}/`, updateData, { headers });

      setEditingUser(null);
      resetForm();
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al actualizar usuario');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUserId) return;

    if (passwordData.password !== passwordData.confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }

    if (passwordData.password.length < 8) {
      alert('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.post(
        `${API_URL}/api/admin/users/${selectedUserId}/change_password/`,
        { password: passwordData.password },
        { headers }
      );

      setShowPasswordModal(false);
      setPasswordData({ password: '', confirmPassword: '' });
      setSelectedUserId(null);
      alert('Contraseña actualizada exitosamente');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al cambiar contraseña');
    }
  };

  const handleToggleActive = async (userId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.post(`${API_URL}/api/admin/users/${userId}/toggle_active/`, {}, { headers });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al cambiar estado');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('¿Está seguro de eliminar este usuario?')) return;

    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      await axios.delete(`${API_URL}/api/admin/users/${userId}/`, { headers });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error al eliminar usuario');
    }
  };

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      is_active: true,
      is_staff: false,
      is_superuser: false,
      group_ids: [],
    });
  };

  const openEditModal = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      password: '',
      is_active: user.is_active,
      is_staff: user.is_staff,
      is_superuser: user.is_superuser,
      group_ids: user.groups.map((g) => g.id),
    });
  };

  if (loading) {
    return <div className="p-8">Cargando...</div>;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <h1 className="text-2xl font-bold text-gray-900">Gestión de Usuarios</h1>
            </div>
          </div>
        </header>
        <div className="p-8">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header Navigation */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">
                Sistema de Mantenimiento
              </h1>
              {userRole && (
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  userRole === 'admin'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-blue-100 text-blue-800'
                }`}>
                  {userRole === 'admin' ? 'Admin' : 'Técnico'}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="/dashboard"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
              >
                Dashboard
              </a>
              <a
                href="/equipment/new"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
              >
                <svg
                  className="mr-2 h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Nuevo Equipo
              </a>
              <a
                href="/maintenance/new"
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700"
              >
                <svg
                  className="mr-2 h-4 w-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 4v16m8-8H4"
                  />
                </svg>
                Nuevo Mantenimiento
              </a>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Gestión de Usuarios</h2>
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Crear Usuario
          </button>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Usuario
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Nombre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Grupos
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {user.username}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.first_name} {user.last_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.groups.map((g) => g.name).join(', ') || 'Sin grupos'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {user.is_active ? (
                      <span className="px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded-full">
                        Activo
                      </span>
                    ) : (
                      <span className="px-2 py-1 text-xs font-semibold text-red-800 bg-red-100 rounded-full">
                        Inactivo
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => openEditModal(user)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => {
                        setSelectedUserId(user.id);
                        setShowPasswordModal(true);
                      }}
                      className="text-yellow-600 hover:text-yellow-900 mr-3"
                    >
                      Cambiar Contraseña
                    </button>
                    <button
                      onClick={() => handleToggleActive(user.id)}
                      className="text-purple-600 hover:text-purple-900 mr-3"
                    >
                      {user.is_active ? 'Desactivar' : 'Activar'}
                    </button>
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Create User Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
            <div className="bg-white rounded-lg p-8 max-w-md w-full max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold mb-4">Crear Usuario</h2>
              <form onSubmit={handleCreateUser}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Usuario</label>
                  <input
                    type="text"
                    required
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Contraseña</label>
                  <input
                    type="password"
                    required
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Nombre</label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Apellido</label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Grupos</label>
                  <select
                    multiple
                    value={formData.group_ids.map(String)}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        group_ids: Array.from(e.target.selectedOptions, (option) =>
                          Number(option.value)
                        ),
                      })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  >
                    {groups.map((group) => (
                      <option key={group.id} value={group.id}>
                        {group.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mb-4 space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Activo</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_staff}
                      onChange={(e) => setFormData({ ...formData, is_staff: e.target.checked })}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Staff</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_superuser}
                      onChange={(e) =>
                        setFormData({ ...formData, is_superuser: e.target.checked })
                      }
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Superusuario</span>
                  </label>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateModal(false);
                      resetForm();
                    }}
                    className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600"
                  >
                    Crear
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Edit User Modal */}
        {editingUser && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
            <div className="bg-white rounded-lg p-8 max-w-md w-full max-h-[90vh] overflow-y-auto">
              <h2 className="text-2xl font-bold mb-4">Editar Usuario</h2>
              <form onSubmit={handleUpdateUser}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Usuario</label>
                  <input
                    type="text"
                    required
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Nombre</label>
                  <input
                    type="text"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Apellido</label>
                  <input
                    type="text"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">Grupos</label>
                  <select
                    multiple
                    value={formData.group_ids.map(String)}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        group_ids: Array.from(e.target.selectedOptions, (option) =>
                          Number(option.value)
                        ),
                      })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  >
                    {groups.map((group) => (
                      <option key={group.id} value={group.id}>
                        {group.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="mb-4 space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Activo</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_staff}
                      onChange={(e) => setFormData({ ...formData, is_staff: e.target.checked })}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Staff</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.is_superuser}
                      onChange={(e) =>
                        setFormData({ ...formData, is_superuser: e.target.checked })
                      }
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Superusuario</span>
                  </label>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setEditingUser(null);
                      resetForm();
                    }}
                    className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600"
                  >
                    Actualizar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Change Password Modal */}
        {showPasswordModal && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold mb-4">Cambiar Contraseña</h2>
              <form onSubmit={handleChangePassword}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Nueva Contraseña
                  </label>
                  <input
                    type="password"
                    required
                    value={passwordData.password}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, password: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700">
                    Confirmar Contraseña
                  </label>
                  <input
                    type="password"
                    required
                    value={passwordData.confirmPassword}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, confirmPassword: e.target.value })
                    }
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border"
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowPasswordModal(false);
                      setPasswordData({ password: '', confirmPassword: '' });
                      setSelectedUserId(null);
                    }}
                    className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600"
                  >
                    Cambiar
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
