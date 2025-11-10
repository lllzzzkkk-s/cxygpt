import { useCallback, useEffect, useMemo, useState } from 'react';
import type { KnowledgeDocument } from '../types';
import { knowledgeClient } from '../lib/knowledge';
import { APIError } from '../lib/openai';

function mergeDocuments(list: KnowledgeDocument[], incoming: KnowledgeDocument): KnowledgeDocument[] {
  const index = list.findIndex(doc => doc.id === incoming.id);
  if (index === -1) {
    return [...list, incoming].sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
  }

  const copy = [...list];
  copy[index] = incoming;
  return copy.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
}

function formatError(error: unknown): string {
  if (error instanceof APIError) {
    return error.getUserMessage();
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return '操作失败，请稍后重试。';
}

export interface KnowledgeDocumentsState {
  documents: KnowledgeDocument[];
  loading: boolean;
  uploading: boolean;
  refreshing: boolean;
  error: string | null;
  embeddingIds: Set<string>;
  deletingIds: Set<string>;
  refresh: () => Promise<void>;
  uploadDocuments: (files: File[]) => Promise<void>;
  triggerEmbedding: (documentId: string, embeddingModel?: string) => Promise<void>;
  removeDocument: (documentId: string) => Promise<void>;
}

export function useKnowledgeDocuments(enabled: boolean): KnowledgeDocumentsState {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [embeddingIds, setEmbeddingIds] = useState<Set<string>>(new Set());
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());

  const refresh = useCallback(async () => {
    if (!enabled) return;
    setRefreshing(true);
    setError(null);

    try {
      const docs = await knowledgeClient.listDocuments();
      docs.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime());
      setDocuments(docs);
    } catch (err) {
      setError(formatError(err));
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  }, [enabled]);

  useEffect(() => {
    if (!enabled) return;
    setLoading(true);
    void refresh();
  }, [enabled, refresh]);

  const markEmbedding = useCallback((documentId: string, active: boolean) => {
    setEmbeddingIds(prev => {
      const next = new Set(prev);
      if (active) {
        next.add(documentId);
      } else {
        next.delete(documentId);
      }
      return next;
    });
  }, []);

  const markDeleting = useCallback((documentId: string, active: boolean) => {
    setDeletingIds(prev => {
      const next = new Set(prev);
      if (active) {
        next.add(documentId);
      } else {
        next.delete(documentId);
      }
      return next;
    });
  }, []);

  const uploadDocuments = useCallback(
    async (files: File[]): Promise<void> => {
      if (!files.length) return;
      setUploading(true);
      setError(null);

      try {
        for (const file of files) {
          const document = await knowledgeClient.uploadDocument(file);
          setDocuments(prev => mergeDocuments(prev, document));
        }
      } catch (err) {
        setError(formatError(err));
      } finally {
        setUploading(false);
        void refresh();
      }
    },
    [refresh]
  );

  const triggerEmbedding = useCallback(
    async (documentId: string, embeddingModel?: string): Promise<void> => {
      markEmbedding(documentId, true);
      setError(null);

      try {
        const document = await knowledgeClient.requestEmbedding(documentId, embeddingModel);
        setDocuments(prev => mergeDocuments(prev, document));
      } catch (err) {
        setError(formatError(err));
      } finally {
        markEmbedding(documentId, false);
        void refresh();
      }
    },
    [markEmbedding, refresh]
  );

  const removeDocument = useCallback(
    async (documentId: string): Promise<void> => {
      markDeleting(documentId, true);
      setError(null);

      try {
        await knowledgeClient.deleteDocument(documentId);
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
      } catch (err) {
        setError(formatError(err));
      } finally {
        markDeleting(documentId, false);
        void refresh();
      }
    },
    [markDeleting, refresh]
  );

  const stableEmbeddingIds = useMemo(() => embeddingIds, [embeddingIds]);
  const stableDeletingIds = useMemo(() => deletingIds, [deletingIds]);

  return {
    documents,
    loading,
    uploading,
    refreshing,
    error,
    embeddingIds: stableEmbeddingIds,
    deletingIds: stableDeletingIds,
    refresh,
    uploadDocuments,
    triggerEmbedding,
    removeDocument,
  };
}
