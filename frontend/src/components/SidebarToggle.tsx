"use client";


export default function SidebarToggle() {
  const handleToggle = () => {
    if (typeof window !== 'undefined') {
      // Dispatch a custom event that Sidebar listens to
      window.dispatchEvent(new CustomEvent('sidebar:toggle'));
    }
  };

  return (
    <button
      onClick={handleToggle}
      className="fixed top-4 left-4 z-50 p-2 rounded-md bg-blue-700 text-white shadow-lg hover:bg-blue-800 transition-colors"
      aria-label="Abrir menú"
      title="Abrir menú"
    >
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>
  );
}
