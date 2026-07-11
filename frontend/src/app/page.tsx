"use client";

import React, { useState, useEffect, useRef } from "react";

interface Strategy {
  id: number;
  name: string;
  description: string;
  content: string;
  is_active: boolean;
}

interface Analysis {
  id: number;
  timestamp: string;
  symbol: string;
  timeframe: string;
  signal: string;
  confidence: number;
  reasoning: string;
  invalidation: string;
  risk_notes: string;
  chart_data?: string;
}

interface ChatMessage {
  sender: "user" | "falcon";
  text: string;
  timestamp: Date;
}

export default function Dashboard() {
  const [symbols] = useState(["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]);
  const [timeframes] = useState(["1m", "5m", "15m", "30m", "1h", "4h", "1d"]);
  
  const [selectedSymbol, setSelectedSymbol] = useState("BTCUSDT");
  const [searchInput, setSearchInput] = useState("");
  const [selectedTimeframe, setSelectedTimeframe] = useState("4h");
  
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [activeStrategy, setActiveStrategy] = useState<Strategy | null>(null);
  const [newStratName, setNewStratName] = useState("");
  const [newStratDesc, setNewStratDesc] = useState("");
  const [newStratContent, setNewStratContent] = useState("");
  const [showAddStrat, setShowAddStrat] = useState(false);
  
  const [history, setHistory] = useState<Analysis[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [backendHealth, setBackendHealth] = useState<"online" | "offline">("offline");

  // Settings & preferences states
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [tempApiKey, setTempApiKey] = useState("");
  const [showSettings, setShowSettings] = useState(false);

  // News states
  const [news, setNews] = useState<any[]>([]);
  const [newsLoading, setNewsLoading] = useState(false);
  const [activeView, setActiveView] = useState<"dashboard" | "news">("dashboard");

  // Chat interface state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

  // Fetch initial data
  useEffect(() => {
    checkHealth();
    fetchStrategies();
    fetchHistory();
    fetchNews();
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      const res = await fetch(`${API_BASE}/preferences`);
      if (res.ok) {
        const data = await res.json();
        const apiKeyPref = data.find((p: any) => p.key === "gemini_api_key");
        if (apiKeyPref) {
          setGeminiApiKey(apiKeyPref.value);
          setTempApiKey(apiKeyPref.value);
        }
      }
    } catch (e) {
      console.error("Error fetching preferences:", e);
    }
  };

  const saveApiKey = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/preferences`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: "gemini_api_key", value: tempApiKey }),
      });
      if (res.ok) {
        setGeminiApiKey(tempApiKey);
        setShowSettings(false);
        alert("API Key saved successfully!");
        checkHealth();
      } else {
        alert("Failed to save API key.");
      }
    } catch (e) {
      console.error("Error saving API key:", e);
      alert("Error saving API key.");
    }
  };

  // Scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleSearchSymbol = () => {
    if (!searchInput.trim()) return;
    let normalized = searchInput.trim().toUpperCase();
    if (!normalized.endsWith("USDT")) {
      normalized = `${normalized}USDT`;
    }
    setSelectedSymbol(normalized);
    setSearchInput("");
  };

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        setBackendHealth("online");
      } else {
        setBackendHealth("offline");
      }
    } catch {
      setBackendHealth("offline");
    }
  };

  const fetchStrategies = async () => {
    try {
      const res = await fetch(`${API_BASE}/strategies`);
      if (res.ok) {
        const data = await res.json();
        setStrategies(data);
        const active = data.find((s: Strategy) => s.is_active);
        if (active) setActiveStrategy(active);
      }
    } catch (e) {
      console.error("Error fetching strategies:", e);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/analysis/history`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data);
        if (data.length > 0 && !currentAnalysis) {
          setCurrentAnalysis(data[0]);
          initializeChatWithAnalysis(data[0]);
        }
      }
    } catch (e) {
      console.error("Error fetching history:", e);
    }
  };

  const fetchNews = async () => {
    setNewsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/news`);
      if (res.ok) {
        const data = await res.json();
        setNews(data);
      }
    } catch (e) {
      console.error("Error fetching news:", e);
    } finally {
      setNewsLoading(false);
    }
  };

  const activateStrategy = async (id: number) => {
    try {
      const res = await fetch(`${API_BASE}/strategies/${id}/activate`, {
        method: "PUT",
      });
      if (res.ok) {
        fetchStrategies();
      }
    } catch (e) {
      console.error("Error activating strategy:", e);
    }
  };

  const handleCreateStrategy = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newStratName || !newStratContent) return;

    try {
      const res = await fetch(`${API_BASE}/strategies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newStratName,
          description: newStratDesc,
          content: newStratContent,
          is_active: true,
        }),
      });
      if (res.ok) {
        setNewStratName("");
        setNewStratDesc("");
        setNewStratContent("");
        setShowAddStrat(false);
        fetchStrategies();
      } else {
        const error = await res.json();
        alert(error.detail || "Failed to create strategy");
      }
    } catch (e) {
      console.error("Error creating strategy:", e);
    }
  };

  const triggerAnalysis = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/analysis/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: selectedSymbol,
          timeframe: selectedTimeframe,
          custom_strategy_id: activeStrategy?.id || null,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setCurrentAnalysis(data);
        fetchHistory();
        initializeChatWithAnalysis(data);
      } else {
        const error = await res.json();
        alert(error.detail || "Failed to run analysis");
      }
    } catch (e) {
      console.error("Error running analysis:", e);
      alert("Error: Backend is offline. Please make sure the FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  };

  const initializeChatWithAnalysis = (analysis: Analysis) => {
    setChatMessages([
      {
        sender: "falcon",
        text: `Falcon active analysis for **${analysis.symbol}** (${analysis.timeframe}) loaded.\n\nSignal is **${analysis.signal}** with a confidence of **${analysis.confidence}%**.\n\nAsk me any questions about the setup, invalidations, or the SMC structures identified!`,
        timestamp: new Date(),
      },
    ]);
  };

  const sendChatMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || chatLoading) return;

    const userText = inputMessage;
    const currentHistory = chatMessages.map(msg => ({
      sender: msg.sender,
      text: msg.text
    }));

    setChatMessages((prev) => [
      ...prev,
      { sender: "user", text: userText, timestamp: new Date() },
    ]);
    setInputMessage("");
    setChatLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userText,
          symbol: selectedSymbol,
          timeframe: selectedTimeframe,
          analysis_id: currentAnalysis?.id || null,
          history: currentHistory
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setChatMessages((prev) => [
          ...prev,
          { sender: "falcon", text: data.response, timestamp: new Date() },
        ]);
      } else {
        const error = await res.json();
        setChatMessages((prev) => [
          ...prev,
          { sender: "falcon", text: `Error: ${error.detail || "Failed to query AI assistant."}`, timestamp: new Date() },
        ]);
      }
    } catch (err) {
      console.error("Chat error:", err);
      setChatMessages((prev) => [
        ...prev,
        { sender: "falcon", text: "Error: Unable to connect to the backend server.", timestamp: new Date() },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const getSignalColor = (signal?: string) => {
    if (!signal) return "text-gray-400 border-gray-500/30 bg-gray-500/10";
    switch (signal.toUpperCase()) {
      case "BULLISH":
        return "text-[#10B981] border-[#10B981]/30 bg-[#10B981]/10 shadow-[0_0_15px_rgba(16,185,129,0.15)]";
      case "BEARISH":
        return "text-[#F43F5E] border-[#F43F5E]/30 bg-[#F43F5E]/10 shadow-[0_0_15px_rgba(244,63,94,0.15)]";
      default:
        return "text-[#F59E0B] border-[#F59E0B]/30 bg-[#F59E0B]/10 shadow-[0_0_15px_rgba(245,158,11,0.15)]";
    }
  };

  const getIntervalForTradingView = (tf: string) => {
    switch (tf) {
      case "1m": return "1";
      case "5m": return "5";
      case "15m": return "15";
      case "30m": return "30";
      case "1h": return "60";
      case "4h": return "240";
      case "1d": return "D";
      default: return "240";
    }
  };

  return (
    <div className="flex-1 bg-[#090A0F] text-[#E4E6EB] min-h-screen font-sans flex flex-col selection:bg-[#6366F1] selection:text-white">
      {/* Top Navigation */}
      <header className="border-b border-[#1E2235] bg-[#0E1017] px-6 py-4 flex items-center justify-between sticky top-0 z-50 backdrop-blur-md bg-opacity-85">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#6366F1] to-[#8B5CF6] flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              PROJECT FALCON
              <span className="text-[10px] bg-[#6366F1]/10 text-[#8B5CF6] border border-[#6366F1]/30 px-2 py-0.5 rounded font-mono">v2.0</span>
            </h1>
            <p className="text-xs text-gray-400">Personal AI Trading Assistant & Analyst</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 bg-[#141626]/80 border border-[#1E2235] rounded-xl p-1">
          <button
            onClick={() => setActiveView("dashboard")}
            className={`px-4 py-2 rounded-lg text-xs font-semibold tracking-wider uppercase transition-all flex items-center gap-1.5 ${
              activeView === "dashboard"
                ? "bg-[#6366F1] text-white shadow-md shadow-indigo-500/10"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2H6a2 2 0 01-2-2v-4zM14 16a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2v-4z" />
            </svg>
            Dashboard
          </button>
          <button
            onClick={() => setActiveView("news")}
            id="btn-news-feed"
            className={`px-4 py-2 rounded-lg text-xs font-semibold tracking-wider uppercase transition-all flex items-center gap-1.5 ${
              activeView === "news"
                ? "bg-[#6366F1] text-white shadow-md shadow-indigo-500/10"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1M19 20a2 2 0 002-2V8a2 2 0 00-2-2h-5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            News Feed
            {news.length > 0 && (
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
            )}
          </button>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-[#161924] border border-[#242736] px-3.5 py-1.5 rounded-lg text-sm">
            <span className={`w-2.5 h-2.5 rounded-full ${backendHealth === "online" ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`}></span>
            <span className="font-medium text-xs tracking-wider uppercase text-gray-300">
              {backendHealth === "online" ? "API ONLINE" : "API OFFLINE"}
            </span>
          </div>
          <button
            onClick={() => {
              setTempApiKey(geminiApiKey);
              setShowSettings(true);
            }}
            id="btn-settings"
            className="bg-[#1E2138]/60 border border-[#1E2235] hover:border-indigo-500 text-gray-300 hover:text-white p-2 rounded-xl transition-all cursor-pointer flex items-center justify-center"
            title="Settings"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className={`flex-1 p-6 ${activeView === "news" ? "flex flex-col" : "grid grid-cols-1 xl:grid-cols-4"} gap-6 max-w-[1800px] w-full mx-auto pb-16`}>
        
        {activeView === "news" ? (
          <section className="flex flex-col gap-6" id="news-feed-section">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-md font-bold text-white uppercase tracking-wider">Crypto News Feed</h2>
                <p className="text-xs text-gray-500 font-mono">Daily cryptocurrency updates, announcements and analysis</p>
              </div>
              <button
                onClick={fetchNews}
                disabled={newsLoading}
                id="btn-refresh-news"
                className="bg-[#1E2138]/60 border border-[#1E2235] hover:border-indigo-500 text-white text-xs px-4 py-2 rounded-xl transition-all font-semibold flex items-center gap-2"
              >
                {newsLoading ? (
                  <span className="w-3.5 h-3.5 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"></span>
                ) : (
                  <svg className="w-3.5 h-3.5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17" />
                  </svg>
                )}
                Refresh
              </button>
            </div>

            {newsLoading && news.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center py-20 gap-3">
                <span className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin"></span>
                <span className="text-xs text-gray-500 font-mono">Loading news articles...</span>
              </div>
            ) : news.length === 0 ? (
              <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-10 text-center text-gray-500">
                <svg className="w-12 h-12 text-gray-600 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1M19 20a2 2 0 002-2V8a2 2 0 00-2-2h-5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <p className="font-semibold text-sm text-white mb-1">No news articles found</p>
                <p className="text-xs text-gray-500 mb-4 font-mono">Failed to fetch RSS feed. Please check your network connection.</p>
                <button onClick={fetchNews} className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-4 py-2 rounded-xl transition-colors font-semibold">Try Again</button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 overflow-y-auto max-h-[calc(100vh-220px)] pb-12 pr-1" id="news-cards-container">
                {news.map((item, idx) => (
                  <div key={idx} className="bg-[#11131F]/90 border border-[#1E2235] hover:border-indigo-500/40 rounded-2xl overflow-hidden flex flex-col shadow-xl transition-all hover:translate-y-[-2px] group">
                    {/* Image Area */}
                    <div className="h-44 bg-[#0E1017] relative overflow-hidden border-b border-[#1E2235]">
                      {item.imageUrl ? (
                        <img 
                          src={item.imageUrl} 
                          alt={item.title} 
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-[#1E2138]/40 to-[#0F111E]">
                          <svg className="w-8 h-8 text-indigo-500/20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1M19 20a2 2 0 002-2V8a2 2 0 00-2-2h-5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                          </svg>
                        </div>
                      )}
                      <div className="absolute top-3 left-3 bg-[#6366F1]/90 text-white text-[9px] font-bold px-2 py-0.5 rounded uppercase tracking-wider font-mono">News</div>
                    </div>
                    {/* Content Area */}
                    <div className="p-4 flex flex-col gap-2 flex-1 justify-between">
                      <div className="flex flex-col gap-2">
                        <span className="text-[10px] text-gray-500 font-mono">{item.pubDate}</span>
                        <h3 className="text-xs font-bold text-white line-clamp-2 leading-snug group-hover:text-indigo-300 transition-colors">{item.title}</h3>
                        <p className="text-[11px] text-gray-400 line-clamp-3 leading-relaxed font-mono mt-1">{item.description}</p>
                      </div>
                      <a 
                        href={item.link} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="mt-4 border border-[#1E2235] hover:border-indigo-600 hover:bg-indigo-600/10 text-[#6366F1] hover:text-white text-[11px] font-semibold py-2 rounded-xl text-center transition-all flex items-center justify-center gap-1.5 font-mono"
                      >
                        Read Full Article
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        ) : (
          <>
            {/* LEFT COLUMN: Strategy Control Panel */}
            <section className="xl:col-span-1 flex flex-col gap-6" id="strategy-section">
          {/* Strategy Details Block */}
          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 flex flex-col gap-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h2 className="text-md font-semibold tracking-wide text-white flex items-center gap-2">
                <svg className="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Trading Strategy
              </h2>
              <button 
                onClick={() => setShowAddStrat(!showAddStrat)}
                id="btn-add-strategy"
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
              >
                {showAddStrat ? "Cancel" : "+ Custom"}
              </button>
            </div>

            {/* List Strategies */}
            {!showAddStrat ? (
              <div className="flex flex-col gap-2.5">
                {strategies.map((strat) => (
                  <button
                    key={strat.id}
                    onClick={() => activateStrategy(strat.id)}
                    className={`text-left p-3.5 rounded-xl border transition-all flex flex-col gap-1 ${
                      strat.is_active 
                        ? "bg-[#1E2138]/60 border-[#6366F1]/50 text-white" 
                        : "bg-[#141626]/40 border-[#1E2235] text-gray-400 hover:border-gray-700 hover:text-gray-200"
                    }`}
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="font-semibold text-sm">{strat.name}</span>
                      {strat.is_active && (
                        <span className="text-[10px] text-indigo-400 font-mono tracking-wider font-semibold uppercase">Active</span>
                      )}
                    </div>
                    <span className="text-xs text-gray-500 line-clamp-2 mt-1">{strat.description}</span>
                  </button>
                ))}
              </div>
            ) : (
              <form onSubmit={handleCreateStrategy} className="flex flex-col gap-3">
                <input
                  type="text"
                  placeholder="Strategy Name"
                  value={newStratName}
                  onChange={(e) => setNewStratName(e.target.value)}
                  className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-[#6366F1]"
                  required
                />
                <input
                  type="text"
                  placeholder="Short Description"
                  value={newStratDesc}
                  onChange={(e) => setNewStratDesc(e.target.value)}
                  className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-[#6366F1]"
                />
                <textarea
                  placeholder="Paste your markdown Strategy Rules..."
                  value={newStratContent}
                  onChange={(e) => setNewStratContent(e.target.value)}
                  className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-[#6366F1] h-32 font-mono"
                  required
                />
                <button
                  type="submit"
                  className="bg-[#6366F1] hover:bg-[#5053df] text-white py-2 rounded-xl text-sm font-semibold transition-colors shadow-lg shadow-indigo-500/10"
                >
                  Save & Activate
                </button>
              </form>
            )}

            {/* Active Strategy Rules Box */}
            {activeStrategy && (
              <div className="mt-2 border-t border-[#1E2235] pt-4">
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Active Strategy Rules</h3>
                <div className="bg-[#141626]/80 rounded-xl p-3 border border-[#1E2235] max-h-56 overflow-y-auto text-xs leading-relaxed text-gray-400 font-mono whitespace-pre-line">
                  {activeStrategy.content}
                </div>
              </div>
            )}
          </div>

          {/* Historical Logs Block */}
          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 flex flex-col gap-4 shadow-xl flex-1 max-h-[400px]">
            <h2 className="text-md font-semibold tracking-wide text-white flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Analysis History
            </h2>

            <div className="flex-1 overflow-y-auto flex flex-col gap-2 pr-1">
              {history.length === 0 ? (
                <p className="text-xs text-gray-500 text-center py-8">No analyses recorded yet.</p>
              ) : (
                history.map((h) => (
                  <button
                    key={h.id}
                    onClick={() => {
                      setCurrentAnalysis(h);
                      initializeChatWithAnalysis(h);
                    }}
                    className={`text-left p-3 rounded-xl border transition-all flex items-center justify-between ${
                      currentAnalysis?.id === h.id
                        ? "bg-[#1E2138]/40 border-[#6366F1]/40 text-white"
                        : "bg-[#141626]/20 border-transparent text-gray-400 hover:bg-[#141626]/50 hover:text-white"
                    }`}
                  >
                    <div className="flex flex-col gap-0.5">
                      <span className="font-semibold text-xs text-white">{h.symbol} <span className="text-gray-500 font-normal">({h.timeframe})</span></span>
                      <span className="text-[10px] text-gray-500">{new Date(h.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className={`px-2 py-0.5 rounded text-[10px] font-bold border ${h.signal === 'BULLISH' ? 'text-emerald-500 border-emerald-500/20 bg-emerald-500/5' : h.signal === 'BEARISH' ? 'text-rose-500 border-rose-500/20 bg-rose-500/5' : 'text-amber-500 border-amber-500/20 bg-amber-500/5'}`}>
                      {h.signal}
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </section>

        {/* CENTER COLUMN: Analysis Dashboard */}
        <section className="xl:col-span-2 flex flex-col gap-6" id="dashboard-section">
          {/* Controls Bar */}
          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
            <div className="flex flex-wrap items-center gap-4">
              {/* Symbol Selection */}
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Trading Pair</label>
                <div className="flex flex-wrap items-center bg-[#141626] border border-[#1E2235] rounded-xl p-1 gap-2">
                  {/* Quick Select Buttons */}
                  <div className="flex gap-1">
                    {symbols.map((sym) => (
                      <button
                        key={sym}
                        id={`symbol-${sym.toLowerCase()}`}
                        onClick={() => setSelectedSymbol(sym)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                          selectedSymbol === sym 
                            ? "bg-[#6366F1] text-white shadow-md shadow-indigo-500/10" 
                            : "text-gray-400 hover:text-gray-200"
                        }`}
                      >
                        {sym.replace("USDT", "")}
                      </button>
                    ))}
                  </div>

                  {/* Vertical Divider */}
                  <div className="h-5 w-[1px] bg-[#1E2235] mx-1"></div>

                  {/* Search Input Box */}
                  <div className="flex items-center gap-1 bg-[#090A0F]/60 border border-[#1E2235]/40 rounded-lg px-2 py-0.5">
                    <svg className="w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <input
                      type="text"
                      id="search-pair-input"
                      placeholder="Other e.g. XRP, DOGE..."
                      value={searchInput}
                      onChange={(e) => setSearchInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          handleSearchSymbol();
                        }
                      }}
                      className="bg-transparent text-xs text-[#E4E6EB] py-1 focus:outline-none w-28 placeholder-gray-600 font-semibold"
                    />
                    <button
                      onClick={handleSearchSymbol}
                      id="btn-search-pair"
                      type="button"
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-bold px-1.5 py-1"
                    >
                      Search
                    </button>
                  </div>
                </div>
              </div>

              {/* Timeframe Selection */}
              <div className="flex flex-col gap-1.5">
                <label className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Timeframe</label>
                <div className="flex bg-[#141626] border border-[#1E2235] rounded-xl p-1 gap-1">
                  {timeframes.map((tf) => (
                    <button
                      key={tf}
                      id={`tf-${tf}`}
                      onClick={() => setSelectedTimeframe(tf)}
                      className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        selectedTimeframe === tf
                          ? "bg-[#6366F1] text-white shadow-md shadow-indigo-500/10"
                          : "text-gray-400 hover:text-gray-200"
                      }`}
                    >
                      {tf}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Run Analysis Trigger Button */}
            <button
              onClick={triggerAnalysis}
              id="btn-trigger-analysis"
              disabled={loading}
              className={`bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] hover:from-[#5053df] hover:to-[#7c4ee5] text-white font-bold px-6 py-3 rounded-xl shadow-lg shadow-indigo-500/20 transition-all flex items-center justify-center gap-2 min-w-[180px] self-end md:self-center disabled:opacity-55`}
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Scanning...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Scan Market
                </>
              )}
            </button>
          </div>

          {/* TradingView Live Chart */}
          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-4 shadow-xl h-[450px] flex flex-col gap-2 relative">
            <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-widest font-mono px-1">TradingView Live Chart</span>
            <div className="flex-1 w-full rounded-xl overflow-hidden border border-[#1E2235]/60 bg-black/40">
              <iframe
                id="tradingview-chart-widget"
                src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview-chart-widget&symbol=BINANCE%3A${selectedSymbol}&interval=${getIntervalForTradingView(selectedTimeframe)}&theme=dark&style=1&timezone=Etc%2FUTC&hide_volume=true`}
                className="w-full h-full border-none"
                allowFullScreen
              />
            </div>
          </div>

          {/* TradingView RSI Chart */}
          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-4 shadow-xl h-[450px] flex flex-col gap-2 relative">
            <span className="text-[10px] font-semibold text-[#8B5CF6] uppercase tracking-widest font-mono px-1">Relative Strength Index (RSI)</span>
            <div className="flex-1 w-full rounded-xl overflow-hidden border border-[#1E2235]/60 bg-black/40">
              <iframe
                id="tradingview-rsi-widget"
                src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview-rsi-widget&symbol=BINANCE%3A${selectedSymbol}&interval=${getIntervalForTradingView(selectedTimeframe)}&theme=dark&style=2&timezone=Etc%2FUTC&studies=RSI%40tv-basicstudies&hide_volume=true`}
                className="w-full h-full border-none"
                allowFullScreen
              />
            </div>
          </div>

          {/* Analysis View Details */}
          {loading ? (
            <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-12 flex flex-col items-center justify-center gap-4 shadow-xl flex-1">
              <div className="relative w-20 h-20">
                <div className="absolute inset-0 border-4 border-indigo-500/20 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-[#6366F1] border-t-transparent rounded-full animate-spin"></div>
              </div>
              <p className="text-sm font-semibold tracking-wide text-indigo-400 mt-2 animate-pulse uppercase">Retrieving live Binance book tickers and candles...</p>
              <p className="text-xs text-gray-500 text-center max-w-sm">Applying user-defined strategy rules to evaluate structural breaks and inefficiencies.</p>
            </div>
          ) : currentAnalysis ? (
            <div className="flex-1 flex flex-col gap-6">
              {/* Signal Panel with Neon Accent */}
              <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-6 shadow-xl flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden">
                <div className="absolute right-0 top-0 w-32 h-32 bg-[#6366F1]/5 rounded-full blur-3xl pointer-events-none"></div>
                
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-widest font-mono">Market Setup Verdict</span>
                  <div className="flex items-baseline gap-3">
                    <h2 className="text-3xl font-extrabold tracking-tight text-white">{currentAnalysis.symbol}</h2>
                    <span className="text-sm text-gray-400 font-semibold">{currentAnalysis.timeframe} timeframe</span>
                  </div>
                  <p className="text-xs text-gray-500 font-mono mt-1">Generated: {new Date(currentAnalysis.timestamp).toLocaleString()}</p>
                </div>

                <div className="flex items-center gap-6">
                  {/* Confidence Ring */}
                  <div className="flex flex-col items-center gap-1.5">
                    <span className="text-[9px] font-semibold text-gray-500 uppercase tracking-wider">Confidence</span>
                    <div className="relative w-16 h-16 flex items-center justify-center">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle cx="32" cy="32" r="28" className="stroke-current text-[#1E2235]" strokeWidth="4" fill="transparent" />
                        <circle cx="32" cy="32" r="28" className="stroke-current text-indigo-500" strokeWidth="4" fill="transparent"
                          strokeDasharray={175.9}
                          strokeDashoffset={175.9 - (175.9 * currentAnalysis.confidence) / 100}
                        />
                      </svg>
                      <span className="absolute text-sm font-extrabold text-white">{currentAnalysis.confidence}%</span>
                    </div>
                  </div>

                  {/* Signal Box */}
                  <div className="flex flex-col items-center gap-1.5">
                    <span className="text-[9px] font-semibold text-gray-500 uppercase tracking-wider">Signal</span>
                    <div className={`px-5 py-3 rounded-xl border text-sm font-extrabold tracking-wider ${getSignalColor(currentAnalysis.signal)}`}>
                      {currentAnalysis.signal}
                    </div>
                  </div>
                </div>
              </div>

              {/* Analysis Explanation & Teacher Reasoning */}
              <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-6 shadow-xl flex flex-col gap-4">
                <h3 className="text-sm font-semibold tracking-wide text-white flex items-center gap-2">
                  <svg className="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  Technical Reasoning & Structure Analysis
                </h3>
                <div className="text-sm leading-relaxed text-gray-300 font-mono whitespace-pre-wrap bg-[#141626]/50 p-4 rounded-xl border border-[#1E2235]">
                  {currentAnalysis.reasoning}
                </div>
              </div>

              {/* Risk Management / Stop Loss / Invalidation */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Invalidation Zone */}
                <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 shadow-xl flex flex-col gap-3">
                  <h4 className="text-xs font-semibold tracking-wider text-rose-400 uppercase flex items-center gap-1.5">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Setup Invalidation Conditions
                  </h4>
                  <p className="text-xs leading-relaxed text-gray-400 font-mono">
                    {currentAnalysis.invalidation}
                  </p>
                </div>

                {/* Risk Warning & Management */}
                <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 shadow-xl flex flex-col gap-3">
                  <h4 className="text-xs font-semibold tracking-wider text-amber-400 uppercase flex items-center gap-1.5">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Risk Mitigation Guidelines
                  </h4>
                  <p className="text-xs leading-relaxed text-gray-400 font-mono">
                    {currentAnalysis.risk_notes}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-16 flex flex-col items-center justify-center gap-5 shadow-xl flex-1">
              <div className="w-16 h-16 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
                <svg className="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div className="text-center max-w-sm flex flex-col gap-1.5">
                <h3 className="text-md font-semibold text-white">No active scan loaded</h3>
                <p className="text-xs text-gray-500">Select a trading pair and timeframe above, then click &quot;Scan Market&quot; to fetch live Binance data and evaluate structural trade setups.</p>
              </div>
            </div>
          )}
        </section>

        {/* RIGHT COLUMN: AI Brain Assistant Chat Console */}
        <section className="xl:col-span-1 flex flex-col bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 shadow-xl h-[calc(100vh-140px)] min-h-[500px]" id="chat-section">
          <div className="flex items-center gap-2 border-b border-[#1E2235] pb-4">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20">
              <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Falcon Chat Console</h2>
              <p className="text-[10px] text-gray-500 font-mono">Ask about structures, levels &amp; strategy</p>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto py-4 flex flex-col gap-4 pr-1">
            {chatMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col gap-1 max-w-[85%] ${
                  msg.sender === "user" ? "self-end items-end" : "self-start items-start"
                }`}
              >
                <div
                  className={`p-3 rounded-2xl text-xs leading-relaxed font-mono whitespace-pre-wrap ${
                    msg.sender === "user"
                      ? "bg-indigo-600 text-white rounded-tr-none"
                      : "bg-[#141626] border border-[#1E2235] text-gray-300 rounded-tl-none"
                  }`}
                >
                  {msg.text}
                </div>
                <span className="text-[9px] text-gray-500 px-1">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
            {chatLoading && (
              <div className="self-start flex flex-col gap-1.5 items-start">
                <div className="bg-[#141626] border border-[#1E2235] p-3 rounded-2xl rounded-tl-none text-xs text-indigo-400 font-mono flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Chat Input */}
          <form onSubmit={sendChatMessage} className="border-t border-[#1E2235] pt-4 flex gap-2">
            <input
              type="text"
              id="chat-input-text"
              placeholder="Ask: 'Why is this bullish?' or 'Show SL rules'..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              className="flex-1 bg-[#141626] border border-[#1E2235] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#6366F1] font-mono"
            />
            <button
              type="submit"
              id="btn-chat-send"
              className="bg-indigo-600 hover:bg-indigo-500 text-white p-2.5 rounded-xl transition-colors flex items-center justify-center"
            >
              <svg className="w-4 h-4 transform rotate-90" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </form>
        </section>
          </>
        )}

      </main>

      {/* Bottom Fixed News Ticker */}
      {news.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-[#0E1017] border-t border-[#1E2235] py-2 z-50 h-9 flex items-center backdrop-blur-md bg-opacity-95 shadow-[0_-5px_20px_rgba(0,0,0,0.4)]">
          <div className="bg-[#6366F1] text-white text-[9px] font-bold px-3 py-1 flex items-center gap-1 uppercase tracking-wider shrink-0 h-full font-sans select-none z-10">
            <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
            Live Headlines
          </div>
          <div className="marquee-container flex-1" id="news-marquee-container">
            <div className="marquee-content flex gap-8 pr-8">
              {/* Render twice for continuous loop */}
              {[...news, ...news].map((item, idx) => (
                <a 
                  key={idx}
                  href={item.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-xs font-mono text-gray-400 hover:text-white transition-colors shrink-0 group select-none"
                >
                  <span className="text-[#8B5CF6]">•</span>
                  <span className="group-hover:underline">{item.title}</span>
                  <span className="text-gray-600 text-[10px]">({item.pubDate.split(' ')[4] || ''})</span>
                </a>
              ))}
            </div>
          </div>
        </div>
      )}

      {showSettings && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
          <div className="bg-[#11131F] border border-[#1E2235] rounded-2xl w-full max-w-md p-6 shadow-2xl relative">
            <button
              onClick={() => setShowSettings(false)}
              className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            <h3 className="text-lg font-bold text-white mb-1">Falcon Configuration</h3>
            <p className="text-xs text-gray-500 font-mono mb-4">Set your preferences and API credentials</p>
            
            <form onSubmit={saveApiKey} className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Gemini API Key</label>
                <input
                  type="password"
                  placeholder="AIzaSy... or AQ..."
                  value={tempApiKey}
                  onChange={(e) => setTempApiKey(e.target.value)}
                  className="w-full bg-[#141626] border border-[#1E2235] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#6366F1] font-mono"
                />
                <p className="text-[10px] text-gray-500 leading-normal mt-1">
                  This key is stored securely in the database preferences and used by the AI Brain for technical analysis.
                </p>
              </div>
              
              <div className="flex justify-end gap-3 mt-2 border-t border-[#1E2235] pt-4">
                <button
                  type="button"
                  onClick={() => setShowSettings(false)}
                  className="px-4 py-2 text-xs font-semibold text-gray-400 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-[#6366F1] hover:bg-[#5053df] text-white px-4 py-2 rounded-xl text-xs font-semibold transition-colors shadow-lg shadow-indigo-500/10"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
