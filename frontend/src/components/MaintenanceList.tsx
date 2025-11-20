import React from 'react';

const MaintenanceList: React.FC = () => {
  const openMaintenanceFormInNewWindow = (maintenanceId?: number) => {
    const url = maintenanceId 
      ? `/maintenance-form?id=${maintenanceId}` 
      : '/maintenance-form';
    
    const windowFeatures = 'width=1200,height=800,scrollbars=yes,resizable=yes';
    window.open(url, '_blank', windowFeatures);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Mantenimientos</h1>
        <button
          onClick={() => openMaintenanceFormInNewWindow()}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          🗗 Nuevo Mantenimiento (Nueva Ventana)
        </button>
      </div>
      
      {/* Lista de mantenimientos */}
      <div className="grid gap-4">
        {/* Ejemplo de edición */}
        <button 
          onClick={() => openMaintenanceFormInNewWindow(123)}
          className="text-blue-600 hover:text-blue-800"
        >
          Editar en Nueva Ventana
        </button>
      </div>
    </div>
  );
};

export default MaintenanceList;