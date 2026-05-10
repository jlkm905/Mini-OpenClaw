'use client';

import { useState, useCallback, useEffect } from 'react';
import { Save, FolderOpen, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { getFile, saveFile } from '@/lib/api';
import DynamicMonaco from './DynamicMonaco';

const PRESET_FILES = [
  'MEMORY.md',
  'workspace/SOUL.md',
  'workspace/IDENTITY.md',
  'workspace/USER.md',
  'workspace/AGENTS.md',
  'SKILLS_SNAPSHOT.md',
  'skills/get_weather/SKILL.md',
];

interface InspectorProps {
  initialFile?: string | null;
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export default function Inspector({ initialFile }: InspectorProps) {
  const [selectedPreset, setSelectedPreset] = useState(initialFile ?? PRESET_FILES[0]);
  const [customPath, setCustomPath] = useState('');
  const [content, setContent] = useState('');
  const [loadedPath, setLoadedPath] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');

  const activePath = customPath.trim() || selectedPreset;

  const loadFile = useCallback(async (path: string) => {
    setIsLoading(true);
    setLoadError(null);
    setSaveStatus('idle');
    try {
      const result = await getFile(path);
      setContent(result.content);
      setLoadedPath(result.path);
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load file');
      setContent('');
      setLoadedPath(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialFile) {
      loadFile(initialFile);
    }
  }, [initialFile, loadFile]);

  const handlePresetChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedPreset(e.target.value);
    setCustomPath('');
  };

  const handleLoad = () => {
    if (activePath) loadFile(activePath);
  };

  const handleSave = async () => {
    if (!loadedPath) return;
    setSaveStatus('saving');
    try {
      await saveFile(loadedPath, content);
      setSaveStatus('saved');
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    }
  };

  return (
    <aside className="w-[380px] flex-shrink-0 glass-panel border-l border-gray-200/60 flex flex-col overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200/40">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-4 h-4 text-gray-500" />
          <span className="text-xs font-semibold text-gray-700">File Inspector</span>
        </div>
        <button
          onClick={handleSave}
          disabled={!loadedPath || saveStatus === 'saving'}
          className={cn(
            'flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-lg transition-colors',
            !loadedPath || saveStatus === 'saving'
              ? 'text-gray-400 bg-gray-50 cursor-not-allowed'
              : saveStatus === 'saved'
              ? 'text-green-600 bg-green-50'
              : saveStatus === 'error'
              ? 'text-red-600 bg-red-50'
              : 'text-white bg-accent hover:bg-accent-light',
          )}
        >
          {saveStatus === 'saving' && <Loader2 className="w-3 h-3 animate-spin" />}
          {saveStatus === 'saved' && <CheckCircle className="w-3 h-3" />}
          {saveStatus === 'error' && <AlertCircle className="w-3 h-3" />}
          {saveStatus === 'idle' && <Save className="w-3 h-3" />}
          {saveStatus === 'saving' ? 'Saving…' : saveStatus === 'saved' ? 'Saved!' : saveStatus === 'error' ? 'Error' : 'Save'}
        </button>
      </div>

      <div className="px-4 py-3 space-y-2 border-b border-gray-200/40">
        <div className="flex gap-2">
          <select
            value={selectedPreset}
            onChange={handlePresetChange}
            className="flex-1 text-xs bg-white/80 border border-gray-200 rounded-lg px-2.5 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent/50"
          >
            {PRESET_FILES.map((f) => (
              <option key={f} value={f}>
                {f}
              </option>
            ))}
          </select>
          <button
            onClick={handleLoad}
            className="text-xs font-medium text-white bg-accent hover:bg-accent-light px-3 py-1.5 rounded-lg transition-colors"
          >
            Load
          </button>
        </div>

        <input
          type="text"
          value={customPath}
          onChange={(e) => setCustomPath(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleLoad()}
          placeholder="Custom path (e.g. workspace/notes.md)"
          className="w-full text-xs bg-white/80 border border-gray-200 rounded-lg px-2.5 py-1.5 text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent/50"
        />

        {loadedPath && (
          <div className="flex items-center gap-1.5 text-[10px] text-gray-500">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 flex-shrink-0" />
            <span className="font-mono truncate">{loadedPath}</span>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-hidden relative">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white/60 z-10">
            <Loader2 className="w-6 h-6 text-accent animate-spin" />
          </div>
        )}

        {loadError && (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
            <AlertCircle className="w-8 h-8 text-red-400 mb-2" />
            <p className="text-sm text-red-600 font-medium">Failed to load file</p>
            <p className="text-xs text-gray-500 mt-1">{loadError}</p>
          </div>
        )}

        {!isLoading && !loadError && !loadedPath && (
          <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
            <FolderOpen className="w-10 h-10 text-gray-300 mb-3" />
            <p className="text-sm text-gray-500">Select a file and click Load</p>
          </div>
        )}

        {!isLoading && !loadError && loadedPath && (
          <DynamicMonaco
            height="100%"
            language={loadedPath.endsWith('.md') ? 'markdown' : loadedPath.endsWith('.json') ? 'json' : loadedPath.endsWith('.py') ? 'python' : 'plaintext'}
            value={content}
            onChange={(value) => setContent(value ?? '')}
            theme="light"
            options={{
              minimap: { enabled: false },
              wordWrap: 'on',
              fontSize: 12,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              padding: { top: 12, bottom: 12 },
              fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
              renderLineHighlight: 'line',
              smoothScrolling: true,
            }}
          />
        )}
      </div>
    </aside>
  );
}
