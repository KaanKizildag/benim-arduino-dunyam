/**
 * Centralized API client and Server-Sent Events (SSE) stream handler.
 */

import type { SavedProjectEntry, AILogEntry, ProjeTasarimi } from '../types/project';

export interface SSEStageEvent {
  type: 'stage';
  stageIndex: number;
  stageName: string;
  totalStages: number;
}

export interface SSEIncrementalEvent {
  type: 'incremental';
  partialProject: ProjeTasarimi;
}

export interface SSECompletedEvent {
  type: 'completed';
  project: ProjeTasarimi;
  notes?: string[];
  durationMs?: number;
}

export interface SSEErrorEvent {
  type: 'error';
  message: string;
}

export type SSEEvent = SSEStageEvent | SSEIncrementalEvent | SSECompletedEvent | SSEErrorEvent;

/**
 * Robust SSE reader that handles chunked streams and yields parsed events.
 */
export async function streamSSE(
  url: string,
  body: unknown,
  onEvent: (event: any) => void,
  signal?: AbortSignal
): Promise<void> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    signal,
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let detail = `Sunucudan yanıt alınamadı (HTTP ${res.status})`;
    try {
      const errBody = await res.json();
      if (errBody?.detail) detail = errBody.detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }

  if (!res.body) {
    throw new Error('Tarayıcı stream okuyucusunu desteklemiyor.');
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      for (const part of parts) {
        const lines = part.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onEvent(data);
            } catch {
              // ignore malformed JSON chunk
            }
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

export const api = {
  async getModels(geminiApiKey?: string, ollamaUrl?: string) {
    const params = new URLSearchParams();
    if (geminiApiKey) params.set('gemini_api_key', geminiApiKey);
    if (ollamaUrl) params.set('ollama_url', ollamaUrl);
    const qs = params.toString() ? `?${params.toString()}` : '';
    const res = await fetch(`/api/models${qs}`);
    if (!res.ok) throw new Error(`Modeller alınamadı: HTTP ${res.status}`);
    return res.json();
  },

  async getPorts(): Promise<string[]> {
    const res = await fetch('/api/ports');
    if (!res.ok) throw new Error(`Portlar alınamadı: HTTP ${res.status}`);
    const data = await res.json();
    return data.ports || [];
  },

  async getSavedProjects(): Promise<SavedProjectEntry[]> {
    const res = await fetch('/api/projects');
    if (!res.ok) throw new Error(`Projeler alınamadı: HTTP ${res.status}`);
    return res.json();
  },

  async saveProject(payload: {
    id?: string;
    prompt?: string;
    badge?: string;
    project: ProjeTasarimi;
  }): Promise<SavedProjectEntry> {
    const res = await fetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Proje kaydedilemedi: HTTP ${res.status}`);
    return res.json();
  },

  async deleteProject(id: string): Promise<boolean> {
    const res = await fetch(`/api/projects/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`Proje silinemedi: HTTP ${res.status}`);
    return true;
  },

  async getAILogs(): Promise<AILogEntry[]> {
    const res = await fetch('/api/ai-logs');
    if (!res.ok) throw new Error(`Loglar alınamadı: HTTP ${res.status}`);
    return res.json();
  },

  async clearAILogs(): Promise<boolean> {
    const res = await fetch('/api/ai-logs', { method: 'DELETE' });
    if (!res.ok) throw new Error(`Loglar temizlenemedi: HTTP ${res.status}`);
    return true;
  },

  async uploadCode(code: string, port?: string): Promise<{ success: boolean; message: string }> {
    const res = await fetch('/api/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, port }),
    });
    return res.json();
  },

  generateStream(
    payload: { prompt: string; inventory: string[]; model: string; api_key?: string },
    onEvent: (event: SSEEvent) => void,
    signal?: AbortSignal
  ) {
    return streamSSE('/api/generate-stream', payload, onEvent, signal);
  },

  reviseStream(
    payload: {
      current_project: ProjeTasarimi;
      revision_prompt: string;
      inventory: string[];
      model: string;
      api_key?: string;
    },
    onEvent: (event: SSEEvent) => void,
    signal?: AbortSignal
  ) {
    return streamSSE('/api/revise-stream', payload, onEvent, signal);
  },
};
