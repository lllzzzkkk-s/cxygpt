import { useEffect } from 'react';
import { useChatStore } from './store/chat';
import { useAuthStore } from './store/auth';
import { useLimits } from './hooks/useLimits';
import TopBar from './components/TopBar';
import Sidebar from './components/Sidebar';
import ChatPane from './components/ChatPane';
import SettingsDrawer from './components/SettingsDrawer';
import KnowledgeDrawer from './components/KnowledgeDrawer';
import Login from './components/Login';
import { Loader2 } from 'lucide-react';
import './index.css';

function App() {
  const accessToken = useAuthStore(state => state.accessToken);
  const user = useAuthStore(state => state.user);
  const refreshProfile = useAuthStore(state => state.refreshProfile);
  const authLoading = useAuthStore(state => state.loading);

  const { limits } = useLimits(!!user);
  const setLimits = useChatStore(state => state.setLimits);
  const sessions = useChatStore(state => state.sessions);
  const createSession = useChatStore(state => state.createSession);

  useEffect(() => {
    if (accessToken && !user) {
      void refreshProfile();
    }
  }, [accessToken, user, refreshProfile]);

  // 加载限额信息
  useEffect(() => {
    if (limits) {
      setLimits(limits);
    }
  }, [limits, setLimits]);

  // 确保至少有一个会话
  useEffect(() => {
    if (!user) return;
    if (sessions.length === 0) {
      createSession();
    }
  }, [sessions.length, createSession, user]);

  if (!accessToken || !user) {
    if (accessToken && authLoading) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-950">
          <div className="flex items-center gap-3 text-gray-600 dark:text-gray-300">
            <Loader2 className="w-5 h-5 animate-spin" />
            正在加载用户信息...
          </div>
        </div>
      );
    }

    return <Login />;
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-950">
      <TopBar />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <ChatPane />
        <SettingsDrawer />
        <KnowledgeDrawer />
      </div>
    </div>
  );
}

export default App;
