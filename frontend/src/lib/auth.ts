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
      window.location.href = '/';
    }
  };

  // Axios response interceptor: if any request returns 401 -> try refresh, otherwise logout
  const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? '').replace(/\/$/, '');

  let isRefreshing = false;
  let refreshPromise: Promise<string | null> | null = null;

  const doRefreshToken = async (): Promise<string | null> => {
    const refresh = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
    if (!refresh) return null;
    try {
      const res = await axios.post(`${API_URL}/api/token/refresh/`, { refresh });
      const newAccess = res.data.access || res.data.token || null;
      if (newAccess) {
        localStorage.setItem('access_token', newAccess);
        return newAccess;
      }
    } catch (e) {
      // ignore and return null -> caller will logout
    }
    return null;
  };

  const interceptorId = axios.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error?.config;
      const status = error?.response?.status;

      // If no response or not 401, forward
      if (status !== 401 || !originalRequest) {
        return Promise.reject(error);
      }

      // Prevent trying to refresh repeatedly for refresh endpoint itself
      if (originalRequest.url && originalRequest.url.includes('/api/token/refresh')) {
        logout();
        return Promise.reject(error);
      }

      try {
        if (!isRefreshing) {
          isRefreshing = true;
          refreshPromise = doRefreshToken();
        }

        const newAccess = await (refreshPromise || Promise.resolve(null));

        // finished refresh attempt
        isRefreshing = false;
        refreshPromise = null;

        if (newAccess) {
          // set header on original request and retry
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
          return axios(originalRequest);
        }
      } catch (e) {
        // fallthrough to logout
      }

      // If refresh didn't work, logout
      logout();
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
