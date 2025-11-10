import React from 'react';
import { useChatStore } from '../store/chat';
import { useAuthStore } from '../store/auth';
import { useHealthCheck } from '../hooks/useHealthCheck';
import { Menu, Settings, Sun, Moon, Library, LogOut } from 'lucide-react';

export function TopBar() {
  const {
    currentSessionId,
    sessions,
    toggleSidebar,
    toggleSettingsDrawer,
    toggleKnowledgeDrawer,
  } = useChatStore();
  const user = useAuthStore(state => state.user);
  const logout = useAuthStore(state => state.logout);
  const healthy = useHealthCheck();
  const [darkMode, setDarkMode] = React.useState(false);

  const currentSession = sessions.find(s => s.id === currentSessionId);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className="h-14 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex items-center justify-between px-4">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-700 dark:text-gray-300"
          title="切换侧边栏"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            CxyGPT
          </h1>

          <div
            className={`w-2 h-2 rounded-full ${
              healthy === null
                ? 'bg-gray-400'
                : healthy
                  ? 'bg-green-500 animate-pulse'
                  : 'bg-red-500'
            }`}
            title={healthy === null ? '检查中...' : healthy ? '服务正常' : '服务异常'}
          />
        </div>

        {currentSession && (
          <span className="text-sm text-gray-600 dark:text-gray-400 ml-2">
            {currentSession.name}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        {user && (
          <div className="hidden md:flex flex-col text-right mr-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-200">{user.username}</span>
            <span className="text-xs text-gray-500 dark:text-gray-400">{user.email}</span>
          </div>
        )}

        <button
          onClick={toggleDarkMode}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-700 dark:text-gray-300"
          title="切换主题"
        >
          {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

        <button
          onClick={toggleKnowledgeDrawer}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-700 dark:text-gray-300"
          title="知识库管理"
        >
          <Library className="w-5 h-5" />
        </button>

        <button
          onClick={toggleSettingsDrawer}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-700 dark:text-gray-300"
          title="设置"
        >
          <Settings className="w-5 h-5" />
        </button>

        <button
          onClick={logout}
          className="p-2 hover:bg-red-50 dark:hover:bg-red-900/40 rounded-lg transition-colors text-red-600 dark:text-red-400"
          title="退出登录"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

export default TopBar;
