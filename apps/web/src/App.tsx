import { useEffect } from 'react';
import { useChatStore } from './store/chat';
import { useLimits } from './hooks/useLimits';
import TopBar from './components/TopBar';
import Sidebar from './components/Sidebar';
import ChatPane from './components/ChatPane';
import SettingsDrawer from './components/SettingsDrawer';
import './index.css';

function App() {
  const { limits } = useLimits();
  const { setLimits, sessions, createSession } = useChatStore();

  // 加载限额信息
  useEffect(() => {
    if (limits) {
      setLimits(limits);
    }
  }, [limits, setLimits]);

  // 确保至少有一个会话
  useEffect(() => {
    if (sessions.length === 0) {
      createSession();
    }
  }, [sessions.length, createSession]);

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-950">
      <TopBar />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar />
        <ChatPane />
        <SettingsDrawer />
      </div>
    </div>
  );
}

export default App;
