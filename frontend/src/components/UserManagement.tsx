import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  groups: string[];
}

interface Role {
  id: number;
  name: string;
  user_count?: number;
}

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    confirm_password: '',
    is_active: true,
    is_staff: false,
  });

  const [roleForm, setRoleForm] = useState({
    name: '',
  });

  useEffect(() => {
    fetchUsers();
    fetchRoles();
  }, []);

  const getAuthConfig = () => {
    const token = localStorage.getItem('token');
    return {
      headers: { Authorization: `Bearer ${token}` }
    };
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/`,
        getAuthConfig()
      );
      setUsers(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching users:', error);
      setLoading(false);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/roles/`,
        getAuthConfig()
      );
      setRoles(response.data);
    } catch (error) {
      console.error('Error fetching roles:', error);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (userForm.password !== userForm.confirm_password) {
      alert('Las contraseñas no coinciden');
      return;
    }

    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/`,
        userForm,
        getAuthConfig()
      );
      alert('Usuario creado exitosamente');
      setShowUserModal(false);
      resetUserForm();
      fetchUsers();
    } catch (error: any) {
      alert('Error creando usuario: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!editingUser) return;

    try {
      await axios.patch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/${editingUser.id}/`,
        {
          email: userForm.email,
          first_name: userForm.first_name,
          last_name: userForm.last_name,
          is_active: userForm.is_active,
          is_staff: userForm.is_staff,
        },
        getAuthConfig()
      );
      alert('Usuario actualizado exitosamente');
      setShowUserModal(false);
      setEditingUser(null);
      resetUserForm();
      fetchUsers();
    } catch (error: any) {
      alert('Error actualizando usuario: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('¿Está seguro de eliminar este usuario?')) return;

    try {
      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/${userId}/`,
        getAuthConfig()
      );
      alert('Usuario eliminado exitosamente');
      fetchUsers();
    } catch (error: any) {
      alert('Error eliminando usuario: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleChangePassword = async (userId: number) => {
    const newPassword = prompt('Nueva contraseña:');
    if (!newPassword) return;
    
    const confirmPassword = prompt('Confirmar contraseña:');
    if (!confirmPassword) return;

    if (newPassword !== confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }

    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/${userId}/change_password/`,
        { new_password: newPassword, confirm_password: confirmPassword },
        getAuthConfig()
      );
      alert('Contraseña cambiada exitosamente');
    } catch (error: any) {
      alert('Error cambiando contraseña: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleAssignRole = async (userId: number, roleName: string) => {
    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/${userId}/assign_role/`,
        { role: roleName },
        getAuthConfig()
      );
      alert('Rol asignado exitosamente');
      fetchUsers();
    } catch (error: any) {
      alert('Error asignando rol: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleRemoveRole = async (userId: number, roleName: string) => {
    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/${userId}/remove_role/`,
        { role: roleName },
        getAuthConfig()
      );
      alert('Rol removido exitosamente');
      fetchUsers();
    } catch (error: any) {
      alert('Error removiendo rol: ' + (error.response?.data?.error || error.message));
    }
  };

  const handleCreateRole = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/user-management/users/create_role/`,
        roleForm,
        getAuthConfig()
      );
      alert('Rol creado exitosamente');
      setShowRoleModal(false);
      setRoleForm({ name: '' });
      fetchRoles();
    } catch (error: any) {
      alert('Error creando rol: ' + (error.response?.data?.error || error.message));
    }
  };

  const openEditModal = (user: User) => {
    setEditingUser(user);
    setUserForm({
      username: user.username,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      password: '',
      confirm_password: '',
      is_active: user.is_active,
      is_staff: user.is_staff,
    });
    setShowUserModal(true);
  };

  const resetUserForm = () => {
    setUserForm({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      confirm_password: '',
      is_active: true,
      is_staff: false,
    });
  };

  if (loading) {
    return <div className="p-6">Cargando usuarios...</div>;
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Gestión de Usuarios</h1>
        <div className="space-x-2">
          <button
            onClick={() => { setEditingUser(null); resetUserForm(); setShowUserModal(true); }}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            + Crear Usuario
          </button>
          <button
            onClick={() => setShowRoleModal(true)}
            className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition"
          >
            + Crear Rol
          </button>
        </div>
      </div>

      {/* Roles disponibles */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <h2 className="text-lg font-semibold mb-3">Roles Disponibles</h2>
        <div className="flex flex-wrap gap-2">
          {roles.map((role) => (
            <span
              key={role.id}
              className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
            >
              {role.name} ({role.user_count || 0} usuarios)
            </span>
          ))}
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Usuario</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Nombre</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Roles</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Estado</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {users.map((user) => (
              <tr key={user.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap font-medium">{user.username}</td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">{user.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                  {`${user.first_name} ${user.last_name}`.trim() || '-'}
                </td>
                <td className="px-6 py-4">
                  <div className="flex flex-wrap gap-1">
                    {user.groups.map((group, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded cursor-pointer hover:bg-blue-200"
                        onClick={() => handleRemoveRole(user.id, group)}
                        title="Click para remover"
                      >
                        {group} ×
                      </span>
                    ))}
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          handleAssignRole(user.id, e.target.value);
                          e.target.value = '';
                        }
                      }}
                      className="text-xs border rounded px-2 py-1 bg-white"
                    >
                      <option value="">+ Asignar rol</option>
                      {roles.filter(r => !user.groups.includes(r.name)).map((role) => (
                        <option key={role.id} value={role.name}>{role.name}</option>
                      ))}
                    </select>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-3 py-1 text-xs rounded-full font-medium ${
                    user.is_active 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                  <button
                    onClick={() => openEditModal(user)}
                    className="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Editar
                  </button>
                  <button
                    onClick={() => handleChangePassword(user.id)}
                    className="text-yellow-600 hover:text-yellow-800 font-medium"
                  >
                    Cambiar Contraseña
                  </button>
                  <button
                    onClick={() => handleDeleteUser(user.id)}
                    className="text-red-600 hover:text-red-800 font-medium"
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* User Modal */}
      {showUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md shadow-xl">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">
              {editingUser ? 'Editar Usuario' : 'Crear Usuario'}
            </h2>
            <form onSubmit={editingUser ? handleUpdateUser : handleCreateUser}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre de usuario *
                  </label>
                  <input
                    type="text"
                    placeholder="Nombre de usuario"
                    value={userForm.username}
                    onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                    disabled={!!editingUser}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email *
                  </label>
                  <input
                    type="email"
                    placeholder="Email"
                    value={userForm.email}
                    onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre
                  </label>
                  <input
                    type="text"
                    placeholder="Nombre"
                    value={userForm.first_name}
                    onChange={(e) => setUserForm({ ...userForm, first_name: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Apellido
                  </label>
                  <input
                    type="text"
                    placeholder="Apellido"
                    value={userForm.last_name}
                    onChange={(e) => setUserForm({ ...userForm, last_name: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                {!editingUser && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Contraseña *
                      </label>
                      <input
                        type="password"
                        placeholder="Contraseña"
                        value={userForm.password}
                        onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Confirmar contraseña *
                      </label>
                      <input
                        type="password"
                        placeholder="Confirmar contraseña"
                        value={userForm.confirm_password}
                        onChange={(e) => setUserForm({ ...userForm, confirm_password: e.target.value })}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                  </>
                )}
                <div className="flex items-center space-x-6">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={userForm.is_active}
                      onChange={(e) => setUserForm({ ...userForm, is_active: e.target.checked })}
                      className="mr-2 w-4 h-4"
                    />
                    <span className="text-sm font-medium text-gray-700">Activo</span>
                  </label>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={userForm.is_staff}
                      onChange={(e) => setUserForm({ ...userForm, is_staff: e.target.checked })}
                      className="mr-2 w-4 h-4"
                    />
                    <span className="text-sm font-medium text-gray-700">Staff</span>
                  </label>
                </div>
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => { setShowUserModal(false); setEditingUser(null); resetUserForm(); }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  {editingUser ? 'Actualizar' : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Role Modal */}
      {showRoleModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md shadow-xl">
            <h2 className="text-2xl font-bold mb-4 text-gray-800">Crear Rol</h2>
            <form onSubmit={handleCreateRole}>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre del rol *
                </label>
                <input
                  type="text"
                  placeholder="Nombre del rol"
                  value={roleForm.name}
                  onChange={(e) => setRoleForm({ name: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  required
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => { setShowRoleModal(false); setRoleForm({ name: '' }); }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-100 transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
                  Crear
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;