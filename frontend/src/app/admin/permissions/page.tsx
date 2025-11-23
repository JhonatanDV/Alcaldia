'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import Layout from '../../../components/Layout';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Permission {
  id: number;
  name: string;
  codename: string;
  content_type: number;
}

interface Role {
  id: number;
  name: string;
  permissions: Permission[];
}

interface ModelPermissions {
  model: string;
  label: string;
  permissions: {
    view: Permission | null;
    add: Permission | null;
    change: Permission | null;
    delete: Permission | null;
  };
}

export default function PermissionsPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [modelPermissions, setModelPermissions] = useState<ModelPermissions[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState<'admin' | 'technician' | null>('admin');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('user_role') as 'admin' | 'technician' | null;

    if (!token || role !== 'admin') {
      window.location.href = '/';
      return;
    }

    setUserRole(role);
    setIsAuthenticated(true);
    fetchRoles();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    window.location.href = '/';
  };

  const fetchRoles = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get(`${API_URL}/api/user-management/roles/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setRoles(response.data);
      if (response.data.length > 0) {
        setSelectedRole(response.data[0]);
        fetchPermissions(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching roles:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPermissions = async (roleId: number) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      
      // Obtener todos los permisos disponibles
      const permissionsResponse = await axios.get(`${API_URL}/api/permissions/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Obtener permisos del rol seleccionado
      const roleResponse = await axios.get(`${API_URL}/api/user-management/roles/${roleId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const allPermissions: Permission[] = permissionsResponse.data;
      const rolePermissions: number[] = roleResponse.data.permissions || [];

      // Organizar permisos por modelo
      const models = [
        { model: 'equipment', label: 'Equipos' },
        { model: 'maintenance', label: 'Mantenimientos' },
        { model: 'incident', label: 'Incidentes' },
        { model: 'report', label: 'Reportes' },
        { model: 'sede', label: 'Sedes' },
        { model: 'dependencia', label: 'Dependencias' },
        { model: 'subdependencia', label: 'Subdependencias' },
        { model: 'user', label: 'Usuarios' },
      ];

      const organized: ModelPermissions[] = models.map(({ model, label }) => {
        const modelPerms = allPermissions.filter((p) => p.codename.includes(model));
        
        return {
          model,
          label,
          permissions: {
            view: modelPerms.find((p) => p.codename.startsWith('view_')) || null,
            add: modelPerms.find((p) => p.codename.startsWith('add_')) || null,
            change: modelPerms.find((p) => p.codename.startsWith('change_')) || null,
            delete: modelPerms.find((p) => p.codename.startsWith('delete_')) || null,
          },
        };
      });

      setModelPermissions(organized);
      
      // Actualizar el rol seleccionado con sus permisos
      setSelectedRole({
        ...roleResponse.data,
        permissions: allPermissions.filter((p) => rolePermissions.includes(p.id)),
      });
    } catch (error) {
      console.error('Error fetching permissions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleChange = (roleId: number) => {
    const role = roles.find((r) => r.id === roleId);
    if (role) {
      setSelectedRole(role);
      fetchPermissions(roleId);
    }
  };

  const hasPermission = (permission: Permission | null): boolean => {
    if (!permission || !selectedRole) return false;
    return selectedRole.permissions.some((p) => p.id === permission.id);
  };

  const togglePermission = async (permission: Permission | null, currentValue: boolean) => {
    if (!permission || !selectedRole) return;

    setSaving(true);
    try {
      const token = localStorage.getItem('access_token');
      const updatedPermissions = currentValue
        ? selectedRole.permissions.filter((p) => p.id !== permission.id)
        : [...selectedRole.permissions, permission];

      await axios.patch(
        `${API_URL}/api/user-management/roles/${selectedRole.id}/`,
        {
          permissions: updatedPermissions.map((p) => p.id),
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      setSelectedRole({
        ...selectedRole,
        permissions: updatedPermissions,
      });
    } catch (error) {
      console.error('Error updating permissions:', error);
      alert('Error al actualizar permisos');
    } finally {
      setSaving(false);
    }
  };

  if (!isAuthenticated || loading) {
    return (
      <Layout userRole={userRole} onLogout={handleLogout}>
        <div className="bg-white rounded-lg shadow-sm p-8">
          <p className="text-gray-600">Cargando permisos...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout userRole={userRole} onLogout={handleLogout}>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Gestión de Permisos por Rol
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Configura los permisos para cada rol
          </p>
        </div>

        {/* Role Selector */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Seleccionar Rol
          </label>
          <select
            value={selectedRole?.id || ''}
            onChange={(e) => handleRoleChange(Number(e.target.value))}
            className="w-full md:w-1/3 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </select>
        </div>

        {/* Permissions Table */}
        {selectedRole && (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Permisos para: {selectedRole.name}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Marca las casillas para otorgar permisos específicos a este rol
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Módulo
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ver
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Crear
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Editar
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Eliminar
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {modelPermissions.map((modelPerm) => (
                    <tr key={modelPerm.model} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {modelPerm.label}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <input
                          type="checkbox"
                          checked={hasPermission(modelPerm.permissions.view)}
                          onChange={() =>
                            togglePermission(
                              modelPerm.permissions.view,
                              hasPermission(modelPerm.permissions.view)
                            )
                          }
                          disabled={saving || !modelPerm.permissions.view}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <input
                          type="checkbox"
                          checked={hasPermission(modelPerm.permissions.add)}
                          onChange={() =>
                            togglePermission(
                              modelPerm.permissions.add,
                              hasPermission(modelPerm.permissions.add)
                            )
                          }
                          disabled={saving || !modelPerm.permissions.add}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <input
                          type="checkbox"
                          checked={hasPermission(modelPerm.permissions.change)}
                          onChange={() =>
                            togglePermission(
                              modelPerm.permissions.change,
                              hasPermission(modelPerm.permissions.change)
                            )
                          }
                          disabled={saving || !modelPerm.permissions.change}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-center">
                        <input
                          type="checkbox"
                          checked={hasPermission(modelPerm.permissions.delete)}
                          onChange={() =>
                            togglePermission(
                              modelPerm.permissions.delete,
                              hasPermission(modelPerm.permissions.delete)
                            )
                          }
                          disabled={saving || !modelPerm.permissions.delete}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {saving && (
              <div className="px-6 py-3 bg-blue-50 border-t border-blue-200 text-sm text-blue-700">
                Guardando cambios...
              </div>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
}
