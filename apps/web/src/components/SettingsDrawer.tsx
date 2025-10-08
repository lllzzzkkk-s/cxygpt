import React from 'react';
import { useChatStore } from '../store/chat';
import { X } from 'lucide-react';

const SYSTEM_PROMPT_TEMPLATES = [
  { label: '默认', value: '' },
  { label: '简洁回答', value: '请用简洁的语言回答问题，避免冗长。' },
  { label: '结构化 JSON', value: '请以 JSON 格式返回结构化数据。' },
  { label: '代码优先', value: '尽可能用代码示例回答，附带必要的注释。' },
  { label: '教学模式', value: '请用通俗易懂的方式解释，适合初学者理解。' },
];

export function SettingsDrawer() {
  const { settingsDrawerOpen, toggleSettingsDrawer, settings, updateSettings, limits } =
    useChatStore();

  if (!settingsDrawerOpen) return null;

  const handleTemplateChange = (template: string) => {
    updateSettings({ systemPrompt: template });
  };

  return (
    <>
      {/* 遮罩层 */}
      <div className="fixed inset-0 bg-black/50 z-40" onClick={toggleSettingsDrawer} />

      {/* 抽屉 */}
      <div className="fixed right-0 top-0 bottom-0 w-96 bg-white dark:bg-gray-900 shadow-2xl z-50 flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">设置</h2>
          <button
            onClick={toggleSettingsDrawer}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-700 dark:text-gray-300"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
          {/* 当前档位 */}
          {limits && (
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-sm font-semibold mb-2 text-gray-900 dark:text-gray-100">
                当前档位
              </div>
              <div className="text-xs space-y-1 text-gray-600 dark:text-gray-300">
                <div>模式：{limits.single_user ? '单人模式' : '多人模式'}</div>
                <div>档位：{limits.profile}</div>
                <div>输入限制：{limits.max_input_tokens} tokens</div>
                <div>输出限制：{limits.max_output_tokens} tokens</div>
                {limits.rate_qps > 0 && <div>QPS 限制：{limits.rate_qps}</div>}
                {limits.rate_tpm > 0 && <div>TPM 限制：{limits.rate_tpm}</div>}
              </div>
            </div>
          )}

          {/* Temperature */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Temperature：{settings.temperature.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.05"
              value={settings.temperature}
              onChange={e => updateSettings({ temperature: parseFloat(e.target.value) })}
              className="w-full"
            />
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              控制输出的随机性（0=确定性，2=高随机）
            </div>
          </div>

          {/* Top P */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Top P：{settings.top_p.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.top_p}
              onChange={e => updateSettings({ top_p: parseFloat(e.target.value) })}
              className="w-full"
            />
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">核采样概率阈值</div>
          </div>

          {/* Max Tokens */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              Max Tokens：{settings.max_tokens}
            </label>
            <input
              type="range"
              min="64"
              max={limits?.max_output_tokens || 512}
              step="32"
              value={settings.max_tokens}
              onChange={e => updateSettings({ max_tokens: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              最大输出 token 数（上限：{limits?.max_output_tokens || 512}）
            </div>
          </div>

          {/* 系统提示 */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-900 dark:text-gray-100">
              系统提示模板
            </label>
            <div className="flex flex-wrap gap-2 mb-3">
              {SYSTEM_PROMPT_TEMPLATES.map(t => (
                <button
                  key={t.label}
                  onClick={() => handleTemplateChange(t.value)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                    settings.systemPrompt === t.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <textarea
              value={settings.systemPrompt}
              onChange={e => updateSettings({ systemPrompt: e.target.value })}
              placeholder="自定义系统提示..."
              rows={4}
              className="w-full px-3 py-2 bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none placeholder:text-gray-500 dark:placeholder:text-gray-400"
            />
          </div>

          {/* 长文分析开关 */}
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">长文分析</div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                启用更长的上下文窗口（多人模式降级时禁用）
              </div>
            </div>
            <label className="relative inline-block w-12 h-6">
              <input
                type="checkbox"
                checked={settings.enableLongDoc}
                onChange={e => updateSettings({ enableLongDoc: e.target.checked })}
                className="sr-only peer"
                disabled={!limits?.single_user}
              />
              <span className="absolute inset-0 bg-gray-300 dark:bg-gray-600 rounded-full transition-colors peer-checked:bg-blue-600 peer-disabled:opacity-50 peer-disabled:cursor-not-allowed"></span>
              <span className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-6"></span>
            </label>
          </div>
        </div>

        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={() => {
              updateSettings({
                temperature: 0.7,
                top_p: 0.9,
                max_tokens: 512,
                systemPrompt: '',
                enableLongDoc: true,
              });
            }}
            className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors text-sm font-medium text-gray-900 dark:text-gray-100"
          >
            恢复默认设置
          </button>
        </div>
      </div>
    </>
  );
}

export default SettingsDrawer;
