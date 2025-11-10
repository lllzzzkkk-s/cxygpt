import React from 'react';
import { X, Upload, RefreshCw, Loader2, Database, Trash2, Sparkles, FileText } from 'lucide-react';
import { useChatStore } from '../store/chat';
import { useKnowledgeDocuments } from '../hooks/useKnowledgeDocuments';
import type { KnowledgeDocument } from '../types';

function formatBytes(size: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = size;
  let index = 0;

  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }

  return `${value % 1 === 0 ? value : value.toFixed(1)} ${units[index]}`;
}

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) return '-';
  return date.toLocaleString('zh-CN', {
    hour12: false,
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getStatusPill(status: KnowledgeDocument['status']): { label: string; className: string } {
  switch (status) {
    case 'ready':
      return { label: '已就绪', className: 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-300' };
    case 'embedding':
      return { label: '向量生成中', className: 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-300' };
    case 'uploaded':
      return { label: '待处理', className: 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300' };
    case 'error':
    default:
      return { label: '出错', className: 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300' };
  }
}

export function KnowledgeDrawer(): React.ReactElement | null {
  const {
    knowledgeDrawerOpen,
    toggleKnowledgeDrawer,
  } = useChatStore();

  const {
    documents,
    loading,
    uploading,
    refreshing,
    error,
    embeddingIds,
    deletingIds,
    refresh,
    uploadDocuments,
    triggerEmbedding,
    removeDocument,
  } = useKnowledgeDocuments(knowledgeDrawerOpen);

  const fileInputRef = React.useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = React.useState(false);

  const handleSelectFiles = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    void uploadDocuments(Array.from(files));
    // Reset input to allow selecting the same file twice
    event.target.value = '';
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const files = Array.from(event.dataTransfer.files ?? []);
    if (files.length === 0) return;
    void uploadDocuments(files);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
    if (!isDragging) {
      setIsDragging(true);
    }
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (event.currentTarget.contains(event.relatedTarget as Node)) return;
    setIsDragging(false);
  };

  const closeDrawer = () => {
    setIsDragging(false);
    toggleKnowledgeDrawer();
  };

  if (!knowledgeDrawerOpen) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/50 z-40" onClick={closeDrawer} />

      <div className="fixed right-0 top-0 bottom-0 w-[32rem] bg-white dark:bg-gray-900 shadow-2xl z-50 flex flex-col">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">知识库管理</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              上传文件并生成向量，为后续 RAG 问答提供素材。
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                void refresh();
              }}
              disabled={refreshing}
              className="p-2 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
              title="刷新列表"
            >
              {refreshing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            </button>

            <button
              onClick={closeDrawer}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors text-gray-700 dark:text-gray-300"
              title="关闭"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          onChange={handleSelectFiles}
        />

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
          <section>
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <Upload className="w-4 h-4" /> 上传文档
            </h3>
            <div
              className={`mt-3 border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                isDragging
                  ? 'border-blue-500 bg-blue-50/60 dark:bg-blue-500/10'
                  : 'border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800'
              }`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <div className="flex flex-col items-center gap-3 text-gray-600 dark:text-gray-300">
                {uploading ? (
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                ) : (
                  <Database className="w-8 h-8 text-blue-500" />
                )}
                <div className="text-sm">
                  拖拽文件到此处，或
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="mx-1 text-blue-600 hover:text-blue-700 font-medium"
                  >
                    点击上传
                  </button>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  支持 PDF、Markdown、TXT、DOCX 等常见文本格式，单个文件建议不超过 10MB。
                </p>
              </div>
            </div>
          </section>

          {error && (
            <div className="p-3 rounded-lg bg-red-50 text-red-600 text-sm dark:bg-red-500/10 dark:text-red-200">
              {error}
            </div>
          )}

          <section>
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 flex items-center gap-2">
                <FileText className="w-4 h-4" /> 文档列表
              </h3>
              {documents.length > 0 && (
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  共 {documents.length} 个文档
                </span>
              )}
            </div>

            <div className="mt-3 space-y-3">
              {loading ? (
                <div className="flex items-center justify-center py-10 text-gray-500 dark:text-gray-400">
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  正在加载文档...
                </div>
              ) : documents.length === 0 ? (
                <div className="rounded-xl border border-dashed border-gray-300 dark:border-gray-700 p-8 text-center text-gray-500 dark:text-gray-400 text-sm">
                  暂无文档，请先上传。
                </div>
              ) : (
                documents.map(document => {
                  const { label, className } = getStatusPill(document.status);
                  const isEmbedding = embeddingIds.has(document.id) || document.status === 'embedding';
                  const isDeleting = deletingIds.has(document.id);

                  return (
                    <div
                      key={document.id}
                      className="border border-gray-200 dark:border-gray-700 rounded-xl p-4 bg-white dark:bg-gray-900/80 shadow-sm"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                              {document.display_name ?? document.filename}
                            </h4>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium ${className}`}>
                              {isEmbedding && <Loader2 className="w-3 h-3 animate-spin mr-1" />}
                              {label}
                            </span>
                          </div>

                          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
                            <span>大小：{formatBytes(document.size_bytes)}</span>
                            <span>更新时间：{formatTimestamp(document.updated_at)}</span>
                            {document.chunk_count !== undefined && (
                              <span>分片：{document.chunk_count}</span>
                            )}
                            {document.embedding_model && (
                              <span>模型：{document.embedding_model}</span>
                            )}
                          </div>

                          {document.error_message && (
                            <div className="mt-2 text-xs text-red-500 dark:text-red-300">
                              {document.error_message}
                            </div>
                          )}
                        </div>

                        <div className="flex flex-col gap-2">
                          <button
                            onClick={() => {
                              void triggerEmbedding(document.id);
                            }}
                            disabled={isEmbedding}
                            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-blue-200 text-blue-600 hover:bg-blue-50 dark:border-blue-500/40 dark:text-blue-300 dark:hover:bg-blue-500/10 disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            {isEmbedding ? (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                              <Sparkles className="w-3 h-3" />
                            )}
                            生成向量
                          </button>
                          <button
                            onClick={() => {
                              if (confirm('确定删除该文档及其向量数据？')) {
                                void removeDocument(document.id);
                              }
                            }}
                            disabled={isDeleting}
                            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-red-200 text-red-600 hover:bg-red-50 dark:border-red-500/40 dark:text-red-300 dark:hover:bg-red-500/10 disabled:opacity-60 disabled:cursor-not-allowed"
                          >
                            {isDeleting ? <Loader2 className="w-3 h-3 animate-spin" /> : <Trash2 className="w-3 h-3" />}
                            删除
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </section>
        </div>
      </div>
    </>
  );
}

export default KnowledgeDrawer;
