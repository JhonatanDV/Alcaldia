"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import LoginForm from "@/components/LoginForm";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // If user has a token, redirect to dashboard
    const storedToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    if (storedToken) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <LoginForm 
      onLogin={(newToken) => {
        localStorage.setItem('access_token', newToken);
        router.push('/dashboard');
      }} 
      onRoleSet={(role) => {
        localStorage.setItem('user_role', role || '');
        localStorage.setItem('role', role || '');
      }} 
    />
  );
}
