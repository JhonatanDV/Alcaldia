import type { Metadata } from "next";
// Import Sidebar directly (it's a client component)
import Sidebar from '@/components/Sidebar';
import SidebarToggle from '@/components/SidebarToggle';
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

// Sidebar is a client component (uses "use client"); import directly.

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Sistema de Mantenimiento",
  description: "Sistema de gestión de mantenimientos de equipos",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
            <div className="flex min-h-screen">
              {/* Sidebar is a client component; it handles its own mobile toggle */}
              <Sidebar />
              {/* Global toggle button (client) to open/close sidebar on small screens */}
              <SidebarToggle />
              <main className="flex-1 w-full overflow-x-hidden pt-16 sm:pt-0">{children}</main>
            </div>
      </body>
    </html>
  );
}
