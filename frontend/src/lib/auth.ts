"use client";

import axios from 'axios';

type Cleanup = () => void;

export function initAuth(onLogout?: () => void, onWarn?: (show: boolean, remainingMs: number, extend: () => void) => void): Cleanup {
  // Logout handler used by both interceptor and inactivity timer
  const logout = () => {
    try {
      if (onLogout) {
        onLogout();
        return;
      }
    } catch (e) {
      // fall through to default
    }

    // Default client-side logout
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_role');
      localStorage.removeItem('username');
      localStorage.removeItem('role');
      window.location.href = '/';
    }
  };

  // Axios response interceptor: if any request returns 401 -> logout
  const interceptorId = axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error?.response?.status === 401) {
        logout();
      }
      return Promise.reject(error);
    }
  );

  // Inactivity auto-logout with pre-warning
  const timeoutMinutes = parseInt(process.env.NEXT_PUBLIC_IDLE_TIMEOUT_MIN || '30', 10);
  const warnBeforeMinutes = parseInt(process.env.NEXT_PUBLIC_IDLE_WARN_MIN || '1', 10);
  const timeoutMs = Math.max(1, timeoutMinutes) * 60 * 1000;
  const warnMs = Math.max(0, warnBeforeMinutes) * 60 * 1000;

  let warnTimer: number | undefined;
  let logoutTimer: number | undefined;

  const clearTimers = () => {
    if (warnTimer) {
      window.clearTimeout(warnTimer);
      warnTimer = undefined;
    }
    if (logoutTimer) {
      window.clearTimeout(logoutTimer);
      logoutTimer = undefined;
    }
  };

  const extendSession = () => {
    // Called when user chooses to stay signed in from the warning
    clearTimers();
    scheduleTimers();
    // Hide warning immediately
    if (onWarn) onWarn(false, 0, extendSession);
  };

  const scheduleTimers = () => {
    clearTimers();
    // Schedule logout
    logoutTimer = window.setTimeout(() => {
      // ensure any visible warning is hidden
      if (onWarn) onWarn(false, 0, extendSession);
      logout();
    }, timeoutMs);

    // Schedule warning earlier, if configured
    if (warnMs > 0 && warnMs < timeoutMs) {
      const whenWarn = timeoutMs - warnMs;
      warnTimer = window.setTimeout(() => {
        if (onWarn) onWarn(true, warnMs, extendSession);
      }, whenWarn);
    }
  };

  const resetActivity = () => {
    // Called on user activity. Hide warning and reschedule timers.
    if (onWarn) onWarn(false, 0, extendSession);
    scheduleTimers();
  };

  const events = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'click'];
  events.forEach((ev) => window.addEventListener(ev, resetActivity, true));

  // Start timers
  scheduleTimers();

  // Cleanup function
  return () => {
    axios.interceptors.response.eject(interceptorId);
    clearTimers();
    events.forEach((ev) => window.removeEventListener(ev, resetActivity, true));
  };
}

export default initAuth;
