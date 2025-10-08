import { useRef, useEffect, useState } from 'react';
import { useChatStore } from '../store/chat';

/**
 * 自动滚动到底部（除非用户向上滚动）
 */
export function useAutoScroll<T extends HTMLElement>() {
  const containerRef = useRef<T>(null);
  const isStreaming = useChatStore(state => state.isStreaming);
  const [showScrollButton, setShowScrollButton] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;

      setShowScrollButton(!isNearBottom);
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // 流式渲染时自动滚动
  useEffect(() => {
    if (isStreaming && !showScrollButton) {
      const container = containerRef.current;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }, [isStreaming, showScrollButton]);

  const scrollToBottom = () => {
    const container = containerRef.current;
    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth',
      });
      setShowScrollButton(false);
    }
  };

  return { containerRef, scrollToBottom, showScrollButton };
}
