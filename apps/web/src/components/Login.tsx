import React, { useState } from 'react';
import { Loader2, LogIn } from 'lucide-react';

import { useAuthStore } from '../store/auth';

export function Login(): React.ReactElement {
  const login = useAuthStore(state => state.login);
  const loading = useAuthStore(state => state.loading);
  const error = useAuthStore(state => state.error);
  const clearError = useAuthStore(state => state.clearError);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await login(username.trim(), password);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 to-slate-200 dark:from-gray-950 dark:to-gray-900 px-4">
      <div className="w-full max-w-md bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-3 mb-6">
          <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-white">
            <LogIn className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">创新院大模型应用平台</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">请输入账号信息以继续使用</p>
          </div>
        </div>

        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="username">
              用户名
            </label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={username}
              onChange={event => {
                if (error) clearError();
                setUsername(event.target.value);
              }}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1" htmlFor="password">
              密码
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={password}
              onChange={event => {
                if (error) clearError();
                setPassword(event.target.value);
              }}
              required
            />
          </div>

          {error && (
            <div className="px-3 py-2 rounded-lg bg-red-50 text-red-600 text-sm dark:bg-red-500/10 dark:text-red-200">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 transition-colors text-white font-medium disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
            {loading ? '正在登录...' : '登录'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
