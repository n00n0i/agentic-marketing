"use client";

import { useState, useEffect } from "react";

interface Settings {
  // Ollama (LLM)
  ollama_base_url: string;
  ollama_api_key: string;
  ollama_model: string;
  // OpenAI (Embeddings fallback)
  openai_api_key: string;
  // Qdrant
  qdrant_url: string;
  // Database
  database_url: string;
  // App
  app_name: string;
  app_version: string;
}

const DEFAULT_SETTINGS: Settings = {
  ollama_base_url: "https://ollama.com",
  ollama_api_key: "",
  ollama_model: "gemma4:31b",
  openai_api_key: "",
  qdrant_url: "http://qdrant:6333",
  database_url: "postgresql://agentic:***@db:5432/agentic",
  app_name: "Agentic Marketing",
  app_version: "1.0.0",
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS);
  const [saved, setSaved] = useState(false);
  const [activeTab, setActiveTab] = useState<"ollama" | "embeddings" | "qdrant" | "db">("ollama");

  // Load settings from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem("agentic_settings");
    if (stored) {
      try {
        setSettings(JSON.parse(stored));
      } catch {}
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem("agentic_settings", JSON.stringify(settings));
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
    localStorage.removeItem("agentic_settings");
  };

  const tabs = [
    { id: "ollama" as const, label: "🦙 Ollama (LLM)", desc: "Base URL, API Key, Model" },
    { id: "embeddings" as const, label: "📊 Embeddings", desc: "OpenAI API Key for vector search" },
    { id: "qdrant" as const, label: "🔍 Qdrant", desc: "Vector database connection" },
    { id: "db" as const, label: "🗄️ Database", desc: "PostgreSQL connection" },
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gray-900">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">Settings</h1>
            <p className="text-gray-400 text-sm mt-0.5">Configure your AI pipeline services</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500">v{settings.app_version}</span>
            {saved && (
              <span className="text-xs text-green-400 bg-green-900/30 px-3 py-1 rounded-full">
                ✓ Saved
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-1 mb-8 bg-gray-900 p-1 rounded-xl w-fit">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Ollama */}
        {activeTab === "ollama" && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-1">Ollama Configuration</h2>
              <p className="text-gray-400 text-sm mb-6">
                Configure the Ollama API for LLM-powered content generation.
                Supports Ollama Cloud and self-hosted instances.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">
                    Base URL
                  </label>
                  <input
                    type="url"
                    value={settings.ollama_base_url}
                    onChange={(e) => setSettings({ ...settings, ollama_base_url: e.target.value })}
                    placeholder="https://ollama.com"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    For Ollama Cloud: <code className="text-blue-400">https://ollama.com</code>
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">
                    API Key
                  </label>
                  <input
                    type="password"
                    value={settings.ollama_api_key}
                    onChange={(e) => setSettings({ ...settings, ollama_api_key: e.target.value })}
                    placeholder="oll_..."
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Get your key from{" "}
                    <a href="https://ollama.com/settings" target="_blank" className="text-blue-400 hover:underline">
                      ollama.com/settings
                    </a>
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">
                    Model
                  </label>
                  <input
                    type="text"
                    value={settings.ollama_model}
                    onChange={(e) => setSettings({ ...settings, ollama_model: e.target.value })}
                    placeholder="gemma4:31b"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Available: gemma4:31b, kimi-k2:1t, deepseek-v3.2, qwen3-coder-next, glm-5
                  </p>
                </div>
              </div>
            </div>

            {/* Test Connection */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h3 className="text-sm font-medium text-gray-300 mb-3">Test Connection</h3>
              <TestOllamaButton baseUrl={settings.ollama_base_url} apiKey={settings.ollama_api_key} model={settings.ollama_model} />
            </div>
          </div>
        )}

        {/* Embeddings */}
        {activeTab === "embeddings" && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-1">Embeddings Configuration</h2>
              <p className="text-gray-400 text-sm mb-6">
                OpenAI API key for generating text embeddings (used for Qdrant vector search).
                Alternative: self-hosted Ollama with embedding model.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    value={settings.openai_api_key}
                    onChange={(e) => setSettings({ ...settings, openai_api_key: e.target.value })}
                    placeholder="sk-..."
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Used for: <code className="text-blue-400">text-embedding-3-small</code> (1536 dims)
                  </p>
                </div>

                <div className="bg-amber-900/20 border border-amber-700/30 rounded-lg p-4">
                  <p className="text-amber-300 text-sm font-medium mb-1">💡 Alternative: Ollama Embeddings</p>
                  <p className="text-gray-400 text-xs">
                    If you have a local Ollama instance with embedding support, you can use it instead.
                    Ollama Cloud does NOT support embeddings API — only OpenAI or local Ollama.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Qdrant */}
        {activeTab === "qdrant" && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-1">Qdrant Vector Database</h2>
              <p className="text-gray-400 text-sm mb-6">
                Qdrant stores embedded content for semantic search and retrieval.
                In Docker: <code className="text-blue-400">http://qdrant:6333</code> (internal network)
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">
                  Qdrant URL
                </label>
                <input
                  type="url"
                  value={settings.qdrant_url}
                  onChange={(e) => setSettings({ ...settings, qdrant_url: e.target.value })}
                  placeholder="http://qdrant:6333"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>

            <TestQdrantButton qdrantUrl={settings.qdrant_url} />
          </div>
        )}

        {/* Database */}
        {activeTab === "db" && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-1">PostgreSQL Database</h2>
              <p className="text-gray-400 text-sm mb-6">
                Primary data store for campaigns, pipeline executions, content variants, and analytics.
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">
                  Connection URL
                </label>
                <input
                  type="text"
                  value={settings.database_url}
                  onChange={(e) => setSettings({ ...settings, database_url: e.target.value })}
                  placeholder="postgresql://user:pass@host:5432/dbname"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  In Docker: <code className="text-blue-400">postgresql://agentic:***@db:5432/agentic</code>
                </p>
              </div>
            </div>

            <TestDbButton databaseUrl={settings.database_url} />
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-800">
          <button
            onClick={handleReset}
            className="px-4 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition"
          >
            Reset to Defaults
          </button>
          <button
            onClick={handleSave}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Test Buttons ─────────────────────────────────────────────────────────────

function TestOllamaButton({ baseUrl, apiKey, model }: { baseUrl: string; apiKey: string; model: string }) {
  const [status, setStatus] = useState<"idle" | "testing" | "ok" | "fail">("idle");
  const [msg, setMsg] = useState("");

  const test = async () => {
    setStatus("testing");
    setMsg("");
    try {
      const response = await fetch(`${baseUrl}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(apiKey ? { "Authorization": `Bearer ${apiKey}` } : {}),
        },
        body: JSON.stringify({
          model: model || "gemma4:31b",
          messages: [{ role: "user", content: "Hi" }],
          stream: false,
        }),
      });
      if (response.ok) {
        setStatus("ok");
        setMsg("✓ Connected to Ollama successfully!");
      } else {
        const err = await response.json().catch(() => ({}));
        setStatus("fail");
        setMsg(`✗ Error ${response.status}: ${err.error || response.statusText}`);
      }
    } catch (e: unknown) {
      setStatus("fail");
      setMsg(`✗ Connection failed: ${e instanceof Error ? e.message : String(e)}`);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={test}
        disabled={status === "testing"}
        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-white transition disabled:opacity-50"
      >
        {status === "testing" ? "Testing..." : "Test Ollama Connection"}
      </button>
      {msg && (
        <span className={`text-sm ${status === "ok" ? "text-green-400" : "text-red-400"}`}>
          {msg}
        </span>
      )}
    </div>
  );
}

function TestQdrantButton({ qdrantUrl }: { qdrantUrl: string }) {
  const [status, setStatus] = useState<"idle" | "testing" | "ok" | "fail">("idle");
  const [msg, setMsg] = useState("");

  const test = async () => {
    setStatus("testing");
    setMsg("");
    try {
      const url = qdrantUrl?.replace(/\/$/, "") || "http://localhost:6333";
      const response = await fetch(`${url}/collections`);
      if (response.ok) {
        const data = await response.json();
        const count = data.result?.collections?.length ?? 0;
        setStatus("ok");
        setMsg(`✓ Connected! ${count} collection(s)`);
      } else {
        setStatus("fail");
        setMsg(`✗ Error ${response.status}`);
      }
    } catch (e: unknown) {
      setStatus("fail");
      setMsg(`✗ Connection failed: ${e instanceof Error ? e.message : String(e)}`);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={test}
        disabled={status === "testing"}
        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-white transition disabled:opacity-50"
      >
        {status === "testing" ? "Testing..." : "Test Qdrant Connection"}
      </button>
      {msg && (
        <span className={`text-sm ${status === "ok" ? "text-green-400" : "text-red-400"}`}>
          {msg}
        </span>
      )}
    </div>
  );
}

function TestDbButton({ databaseUrl }: { databaseUrl: string }) {
  const [status, setStatus] = useState<"idle" | "testing" | "ok" | "fail">("idle");
  const [msg, setMsg] = useState("");

  const test = async () => {
    setStatus("testing");
    setMsg("Cannot test DB from browser — this runs server-side. Check backend logs.");
    setStatus("idle");
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={test}
        className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm text-white transition"
      >
        Test DB Connection
      </button>
      {msg && <span className="text-sm text-gray-400">{msg}</span>}
    </div>
  );
}