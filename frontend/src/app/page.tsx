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
  const [geminiStatus, setGeminiStatus] = useState<{ status: string; details: string }>({ status: "UNKNOWN", details: "Checking key status..." });
  const [showSettings, setShowSettings] = useState(false);

  // News states
  const [news, setNews] = useState<any[]>([]);
  const [newsLoading, setNewsLoading] = useState(false);
  const [activeView, setActiveView] = useState<"dashboard" | "news" | "silverbullet" | "smc">("dashboard");
  const [trackers, setTrackers] = useState<any[]>([]);
  const [tradeHistory, setTradeHistory] = useState<any[]>([]);
  const [logLoading, setLogLoading] = useState(false);

  const fetchTradeHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/trades/history");
      if (res.ok) {
        const data = await res.json();
        setTradeHistory(data);
      }
    } catch (err) {
      console.error("Error fetching trade history:", err);
    }
  };

  const handleLogTrade = async () => {
    if (!sbResult) return;

    const direction = (sbResult.daily_bias === "BULLISH" || sbResult.daily_bias === "BEARISH") 
      ? sbResult.daily_bias 
      : sbHtfTrend;
    
    const parsePrice = (val: any) => {
      if (val === null || val === undefined) return 0.0;
      if (typeof val === "number") return val;
      const valStr = String(val);
      const matches = valStr.match(/\d+(?:\.\d+)?/g);
      return matches ? Number(matches[0]) : 0.0;
    };

    const entry = parsePrice(sbResult.entry_price_area) || (Number(sbCurrentPrice) || 0.0);
    let sl = parsePrice(sbResult.stop_loss_level);
    if (sl === 0) {
      sl = direction === "BULLISH" ? entry * 0.9985 : entry * 1.0015;
    }
    let target = parsePrice(sbResult.liquidity_target) || (direction === "BULLISH" ? entry + (entry - sl) * 3 : entry - (sl - entry) * 3);

    // Confirm or edit trade values before logging
    const confirmedEntryStr = prompt(`Confirm/Edit Entry Price for ${sbSymbol}:`, entry.toFixed(4));
    if (confirmedEntryStr === null) return;
    const confirmedEntry = parseFloat(confirmedEntryStr);
    if (isNaN(confirmedEntry) || confirmedEntry <= 0) {
      alert("Invalid Entry Price entered.");
      return;
    }

    const confirmedSlStr = prompt(`Confirm/Edit Stop-Loss (SL) Price for ${sbSymbol}:`, sl.toFixed(4));
    if (confirmedSlStr === null) return;
    const confirmedSl = parseFloat(confirmedSlStr);
    if (isNaN(confirmedSl) || confirmedSl <= 0) {
      alert("Invalid Stop-Loss Price entered.");
      return;
    }

    const riskVal = Math.abs(confirmedEntry - confirmedSl);
    const tp3rr = direction === "BULLISH" ? confirmedEntry + (riskVal * 3.0) : confirmedEntry - (riskVal * 3.0);
    const tp2rr = direction === "BULLISH" ? confirmedEntry + (riskVal * 2.0) : confirmedEntry - (riskVal * 2.0);

    const targetPromptMsg = `Set Take-Profit (TP) Price:\n` +
      `- Standard 1:4 RR: ${target.toFixed(4)}\n` +
      `- Custom 1:3 RR: ${tp3rr.toFixed(4)}\n` +
      `- Quick 1:2 RR: ${tp2rr.toFixed(4)}`;

    const confirmedTargetStr = prompt(targetPromptMsg, target.toFixed(4));
    if (confirmedTargetStr === null) return;
    const confirmedTarget = parseFloat(confirmedTargetStr);
    if (isNaN(confirmedTarget) || confirmedTarget <= 0) {
      alert("Invalid Take-Profit Price entered.");
      return;
    }

    setLogLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/trades/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: sbSymbol,
          direction: direction,
          entry_price: confirmedEntry,
          stop_loss: confirmedSl,
          take_profit: confirmedTarget,
          confidence: sbResult.confidence || 0
        })
      });
      if (res.ok) {
        alert("Trade logged to history successfully! 📈");
        fetchTradeHistory();
      } else {
        const errData = await res.json();
        alert(`Failed to log trade: ${errData.detail || "Unknown error"}`);
      }
    } catch (err) {
      console.error("Error logging trade:", err);
      alert("Error connecting to server to log trade.");
    } finally {
      setLogLoading(false);
    }
  };

  const handleDeleteTrade = async (tradeId: number) => {
    if (!confirm("Are you sure you want to delete this trade from history?")) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/trades/${tradeId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        fetchTradeHistory();
      }
    } catch (err) {
      console.error("Error deleting trade:", err);
    }
  };

  const handleUpdateTradeStatus = async (tradeId: number, newStatus: string) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/trades/${tradeId}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        fetchTradeHistory();
      }
    } catch (err) {
      console.error("Error updating trade status:", err);
    }
  };

  const handleEditTradeField = async (trade: any, field: "entry_price" | "stop_loss" | "take_profit", fieldName: string) => {
    const currentValue = trade[field];
    const newValueStr = prompt(`Edit ${fieldName} price for ${trade.symbol}:`, currentValue.toFixed(4));
    if (newValueStr === null) return;
    const newValue = parseFloat(newValueStr);
    if (isNaN(newValue) || newValue <= 0) {
      alert(`Invalid ${fieldName} price entered.`);
      return;
    }
    
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/trades/${trade.id}/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ [field]: newValue })
      });
      if (res.ok) {
        alert(`${fieldName} updated successfully! 🎯`);
        fetchTradeHistory();
      } else {
        alert(`Failed to update ${fieldName}.`);
      }
    } catch (err) {
      console.error(err);
      alert(`Error updating ${fieldName}.`);
    }
  };

  const fetchTrackersStatus = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/tracker/status");
      if (res.ok) {
        const data = await res.json();
        setTrackers(data);
      }
    } catch (err) {
      console.error("Error fetching trackers status:", err);
    }
  };

  const handleTrackSetup = async (symbol: string) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/tracker/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: symbol,
          timeframe: "1m",
          scenario_text: sbScenarioText,
          htf_trend: sbHtfTrend,
          pullback_days: sbPullbackDays ? Number(sbPullbackDays) : null,
          pdh: sbPdh ? Number(sbPdh) : null,
          pdl: sbPdl ? Number(sbPdl) : null,
          daily_open: sbOpen ? Number(sbOpen) : null,
          daily_close: sbClose ? Number(sbClose) : null,
          asian_sweep: sbAsianSweep,
          demand_mitigation: sbDemandMitigation,
          ltf_shift: sbLtfShift,
          current_price: sbCurrentPrice ? Number(sbCurrentPrice) : null,
          dealing_range_high: sbDealingRangeHigh ? Number(sbDealingRangeHigh) : null,
          dealing_range_low: sbDealingRangeLow ? Number(sbDealingRangeLow) : null,
          killzone: sbKillzone,
          discount_pd_array: sbDiscountPdArray,
          premium_pd_array: sbPremiumPdArray,
          ltf_trigger: sbLtfTrigger,
          has_fresh_fvg: sbHasFreshFvg,
          high_impact_news: sbHighImpactNews,
          candle_9am_high: sbCandle9amHigh ? Number(sbCandle9amHigh) : null,
          candle_9am_low: sbCandle9amLow ? Number(sbCandle9amLow) : null
        })
      });
      if (res.ok) {
        alert(`Started tracking ${symbol} successfully! Check the Active Live Scanners panel on the right.`);
        fetchTrackersStatus();
      }
    } catch (err) {
      console.error("Error starting tracker:", err);
    }
  };

  const handleStopTracking = async (symbol: string) => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/tracker/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol: symbol })
      });
      if (res.ok) {
        fetchTrackersStatus();
      }
    } catch (err) {
      console.error("Error stopping tracker:", err);
    }
  };

  useEffect(() => {
    fetchTrackersStatus();
    fetchTradeHistory();
  }, []);

  useEffect(() => {
    if (trackers.length === 0) return;
    const interval = setInterval(fetchTrackersStatus, 5000);
    return () => clearInterval(interval);
  }, [trackers.length]);

  useEffect(() => {
    const interval = setInterval(fetchTradeHistory, 10000);
    return () => clearInterval(interval);
  }, []);

  // Chat interface state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Silver Bullet States
  const [sbInputMode, setSbInputMode] = useState<"form" | "text">("form");
  const [sbSymbol, setSbSymbol] = useState("GOLD");
  const [sbScenarioText, setSbScenarioText] = useState("");
  const [sbHtfTrend, setSbHtfTrend] = useState("BULLISH");
  const [sbPullbackDays, setSbPullbackDays] = useState(3);
  const [sbPdh, setSbPdh] = useState<number | "">(2350);
  const [sbPdl, setSbPdl] = useState<number | "">(2320);
  const [sbOpen, setSbOpen] = useState<number | "">(2325);
  const [sbClose, setSbClose] = useState<number | "">(2330);
  const [sbAsianSweep, setSbAsianSweep] = useState(true);
  const [sbDemandMitigation, setSbDemandMitigation] = useState(true);
  const [sbLtfShift, setSbLtfShift] = useState(true);
  const [sbCurrentPrice, setSbCurrentPrice] = useState<number | "">(2323);
  
  // Advanced Strategy States
  const [sbDealingRangeHigh, setSbDealingRangeHigh] = useState<number | "">(2360);
  const [sbDealingRangeLow, setSbDealingRangeLow] = useState<number | "">(2310);
  const [sbKillzone, setSbKillzone] = useState("LONDON_SB");
  const [sbAutoDetectSession, setSbAutoDetectSession] = useState(true);

  // Auto-detect killzone based on New York Time
  useEffect(() => {
    if (!sbAutoDetectSession) return;

    const detectSession = () => {
      try {
        const nyString = new Date().toLocaleString("en-US", { timeZone: "America/New_York" });
        const nyDate = new Date(nyString);
        const hours = nyDate.getHours();
        
        // London Open Silver Bullet: 3AM - 4AM NY
        if (hours === 3) {
          setSbKillzone("LONDON_SB");
        }
        // AM Session Silver Bullet: 10AM - 11AM NY
        else if (hours === 10) {
          setSbKillzone("NY_AM_SB");
        }
        // PM Session Silver Bullet: 2PM - 3PM NY
        else if (hours === 14) {
          setSbKillzone("NY_PM_SB");
        }
        // London Killzone: 2AM - 5AM NY (except 3AM SB window)
        else if (hours >= 2 && hours < 5) {
          setSbKillzone("LONDON");
        }
        // New York AM Killzone: 7AM - 10AM NY
        else if (hours >= 7 && hours < 10) {
          setSbKillzone("NY_AM");
        }
        // Outside Killzones
        else {
          setSbKillzone("NONE");
        }
      } catch (error) {
        console.error("Failed to detect New York session time:", error);
      }
    };

    detectSession();
    const interval = setInterval(detectSession, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, [sbAutoDetectSession]);



  const [sbDiscountPdArray, setSbDiscountPdArray] = useState(true);
  const [sbPremiumPdArray, setSbPremiumPdArray] = useState(false);
  const [sbLtfTrigger, setSbLtfTrigger] = useState("MSS");
  const [sbHasFreshFvg, setSbHasFreshFvg] = useState(true);
  const [sbHighImpactNews, setSbHighImpactNews] = useState(false);
  const [sbCandle9amHigh, setSbCandle9amHigh] = useState<number | "">(2335);
  const [sbCandle9amLow, setSbCandle9amLow] = useState<number | "">(2315);
  
  const [sbResult, setSbResult] = useState<any | null>(null);
  const [sbLoading, setSbLoading] = useState(false);
  const [sbSearchLoading, setSbSearchLoading] = useState(false);
  const [sbSearchError, setSbSearchError] = useState<string | null>(null);

  // SMC Method States
  const [smcSymbol, setSmcSymbol] = useState("BTCUSDT");
  const [smcStrategyModel, setSmcStrategyModel] = useState("double_mitigation");
  const [smcTimeframe, setSmcTimeframe] = useState("15m");
  const [smcHtfTrend, setSmcHtfTrend] = useState("BULLISH");
  const [smcLiquidityPoolsSwept, setSmcLiquidityPoolsSwept] = useState(true);
  const [smcInducementSwept, setSmcInducementSwept] = useState(true);
  const [smcSwingValidated, setSmcSwingValidated] = useState(true);
  const [smcBosConfirmed, setSmcBosConfirmed] = useState(true);
  const [smcOrderBlockMitigated, setSmcOrderBlockMitigated] = useState(true);
  const [smcFvgMitigated, setSmcFvgMitigated] = useState(true);
  const [smcLtfChoch, setSmcLtfChoch] = useState(true);
  const [smcPo3Phase, setSmcPo3Phase] = useState("DISTRIBUTION");
  const [smcPdh, setSmcPdh] = useState<number | "">(65000);
  const [smcPdl, setSmcPdl] = useState<number | "">(64000);
  const [smcOpen, setSmcOpen] = useState<number | "">(64200);
  const [smcCurrentPrice, setSmcCurrentPrice] = useState<number | "">(64100);
  const [smcResult, setSmcResult] = useState<any | null>(null);
  const [monitoredCoins, setMonitoredCoins] = useState<any[]>([]);
  const [livePrices, setLivePrices] = useState<Record<string, number>>({});

  // 5-Second Local API Watchlist Polling Loop
  useEffect(() => {
    if (monitoredCoins.length === 0) return;

    const intervalId = setInterval(async () => {
      const currentCoins = [...monitoredCoins];
      if (currentCoins.length === 0) return;

      const updated = await Promise.all(
        currentCoins.map(async (coin) => {
          try {
            const sym = getTradingViewSymbol(coin.symbol);
            const cleanSym = sym.includes(":") ? sym.split(":")[1] : sym;
            const res = await fetch(`http://127.0.0.1:8000/api/market/price?symbol=${encodeURIComponent(cleanSym)}`);
            if (res.ok) {
              const data = await res.json();
              return {
                ...coin,
                currentPrice: data.current_price || coin.currentPrice,
                pdh: data.pdh || coin.pdh,
                pdl: data.pdl || coin.pdl,
                open: data.open || coin.open
              };
            }
          } catch (e) {
            console.error("Error refreshing monitored coin:", coin.symbol, e);
          }
          return coin;
        })
      );

      setMonitoredCoins(prevCoins => {
        // Only keep and update coins that are still in the list
        return prevCoins.map(prevCoin => {
          const match = updated.find(u => u.symbol === prevCoin.symbol);
          return match ? {
            ...prevCoin,
            currentPrice: match.currentPrice,
            pdh: match.pdh,
            pdl: match.pdl,
            open: match.open
          } : prevCoin;
        });
      });
    }, 5000);

    return () => clearInterval(intervalId);
  }, [monitoredCoins]);

  // 5-Second Journal Trades Price Polling Loop
  useEffect(() => {
    if (tradeHistory.length === 0) return;

    const fetchJournalPrices = async () => {
      const uniqueSymbols = Array.from(new Set(tradeHistory.map((t: any) => t.symbol.toUpperCase())));
      const priceMap: Record<string, number> = { ...livePrices };
      let changed = false;

      await Promise.all(
        uniqueSymbols.map(async (symbol) => {
          try {
            const sym = getTradingViewSymbol(symbol);
            const cleanSym = sym.includes(":") ? sym.split(":")[1] : sym;
            const res = await fetch(`http://127.0.0.1:8000/api/market/price?symbol=${encodeURIComponent(cleanSym)}`);
            if (res.ok) {
              const data = await res.json();
              if (data.current_price !== undefined) {
                priceMap[symbol] = data.current_price;
                changed = true;
              }
            }
          } catch (e) {
            console.error("Error fetching live price for journal symbol:", symbol, e);
          }
        })
      );

      if (changed) {
        setLivePrices(priceMap);
      }
    };

    fetchJournalPrices();
    const intervalId = setInterval(fetchJournalPrices, 5000);
    return () => clearInterval(intervalId);
  }, [tradeHistory]);

  // Watchlist Local Strategy Recalculators
  const calculateCoinConfidence = (coin: any) => {
    const isDiscount = coin.currentPrice < (coin.pdh + coin.pdl) / 2;
    const isBelowOpen = coin.currentPrice < coin.open;
    const isBullish = coin.htfTrend === "BULLISH";
    const isBearish = coin.htfTrend === "BEARISH";

    let conf = 0;
    if (isBullish && isDiscount) conf += 15;
    if (isBearish && !isDiscount) conf += 15;
    if (isBullish && isBelowOpen) conf += 15;
    if (isBearish && !isBelowOpen) conf += 15;
    if (coin.liquidityPoolsSwept) conf += 10;
    if (coin.inducementSwept) conf += 15;
    if (coin.swingValidated) conf += 10;
    if (coin.bosConfirmed) conf += 10;
    if (coin.orderBlockMitigated || coin.fvgMitigated) conf += 10;
    if (coin.ltfChoch) conf += 10;

    return {
      confidence: conf,
      is_valid: conf >= 70,
      zone_ok: (isBullish && isDiscount) || (isBearish && !isDiscount),
      open_ok: (isBullish && isBelowOpen) || (isBearish && !isBelowOpen),
      is_discount: isDiscount,
      is_below_open: isBelowOpen
    };
  };

  const getCoinParameters = (coin: any) => {
    const confData = calculateCoinConfidence(coin);
    const risk = coin.currentPrice * 0.0015;
    const isBullish = coin.htfTrend === "BULLISH";
    const entryPrice = isBullish ? coin.currentPrice - (risk * 0.5) : coin.currentPrice + (risk * 0.5);
    const stopLoss = isBullish ? entryPrice - risk : entryPrice + risk;
    const tp2 = isBullish ? entryPrice + (risk * 4.0) : entryPrice - (risk * 4.0);

    return {
      ...confData,
      entry_price: entryPrice,
      stop_loss: stopLoss,
      take_profit: tp2
    };
  };
  const [smcLoading, setSmcLoading] = useState(false);

  const handleRunSmcAnalysis = async (addToWatchlist: boolean = false) => {
    setSmcLoading(true);
    try {
      const resPrice = await fetch(`${API_BASE}/market/price?symbol=${encodeURIComponent(smcSymbol.trim())}`);
      let fetchedPrice = Number(smcCurrentPrice) || 64100;
      let fetchedPdh = Number(smcPdh) || 65000;
      let fetchedPdl = Number(smcPdl) || 64000;
      let fetchedOpen = Number(smcOpen) || 64200;

      let activeHtfTrend = smcHtfTrend;
      if (resPrice.ok) {
        const data = await resPrice.json();
        fetchedPrice = data.current_price || fetchedPrice;
        fetchedPdh = data.pdh || fetchedPdh;
        fetchedPdl = data.pdl || fetchedPdl;
        fetchedOpen = data.open || fetchedOpen;
        setSmcCurrentPrice(fetchedPrice);
        setSmcPdh(fetchedPdh);
        setSmcPdl(fetchedPdl);
        setSmcOpen(fetchedOpen);
        if (data.daily_bias) {
          setSmcHtfTrend(data.daily_bias);
          activeHtfTrend = data.daily_bias;
        }
      }

      const isDiscount = fetchedPrice < (fetchedPdh + fetchedPdl) / 2;
      const isBelowOpen = fetchedPrice < fetchedOpen;
      const isBullish = activeHtfTrend === "BULLISH";
      const isBearish = activeHtfTrend === "BEARISH";

      let conf = 0;
      if (isBullish && isDiscount) conf += 15;
      if (isBearish && !isDiscount) conf += 15;
      if (isBullish && isBelowOpen) conf += 15;
      if (isBearish && !isBelowOpen) conf += 15;
      if (smcLiquidityPoolsSwept) conf += 10;
      if (smcInducementSwept) conf += 15;
      if (smcSwingValidated) conf += 10;
      if (smcBosConfirmed) conf += 10;
      if (smcOrderBlockMitigated || smcFvgMitigated) conf += 10;
      if (smcLtfChoch) conf += 10;

      const isSetupValid = conf >= 70;
      const direction = isBullish ? "BULLISH" : "BEARISH";
      const risk = fetchedPrice * 0.0015;
      const entryPrice = isBullish ? fetchedPrice - (risk * 0.5) : fetchedPrice + (risk * 0.5);
      const stopLoss = isBullish ? entryPrice - risk : entryPrice + risk;
      const tp1 = isBullish ? entryPrice + (risk * 2.0) : entryPrice - (risk * 2.0);
      const tp2 = isBullish ? entryPrice + (risk * 4.0) : entryPrice - (risk * 4.0);
      const tp3 = isBullish ? entryPrice + (risk * 6.0) : entryPrice - (risk * 6.0);

      const action = isBullish ? "Buy Limit" : "Sell Limit";

      const smcAnalysisData = {
        is_valid: isSetupValid,
        confidence: conf,
        daily_bias: direction,
        entry_price_area: isSetupValid ? `${action} at ${entryPrice.toFixed(2)}` : "No Entry (Confidence < 70%)",
        stop_loss_level: isSetupValid ? stopLoss.toFixed(2) : null,
        liquidity_target: isSetupValid ? tp2.toFixed(2) : null,
        tp1_target: isSetupValid ? tp1.toFixed(2) : null,
        tp2_target: isSetupValid ? tp2.toFixed(2) : null,
        tp3_target: isSetupValid ? tp3.toFixed(2) : null,
        target_reward_ratio: "1:4.00",
        equilibrium_price: (fetchedPdh + fetchedPdl) / 2,
        zone_type: isDiscount ? "DISCOUNT" : "PREMIUM",
        daily_open_relation: isBelowOpen ? "BELOW_OPEN" : "ABOVE_OPEN",
        swept_liquidity_pool: smcInducementSwept ? "IDM_PULLBACK_SWEEP" : "NONE",
        mitigated_pd_array_type: smcOrderBlockMitigated ? "ORDER_BLOCK" : (smcFvgMitigated ? "FVG" : "NONE"),
        po3_phase: smcPo3Phase,
        reasoning: `1. Liquidity Pool Identification: Equal Highs/Lows / Trendline liquidity swept (${smcLiquidityPoolsSwept ? "YES" : "NO"}).\n` +
          `2. Inducement (IDM) Sweep: First minor pullback level swept to trap retail liquidity (${smcInducementSwept ? "YES" : "NO"}).\n` +
          `3. Swing High/Low Validation: Major swing extreme validated following IDM sweep (${smcSwingValidated ? "YES" : "NO"}).\n` +
          `4. BOS Body Close: Structure break confirmed strictly via candle body close (${smcBosConfirmed ? "YES" : "NO"}).\n` +
          `5. Unmitigated POI Selection: Fresh Order Block / FVG tapped in ${isDiscount ? "DISCOUNT" : "PREMIUM"} zone (${smcOrderBlockMitigated || smcFvgMitigated ? "YES" : "NO"}).\n` +
          `6. LTF CHOCH & Entry Confirmation: 1m/3m/5m CHOCH verified with limit entry at 50% FVG/OB midpoint.\n\n` +
          `---\n\n` +
          `**සිංහල පරිවර්තනය (Sinhala Translation):**\n` +
          `1. නීතිය 1 (Liquidity Pools): Equal Highs/Lows / Trendline ද්‍රවශීලතාවය සූරා දැමීම (Sweep): ${smcLiquidityPoolsSwept ? "ඔව්" : "නැත"}.\n` +
          `2. නීතිය 2 (Inducement Sweep): පළමු Minor Pullback (IDM) මට්ටම Sweep වීම: ${smcInducementSwept ? "ඔව්" : "නැත"}.\n` +
          `3. නීතිය 3 (Swing Validation): IDM sweep වීමෙන් පසු ප්‍රධාන Swing High/Low එක තහවුරු වීම: ${smcSwingValidated ? "ඔව්" : "නැත"}.\n` +
          `4. නීතිය 4 (BOS Body Close): Candle Body එකකින් BOS සනාථ වීම: ${smcBosConfirmed ? "ඔව්" : "නැත"}.\n` +
          `5. නීතිය 5 (Unmitigated POI): ${isDiscount ? "DISCOUNT" : "PREMIUM"} කලාපයේ Fresh Order Block / FVG කලාපයට මිල පැමිණීම: ${smcOrderBlockMitigated || smcFvgMitigated ? "ඔව්" : "නැත"}.\n` +
          `6. නීතිය 6 (LTF Entry Confirmation): 1m/3m/5m CHOCH සනාථ වී FVG / Order Block 50% මට්ටමේ Limit Order එක පිහිටුවීම.`,
        invalidation: `Setup is invalidated if price breaches the manipulation extreme at ${stopLoss.toFixed(2)} before limit execution.\n\n` +
          `---\n\n` +
          `**සිංහල පරිවර්තනය (Sinhala Translation):**\n` +
          `මිල ${stopLoss.toFixed(2)} මට්ටමෙන් ඔබ්බට ගියහොත් මෙම SMC setup එක සෘජුවම අවලංගු වේ.`,
        risk_notes: `SMC Scalp Risk strictly 0.5% - 1.0% maximum. Hold duration: 10m - 15m max. Stop Loss: ${stopLoss.toFixed(2)}, Target: ${tp2.toFixed(2)} (1:4.00 RR).\n\n` +
          `---\n\n` +
          `**සිංහල පරිවර්තනය (Sinhala Translation):**\n` +
          `SMC Scalp trade එකක් බැවින් එක් trade එකකට උපරිම 0.5% - 1.0% ක් පමණක් අවදානමට ලක් කරන්න. උපරිම රඳවා ගැනීමේ කාලය: විනාඩි 10 - 15. Stop Loss: ${stopLoss.toFixed(2)}, Target: ${tp2.toFixed(2)}.`
      };

      // Add to monitoredCoins watchlist ONLY if explicitly requested
      if (addToWatchlist) {
        setMonitoredCoins(prevCoins => {
          const coinSymbol = smcSymbol.toUpperCase().trim();
          const existingIdx = prevCoins.findIndex((c: any) => c.symbol === coinSymbol);
          const newMonitoredCoin = {
            id: existingIdx >= 0 ? prevCoins[existingIdx].id : Date.now().toString(),
            symbol: coinSymbol,
            timeframe: smcTimeframe,
            htfTrend: activeHtfTrend,
            currentPrice: fetchedPrice,
            open: fetchedOpen,
            pdh: fetchedPdh,
            pdl: fetchedPdl,
            liquidityPoolsSwept: smcLiquidityPoolsSwept,
            inducementSwept: smcInducementSwept,
            swingValidated: smcSwingValidated,
            bosConfirmed: smcBosConfirmed,
            orderBlockMitigated: smcOrderBlockMitigated,
            fvgMitigated: smcFvgMitigated,
            ltfChoch: smcLtfChoch,
            po3Phase: smcPo3Phase
          };

          if (existingIdx >= 0) {
            const copy = [...prevCoins];
            copy[existingIdx] = newMonitoredCoin;
            return copy;
          } else {
            return [...prevCoins, newMonitoredCoin];
          }
        });
      }

      setSmcResult(smcAnalysisData);
    } catch (err) {
      console.error("Error running SMC analysis:", err);
    } finally {
      setSmcLoading(false);
    }
  };

  // Trigger SMC analysis/fetch automatically on timeframe changes
  useEffect(() => {
    if (smcSymbol && smcSymbol.length >= 3) {
      handleRunSmcAnalysis(false);
    }
  }, [smcTimeframe]);

  const handleLogSmcTrade = async () => {
    if (!smcResult) return;

    const direction = (smcResult.daily_bias === "BULLISH" || smcResult.daily_bias === "BEARISH") 
      ? smcResult.daily_bias 
      : smcHtfTrend;

    const entry = parseFloat(smcResult.entry_price_area?.match(/\d+(?:\.\d+)?/)?.[0] || String(smcCurrentPrice || 0));
    let sl = parseFloat(smcResult.stop_loss_level || "0");
    if (isNaN(sl) || sl === 0) {
      sl = direction === "BULLISH" ? entry * 0.9985 : entry * 1.0015;
    }
    let target = parseFloat(smcResult.liquidity_target || "0");
    if (isNaN(target) || target === 0) {
      target = direction === "BULLISH" ? entry + (entry - sl) * 3.0 : entry - (sl - entry) * 3.0;
    }

    // Confirm or edit trade values before logging
    const confirmedEntryStr = prompt(`Confirm/Edit Entry Price for ${smcSymbol}:`, entry.toFixed(2));
    if (confirmedEntryStr === null) return;
    const confirmedEntry = parseFloat(confirmedEntryStr);
    if (isNaN(confirmedEntry) || confirmedEntry <= 0) {
      alert("Invalid Entry Price entered.");
      return;
    }

    const confirmedSlStr = prompt(`Confirm/Edit Stop-Loss (SL) Price for ${smcSymbol}:`, sl.toFixed(2));
    if (confirmedSlStr === null) return;
    const confirmedSl = parseFloat(confirmedSlStr);
    if (isNaN(confirmedSl) || confirmedSl <= 0) {
      alert("Invalid Stop-Loss Price entered.");
      return;
    }

    const confirmedTargetStr = prompt(`Confirm/Edit Take-Profit (TP) Price for ${smcSymbol}:`, target.toFixed(2));
    if (confirmedTargetStr === null) return;
    const confirmedTarget = parseFloat(confirmedTargetStr);
    if (isNaN(confirmedTarget) || confirmedTarget <= 0) {
      alert("Invalid Take-Profit Price entered.");
      return;
    }

    setLogLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/trades/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol: smcSymbol,
          direction: direction,
          entry_price: confirmedEntry,
          stop_loss: confirmedSl,
          take_profit: confirmedTarget,
          confidence: smcResult.confidence || 0
        })
      });
      if (res.ok) {
        alert("SMC Trade logged to history successfully! 📈");
        fetchTradeHistory();
      } else {
        const errData = await res.json();
        alert(`Failed to log trade: ${errData.detail || "Unknown error"}`);
      }
    } catch (err) {
      console.error("Error logging SMC trade:", err);
      alert("Error connecting to server to log SMC trade.");
    } finally {
      setLogLoading(false);
    }
  };

  // Helper calculations for TP1 and TP2 fallback
  const entryPriceNum = (() => {
    if (!sbResult || !sbResult.entry_price_area) return null;
    const matches = sbResult.entry_price_area.match(/\d+(?:\.\d+)?/g);
    return matches ? Number(matches[0]) : null;
  })();
  const stopLossNum = sbResult?.stop_loss_level ? Number(sbResult.stop_loss_level) : null;

  const tp1TargetFallback = (() => {
    if (sbResult?.tp1_target) return sbResult.tp1_target;
    if (!entryPriceNum || !stopLossNum) return null;
    const risk = Math.abs(entryPriceNum - stopLossNum);
    const direction = sbResult.daily_bias;
    if (direction === "BULLISH") return entryPriceNum + (risk * 2.0);
    if (direction === "BEARISH") return entryPriceNum - (risk * 2.0);
    return null;
  })();

  const tp2TargetFallback = (() => {
    if (sbResult?.tp2_target) return sbResult.tp2_target;
    if (sbResult?.liquidity_target) return sbResult.liquidity_target;
    if (!entryPriceNum || !stopLossNum) return null;
    const risk = Math.abs(entryPriceNum - stopLossNum);
    const direction = sbResult.daily_bias;
    if (direction === "BULLISH") return entryPriceNum + (risk * 4.0);
    if (direction === "BEARISH") return entryPriceNum - (risk * 4.0);
    return null;
  })();

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

  const fetchLivePrices = async () => {
    if (!sbSymbol.trim()) return;
    setSbSearchLoading(true);
    setSbSearchError(null);
    try {
      const res = await fetch(`${API_BASE}/market/price?symbol=${encodeURIComponent(sbSymbol.trim())}`);
      if (res.ok) {
        const data = await res.json();
        if (data.pdh !== undefined) {
          setSbPdh(Number(data.pdh));
          setSbDealingRangeHigh(Number(data.pdh));
          setSbCandle9amHigh(Number(data.pdh) - 5);
        }
        if (data.pdl !== undefined) {
          setSbPdl(Number(data.pdl));
          setSbDealingRangeLow(Number(data.pdl));
          setSbCandle9amLow(Number(data.pdl) + 5);
        }
        if (data.open !== undefined) setSbOpen(Number(data.open));
        if (data.close !== undefined) setSbClose(Number(data.close));
        if (data.current_price !== undefined) setSbCurrentPrice(Number(data.current_price));
        if (data.daily_bias !== undefined && data.daily_bias !== null) {
          setSbHtfTrend(data.daily_bias);
        }
      } else {
        const err = await res.json();
        setSbSearchError(err.detail || "Failed to fetch prices");
      }
    } catch (error: any) {
      console.error(error);
      setSbSearchError("Network error. Please try again.");
    } finally {
      setSbSearchLoading(false);
    }
  };

  const triggerSilverBulletAnalysis = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setSbLoading(true);
    setSbResult(null);
    try {
      const payload: any = {
        symbol: sbSymbol,
        timeframe: selectedTimeframe,
        scenario_text: sbInputMode === "text" ? sbScenarioText : null,
        htf_trend: sbInputMode === "form" ? sbHtfTrend : null,
        pullback_days: sbInputMode === "form" ? Number(sbPullbackDays) : null,
        pdh: sbInputMode === "form" && sbPdh !== "" ? Number(sbPdh) : null,
        pdl: sbInputMode === "form" && sbPdl !== "" ? Number(sbPdl) : null,
        daily_open: sbInputMode === "form" && sbOpen !== "" ? Number(sbOpen) : null,
        daily_close: sbInputMode === "form" && sbClose !== "" ? Number(sbClose) : null,
        asian_sweep: sbInputMode === "form" ? sbAsianSweep : null,
        demand_mitigation: sbInputMode === "form" ? sbDemandMitigation : null,
        ltf_shift: sbInputMode === "form" ? sbLtfShift : null,
        current_price: sbInputMode === "form" && sbCurrentPrice !== "" ? Number(sbCurrentPrice) : null,
        
        // Advanced strategy parameters
        dealing_range_high: sbInputMode === "form" && sbDealingRangeHigh !== "" ? Number(sbDealingRangeHigh) : null,
        dealing_range_low: sbInputMode === "form" && sbDealingRangeLow !== "" ? Number(sbDealingRangeLow) : null,
        killzone: sbInputMode === "form" ? sbKillzone : null,
        discount_pd_array: sbInputMode === "form" ? sbDiscountPdArray : null,
        premium_pd_array: sbInputMode === "form" ? sbPremiumPdArray : null,
        ltf_trigger: sbInputMode === "form" ? sbLtfTrigger : null,
        has_fresh_fvg: sbInputMode === "form" ? sbHasFreshFvg : null,
        high_impact_news: sbInputMode === "form" ? sbHighImpactNews : null,
        candle_9am_high: sbInputMode === "form" && sbCandle9amHigh !== "" ? Number(sbCandle9amHigh) : null,
        candle_9am_low: sbInputMode === "form" && sbCandle9amLow !== "" ? Number(sbCandle9amLow) : null,
      };

      const res = await fetch(`${API_BASE}/silverbullet/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setSbResult(data);
      } else {
        alert("Failed to analyze Silver Bullet setup.");
      }
    } catch (err) {
      console.error("Silver Bullet error:", err);
      alert("Error: Backend is offline or failed.");
    } finally {
      setSbLoading(false);
    }
  };

  const handleSelectTracker = (tracker: any) => {
    if (!tracker) return;
    
    // Switch to Silver Bullet tab view to show details
    setActiveView("silverbullet");
    
    // Populate form fields with the tracked parameters
    setSbSymbol(tracker.symbol);
    const p = tracker.req_payload || {};
    
    if (p.htf_trend !== undefined) setSbHtfTrend(p.htf_trend || "BULLISH");
    if (p.pullback_days !== undefined) setSbPullbackDays(Number(p.pullback_days) || 3);
    if (p.pdh !== undefined) setSbPdh(p.pdh ?? "");
    if (p.pdl !== undefined) setSbPdl(p.pdl ?? "");
    if (p.daily_open !== undefined) setSbOpen(p.daily_open ?? "");
    if (p.daily_close !== undefined) setSbClose(p.daily_close ?? "");
    if (tracker.current_price !== undefined) setSbCurrentPrice(tracker.current_price ?? "");
    
    if (p.dealing_range_high !== undefined) setSbDealingRangeHigh(p.dealing_range_high ?? "");
    if (p.dealing_range_low !== undefined) setSbDealingRangeLow(p.dealing_range_low ?? "");
    if (p.killzone !== undefined) setSbKillzone(p.killzone || "LONDON_SB");
    
    if (p.asian_sweep !== undefined) setSbAsianSweep(!!p.asian_sweep);
    if (p.demand_mitigation !== undefined) setSbDemandMitigation(!!p.demand_mitigation);
    if (p.ltf_shift !== undefined) setSbLtfShift(!!p.ltf_shift);
    
    if (p.discount_pd_array !== undefined) setSbDiscountPdArray(!!p.discount_pd_array);
    if (p.premium_pd_array !== undefined) setSbPremiumPdArray(!!p.premium_pd_array);
    if (p.ltf_trigger !== undefined) setSbLtfTrigger(p.ltf_trigger || "MSS");
    if (p.has_fresh_fvg !== undefined) setSbHasFreshFvg(!!p.has_fresh_fvg);
    if (p.high_impact_news !== undefined) setSbHighImpactNews(!!p.high_impact_news);
    
    if (p.candle_9am_high !== undefined) setSbCandle9amHigh(p.candle_9am_high ?? "");
    if (p.candle_9am_low !== undefined) setSbCandle9amLow(p.candle_9am_low ?? "");
    
    // Load the tracker's live computed results into the main detail view panel
    if (tracker.last_result) {
      setSbResult(tracker.last_result);
    }
  };

  // Fetch initial data
  useEffect(() => {
    checkHealth();
    fetchStrategies();
    fetchHistory();
    fetchNews();
    fetchPreferences();
    fetchTradeHistory();
  }, []);

  const fetchGeminiStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/preferences/gemini-status`);
      if (res.ok) {
        const data = await res.json();
        setGeminiStatus(data);
      } else {
        setGeminiStatus({ status: "ERROR", details: "Failed to retrieve status from backend." });
      }
    } catch {
      setGeminiStatus({ status: "ERROR", details: "Could not connect to backend to check status." });
    }
  };

  useEffect(() => {
    fetchGeminiStatus();
    const interval = setInterval(fetchGeminiStatus, 20000); // Poll status every 20 seconds
    return () => clearInterval(interval);
  }, [geminiApiKey]);

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
        fetchGeminiStatus();
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

  // Sinhala translation state & utility functions
  const [translations, setTranslations] = useState<Record<string, string>>({});
  const [translating, setTranslating] = useState<Record<string, boolean>>({});

  const parseTextWithTranslation = (text: string): { english: string; sinhala: string | null } => {
    if (!text) return { english: "", sinhala: null };
    const markers = [
      "--- \n\n**සිංහල පරිවර්තනය (Sinhala Translation):**",
      "---\n\n**සිංහල පරිවර්තනය (Sinhala Translation):**",
      "**සිංහල පරිවර්තනය (Sinhala Translation):**",
      "**සිංහල පරිවර්තනය**",
      "---"
    ];
    for (const marker of markers) {
      const idx = text.indexOf(marker);
      if (idx !== -1) {
        const english = text.substring(0, idx).trim();
        let sinhala = text.substring(idx + marker.length).trim();
        sinhala = sinhala.replace(/^\*+/, "").replace(/\*+$/, "").trim();
        return { english, sinhala };
      }
    }
    return { english: text, sinhala: null };
  };

  const fetchTranslation = async (analysisId: number, fieldKey: string, text: string) => {
    const cacheKey = `${analysisId}_${fieldKey}`;
    setTranslating(prev => ({ ...prev, [cacheKey]: true }));
    try {
      const res = await fetch(`${API_BASE}/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.translated) {
          setTranslations(prev => ({ ...prev, [cacheKey]: data.translated }));
        }
      }
    } catch (e) {
      console.error("Error fetching translation:", e);
    } finally {
      setTranslating(prev => ({ ...prev, [cacheKey]: false }));
    }
  };

  useEffect(() => {
    if (!currentAnalysis) return;
    const fieldsToTranslate = [
      { key: "reasoning", val: currentAnalysis.reasoning },
      { key: "invalidation", val: currentAnalysis.invalidation },
      { key: "risk_notes", val: currentAnalysis.risk_notes }
    ];
    fieldsToTranslate.forEach(field => {
      const hasSinhala = /[\u0D80-\u0DFF]/.test(field.val || "");
      const cacheKey = `${currentAnalysis.id}_${field.key}`;
      if (field.val && !hasSinhala && !translations[cacheKey] && !translating[cacheKey]) {
        fetchTranslation(currentAnalysis.id, field.key, field.val);
      }
    });
  }, [currentAnalysis]);

  const renderFieldText = (originalText: string, fieldKey: string) => {
    if (!currentAnalysis) return null;
    const hasSinhala = /[\u0D80-\u0DFF]/.test(originalText || "");
    let englishText = originalText;
    let sinhalaText: string | null = null;

    if (hasSinhala) {
      const parsed = parseTextWithTranslation(originalText);
      englishText = parsed.english;
      sinhalaText = parsed.sinhala;
    } else {
      const cacheKey = `${currentAnalysis.id}_${fieldKey}`;
      sinhalaText = translations[cacheKey] || null;
    }

    const cacheKey = `${currentAnalysis.id}_${fieldKey}`;
    const isLoading = translating[cacheKey];

    return (
      <div className="flex flex-col gap-3">
        <div className="whitespace-pre-wrap">{englishText}</div>
        {(sinhalaText || isLoading) && (
          <div className="mt-2 pt-3 border-t border-[#1E2235]/60 flex flex-col gap-2 transition-all duration-300 ease-in-out">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold text-indigo-400 tracking-wider uppercase bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 font-sans">
                සිංහල පරිවර්තනය • Sinhala Translation
              </span>
            </div>
            <div className="text-gray-300 leading-relaxed font-sans text-[13px] bg-[#0E101A]/60 p-3.5 rounded-lg border border-[#1E2235]/80 min-h-[45px] flex flex-col justify-center shadow-inner">
              {isLoading ? (
                <div className="flex items-center gap-2 text-indigo-400 text-xs py-1">
                  <svg className="animate-spin h-3.5 w-3.5 text-indigo-400" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>පරිවර්තනය වෙමින් පවතී... (Translating...)</span>
                </div>
              ) : (
                <div className="whitespace-pre-wrap font-normal leading-relaxed">{sinhalaText}</div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };


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

  const getTradingViewSymbol = (symbolStr: string) => {
    const sym = (symbolStr || "BTC").toUpperCase().trim();
    if (sym === "GOLD" || sym === "XAUUSD" || sym === "XAU/USD") {
      return "OANDA:XAUUSD";
    }
    if (sym === "EURUSD" || sym === "EUR/USD") {
      return "FX:EURUSD";
    }
    if (sym === "GBPUSD" || sym === "GBP/USD") {
      return "FX:GBPUSD";
    }
    if (sym.includes(":")) {
      return sym;
    }
    const hasUsdt = sym.endsWith("USDT") || sym.endsWith("USD");
    return `BINANCE:${sym}${hasUsdt ? "" : "USDT"}`;
  };

  const getOverlayLevels = () => {
    if (!sbResult) return null;
    
    const entryMatch = sbResult.entry_price_area?.match(/\d+(?:\.\d+)?/);
    if (!entryMatch) return null;
    const entry = parseFloat(entryMatch[0]);
    
    const sl = sbResult.stop_loss_level;
    const tp = sbResult.liquidity_target;
    
    if (!entry || !sl || !tp) return null;
    
    const prices = [entry, sl, tp];
    const maxP = Math.max(...prices);
    const minP = Math.min(...prices);
    const span = maxP - minP || 1.0;
    
    const chartMax = maxP + span * 0.15;
    const chartMin = minP - span * 0.15;
    const chartSpan = chartMax - chartMin;
    
    const getYPct = (price: number) => {
      const pct = ((chartMax - price) / chartSpan) * 100;
      return 15 + (pct / 100) * 40;
    };
    
    const slPct = ((sl - entry) / entry) * 100;
    const tpPct = ((tp - entry) / entry) * 100;
    
    return {
      entry,
      entryY: getYPct(entry),
      sl,
      slY: getYPct(sl),
      slPct: slPct.toFixed(2),
      tp,
      tpY: getYPct(tp),
      tpPct: tpPct.toFixed(2)
    };
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
          <button
            onClick={() => setActiveView("silverbullet")}
            id="btn-silver-bullet"
            className={`px-4 py-2 rounded-lg text-xs font-semibold tracking-wider uppercase transition-all flex items-center gap-1.5 ${
              activeView === "silverbullet"
                ? "bg-[#6366F1] text-white shadow-md shadow-indigo-500/10"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Silver Bullet
          </button>
          <button
            onClick={() => setActiveView("smc")}
            id="btn-smc-method"
            className={`px-4 py-2 rounded-lg text-xs font-semibold tracking-wider uppercase transition-all flex items-center gap-1.5 ${
              activeView === "smc"
                ? "bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-500/20"
                : "text-gray-400 hover:text-gray-200"
            }`}
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            SMC Method
          </button>
        </div>

        <div className="flex items-center gap-4">
          {/* Gemini API Status Badge */}
          <div 
            className="flex items-center gap-2 bg-[#161924] border px-3.5 py-1.5 rounded-lg text-sm select-none transition-all duration-300"
            title={geminiStatus.details}
            style={{
              borderColor: 
                geminiStatus.status === "VALID" ? "rgba(16, 185, 129, 0.2)" :
                geminiStatus.status === "INVALID" ? "rgba(239, 68, 68, 0.3)" :
                geminiStatus.status === "HIGH_DEMAND" ? "rgba(245, 158, 11, 0.3)" :
                geminiStatus.status === "MISSING" ? "rgba(107, 114, 128, 0.2)" :
                geminiStatus.status === "ERROR" ? "rgba(239, 68, 68, 0.3)" :
                "rgba(59, 130, 246, 0.2)"
            }}
          >
            <span className={`w-2.5 h-2.5 rounded-full ${
              geminiStatus.status === "VALID" ? "bg-emerald-500 animate-pulse" :
              geminiStatus.status === "INVALID" ? "bg-rose-500" :
              geminiStatus.status === "HIGH_DEMAND" ? "bg-amber-500 animate-bounce" :
              geminiStatus.status === "MISSING" ? "bg-gray-500" :
              geminiStatus.status === "ERROR" ? "bg-rose-500" :
              "bg-blue-500 animate-ping"
            }`}></span>
            <span 
              className="font-semibold text-xs tracking-wider uppercase font-mono"
              style={{
                color: 
                  geminiStatus.status === "VALID" ? "#34D399" :
                  geminiStatus.status === "INVALID" ? "#F87171" :
                  geminiStatus.status === "HIGH_DEMAND" ? "#FBBF24" :
                  geminiStatus.status === "MISSING" ? "#9CA3AF" :
                  geminiStatus.status === "ERROR" ? "#F87171" :
                  "#60A5FA"
              }}
            >
              {
                geminiStatus.status === "VALID" ? "GEMINI ACTIVE" :
                geminiStatus.status === "INVALID" ? "GEMINI INVALID" :
                geminiStatus.status === "HIGH_DEMAND" ? "GEMINI BUSY" :
                geminiStatus.status === "MISSING" ? "NO GEMINI KEY" :
                geminiStatus.status === "ERROR" ? "GEMINI ERROR" :
                "CHECKING GEMINI"
              }
            </span>
          </div>

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
      <main className={`flex-1 p-6 ${activeView !== "dashboard" ? "flex flex-col" : "grid grid-cols-1 xl:grid-cols-4"} gap-6 max-w-[1800px] w-full mx-auto pb-16`}>
        
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
        ) : activeView === "silverbullet" ? (
          <section className="flex flex-col gap-6 w-full animate-fadeIn" id="silver-bullet-section">
            <div className="flex flex-col gap-1">
              <h2 className="text-xl font-bold tracking-tight text-white uppercase flex items-center gap-2">
                <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                ICT Silver Bullet Assistant
                <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded font-mono ml-2">Multi-Asset Support</span>
              </h2>
              <p className="text-xs text-gray-400">Evaluate Daily Bias and Liquidity Sweeps programmatically or via AI scenario logic.</p>
            </div>

            {/* Economic News Alerts Widget */}
            <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-4 shadow-xl flex flex-col gap-3 relative overflow-hidden">
              {sbResult?.news_lockout_active && (
                <div className="absolute -inset-0.5 bg-rose-500/10 rounded-2xl blur-md pointer-events-none animate-pulse" />
              )}
              
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 relative z-10">
                <div className="flex items-center gap-2">
                  <span className="flex h-2 w-2 relative">
                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${sbResult?.news_lockout_active ? "bg-rose-400" : "bg-emerald-400"}`} />
                    <span className={`relative inline-flex rounded-full h-2 w-2 ${sbResult?.news_lockout_active ? "bg-rose-500" : "bg-emerald-500"}`} />
                  </span>
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest font-mono">Dynamic Economic Calendar (USD High-Impact)</span>
                </div>
                
                {sbResult?.news_lockout_active && (
                  <span className="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[10px] font-bold px-2.5 py-1 rounded-lg font-mono flex items-center gap-1.5 animate-pulse animate-duration-1000">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-400 animate-ping" />
                    ⚠️ NEWS LOCKOUT ACTIVE: {sbResult.active_news_event} (+/- 60m)
                  </span>
                )}
              </div>

              {sbResult?.upcoming_news_events && sbResult.upcoming_news_events.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mt-1 relative z-10">
                  {sbResult.upcoming_news_events.map((event: any, i: number) => {
                    const isUpcoming = event.seconds_remaining > 0;
                    const isWithinLockout = Math.abs(event.seconds_remaining) <= 3600;
                    
                    let countdownLabel = "";
                    if (isUpcoming) {
                      const minutes = Math.floor(event.seconds_remaining / 60);
                      if (minutes < 60) countdownLabel = `in ${minutes}m`;
                      else countdownLabel = `in ${Math.floor(minutes / 60)}h ${minutes % 60}m`;
                    } else {
                      const minutes = Math.floor(Math.abs(event.seconds_remaining) / 60);
                      countdownLabel = `${minutes}m ago`;
                    }

                    return (
                      <div 
                        key={i} 
                        className={`border rounded-xl p-3 flex flex-col gap-1 transition-all ${
                          isWithinLockout 
                            ? "bg-rose-500/5 border-rose-500/30 text-rose-200 shadow-md shadow-rose-500/5 animate-pulse" 
                            : "bg-[#141626]/40 border-[#1E2235]/60 hover:border-gray-700/60"
                        }`}
                      >
                        <div className="flex justify-between items-center">
                          <span className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded font-mono ${
                            isWithinLockout ? "bg-rose-500/20 text-rose-300" : "bg-[#1E2235] text-gray-300"
                          }`}>
                            {event.country}
                          </span>
                          <span className={`text-[9px] font-bold font-mono ${
                            isWithinLockout ? "text-rose-400 animate-pulse" : isUpcoming ? "text-indigo-400" : "text-gray-500"
                          }`}>
                            {countdownLabel}
                          </span>
                        </div>
                        <span className="text-xs font-semibold truncate text-white leading-relaxed">{event.title}</span>
                        <span className="text-[9px] font-medium text-gray-400 font-mono mt-0.5">{event.time_slst} SLST</span>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-4 bg-[#141626]/20 border border-[#1E2235]/40 rounded-xl relative z-10">
                  <span className="text-xs text-gray-500 font-mono">No upcoming high-impact USD economic events scheduled for today.</span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              {/* INPUT PANEL */}
              <div className="lg:col-span-5 bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-6 shadow-xl flex flex-col gap-5">
                <div className="flex items-center justify-between border-b border-[#1E2235] pb-4">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold tracking-wide text-white">Scenario Input</h3>
                    <button
                      type="button"
                      onClick={() => {
                        setSbResult(null);
                        setSbLoading(false);
                      }}
                      className="px-2.5 py-1 rounded-lg bg-[#141626] border border-[#1E2235] text-[10px] font-bold font-mono tracking-wider text-gray-400 hover:text-indigo-400 hover:border-[#6366F1]/50 transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H18.235" />
                      </svg>
                      <span>REFRESH</span>
                    </button>
                  </div>
                  <div className="flex bg-[#141626] border border-[#1E2235] rounded-lg p-0.5">
                    <button
                      onClick={() => setSbInputMode("form")}
                      className={`px-3 py-1 rounded text-[11px] font-semibold transition-all ${
                        sbInputMode === "form"
                          ? "bg-[#6366F1] text-white shadow-md"
                          : "text-gray-400 hover:text-gray-200"
                      }`}
                    >
                      Form Builder
                    </button>
                    <button
                      onClick={() => setSbInputMode("text")}
                      className={`px-3 py-1 rounded text-[11px] font-semibold transition-all ${
                        sbInputMode === "text"
                          ? "bg-[#6366F1] text-white shadow-md"
                          : "text-gray-400 hover:text-gray-200"
                      }`}
                    >
                      Raw Scenario
                    </button>
                  </div>
                </div>

                <form onSubmit={triggerSilverBulletAnalysis} className="flex flex-col gap-4">
                  {/* Asset Symbol Input */}
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider font-mono">Trading Asset / Symbol</label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="e.g. GOLD, BTC, ETH, EURUSD..."
                        value={sbSymbol}
                        onChange={(e) => setSbSymbol(e.target.value.toUpperCase())}
                        className="bg-[#141626] border border-[#1E2235] rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none focus:border-[#6366F1] font-mono flex-grow"
                        required
                      />
                      <button
                        type="button"
                        onClick={fetchLivePrices}
                        disabled={sbSearchLoading || !sbSymbol.trim()}
                        className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800/40 text-white border border-indigo-500/20 px-4 py-2.5 rounded-xl text-xs font-semibold font-mono tracking-wide transition-all shadow-md active:scale-95 flex items-center gap-1.5"
                      >
                        {sbSearchLoading ? (
                          <>
                            <svg className="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Searching...
                          </>
                        ) : (
                          <>
                            <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            Search
                          </>
                        )}
                      </button>
                    </div>
                    {sbSearchError && (
                      <span className="text-[10px] text-rose-400 font-semibold font-mono leading-relaxed mt-0.5">{sbSearchError}</span>
                    )}
                  </div>

                  {sbInputMode === "form" ? (
                    <div className="flex flex-col gap-4">
                      {/* Trend and Pullback */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">HTF Trend (Daily)</label>
                          <select
                            value={sbHtfTrend}
                            onChange={(e) => setSbHtfTrend(e.target.value)}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          >
                            <option value="BULLISH">Bullish (Higher Highs/Lows)</option>
                            <option value="BEARISH">Bearish (Lower Highs/Lows)</option>
                            <option value="CONSOLIDATING">Consolidating / Range</option>
                          </select>
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Pullback Days</label>
                          <input
                            type="number"
                            min="0"
                            max="10"
                            value={sbPullbackDays}
                            onChange={(e) => setSbPullbackDays(Number(e.target.value))}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          />
                        </div>
                      </div>

                      {/* Daily Levels */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Previous Daily High (PDH)</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="e.g. 2350"
                            value={sbPdh}
                            onChange={(e) => setSbPdh(e.target.value === "" ? "" : Number(e.target.value))}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          />
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Previous Daily Low (PDL)</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="e.g. 2320"
                            value={sbPdl}
                            onChange={(e) => setSbPdl(e.target.value === "" ? "" : Number(e.target.value))}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          />
                        </div>
                      </div>

                      {/* Open / Close */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Daily Open (Optional)</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="e.g. 2325"
                            value={sbOpen}
                            onChange={(e) => setSbOpen(e.target.value === "" ? "" : Number(e.target.value))}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          />
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Daily Close (Optional)</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="e.g. 2330"
                            value={sbClose}
                            onChange={(e) => setSbClose(e.target.value === "" ? "" : Number(e.target.value))}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider font-mono">Dealing Range High</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="e.g. 2360"
                            value={sbDealingRangeHigh}
                            onChange={(e) => setSbDealingRangeHigh(e.target.value === "" ? "" : Number(e.target.value))}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          />
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider font-mono">Dealing Range Low</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="e.g. 2310"
                            value={sbDealingRangeLow}
                            onChange={(e) => setSbDealingRangeLow(e.target.value === "" ? "" : Number(e.target.value))}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          />
                        </div>
                      </div>

                      {/* Current Price & Killzone Session */}
                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider font-mono">Current Price</label>
                          <input
                            type="number"
                            step="0.01"
                            placeholder="e.g. 2323"
                            value={sbCurrentPrice}
                            onChange={(e) => setSbCurrentPrice(e.target.value === "" ? "" : Number(e.target.value))}
                            className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1]"
                          />
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <div className="flex justify-between items-center">
                            <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider font-mono">Killzone Session</label>
                            <label className="flex items-center gap-1 cursor-pointer">
                              <input 
                                type="checkbox" 
                                checked={sbAutoDetectSession} 
                                onChange={(e) => {
                                  setSbAutoDetectSession(e.target.checked);
                                  if (e.target.checked) {
                                    const nyString = new Date().toLocaleString("en-US", { timeZone: "America/New_York" });
                                    const nyDate = new Date(nyString);
                                    const hours = nyDate.getHours();
                                    if (hours === 3) setSbKillzone("LONDON_SB");
                                    else if (hours === 10) setSbKillzone("NY_AM_SB");
                                    else if (hours === 14) setSbKillzone("NY_PM_SB");
                                    else if (hours >= 2 && hours < 5) setSbKillzone("LONDON");
                                    else if (hours >= 7 && hours < 10) setSbKillzone("NY_AM");
                                    else setSbKillzone("NONE");
                                  }
                                }} 
                                className="w-2.5 h-2.5 rounded bg-[#141626] border-[#1E2235] text-indigo-500 focus:ring-0 cursor-pointer"
                              />
                              <span className="text-[9px] text-[#8B5CF6] font-bold font-mono">AUTO (SL/NY TIME)</span>
                            </label>
                          </div>
                          <select
                            value={sbKillzone}
                            onChange={(e) => {
                              setSbKillzone(e.target.value);
                              setSbAutoDetectSession(false);
                            }}
                            className={`bg-[#141626] border rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1] ${
                              sbAutoDetectSession ? "border-[#8B5CF6]/50 text-indigo-200" : "border-[#1E2235]"
                            }`}
                          >
                            <option value="LONDON_SB">London Open Silver Bullet (3AM - 4AM NY / 12:30PM - 1:30PM LK)</option>
                            <option value="NY_AM_SB">AM Session Silver Bullet (10AM - 11AM NY / 7:30PM - 8:30PM LK)</option>
                            <option value="NY_PM_SB">PM Session Silver Bullet (2PM - 3PM NY / 11:30PM - 12:30AM LK)</option>
                            <option value="LONDON">London Killzone (2AM - 5AM NY / 11:30AM - 2:30PM LK)</option>
                            <option value="NY_AM">New York AM Killzone (7AM - 10AM NY / 4:30PM - 7:30PM LK)</option>
                            <option value="ALL_TIME">All Time Analysis (24/7 Active)</option>
                            <option value="NONE">Outside Killzones (Inactive)</option>
                          </select>
                        </div>
                      </div>

                      {/* Dynamic 9:00 AM Candle Range inputs (specifically for NY AM Silver Bullet and AM Killzone) */}
                      {(sbKillzone === "NY_AM_SB" || sbKillzone === "NY_AM") && (
                        <div className="grid grid-cols-2 gap-4 animate-fadeIn border border-[#1E2235] bg-[#141626]/20 p-4 rounded-xl">
                          <div className="flex flex-col gap-1.5 col-span-2">
                            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider font-mono">Advanced 9:00 AM Range Filter</span>
                            <span className="text-[9px] text-gray-500">Scan for liquidity sweep of 9:00 AM 1H candle boundaries</span>
                          </div>
                          <div className="flex flex-col gap-1.5">
                            <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider font-mono">9:00 AM Candle High</label>
                            <input
                              type="number"
                              step="0.01"
                              placeholder="e.g. 2335"
                              value={sbCandle9amHigh}
                              onChange={(e) => setSbCandle9amHigh(e.target.value === "" ? "" : Number(e.target.value))}
                              className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1] font-mono"
                            />
                          </div>
                          <div className="flex flex-col gap-1.5">
                            <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider font-mono">9:00 AM Candle Low</label>
                            <input
                              type="number"
                              step="0.01"
                              placeholder="e.g. 2315"
                              value={sbCandle9amLow}
                              onChange={(e) => setSbCandle9amLow(e.target.value === "" ? "" : Number(e.target.value))}
                              className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-[#6366F1] font-mono"
                            />
                          </div>
                        </div>
                      )}

                      {/* Strategy Rules Checkboxes */}
                      <div className="flex flex-col gap-2.5 mt-2 bg-[#141626]/40 p-4 rounded-xl border border-[#1E2235]">
                        <span className="text-[10px] font-bold text-[#8B5CF6] uppercase tracking-wider">Session & Sweep Conditions</span>
                        
                        <label className="flex items-center gap-3 cursor-pointer select-none py-1">
                          <input
                            type="checkbox"
                            checked={sbAsianSweep}
                            onChange={(e) => {
                              setSbAsianSweep(e.target.checked);
                            }}
                            className="w-4 h-4 rounded text-indigo-600 bg-[#141626] border-[#1E2235] focus:ring-indigo-500"
                          />
                          <div className="flex flex-col">
                            <span className="text-xs font-semibold text-white">Asian Session Swept PDL</span>
                            <span className="text-[9px] text-gray-500">Retail sell-side liquidity swept before London</span>
                          </div>
                        </label>

                        <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                          <input
                            type="checkbox"
                            checked={sbDiscountPdArray}
                            onChange={(e) => {
                              setSbDiscountPdArray(e.target.checked);
                              setSbDemandMitigation(e.target.checked);
                            }}
                            className="w-4 h-4 rounded text-indigo-600 bg-[#141626] border-[#1E2235] focus:ring-indigo-500"
                          />
                          <div className="flex flex-col">
                            <span className="text-xs font-semibold text-white">Tapped Discount PD Array (OB/FVG)</span>
                            <span className="text-[9px] text-gray-500">Mitigated institutional buy zone under 50% Equilibrium</span>
                          </div>
                        </label>

                        <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                          <input
                            type="checkbox"
                            checked={sbPremiumPdArray}
                            onChange={(e) => setSbPremiumPdArray(e.target.checked)}
                            className="w-4 h-4 rounded text-indigo-600 bg-[#141626] border-[#1E2235] focus:ring-indigo-500"
                          />
                          <div className="flex flex-col">
                            <span className="text-xs font-semibold text-white">Tapped Premium PD Array (OB/FVG)</span>
                            <span className="text-[9px] text-gray-500">Mitigated institutional sell zone above 50% Equilibrium</span>
                          </div>
                        </label>

                        {/* LTF Shift Type Dropdown inside Checkbox section */}
                        <div className="flex flex-col gap-1 border-t border-[#1E2235]/40 mt-1 pt-2 pb-1">
                          <span className="text-xs font-semibold text-white">LTF Structural Shift (M15/M5)</span>
                          <select
                            value={sbLtfTrigger}
                            onChange={(e) => {
                              setSbLtfTrigger(e.target.value);
                              setSbLtfShift(e.target.value !== "NONE");
                            }}
                            className="bg-[#141626] border border-[#1E2235] rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-[#6366F1] mt-1"
                          >
                            <option value="MSS">MSS (Market Structure Shift)</option>
                            <option value="CISD">CISD (Change in State of Delivery)</option>
                            <option value="NONE">None / No Shift</option>
                          </select>
                        </div>

                        <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                          <input
                            type="checkbox"
                            checked={sbHasFreshFvg}
                            onChange={(e) => setSbHasFreshFvg(e.target.checked)}
                            className="w-4 h-4 rounded text-indigo-600 bg-[#141626] border-[#1E2235] focus:ring-indigo-500"
                          />
                          <div className="flex flex-col">
                            <span className="text-xs font-semibold text-white">Fresh FVG Formed at Shift Point</span>
                            <span className="text-[9px] text-gray-500">Validates institutional momentum displacement</span>
                          </div>
                        </label>

                        <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                          <input
                            type="checkbox"
                            checked={sbHighImpactNews}
                            onChange={(e) => setSbHighImpactNews(e.target.checked)}
                            className="w-4 h-4 rounded text-indigo-600 bg-[#141626] border-[#1E2235] focus:ring-indigo-500"
                          />
                          <div className="flex flex-col">
                            <span className="text-xs font-semibold text-rose-400">High-Impact News Release (NFP/CPI/FOMC)</span>
                            <span className="text-[9px] text-gray-500">Enable to test safety lockout filters</span>
                          </div>
                        </label>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider font-mono">Market Scenario / Notes</label>
                      <textarea
                        placeholder="Paste or write your market observations here... (e.g. HTF trend is bullish. Pullback of 3 days. Yesterday PDH 2350, PDL 2320. Asian session swept PDL and hit demand at 2318. Now we saw structure shift...)"
                        value={sbScenarioText}
                        onChange={(e) => setSbScenarioText(e.target.value)}
                        className="bg-[#141626] border border-[#1E2235] rounded-xl px-4 py-3 text-xs text-white focus:outline-none focus:border-[#6366F1] h-64 font-mono leading-relaxed"
                      />
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={sbLoading}
                    className="mt-2 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] hover:from-[#5053df] hover:to-[#7c4ee5] text-white text-xs font-bold py-3.5 rounded-xl transition-all shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2 disabled:opacity-55 cursor-pointer"
                  >
                    {sbLoading ? (
                      <>
                        <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                        Evaluating setup...
                      </>
                    ) : (
                      <>
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 002-2" />
                        </svg>
                        Analyze Strategy Setup
                      </>
                    )}
                  </button>
                </form>

                {/* TradingView RSI Chart for Silver Bullet */}
                <div className="bg-[#141626]/60 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-2 h-[520px] mt-2 relative">
                  <div className="flex justify-between items-center px-1">
                    <span className="text-[10px] font-semibold text-[#8B5CF6] uppercase tracking-widest font-mono">Relative Strength Index (RSI)</span>
                    <a
                      href={`https://www.tradingview.com/chart/?symbol=${getTradingViewSymbol(sbSymbol)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[10px] text-indigo-400 hover:text-indigo-300 transition-colors font-semibold flex items-center gap-1 font-mono"
                    >
                      Open in TradingView ↗
                    </a>
                  </div>
                  <div className="flex-1 w-full rounded-lg overflow-hidden border border-[#1E2235]/40 bg-black/40 relative">
                    <iframe
                      id="tradingview-sb-rsi-widget"
                      src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview-sb-rsi-widget&symbol=${getTradingViewSymbol(sbSymbol)}&interval=240&theme=dark&style=1&timezone=America%2FNew_York&studies=RSI%40tv-basicstudies&hide_volume=true`}
                      className="w-full h-full border-none"
                      allowFullScreen
                    />
                    
                    {/* Dynamic TradingView Overlay Levels */}
                    {(() => {
                      const levels = getOverlayLevels();
                      if (!levels) return null;
                      
                      return (
                        <div className="absolute inset-0 pointer-events-none z-10 font-mono">
                          {/* Take Profit (TP) Line */}
                          <div 
                            className="absolute left-0 right-0 border-t border-emerald-500/80 flex justify-between items-center transition-all duration-300"
                            style={{ top: `${levels.tpY}%` }}
                          >
                            <div className="h-[1px] bg-gradient-to-r from-emerald-500/80 to-transparent w-24" />
                            <span className="absolute right-4 transform -translate-y-1/2 bg-emerald-500 text-black text-[9px] font-extrabold px-1.5 py-0.5 rounded shadow-lg flex items-center gap-1">
                              <span>TP (1:4.0R)</span>
                              <span className="opacity-75">(+{levels.tpPct}%)</span>
                              <span className="bg-black/15 px-1 rounded">{levels.tp.toFixed(2)}</span>
                            </span>
                          </div>

                          {/* Entry Line */}
                          <div 
                            className="absolute left-0 right-0 border-t-2 border-dashed border-amber-500/80 flex justify-between items-center transition-all duration-300"
                            style={{ top: `${levels.entryY}%` }}
                          >
                            <div className="h-[1px] bg-gradient-to-r from-amber-500/80 to-transparent w-24" />
                            <span className="absolute right-4 transform -translate-y-1/2 bg-amber-500 text-black text-[9px] font-extrabold px-1.5 py-0.5 rounded shadow-lg flex items-center gap-1 animate-pulse">
                              <span>ENTRY</span>
                              <span className="bg-black/15 px-1 rounded">{levels.entry.toFixed(2)}</span>
                            </span>
                          </div>

                          {/* Stop Loss (SL) Line */}
                          <div 
                            className="absolute left-0 right-0 border-t border-rose-500/80 flex justify-between items-center transition-all duration-300"
                            style={{ top: `${levels.slY}%` }}
                          >
                            <div className="h-[1px] bg-gradient-to-r from-rose-500/80 to-transparent w-24" />
                            <span className="absolute right-4 transform -translate-y-1/2 bg-rose-500 text-white text-[9px] font-extrabold px-1.5 py-0.5 rounded shadow-lg flex items-center gap-1">
                              <span>STOP</span>
                              <span className="opacity-75">({levels.slPct}%)</span>
                              <span className="bg-black/25 px-1 rounded">{levels.sl.toFixed(2)}</span>
                            </span>
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>

                {/* Active Live Scanners Block */}
                <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-6 shadow-xl flex flex-col gap-5 mt-6">
                  <h2 className="text-md font-semibold tracking-wide text-white flex items-center gap-2">
                    <span className="relative flex h-2 w-2">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    Active Live Scanners (Running Setups)
                  </h2>
                  <div className="flex flex-col gap-2.5 max-h-[300px] overflow-y-auto pr-1">
                    {trackers.length === 0 ? (
                      <p className="text-xs text-gray-500 text-center py-6 font-mono">No active scanners running currently. Set a trade setup above and click "Track Setup" to monitor it here.</p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {trackers.map((tracker) => (
                          <div 
                            key={tracker.symbol} 
                            onClick={() => handleSelectTracker(tracker)}
                            className="bg-[#141626]/60 border border-[#1E2235] hover:border-[#6366F1]/50 rounded-xl p-4 flex flex-col gap-2 transition-all cursor-pointer hover:bg-[#1c1f35]/80 hover:shadow-lg hover:shadow-indigo-500/5 select-none"
                            title={`Click to view ${tracker.symbol} setup details`}
                          >
                            <div className="flex justify-between items-center">
                              <span className="font-bold text-sm text-white font-mono">{tracker.symbol}</span>
                              <div className="flex items-center gap-1.5">
                                <span className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded font-mono ${
                                  tracker.status === "ENTRY READY" ? "bg-emerald-500/20 text-emerald-400 animate-pulse" : "bg-[#1E2235] text-indigo-400"
                                }`}>
                                  {tracker.status}
                                </span>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleStopTracking(tracker.symbol);
                                  }}
                                  className="text-gray-500 hover:text-rose-400 text-xs transition-colors cursor-pointer p-1"
                                  title="Stop tracking"
                                >
                                  ✕
                                </button>
                              </div>
                            </div>
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-gray-400 font-mono">Confluences:</span>
                              <span className={`font-mono font-bold ${
                                tracker.confluences >= 10 ? "text-emerald-400" : tracker.confluences >= 7 ? "text-indigo-400" : "text-gray-400"
                              }`}>{tracker.confluences}/16</span>
                            </div>
                            {/* Progress Bar */}
                            <div className="w-full bg-[#1E2235] h-1.5 rounded-full overflow-hidden">
                              <div 
                                className={`h-full transition-all duration-500 ${
                                  tracker.confluences >= 10 ? "bg-emerald-400" : tracker.confluences >= 7 ? "bg-indigo-400" : "bg-gray-500"
                                }`}
                                style={{ width: `${(tracker.confluences / 16) * 100}%` }}
                              />
                            </div>
                            <div className="flex justify-between items-center text-[10px] text-gray-500 font-mono mt-0.5">
                              <span>Price:</span>
                              <span>${tracker.current_price?.toFixed(2)}</span>
                            </div>
                            
                            {/* Confidence Rate Display */}
                            <div className="flex justify-between items-center text-[10px] border-t border-[#1E2235]/40 pt-1.5 mt-1 font-mono">
                              <span className="text-gray-400">Confidence:</span>
                              <span className={`font-bold ${
                                (tracker.confidence || 0) >= 70 ? "text-emerald-400 font-extrabold" : "text-gray-400"
                              }`}>
                                {tracker.confidence || 0}% {(tracker.confidence || 0) >= 70 ? "🔥 (READY)" : ""}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* OUTPUT PANEL */}
              <div className="lg:col-span-7 bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-6 shadow-xl flex flex-col gap-6 min-h-[500px]">
                {!sbResult && !sbLoading && (
                  <div className="flex-1 flex flex-col items-center justify-center text-center p-10 gap-4">
                    <div className="w-16 h-16 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <h4 className="text-sm font-semibold text-white">Awaiting Strategy Inputs</h4>
                    <p className="text-xs text-gray-500 max-w-sm">Use the Form Builder or Raw Scenario tab to configure the current market scenario, then click Analyze.</p>
                  </div>
                )}

                {sbLoading && (
                  <div className="flex-1 flex flex-col items-center justify-center text-center p-10 gap-4">
                    <div className="relative w-16 h-16">
                      <div className="absolute inset-0 border-4 border-indigo-500/10 rounded-full"></div>
                      <div className="absolute inset-0 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    </div>
                    <h4 className="text-sm font-semibold text-indigo-400 animate-pulse">Running Technical Rules Analysis...</h4>
                    <p className="text-xs text-gray-500 max-w-sm">Gemini is checking the daily bias conditions, identifying the sweep of PDL, and verifying demand mitigation zones.</p>
                  </div>
                )}

                {sbResult && (
                  <div className="flex flex-col gap-6">
                    {!sbResult.is_valid ? (
                      <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-5 flex items-start gap-3 shadow-[0_0_15px_rgba(245,158,11,0.05)] w-full">
                        <svg className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <div className="flex flex-col gap-1 w-full">
                          <div className="flex items-center justify-between w-full">
                            <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Incomplete Information Warning</h4>
                            <button
                              type="button"
                              onClick={() => handleTrackSetup(sbSymbol)}
                              className="bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 text-[10px] font-bold py-1.5 px-3 rounded-lg transition-all cursor-pointer active:scale-95 flex items-center gap-1"
                            >
                              Track Setup 🛰️
                            </button>
                          </div>
                          <p className="text-xs text-gray-300 font-mono leading-relaxed mt-1">{sbResult.status_message}</p>
                        </div>
                      </div>
                    ) : (
                      <>
                        {/* Bias Header Banner */}
                        <div className="bg-[#141626]/60 border border-[#1E2235] p-5 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative overflow-hidden">
                          <div className="absolute right-0 top-0 w-32 h-32 bg-[#6366F1]/5 rounded-full blur-3xl pointer-events-none"></div>
                          <div className="flex flex-col gap-1">
                            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider font-mono">Daily bias report</span>
                            <div className="flex items-baseline gap-2">
                              <h3 className="text-xl font-bold text-white">{sbSymbol}</h3>
                              <span className="text-[10px] text-gray-400 font-semibold font-mono">London Session Bias</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-400 font-medium">Session Bias:</span>
                            <div className={`px-4 py-2 rounded-xl text-xs font-extrabold tracking-wider border ${
                              sbResult.daily_bias === "BULLISH" 
                                ? "text-emerald-400 border-emerald-500/20 bg-emerald-500/5 shadow-[0_0_15px_rgba(16,185,129,0.1)]" 
                                : "text-amber-400 border-amber-500/20 bg-amber-500/5"
                            }`}>
                              {sbResult.daily_bias}
                            </div>
                          </div>
                        </div>

                        {/* Advanced Computed Banners */}
                        <div className="flex flex-col gap-4">
                          {sbResult.counter_trend_locked && (
                            <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-5 flex items-start gap-3 shadow-[0_0_15px_rgba(244,63,94,0.05)]">
                              <svg className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <div className="flex flex-col gap-1">
                                <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider">⚠️ Strategy Rule Lockout</h4>
                                <p className="text-xs text-gray-300 leading-relaxed font-sans mt-1">
                                  Silver Bullet execution has locked this setup. Reasons: Buys are strictly locked in the Premium Zone (&gt; 50% Equilibrium), above the Daily Open, or high-impact news release is active.
                                </p>
                                <span className="text-[10px] text-rose-300/85 font-sans mt-0.5">
                                  සිංහල: Premium Zone එක තුළ මිලදී ගැනීම් (Buys) සිදු කිරීම සපුරා තහනම් බැවින් හෝ පුවත් විකාශනයක් නිසා setup එක අවහිර කර ඇත.
                                </span>
                              </div>
                            </div>
                          )}

                          {/* Pre-Warning Setup Alert */}
                          {sbResult.is_valid && sbResult.daily_bias === "NEUTRAL" && !sbResult.counter_trend_locked && sbResult.entry_price_area && sbResult.entry_price_area !== "No Entry Triggered" && sbResult.entry_price_area !== "No Entry Triggered (Poor RR)" && (
                            <div className="bg-[#4F46E5]/10 border border-[#4F46E5]/30 rounded-xl p-5 flex items-start gap-3 shadow-[0_0_15px_rgba(79,70,229,0.08)] animate-pulse">
                              <svg className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <div className="flex flex-col gap-1 w-full">
                                <div className="flex justify-between items-center">
                                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">⏳ Pre-Warning: Potential Setup Forming</h4>
                                  <span className="text-[9px] font-bold bg-[#4F46E5]/20 text-indigo-300 px-2 py-0.5 rounded font-mono">EST. 5 MINS TO TRIGGER</span>
                                </div>
                                <p className="text-xs text-gray-300 leading-relaxed font-sans mt-1 font-mono">
                                  {sbResult.advanced_setup_status === "9AM_LOW_SWEPT_MSS_PENDING" || sbResult.swept_liquidity_pool === "PDL_SSL"
                                    ? "Liquidity has been swept! A potential BUY setup is forming. Wait for M1/M5 Market Structure Shift (MSS) and fresh FVG confirmation before entering."
                                    : "Liquidity has been swept! A potential SELL setup is forming. Wait for M1/M5 Market Structure Shift (MSS) and fresh FVG confirmation before entering."
                                  }
                                </p>
                                <div className="grid grid-cols-3 gap-2 mt-3 bg-black/40 p-2.5 rounded-lg border border-[#4F46E5]/20 text-xs font-mono">
                                  <div className="flex flex-col">
                                    <span className="text-[9px] text-gray-500 uppercase">Est. Entry Area</span>
                                    <span className="text-white font-bold">{sbResult.entry_price_area}</span>
                                  </div>
                                  <div className="flex flex-col">
                                    <span className="text-[9px] text-gray-500 uppercase">Est. Stop-Loss</span>
                                    <span className="text-rose-400 font-bold">{sbResult.stop_loss_level || "N/A"}</span>
                                  </div>
                                  <div className="flex flex-col">
                                    <span className="text-[9px] text-gray-500 uppercase">Est. Reward (1:3)</span>
                                    <span className="text-emerald-400 font-bold">{sbResult.liquidity_target || "N/A"}</span>
                                  </div>
                                </div>
                                <span className="text-[10px] text-indigo-300/85 font-sans mt-2">
                                  {sbResult.advanced_setup_status === "9AM_LOW_SWEPT_MSS_PENDING" || sbResult.swept_liquidity_pool === "PDL_SSL"
                                    ? "සිංහල: ද්‍රවශීලතාවය (Liquidity) sweep කර ඇත! මිලදී ගැනීමේ (BUY) setup එකක් සෑදෙමින් පවතී. M1/M5 MSS තහවුරු වූ පසු ළඟ TP සහ tight SL සහිතව ඇතුල් වීමට සූදානම් වන්න."
                                    : "සිංහල: ද්‍රවශීලතාවය (Liquidity) sweep කර ඇත! විකිණීමේ (SELL) setup එකක් සෑදෙමින් පවතී. M1/M5 MSS තහවුරු වූ පසු ළඟ TP සහ tight SL සහිතව ඇතුල් වීමට සූදානම් වන්න."
                                  }
                                </span>
                              </div>
                            </div>
                          )}

                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            {/* Equilibrium Zone Card */}
                            {sbResult.equilibrium_price && (
                              <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-1.5">
                                <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-wider font-mono">50% Fibonacci Equilibrium</h4>
                                <div className="flex items-center justify-between mt-1">
                                  <span className="text-sm font-bold text-white font-mono">{Number(sbResult.equilibrium_price).toFixed(2)}</span>
                                  <span className={`text-[9px] font-extrabold tracking-wider px-2 py-1 rounded-lg border ${
                                    sbResult.zone_type === "DISCOUNT" 
                                      ? "text-emerald-400 border-emerald-500/20 bg-emerald-500/5"
                                      : sbResult.zone_type === "PREMIUM"
                                        ? "text-rose-400 border-rose-500/20 bg-rose-500/5"
                                        : "text-gray-400 border-gray-500/20 bg-gray-500/5"
                                  }`}>
                                    {sbResult.zone_type} ZONE
                                  </span>
                                </div>
                              </div>
                            )}

                            {/* Daily Open Relation Card */}
                            {sbResult.daily_open_relation && (
                              <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-1.5">
                                <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-wider font-mono">Daily Open Reference</h4>
                                <div className="flex items-center justify-between mt-1">
                                  <span className="text-xs font-bold text-gray-300 font-mono">Open: {sbOpen !== "" ? Number(sbOpen).toFixed(2) : "N/A"}</span>
                                  <span className={`text-[9px] font-extrabold tracking-wider px-2 py-1 rounded-lg border ${
                                    sbResult.daily_open_relation === "BELOW_OPEN" 
                                      ? "text-emerald-400 border-emerald-500/20 bg-emerald-500/5"
                                      : sbResult.daily_open_relation === "ABOVE_OPEN"
                                        ? "text-rose-400 border-rose-500/20 bg-rose-500/5"
                                        : "text-gray-400 border-gray-500/20 bg-gray-500/5"
                                  }`}>
                                    {sbResult.daily_open_relation === "BELOW_OPEN" ? "BELOW OPEN (Discount)" : sbResult.daily_open_relation === "ABOVE_OPEN" ? "ABOVE OPEN (Premium)" : "N/A"}
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Trade Parameters Table */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-2.5 md:col-span-2">
                            <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-wider font-mono">Market Structure Status</h4>
                            <div className="text-xs font-semibold text-white leading-relaxed font-sans">
                              {(() => {
                                const parsed = parseTextWithTranslation(sbResult.market_structure_status || "");
                                return (
                                  <div className="flex flex-col gap-2">
                                    <div className="whitespace-pre-wrap">{parsed.english}</div>
                                    {parsed.sinhala && (
                                      <div className="mt-1.5 pt-2 border-t border-[#1E2235]/40 flex flex-col gap-1.5 transition-all">
                                        <span className="text-[9px] font-bold text-indigo-400 tracking-wider uppercase font-sans">සිංහල පරිවර්තනය • Sinhala Translation</span>
                                        <div className="text-gray-300 font-sans text-[11px] whitespace-pre-wrap bg-[#0E101A]/40 p-2.5 rounded-lg border border-[#1E2235]/40">{parsed.sinhala}</div>
                                      </div>
                                    )}
                                  </div>
                                );
                              })()}
                            </div>
                          </div>

                          <div className={`bg-[#141626]/40 border rounded-xl p-4 flex flex-col gap-2.5 transition-all md:col-span-2 ${
                            sbResult.news_lockout_active 
                              ? "border-rose-500/50 shadow-md shadow-rose-500/5"
                              : sbResult.confidence && sbResult.confidence >= 70 
                                ? "border-indigo-500/50 shadow-md shadow-indigo-500/5" 
                                : "border-[#1E2235]/60"
                          }`}>
                            <div className="flex justify-between items-center">
                              <h4 className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider font-mono">Entry Price Area</h4>
                              <div className="flex items-center gap-1.5">
                                {sbResult.news_lockout_active ? (
                                  <span className="bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[9px] font-bold px-1.5 py-0.5 rounded font-mono flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping" />
                                    NEWS LOCKOUT
                                  </span>
                                ) : sbResult.entry_price_area && sbResult.entry_price_area.includes("Price Already Past Entry") ? (
                                  <span className="bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[9px] font-bold px-1.5 py-0.5 rounded font-mono flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping" />
                                    PRICE PAST ENTRY
                                  </span>
                                ) : sbResult.confidence !== undefined && sbResult.confidence !== null && (
                                  <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono flex items-center gap-1 ${
                                    sbResult.confidence >= 70 ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20" : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                  }`}>
                                    <span className={`w-1.5 h-1.5 rounded-full ${sbResult.confidence >= 70 ? "bg-indigo-400 animate-pulse" : "bg-rose-400"}`} />
                                    {sbResult.confidence}% CONFIRMED
                                  </span>
                                )}
                                {sbResult.daily_bias === "BULLISH" && (
                                  <span className="bg-emerald-500/10 text-emerald-400 text-[9px] font-bold px-2 py-0.5 rounded font-mono">BUY (LONG)</span>
                                )}
                                {sbResult.daily_bias === "BEARISH" && (
                                  <span className="bg-rose-500/10 text-rose-400 text-[9px] font-bold px-2 py-0.5 rounded font-mono">SELL (SHORT)</span>
                                )}
                                {sbResult.daily_bias === "NEUTRAL" && (
                                  <span className="bg-gray-500/10 text-gray-400 text-[9px] font-bold px-2 py-0.5 rounded font-mono">NEUTRAL</span>
                                )}
                              </div>
                            </div>
                            <span className="text-xs font-semibold text-white font-mono">{sbResult.entry_price_area || "N/A"}</span>
                          </div>

                          <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-2.5">
                            <h4 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider font-mono">Stop-Loss Level</h4>
                            <span className="text-xs font-semibold text-rose-400 font-mono flex items-center gap-1.5">
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                              </svg>
                              {sbResult.stop_loss_level || "N/A"}
                            </span>
                          </div>

                          <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-2.5">
                            <div className="flex justify-between items-center">
                              <h4 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider font-mono">Take Profit 1 (TP1)</h4>
                              <span className="bg-emerald-500/10 text-emerald-400 text-[9px] font-extrabold px-1.5 py-0.5 rounded font-mono">1:2.00 RR</span>
                            </div>
                            <span className="text-xs font-semibold text-emerald-400 font-mono flex items-center gap-1.5">
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 11l3-3m0 0l3 3m-3-3v8" />
                              </svg>
                              {tp1TargetFallback ? (typeof tp1TargetFallback === 'number' ? tp1TargetFallback.toFixed(4).replace(/\.?0+$/, '') : tp1TargetFallback) : "N/A"}
                            </span>
                          </div>

                          <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-2.5">
                            <div className="flex justify-between items-center">
                              <h4 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider font-mono">Take Profit 2 (TP2)</h4>
                              <span className="bg-emerald-500/10 text-emerald-400 text-[9px] font-extrabold px-1.5 py-0.5 rounded font-mono">1:4.00 RR</span>
                            </div>
                            <span className="text-xs font-semibold text-emerald-400 font-mono flex items-center gap-1.5">
                              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 11l7-7m0 0l7 7m-7-7v18" />
                              </svg>
                              {tp2TargetFallback ? (typeof tp2TargetFallback === 'number' ? tp2TargetFallback.toFixed(4).replace(/\.?0+$/, '') : tp2TargetFallback) : "N/A"}
                            </span>
                          </div>

                          <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-2.5">
                            <h4 className="text-[10px] font-bold text-[#8B5CF6] uppercase tracking-wider font-mono">Target Reward Ratio</h4>
                            <span className="text-xs font-semibold text-[#8B5CF6] font-mono">{sbResult.target_reward_ratio || "1:3 Minimum"}</span>
                          </div>
                          
                          <button
                            type="button"
                            onClick={() => handleTrackSetup(sbSymbol)}
                            className="bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-indigo-400 text-xs font-bold py-3 px-4 rounded-xl transition-all shadow-md flex items-center justify-center gap-1.5 md:col-span-2 cursor-pointer active:scale-95 animate-pulse"
                          >
                            Track Setup 🛰️
                          </button>

                          <button
                            type="button"
                            onClick={handleLogTrade}
                            disabled={logLoading || !sbResult}
                            className="bg-emerald-600/20 hover:bg-emerald-600/30 disabled:opacity-40 disabled:hover:bg-emerald-600/20 border border-emerald-500/30 text-emerald-400 text-xs font-bold py-3 px-4 rounded-xl transition-all shadow-md flex items-center justify-center gap-1.5 md:col-span-2 cursor-pointer active:scale-95"
                          >
                            {logLoading ? "Logging Trade..." : "Log Trade 📈"}
                          </button>
                        </div>

                        {/* Interactive SVG Diagram Visualizer */}
                        {sbResult && (
                          <div className="bg-black/20 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-2">
                            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">Dynamic Price Level Visualizer (Actual {sbSymbol || "SOL"} Levels)</span>
                            <div className="w-full h-80 bg-[#07080E] rounded-xl relative overflow-hidden border border-[#1E2235]/40 flex items-center justify-center">
                              {(() => {
                                const entryPriceVal = (() => {
                                  if (!sbResult.entry_price_area) return null;
                                  const matches = sbResult.entry_price_area.match(/\d+(?:\.\d+)?/g);
                                  if (!matches) return null;
                                  const pdlVal = Number(sbPdl);
                                  if (!isNaN(pdlVal) && pdlVal > 50) {
                                    const priceMatch = matches.find((m: string) => Number(m) > 50);
                                    if (priceMatch) return Number(priceMatch);
                                  }
                                  return Number(matches[matches.length - 1]);
                                })();

                                const pdhVal = Number(sbPdh) || 2350;
                                const pdlVal = Number(sbPdl) || 2320;
                                const openVal = Number(sbOpen) || ((pdhVal + pdlVal) / 2);
                                const currentPriceVal = Number(sbCurrentPrice) || openVal;
                                const eqPriceVal = sbResult.equilibrium_price ? Number(sbResult.equilibrium_price) : ((pdhVal + pdlVal) / 2);
                                const stopLossVal = sbResult.stop_loss_level ? Number(sbResult.stop_loss_level) : (pdlVal - (pdhVal - pdlVal) * 0.15);
                                const rangeP = pdhVal - pdlVal || 10;

                                // Margins for SVG y coordinates (60 to 250) - spreads the chart vertically
                                const svgMinY = 60;
                                const svgMaxY = 250;
                                const getSvgY = (price: number) => {
                                  if (isNaN(price)) return 155;
                                  return svgMaxY - ((price - pdlVal) / rangeP) * (svgMaxY - svgMinY);
                                };

                                const eqY = getSvgY(eqPriceVal);
                                const openY = getSvgY(openVal);
                                const currY = getSvgY(currentPriceVal);
                                const pdhY = getSvgY(pdhVal);
                                const pdlY = getSvgY(pdlVal);
                                const entryY = entryPriceVal ? getSvgY(entryPriceVal) : null;
                                const slY = getSvgY(stopLossVal);
                                // Detect if setup is BEARISH to dynamically invert the candles and labels for Sells
                                const isBearishSetup = sbResult.daily_bias === "BEARISH";

                                // Map 11 candle columns with wide spacing (60px step) for maximum TradingView look
                                const candles = isBearishSetup ? [
                                  // Bearish/Short Scenario (Inverted structure)
                                  // 1. Pullback Leg (Bullish candles ascending from PDL to PDH)
                                  { x: 40, open: getSvgY(pdlVal + rangeP * 0.05), close: getSvgY(pdlVal + rangeP * 0.3), high: getSvgY(pdlVal - rangeP * 0.05), low: getSvgY(pdlVal + rangeP * 0.35), isBullish: true },
                                  { x: 100, open: getSvgY(pdlVal + rangeP * 0.25), close: getSvgY(pdlVal + rangeP * 0.55), high: getSvgY(pdlVal + rangeP * 0.2), low: getSvgY(pdlVal + rangeP * 0.6), isBullish: true },
                                  { x: 160, open: getSvgY(pdlVal + rangeP * 0.5), close: getSvgY(pdlVal + rangeP * 0.8), high: getSvgY(pdlVal + rangeP * 0.45), low: getSvgY(pdlVal + rangeP * 0.85), isBullish: true },
                                  
                                  // 2. Consolidation before sweep
                                  { x: 220, open: getSvgY(pdhVal - rangeP * 0.2), close: getSvgY(pdhVal - rangeP * 0.1), high: getSvgY(pdhVal - rangeP * 0.25), low: getSvgY(pdhVal - rangeP * 0.05), isBullish: true },
                                  { x: 280, open: getSvgY(pdhVal - rangeP * 0.1), close: getSvgY(pdhVal - rangeP * 0.25), high: getSvgY(pdhVal - rangeP * 0.3), low: getSvgY(pdhVal - rangeP * 0.08), isBullish: false },
                                  
                                  // 3. PDH Liquidity Sweep (Sweeps above PDH high)
                                  { x: 340, open: getSvgY(pdhVal - rangeP * 0.12), close: getSvgY(pdhVal + rangeP * 0.05), high: getSvgY(pdhVal + rangeP * 0.25), low: getSvgY(pdhVal - rangeP * 0.2), isBullish: true, isSweep: true },
                                  
                                  // 4. MSS Breakout Leg Downward (Bearish candles breaking structure low)
                                  { x: 400, open: getSvgY(pdhVal + rangeP * 0.05), close: getSvgY(pdhVal - rangeP * 0.3), high: getSvgY(pdhVal + rangeP * 0.08), low: getSvgY(pdhVal - rangeP * 0.35), isBullish: false },
                                  { x: 460, open: getSvgY(pdhVal - rangeP * 0.25), close: getSvgY(pdhVal - rangeP * 0.65), high: getSvgY(pdhVal - rangeP * 0.2), low: getSvgY(pdhVal - rangeP * 0.7), isBullish: false, isMSS: true },
                                  
                                  // 5. Limit Entry Retest (Bullish candle tapping Premium Supply zone / FVG)
                                  { x: 520, open: getSvgY(pdhVal - rangeP * 0.65), close: getSvgY(pdhVal - rangeP * 0.38), high: getSvgY(pdhVal - rangeP * 0.68), low: getSvgY(pdhVal - rangeP * 0.35), isBullish: true, isEntry: true },
                                  
                                  // 6. Expansion down to PDL Target (Bearish expansion)
                                  { x: 580, open: getSvgY(pdhVal - rangeP * 0.45), close: getSvgY(pdlVal + rangeP * 0.15), high: getSvgY(pdhVal - rangeP * 0.4), low: getSvgY(pdlVal + rangeP * 0.15), isBullish: false },
                                  { x: 640, open: getSvgY(pdlVal + rangeP * 0.2), close: getSvgY(pdlVal - rangeP * 0.05), high: getSvgY(pdlVal + rangeP * 0.25), low: getSvgY(pdlVal - rangeP * 0.1), isBullish: false }
                                ] : [
                                  // Bullish/Long Scenario
                                  // 1. Pullback Leg (Bearish candles descending from PDH)
                                  { x: 40, open: getSvgY(pdhVal - rangeP * 0.05), close: getSvgY(pdhVal - rangeP * 0.3), high: getSvgY(pdhVal + rangeP * 0.05), low: getSvgY(pdhVal - rangeP * 0.35), isBullish: false },
                                  { x: 100, open: getSvgY(pdhVal - rangeP * 0.25), close: getSvgY(pdhVal - rangeP * 0.55), high: getSvgY(pdhVal - rangeP * 0.2), low: getSvgY(pdhVal - rangeP * 0.6), isBullish: false },
                                  { x: 160, open: getSvgY(pdhVal - rangeP * 0.5), close: getSvgY(pdhVal - rangeP * 0.8), high: getSvgY(pdhVal - rangeP * 0.45), low: getSvgY(pdhVal - rangeP * 0.85), isBullish: false },
                                  
                                  // 2. Consolidation before sweep
                                  { x: 220, open: getSvgY(pdlVal + rangeP * 0.2), close: getSvgY(pdlVal + rangeP * 0.1), high: getSvgY(pdlVal + rangeP * 0.25), low: getSvgY(pdlVal + rangeP * 0.05), isBullish: false },
                                  { x: 280, open: getSvgY(pdlVal + rangeP * 0.1), close: getSvgY(pdlVal + rangeP * 0.25), high: getSvgY(pdlVal + rangeP * 0.3), low: getSvgY(pdlVal + rangeP * 0.08), isBullish: true },
                                  
                                  // 3. Asian Sweep (Bearish candle sweeping low below PDL)
                                  { x: 340, open: getSvgY(pdlVal + rangeP * 0.12), close: getSvgY(pdlVal - rangeP * 0.05), high: getSvgY(pdlVal + rangeP * 0.2), low: getSvgY(pdlVal - rangeP * 0.25), isBullish: false, isSweep: true },
                                  
                                  // 4. MSS Breakout Leg (Bullish candles breaking structure)
                                  { x: 400, open: getSvgY(pdlVal - rangeP * 0.05), close: getSvgY(pdlVal + rangeP * 0.3), high: getSvgY(pdlVal - rangeP * 0.08), low: getSvgY(pdlVal + rangeP * 0.35), isBullish: true },
                                  { x: 460, open: getSvgY(pdlVal + rangeP * 0.25), close: getSvgY(pdlVal + rangeP * 0.65), high: getSvgY(pdlVal + rangeP * 0.2), low: getSvgY(pdlVal + rangeP * 0.7), isBullish: true, isMSS: true },
                                  
                                  // 5. Limit Entry Retest (Bearish candle tapping FVG/Discount)
                                  { x: 520, open: getSvgY(pdlVal + rangeP * 0.65), close: getSvgY(pdlVal + rangeP * 0.38), high: getSvgY(pdlVal + rangeP * 0.68), low: getSvgY(pdlVal + rangeP * 0.35), isBullish: false, isEntry: true },
                                  
                                  // 6. Expansion to PDH Target (Bullish expansion)
                                  { x: 580, open: getSvgY(pdlVal + rangeP * 0.45), close: getSvgY(pdhVal - rangeP * 0.15), high: getSvgY(pdlVal + rangeP * 0.4), low: getSvgY(pdhVal - rangeP * 0.15), isBullish: true },
                                  { x: 640, open: getSvgY(pdhVal - rangeP * 0.2), close: getSvgY(pdhVal + rangeP * 0.05), high: getSvgY(pdhVal - rangeP * 0.25), low: getSvgY(pdhVal + rangeP * 0.1), isBullish: true }
                                ];

                                const mssLineY = isBearishSetup ? getSvgY(pdhVal - rangeP * 0.3) : getSvgY(pdlVal + rangeP * 0.3);
                                const target1Val = entryPriceVal ? (isBearishSetup ? entryPriceVal - Math.abs(entryPriceVal - pdlVal) * 0.5 : entryPriceVal + Math.abs(pdhVal - entryPriceVal) * 0.5) : (isBearishSetup ? pdlVal + rangeP * 0.3 : pdhVal - rangeP * 0.3);
                                const target1Y = getSvgY(target1Val);
                                const target2Y = isBearishSetup ? pdlY : pdhY;

                                return (
                                  <svg className="w-full h-full p-2 bg-[#07080E]" viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg">
                                    <defs>
                                      <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#10B981" />
                                      </marker>
                                      <marker id="arrow-bearish" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                                        <path d="M 0 0 L 10 5 L 0 10 z" fill="#EF4444" />
                                      </marker>
                                    </defs>

                                    {/* Subtle Background Grid (Horizontal & Vertical) */}
                                    {Array.from({ length: 21 }).map((_, idx) => (
                                      <line key={`v-${idx}`} x1={33 * idx + 20} y1="10" x2={33 * idx + 20} y2="310" stroke="#1E2235" strokeOpacity="0.25" strokeWidth="0.5" />
                                    ))}
                                    {Array.from({ length: 11 }).map((_, idx) => (
                                      <line key={`h-${idx}`} x1="10" y1={25 + 26 * idx} x2="790" y2={25 + 26 * idx} stroke="#1E2235" strokeOpacity="0.25" strokeWidth="0.5" />
                                    ))}

                                    {/* Shaded Premium and Discount Zones */}
                                    <rect x="10" y={svgMinY} width="665" height={Math.max(0, eqY - svgMinY)} fill="#EF4444" fillOpacity="0.025" rx="2" />
                                    <rect x="10" y={eqY} width="665" height={Math.max(0, svgMaxY - eqY)} fill="#10B981" fillOpacity="0.025" rx="2" />

                                    {/* Center Chart Title */}
                                    <text x="338" y="28" textAnchor="middle" fill="#FFFFFF" fontSize="16" fontWeight="extrabold" fontFamily="sans-serif" letterSpacing="1.5">ICT Silver Bullet</text>
                                    
                                    {/* TradingView-Style Long/Short Position Tool Shading */}
                                    {sbResult.is_valid && entryY !== null && (
                                       <g>
                                         {isBearishSetup ? (
                                           // Bearish Short Position: Red Stop Loss above Entry, Green Targets below Entry
                                           <>
                                             {/* SL Red zone */}
                                             <rect x="500" y={Math.min(slY, entryY)} width="165" height={Math.abs(slY - entryY)} fill="#EF4444" fillOpacity="0.1" stroke="#EF4444" strokeWidth="0.75" strokeOpacity="0.25" />
                                             {/* Target Green zone */}
                                             <rect x="500" y={Math.min(entryY, target2Y)} width="165" height={Math.abs(entryY - target2Y)} fill="#10B981" fillOpacity="0.1" stroke="#10B981" strokeWidth="0.75" strokeOpacity="0.25" />
                                           </>
                                         ) : (
                                           // Bullish Long Position: Green Targets above Entry, Red Stop Loss below Entry
                                           <>
                                             {/* Target Green zone */}
                                             <rect x="500" y={Math.min(target2Y, entryY)} width="165" height={Math.abs(target2Y - entryY)} fill="#10B981" fillOpacity="0.1" stroke="#10B981" strokeWidth="0.75" strokeOpacity="0.25" />
                                             {/* SL Red zone */}
                                             <rect x="500" y={Math.min(entryY, slY)} width="165" height={Math.abs(entryY - slY)} fill="#EF4444" fillOpacity="0.1" stroke="#EF4444" strokeWidth="0.75" strokeOpacity="0.25" />
                                           </>
                                         )}
                                       </g>
                                     )}

                                    {/* Price Target and Level dashed lines */}
                                    <line x1="10" y1={pdhY} x2="675" y2={pdhY} stroke={isBearishSetup ? "#EF4444" : "#10B981"} strokeWidth="1" strokeDasharray="3,3" />
                                    <line x1="10" y1={eqY} x2="675" y2={eqY} stroke="#F59E0B" strokeWidth="0.75" strokeDasharray="3,3" />
                                    <line x1="10" y1={openY} x2="675" y2={openY} stroke="#6366F1" strokeWidth="0.75" strokeDasharray="2,2" />
                                    <line x1="10" y1={currY} x2="675" y2={currY} stroke="#E0E7FF" strokeWidth="1" strokeOpacity="0.6" />
                                    <line x1="10" y1={pdlY} x2="675" y2={pdlY} stroke={isBearishSetup ? "#10B981" : "#EF4444"} strokeWidth="1" strokeDasharray="3,3" />

                                    {/* Left Margin Helper Labels (Keeps chart center clean) */}
                                    <text x="20" y={pdhY - 6} fill={isBearishSetup ? "#EF4444" : "#10B981"} fontSize="9" fontWeight="bold" fontFamily="sans-serif">
                                      {isBearishSetup ? "PDH (Sweep Target)" : "PDH (Target)"}
                                    </text>
                                    <text x="20" y={pdlY + 12} fill={isBearishSetup ? "#10B981" : "#EF4444"} fontSize="9" fontWeight="bold" fontFamily="sans-serif">
                                      {isBearishSetup ? "PDL (Target)" : "PDL (Previous Daily Low)"}
                                    </text>

                                    {/* MSS / CHoCH Horizontal Breakout Line */}
                                    <line x1="300" y1={mssLineY} x2="430" y2={mssLineY} stroke="#FFFFFF" strokeWidth="1.5" strokeDasharray="1,1" />
                                    <text x="365" y={mssLineY - 6} textAnchor="middle" fill="#FFFFFF" fontSize="8" fontWeight="bold" fontFamily="sans-serif" letterSpacing="0.5">MSS / CHoCH</text>

                                    {/* Fair Value Gap (FVG) and Demand/Supply Shading */}
                                    {(() => {
                                       const fvgTop = isBearishSetup ? getSvgY(pdhVal - rangeP * 0.35) : getSvgY(pdlVal + rangeP * 0.55);
                                       const fvgBottom = isBearishSetup ? getSvgY(pdhVal - rangeP * 0.55) : getSvgY(pdlVal + rangeP * 0.35);
                                       return (
                                         <g>
                                           <rect x="350" y={Math.min(fvgTop, fvgBottom)} width="120" height={Math.abs(fvgTop - fvgBottom)} fill="#8B5CF6" fillOpacity="0.08" stroke="#8B5CF6" strokeWidth="0.75" strokeDasharray="2,2" rx="3" />
                                           <text x="358" y={Math.min(fvgTop, fvgBottom) + 13} fill="#C084FC" fontSize="8" fontWeight="bold" fontFamily="sans-serif">
                                             {isBearishSetup ? "Bearish FVG (Supply)" : "Bullish FVG (Demand)"}
                                           </text>
                                         </g>
                                       );
                                     })()}

                                    {/* Limit Entry Pointer Arrow */}
                                    {entryY !== null && (
                                      <g>
                                        {isBearishSetup ? (
                                          <>
                                            <path d={`M 570 ${entryY - 35} L 535 ${entryY - 6}`} fill="none" stroke="#EF4444" strokeWidth="1.5" markerEnd="url(#arrow-bearish)" />
                                            <text x="575" y={entryY - 32} fill="#EF4444" fontSize="10" fontWeight="bold" fontFamily="sans-serif">Limit Entry (Sell)</text>
                                          </>
                                        ) : (
                                          <>
                                            <path d={`M 570 ${entryY + 35} L 535 ${entryY + 6}`} fill="none" stroke="#10B981" strokeWidth="1.5" markerEnd="url(#arrow)" />
                                            <text x="575" y={entryY + 38} fill="#10B981" fontSize="10" fontWeight="bold" fontFamily="sans-serif">Limit Entry (Buy)</text>
                                          </>
                                        )}
                                      </g>
                                    )}

                                    {/* Stop Loss Line & Dotted Markers */}
                                    {(sbResult.daily_bias === "BULLISH" || sbResult.daily_bias === "BEARISH") && (
                                      <>
                                        <line x1="10" y1={slY} x2="675" y2={slY} stroke="#EF4444" strokeWidth="0.75" strokeDasharray="4,4" />
                                        <text x="20" y={isBearishSetup ? slY - 6 : slY + 12} fill="#EF4444" fontSize="8" fontWeight="bold" fontFamily="monospace">Stop Loss</text>
                                      </>
                                    )}

                                    {/* Target Lines inside Position Tool */}
                                    {sbResult.is_valid && entryPriceVal && (
                                       <>
                                         {/* Target 1 */}
                                         <line x1="500" y1={target1Y} x2="665" y2={target1Y} stroke="#34D399" strokeWidth="0.75" strokeDasharray="3,3" />
                                         <text x="508" y={isBearishSetup ? target1Y + 9 : target1Y - 4} fill="#34D399" fontSize="7" fontWeight="bold" fontFamily="monospace">Target 1 (1:1.5 RR)</text>

                                         {/* Target 2 */}
                                         <line x1="500" y1={target2Y} x2="665" y2={target2Y} stroke="#10B981" strokeWidth="1" strokeDasharray="4,4" />
                                         <text x="508" y={isBearishSetup ? target2Y + 9 : target2Y - 4} fill="#10B981" fontSize="7" fontWeight="bold" fontFamily="monospace">Target 2 (Final Target)</text>
                                       </>
                                     )}

                                    {/* RIGHT SIDE PRICE SCALE ACTIVE PANEL (Exactly like TradingView) */}
                                    <line x1="680" y1="15" x2="680" y2="305" stroke="#1E2235" strokeWidth="1.5" />
                                    
                                    {/* PDH Price Tick */}
                                    <line x1="680" y1={pdhY} x2="685" y2={pdhY} stroke={isBearishSetup ? "#EF4444" : "#10B981"} strokeWidth="1" />
                                    <text x="690" y={pdhY + 3} fill={isBearishSetup ? "#EF4444" : "#10B981"} fontSize="8" fontWeight="bold" fontFamily="monospace">PDH: {pdhVal.toFixed(2)}</text>

                                    {/* Equilibrium Price Tick */}
                                    <line x1="680" y1={eqY} x2="685" y2={eqY} stroke="#F59E0B" strokeWidth="1" />
                                    <text x="690" y={eqY + 3} fill="#F59E0B" fontSize="8" fontWeight="bold" fontFamily="monospace">EQ: {eqPriceVal.toFixed(2)}</text>

                                    {/* Daily Open Price Tick */}
                                    <line x1="680" y1={openY} x2="685" y2={openY} stroke="#818CF8" strokeWidth="1" />
                                    <text x="690" y={openY + 3} fill="#818CF8" fontSize="8" fontWeight="bold" fontFamily="monospace">OPEN: {openVal.toFixed(2)}</text>

                                    {/* Current Price Active Badge */}
                                    <g transform={`translate(680, ${currY - 8})`}>
                                      <polygon points="0,8 6,2 45,2 45,14 6,14" fill="#6366F1" />
                                      <rect x="45" y="2" width="75" height="12" fill="#6366F1" rx="1" />
                                      <text x="8" y="11" fill="#FFFFFF" fontSize="8" fontWeight="bold" fontFamily="monospace">
                                        {currentPriceVal.toFixed(2)}
                                      </text>
                                      <text x="58" y="11" fill="#E0E7FF" fontSize="7" fontWeight="bold" fontFamily="sans-serif">
                                        {currentPriceVal > openVal ? "PREMIUM" : "DISCOUNT"}
                                      </text>
                                    </g>

                                    {/* PDL Price Tick */}
                                    <line x1="680" y1={pdlY} x2="685" y2={pdlY} stroke={isBearishSetup ? "#10B981" : "#EF4444"} strokeWidth="1" />
                                    <text x="690" y={pdlY + 3} fill={isBearishSetup ? "#10B981" : "#EF4444"} fontSize="8" fontWeight="bold" fontFamily="monospace">PDL: {pdlVal.toFixed(2)}</text>

                                    {/* Entry price tick */}
                                    {entryY !== null && (
                                      <>
                                        <line x1="680" y1={entryY} x2="685" y2={entryY} stroke={isBearishSetup ? "#EF4444" : "#10B981"} strokeWidth="1" />
                                        <text x="690" y={entryY + 3} fill={isBearishSetup ? "#EF4444" : "#10B981"} fontSize="8" fontWeight="bold" fontFamily="monospace">ENTRY: {entryPriceVal?.toFixed(2)}</text>
                                      </>
                                    )}

                                    {/* Stop Loss price tick */}
                                    {(sbResult.daily_bias === "BULLISH" || sbResult.daily_bias === "BEARISH") && (
                                      <>
                                        <line x1="680" y1={slY} x2="685" y2={slY} stroke="#EF4444" strokeWidth="1" />
                                        <text x="690" y={slY + 3} fill="#EF4444" fontSize="8" fontWeight="bold" fontFamily="monospace">SL: {stopLossVal.toFixed(2)}</text>
                                      </>
                                    )}

                                    {/* Render Candlesticks */}
                                    {candles.map((c, i) => {
                                      const color = c.isBullish ? "#10B981" : "#EF4444";
                                      const bodyY = c.isBullish ? c.close : c.open;
                                      const bodyHeight = Math.abs(c.close - c.open);
                                      return (
                                        <g key={i}>
                                          {/* Wick */}
                                          <line
                                            x1={c.x + 8}
                                            y1={c.high}
                                            x2={c.x + 8}
                                            y2={c.low}
                                            stroke={color}
                                            strokeWidth="2"
                                          />
                                          {/* Body */}
                                          <rect
                                            x={c.x}
                                            y={bodyY}
                                            width="16"
                                            height={bodyHeight || 1}
                                            fill={c.isBullish ? "#10B981" : "#EF4444"}
                                            stroke={color}
                                            strokeWidth="1.25"
                                          />
                                          {c.isSweep && (
                                            <circle cx={c.x + 8} cy={pdlY} r="4" fill="#EF4444" />
                                          )}
                                          {c.isEntry && entryY !== null && (
                                            <circle cx={c.x + 8} cy={entryY} r="4.5" fill="#10B981" stroke="#FFFFFF" strokeWidth="1" />
                                          )}
                                        </g>
                                      );
                                    })}
                                  </svg>
                                );
                              })()}
                            </div>
                          </div>
                        )}

                        {/* Antigravity Checklist Structural Tree */}
                        {sbResult && (
                          <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-5 flex flex-col gap-4">
                            <div className="flex justify-between items-center border-b border-[#1E2235]/40 pb-3">
                              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2 font-mono">
                                <span className={`w-2 h-2 rounded-full ${sbResult.is_valid && !sbResult.counter_trend_locked ? "bg-emerald-500 animate-pulse" : "bg-rose-500 animate-pulse"}`} />
                                Antigravity Master Spec Validation Tree
                              </h4>
                              <span className="text-[10px] text-gray-400 font-mono">
                                System Status: <span className={sbResult.counter_trend_locked ? "text-rose-400 font-bold" : sbResult.daily_bias !== "NEUTRAL" ? "text-emerald-400 font-bold" : "text-amber-400 font-bold"}>
                                  {sbResult.counter_trend_locked ? "LOCKOUT ACTIVE" : sbResult.daily_bias !== "NEUTRAL" ? "EXECUTION CONFIRMED" : "PENDING CRITERIA"}
                                </span>
                              </span>
                            </div>
                            
                            {/* Sleek Vertical Tree Structure */}
                            <div className="relative pl-6 border-l-2 border-dashed border-[#1E2235]/80 flex flex-col gap-5 py-2">
                              {/* Node 1: HTF Trend (Daily Bias) */}
                              <div className="relative flex flex-col gap-1">
                                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-[#07080E] border-2 border-[#1E2235] flex items-center justify-center">
                                  <div className={`w-1.5 h-1.5 rounded-full ${sbResult.daily_bias !== "NEUTRAL" ? "bg-emerald-400" : "bg-amber-400"}`} />
                                </div>
                                <div className="bg-[#07080E]/70 p-3 rounded-lg border border-[#1E2235]/40 hover:border-[#6366F1]/30 transition-colors">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">1. HTF Trend / Daily Bias Vector</span>
                                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                                      sbResult.daily_bias === "BULLISH" ? "bg-emerald-500/10 text-emerald-400" :
                                      sbResult.daily_bias === "BEARISH" ? "bg-rose-500/10 text-rose-400" : "bg-amber-500/10 text-amber-400"
                                    }`}>{sbResult.daily_bias}</span>
                                  </div>
                                  <span className="text-xs font-semibold text-white mt-1 block">
                                    {sbResult.daily_bias === "BULLISH" ? "Bullish Institutional Order Flow" :
                                     sbResult.daily_bias === "BEARISH" ? "Bearish Institutional Order Flow" :
                                     "Consolidating / Strategy Neutral State"}
                                  </span>
                                  <span className="text-[10px] text-indigo-300/80 font-sans mt-0.5 block">
                                    {sbResult.daily_bias === "BULLISH" ? "ගොන් (Bullish) ආයතනික ඇණවුම් ප්‍රවාහය" :
                                     sbResult.daily_bias === "BEARISH" ? "වලස් (Bearish) ආයතනික ඇණවුම් ප්‍රවාහය" :
                                     "ඒකාබද්ධ වෙළඳපල / උදාසීන තත්ත්වය"}
                                  </span>
                                  <span className="text-[9px] text-gray-500 font-mono mt-1 block">HTF Context Mapped</span>
                                </div>
                              </div>

                              {/* Node 2: Active Silver Bullet Window */}
                              <div className="relative flex flex-col gap-1">
                                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-[#07080E] border-2 border-[#1E2235] flex items-center justify-center">
                                  <div className={`w-1.5 h-1.5 rounded-full ${sbResult.killzone_valid ? "bg-emerald-400" : "bg-rose-400"}`} />
                                </div>
                                <div className="bg-[#07080E]/70 p-3 rounded-lg border border-[#1E2235]/40 hover:border-[#6366F1]/30 transition-colors">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">2. Active Silver Bullet Window</span>
                                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                                      sbResult.killzone_valid ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                                    }`}>{sbResult.killzone_valid ? "ACTIVE" : "INACTIVE"}</span>
                                  </div>
                                  <span className="text-xs font-semibold text-white mt-1 block font-mono">
                                    Window: {sbKillzone === "LONDON_SB" ? "London Open (3-4 AM NY / 12:30-1:30 PM LK)" :
                                             sbKillzone === "NY_AM_SB" ? "AM Session (10-11 AM NY / 7:30-8:30 PM LK)" :
                                             sbKillzone === "NY_PM_SB" ? "PM Session (2-3 PM NY / 11:30 PM-12:30 AM LK)" :
                                             sbKillzone === "LONDON" ? "London Killzone (2-5 AM NY)" :
                                             sbKillzone === "NY_AM" ? "New York AM Killzone (7-10 AM NY)" : "None (Outside Designated Windows)"}
                                  </span>
                                  <span className="text-[10px] text-indigo-300/80 font-sans mt-0.5 block">
                                    {sbKillzone === "LONDON_SB" ? "ලන්ඩන් ආරම්භක සැසිය (ප.ව. 12:30 - ප.ව. 1:30 ලංකා වේලාවෙන්)" :
                                     sbKillzone === "NY_AM_SB" ? "AM සැසිය (ප.ව. 7:30 - ප.ව. 8:30 ලංකා වේලාවෙන්)" :
                                     sbKillzone === "NY_PM_SB" ? "PM සැසිය (රාත්‍රී 11:30 - පෙ.ව. 12:30 ලංකා වේලාවෙන්)" :
                                     sbKillzone === "LONDON" ? "ලන්ඩන් කිල්සෝන් (ප.ව. 11:30 - පෙ.ව. 2:30 ලංකා වේලාවෙන්)" :
                                     sbKillzone === "NY_AM" ? "නිව් යෝර්ක් පෙරවරු කිල්සෝන් (ප.ව. 4:30 - ප.ව. 7:30 ලංකා වේලාවෙන්)" : "කිසිවක් නැත (නියමිත වේලාවෙන් බැහැර)"}
                                  </span>
                                </div>
                              </div>

                              {/* Node 3: Daily Open Bias Vector */}
                              <div className="relative flex flex-col gap-1">
                                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-[#07080E] border-2 border-[#1E2235] flex items-center justify-center">
                                  <div className={`w-1.5 h-1.5 rounded-full ${sbResult.daily_open_relation ? "bg-emerald-400" : "bg-gray-500"}`} />
                                </div>
                                <div className="bg-[#07080E]/70 p-3 rounded-lg border border-[#1E2235]/40 hover:border-[#6366F1]/30 transition-colors">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">3. Daily Open Bias Vector</span>
                                    <span className="text-[9px] font-mono text-gray-400 font-bold">Open: {sbOpen !== "" ? Number(sbOpen).toFixed(2) : "N/A"}</span>
                                  </div>
                                  <span className="text-xs font-semibold text-white mt-1 block">
                                    Price relation is {sbResult.daily_open_relation === "BELOW_OPEN" ? "BELOW DAILY OPEN (Discount Pricing Vector)" :
                                                       sbResult.daily_open_relation === "ABOVE_OPEN" ? "ABOVE DAILY OPEN (Premium Pricing Vector)" : "N/A"}
                                  </span>
                                  <span className="text-[10px] text-indigo-300/80 font-sans mt-0.5 block">
                                    {sbResult.daily_open_relation === "BELOW_OPEN" ? "මිල දෛනික ආරම්භක මිලට වඩා පහළින් පවතී (ඩිස්කවුන්ට් කලාපය)" :
                                     sbResult.daily_open_relation === "ABOVE_OPEN" ? "මිල දෛනික ආරම්භක මිලට වඩා ඉහළින් පවතී (ප්‍රීමියම් කලාපය)" : "නොමැත"}
                                  </span>
                                </div>
                              </div>

                              {/* Node 4: Swept Liquidity Pool */}
                              <div className="relative flex flex-col gap-1">
                                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-[#07080E] border-2 border-[#1E2235] flex items-center justify-center">
                                  <div className={`w-1.5 h-1.5 rounded-full ${sbResult.swept_liquidity_pool && sbResult.swept_liquidity_pool !== "NONE" ? "bg-emerald-400" : "bg-amber-400"}`} />
                                </div>
                                <div className="bg-[#07080E]/70 p-3 rounded-lg border border-[#1E2235]/40 hover:border-[#6366F1]/30 transition-colors">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">4. Swept Liquidity Pool</span>
                                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                                      sbResult.swept_liquidity_pool && sbResult.swept_liquidity_pool !== "NONE" ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"
                                    }`}>{sbResult.swept_liquidity_pool && sbResult.swept_liquidity_pool !== "NONE" ? "SWEPT" : "NO SWEEP DETECTED"}</span>
                                  </div>
                                  <span className="text-xs font-semibold text-white mt-1 block">
                                    {sbResult.swept_liquidity_pool === "9AM_LOW_SSL" ? "9:00 AM Candle Low (Sell-Side Liquidity) Swept" :
                                     sbResult.swept_liquidity_pool === "9AM_HIGH_BSL" ? "9:00 AM Candle High (Buy-Side Liquidity) Swept" :
                                     sbResult.swept_liquidity_pool === "PDL_SSL" ? "Previous Daily Low (PDL/SSL) Swept" :
                                     sbResult.swept_liquidity_pool === "PDH_BSL" ? "Previous Daily High (PDH/BSL) Swept" :
                                     "Waiting for retail stop raid / liquidity sweep"}
                                  </span>
                                  <span className="text-[10px] text-indigo-300/80 font-sans mt-0.5 block">
                                    {sbResult.swept_liquidity_pool === "9AM_LOW_SSL" ? "පෙ.ව. 9:00 ඉටිපන්දමේ පහළ සීමාවේ (SSL) ද්‍රවශීලතාවය බිඳ දැමීම" :
                                     sbResult.swept_liquidity_pool === "9AM_HIGH_BSL" ? "පෙ.ව. 9:00 ඉටිපන්දමේ ඉහළ සීමාවේ (BSL) ද්‍රවශීලතාවය බිඳ දැමීම" :
                                     sbResult.swept_liquidity_pool === "PDL_SSL" ? "පෙර දින අවම සීමාවේ (PDL/SSL) ද්‍රවශීලතාවය බිඳ දැමීම" :
                                     sbResult.swept_liquidity_pool === "PDH_BSL" ? "පෙර දින උපරිම සීමාවේ (PDH/BSL) ද්‍රවශීලතාවය බිඳ දැමීම" :
                                     "retail stop raid / ද්‍රවශීලතාවය බිඳ දමන තෙක් බලා සිටී"}
                                  </span>
                                </div>
                              </div>

                              {/* Node 5: Mitigated PD Array */}
                              <div className="relative flex flex-col gap-1">
                                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-[#07080E] border-2 border-[#1E2235] flex items-center justify-center">
                                  <div className={`w-1.5 h-1.5 rounded-full ${sbResult.mitigated_pd_array_type && sbResult.mitigated_pd_array_type !== "NONE" ? "bg-emerald-400" : "bg-gray-500"}`} />
                                </div>
                                <div className="bg-[#07080E]/70 p-3 rounded-lg border border-[#1E2235]/40 hover:border-[#6366F1]/30 transition-colors">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">5. Mitigated PD Array Type</span>
                                    <span className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                                      sbResult.mitigated_pd_array_type && sbResult.mitigated_pd_array_type !== "NONE" ? "bg-emerald-500/10 text-emerald-400" : "bg-gray-500/10 text-gray-400"
                                    }`}>{sbResult.mitigated_pd_array_type || "NONE"}</span>
                                  </div>
                                  <span className="text-xs font-semibold text-white mt-1 block">
                                    Footprint: {sbResult.mitigated_pd_array_type === "FVG" ? "Fair Value Gap (Inefficiency Rebalanced)" :
                                               sbResult.mitigated_pd_array_type === "OB" ? "Order Block (Institutional Buy/Sell Zone Mitigated)" :
                                               sbResult.mitigated_pd_array_type === "BREAKER" ? "Breaker Block Mitigated" :
                                               sbResult.mitigated_pd_array_type === "MITIGATION" ? "Mitigation Block Mitigated" :
                                               sbResult.mitigated_pd_array_type === "REJECTION" ? "Rejection Block Mitigated" :
                                               "No active mitigated array matched"}
                                  </span>
                                  <span className="text-[10px] text-indigo-300/80 font-sans mt-0.5 block">
                                    {sbResult.mitigated_pd_array_type === "FVG" ? "Fair Value Gap (අසමතුලිතතාවය නැවත තුලනය විය)" :
                                     sbResult.mitigated_pd_array_type === "OB" ? "Order Block (ආයතනික මිල කලාපය ස්පර්ශ විය)" :
                                     sbResult.mitigated_pd_array_type === "BREAKER" ? "Breaker Block ස්පර්ශ විය" :
                                     sbResult.mitigated_pd_array_type === "MITIGATION" ? "Mitigation Block ස්පර්ශ විය" :
                                     sbResult.mitigated_pd_array_type === "REJECTION" ? "Rejection Block ස්පර්ශ විය" :
                                     "වලංගු සක්‍රීය PD Array එකක් හමු නොවීය"}
                                  </span>
                                  <span className="text-[9px] text-gray-500 font-mono mt-1 block">State tracking: ERL vs IRL State is {sbResult.erl_irl_state || "NONE"}</span>
                                </div>
                              </div>

                              {/* Node 6: Execution Parameters */}
                              <div className="relative flex flex-col gap-1">
                                <div className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-[#07080E] border-2 border-rose-500/50 flex items-center justify-center">
                                  <div className={`w-1.5 h-1.5 rounded-full ${sbResult.is_valid && !sbResult.counter_trend_locked ? "bg-emerald-400" : "bg-rose-500 animate-pulse"}`} />
                                </div>
                                <div className="bg-[#07080E]/70 p-3 rounded-lg border border-rose-500/30 hover:border-rose-500/50 transition-colors">
                                  <span className="text-[9px] font-bold text-rose-400 uppercase tracking-wider font-mono">6. Execution Parameters (1:3 RR Target Output)</span>
                                  {sbResult.is_valid && !sbResult.counter_trend_locked ? (
                                    <div className="flex flex-col gap-2 mt-2 bg-[#0E101A]/60 p-3 rounded-lg border border-[#1E2235]">
                                      <div className="flex justify-between items-center text-xs text-white">
                                        <span>Order Type:</span>
                                        <span className="font-bold text-indigo-400 uppercase">{sbResult.daily_bias === "BULLISH" ? "Buy Limit" : "Sell Limit"}</span>
                                      </div>
                                      <div className="flex justify-between items-center text-xs text-emerald-400 font-bold">
                                        <span>Entry Price Area:</span>
                                        <span className="font-mono">{sbResult.entry_price_area || "Midpoint / Consequent Encroachment of FVG"}</span>
                                      </div>
                                      <div className="flex justify-between items-center text-xs text-rose-400">
                                        <span>Stop Loss (Absolute SL):</span>
                                        <span className="font-mono">{sbResult.stop_loss_level ? Number(sbResult.stop_loss_level).toFixed(2) : "N/A"}</span>
                                      </div>
                                      <div className="flex justify-between items-center text-xs text-indigo-300">
                                        <span>Take Profit Target:</span>
                                        <span className="font-mono font-bold text-indigo-400">{sbResult.liquidity_target ? Number(sbResult.liquidity_target).toFixed(2) : "N/A"} ({sbResult.target_reward_ratio || "1:3 RR"})</span>
                                      </div>
                                    </div>
                                  ) : (
                                    <div className="mt-2 bg-rose-950/20 border border-rose-500/30 p-3 rounded-lg text-rose-400 text-xs font-bold font-mono">
                                      {sbResult.counter_trend_locked ? "STRATEGY RULE LOCKOUT / COUNTER-BIAS SETUP IGNORED" : "LOCKED / INACTIVE - Setup criteria not fully met"}
                                      <div className="text-[10px] text-rose-300/80 font-sans font-normal mt-1 leading-relaxed">
                                        {sbResult.counter_trend_locked ? "උපායමාර්ගික නීති අවහිරය / දෛනික නැඹුරුවට පටහැනි සැකසුම ප්‍රතික්ෂේප විය" : "අවහිර කර ඇත / අක්‍රීයයි - අවශ්‍ය නිර්ණායක සම්පූර්ණ වී නොමැත"}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Detailed ICT Silver Bullet 12-Step Confirmation Pipeline */}
                        {sbResult && (
                          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 shadow-xl flex flex-col gap-4">
                            <div className="flex justify-between items-center border-b border-[#1E2235]/40 pb-3">
                              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2 font-mono">
                                <svg className="w-4 h-4 text-[#8B5CF6] shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                                </svg>
                                ICT Silver Bullet & PO3 12-Step Confirmation Pipeline
                              </h4>
                              {sbResult.sb_step_1_time_window_ok && 
                               sbResult.sb_step_2_liquidity_sweep_ok && 
                               sbResult.sb_step_3_displacement_mss_ok && 
                               sbResult.sb_step_4_fvg_bpr_ok && 
                               sbResult.sb_step_5_entry_exec_ok && 
                               sbResult.sb_step_6_risk_mgmt_ok && 
                               sbResult.sb_step_7_london_asian_sweep_ok && 
                               sbResult.sb_step_8_htf_pd_mitigation_ok && 
                               sbResult.sb_step_9_ltf_choch_ok && 
                               sbResult.sb_step_10_fvg_limit_ok && sbResult.sb_step_11_equilibrium_ok && sbResult.sb_step_12_po3_align_ok && (
                                 <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[9px] font-bold px-1.5 py-0.5 rounded font-mono animate-pulse flex items-center gap-1">
                                    <span>✓</span> 12/12 CONFLUENCES VERIFIED
                                 </span>
                              )}
                              <span className="text-[10px] text-gray-400 font-mono">1m Execution Timeframe</span>
                            </div>

                            <div className="flex flex-col gap-4">
                              {/* Step 1: Time Window Filter */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_1_time_window_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_1_time_window_ok ? "✓" : "1"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 1: Time Window Filter</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_1_time_window_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"
                                    }`}>
                                      {sbResult.sb_step_1_time_window_ok ? "ACTIVE" : "INACTIVE"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_1_details ? sbResult.sb_step_1_details.split("|")[0].trim() : "Time window filter check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_1_details ? (sbResult.sb_step_1_details.split("|")[1]?.trim() || "කාලසීමාව පරීක්ෂාව.") : "කාලසීමාව පරීක්ෂාව."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 2: Liquidity Sweep */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_2_liquidity_sweep_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_2_liquidity_sweep_ok ? "✓" : "2"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 2: Liquidity Sweep (SSL/BSL)</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_2_liquidity_sweep_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"
                                    }`}>
                                      {sbResult.sb_step_2_liquidity_sweep_ok ? "DETECTED" : "AWAITING"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_2_details ? sbResult.sb_step_2_details.split("|")[0].trim() : "Wick sweep detection."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_2_details ? (sbResult.sb_step_2_details.split("|")[1]?.trim() || "ද්‍රවශීලතාවය sweep වීම හඳුනාගැනීම.") : "ද්‍රවශීලතාවය sweep වීම හඳුනාගැනීම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 3: Displacement & MSS */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_3_displacement_mss_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_3_displacement_mss_ok ? "✓" : "3"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 3: Displacement & MSS</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_3_displacement_mss_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"
                                    }`}>
                                      {sbResult.sb_step_3_displacement_mss_ok ? "CONFIRMED" : "PENDING"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_3_details ? sbResult.sb_step_3_details.split("|")[0].trim() : "Candle body close break check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_3_details ? (sbResult.sb_step_3_details.split("|")[1]?.trim() || "MSS ඉටිපන්දම් සිරුරකින් බිඳවැටීම පරීක්ෂාව.") : "MSS ඉටිපන්දම් සිරුරකින් බිඳවැටීම පරීක්ෂාව."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 4: FVG / BPR Unicorn Setup */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_4_fvg_bpr_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_4_fvg_bpr_ok ? "✓" : "4"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 4: Fair Value Gap / Balanced Price Range</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_4_fvg_bpr_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_4_fvg_bpr_ok ? "FOUND" : "AWAITING"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_4_details ? sbResult.sb_step_4_details.split("|")[0].trim() : "Unicorn block overlap check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_4_details ? (sbResult.sb_step_4_details.split("|")[1]?.trim() || "FVG හෝ PD array කලාපයන් හඳුනාගැනීම.") : "FVG හෝ PD array කලාපයන් හඳුනාගැනීම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 5: Entry Execution */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_5_entry_exec_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_5_entry_exec_ok ? "✓" : "5"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 5: Limit Entry Only (No Market)</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_5_entry_exec_ok ? "bg-indigo-500/10 text-indigo-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_5_entry_exec_ok ? "ORDER READY" : "INACTIVE"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_5_details ? sbResult.sb_step_5_details.split("|")[0].trim() : "Limit entry trigger."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_5_details ? (sbResult.sb_step_5_details.split("|")[1]?.trim() || "ලිමිට් ඕඩරය සක්‍රීය වීම.") : "ලිමිට් ඕඩරය සක්‍රීය වීම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 6: Risk Management */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_6_risk_mgmt_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_6_risk_mgmt_ok ? "✓" : "6"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 6: Risk Management</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_6_risk_mgmt_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_6_risk_mgmt_ok ? "VERIFIED" : "LOCKED"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_6_details ? sbResult.sb_step_6_details.split("|")[0].trim() : "SL / TP settings."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_6_details ? (sbResult.sb_step_6_details.split("|")[1]?.trim() || "අවදානම් කළමනාකරණය (SL සහ TP මට්ටම්).") : "අවදානම් කළමනාකරණය (SL සහ TP මට්ටම්)."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 7: Asian Session Liquidity Sweep */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_7_london_asian_sweep_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_7_london_asian_sweep_ok ? "✓" : "7"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 7: Asian Liquidity Sweep</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_7_london_asian_sweep_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_7_london_asian_sweep_ok ? "SWEPT" : "AWAITING"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_7_details ? sbResult.sb_step_7_details.split("|")[0].trim() : "Asian session liquidity filter."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_7_details ? (sbResult.sb_step_7_details.split("|")[1]?.trim() || "ආසියානු සෙෂන් ද්‍රවශීලතා පෙරහන.") : "ආසියානු සෙෂන් ද්‍රවශීලතා පෙරහන."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 8: HTF PD Array Mitigation */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_8_htf_pd_mitigation_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_8_htf_pd_mitigation_ok ? "✓" : "8"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 8: HTF PD Array Mitigation</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_8_htf_pd_mitigation_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_8_htf_pd_mitigation_ok ? "MITIGATED" : "AWAITING"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_8_details ? sbResult.sb_step_8_details.split("|")[0].trim() : "HTF PD array check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_8_details ? (sbResult.sb_step_8_details.split("|")[1]?.trim() || "HTF PD array පරීක්ෂාව.") : "HTF PD array පරීක්ෂාව."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 9: LTF Choch Confirmation */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_9_ltf_choch_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_9_ltf_choch_ok ? "✓" : "9"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 9: 1m Choch Confirmation</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_9_ltf_choch_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_9_ltf_choch_ok ? "CONFIRMED" : "AWAITING"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_9_details ? sbResult.sb_step_9_details.split("|")[0].trim() : "LTF Choch validation."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_9_details ? (sbResult.sb_step_9_details.split("|")[1]?.trim() || "LTF Choch තහවුරු කිරීම.") : "LTF Choch තහවුරු කිරීම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 10: 1m FVG Limit Entry Placement */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_10_fvg_limit_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_10_fvg_limit_ok ? "✓" : "10"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 10: Wait for Pullback / Mitigation</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_10_fvg_limit_ok ? "bg-indigo-500/10 text-indigo-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_10_fvg_limit_ok ? "ORDER READY" : "INACTIVE"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_10_details ? sbResult.sb_step_10_details.split("|")[0].trim() : "Limit entry placement."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_10_details ? (sbResult.sb_step_10_details.split("|")[1]?.trim() || "Limit entry ඕඩරය පිහිටුවීම.") : "Limit entry ඕඩරය පිහිටුවීම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 11: Equilibrium Zone Verification (50% Rule) */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_11_equilibrium_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_11_equilibrium_ok ? "✓" : "11"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 11: Equilibrium Verification</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_11_equilibrium_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_11_equilibrium_ok ? "DISCOUNT/PREMIUM OK" : "LOCKED"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_11_details ? sbResult.sb_step_11_details.split("|")[0].trim() : "Discount/Premium 50% zone check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_11_details ? (sbResult.sb_step_11_details.split("|")[1]?.trim() || "Discount/Premium 50% කලාපය පරීක්ෂාව.") : "Discount/Premium 50% කලාපය පරීක්ෂාව."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 12: PO3 Open Bias Alignment */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_12_po3_align_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_12_po3_align_ok ? "✓" : "12"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 12: PO3 AMD & Dual Entry Alignment</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_12_po3_align_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_12_po3_align_ok ? "ALIGNED" : "MISMATCH"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_12_details ? sbResult.sb_step_12_details.split("|")[0].trim() : "PO3 AMD setup check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_12_details ? (sbResult.sb_step_12_details.split("|")[1]?.trim() || "PO3 AMD සහ ඇතුල්වීම් ක්‍රමවේද පෙළගැස්ම.") : "PO3 AMD සහ ඇතුල්වීම් ක්‍රමවේද පෙළගැස්ම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 13: HTF Structure Bias & POI Mapped */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_13_htf_mapped_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_13_htf_mapped_ok ? "✓" : "13"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 13: HTF Structure & POI Mapped</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_13_htf_mapped_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_13_htf_mapped_ok ? "MAPPED" : "UNMAPPED"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_13_details ? sbResult.sb_step_13_details.split("|")[0].trim() : "HTF Structure mapping."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_13_details ? (sbResult.sb_step_13_details.split("|")[1]?.trim() || "HTF ව්‍යුහය සහ POI සලකුණු කිරීම.") : "HTF ව්‍යුහය සහ POI සලකුණු කිරීම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 14: LTF Alignment & POI Mitigation Tap */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_14_ltf_tap_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_14_ltf_tap_ok ? "✓" : "14"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 14: LTF POI Mitigation Tap</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_14_ltf_tap_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_14_ltf_tap_ok ? "MITIGATED" : "PENDING"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_14_details ? sbResult.sb_step_14_details.split("|")[0].trim() : "LTF POI Mitigation tap check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_14_details ? (sbResult.sb_step_14_details.split("|")[1]?.trim() || "LTF POI ස්පර්ශ කිරීම.") : "LTF POI ස්පර්ශ කිරීම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 15: LTF Reversal & Dual Entry Execution */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_15_dual_entry_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_15_dual_entry_ok ? "✓" : "15"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 15: LTF Reversal & Dual Entry Execution</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_15_dual_entry_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_15_dual_entry_ok ? "ENTRY ACTIVE" : "LOCKED"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_15_details ? sbResult.sb_step_15_details.split("|")[0].trim() : "LTF Reversal and Dual Entry execution check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_15_details ? (sbResult.sb_step_15_details.split("|")[1]?.trim() || "LTF Reversal සහ Limit Order පිහිටුවීම.") : "LTF Reversal සහ Limit Order පිහිටුවීම."}
                                  </span>
                                </div>
                              </div>

                              {/* Step 16: HTF (1H) Trend Directional Alignment */}
                              <div className="bg-[#07080E]/40 border border-[#1E2235]/40 rounded-xl p-3.5 flex items-start gap-3.5 hover:border-indigo-500/20 transition-all">
                                <div className={`w-6 h-6 rounded-full shrink-0 flex items-center justify-center font-bold text-xs font-mono border ${
                                  sbResult.sb_step_16_htf_align_ok 
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                                    : "bg-[#1E2235]/30 text-gray-500 border-[#1E2235]"
                                }`}>
                                  {sbResult.sb_step_16_htf_align_ok ? "✓" : "16"}
                                </div>
                                <div className="flex flex-col gap-1 w-full">
                                  <div className="flex justify-between items-center">
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Step 16: HTF (1H) Trend Directional Alignment</span>
                                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded font-mono ${
                                      sbResult.sb_step_16_htf_align_ok ? "bg-emerald-500/10 text-emerald-400" : "bg-[#1E2235]/30 text-gray-400"
                                    }`}>
                                      {sbResult.sb_step_16_htf_align_ok ? "ALIGNED" : "LOCKED"}
                                    </span>
                                  </div>
                                  <p className="text-xs text-white leading-relaxed mt-0.5">
                                    {sbResult.sb_step_16_details ? sbResult.sb_step_16_details.split("|")[0].trim() : "HTF (1H) Trend Directional alignment check."}
                                  </p>
                                  <span className="text-[10px] text-indigo-300/80 font-sans">
                                    {sbResult.sb_step_16_details ? (sbResult.sb_step_16_details.split("|")[1]?.trim() || "HTF (1H) ප්‍රවණතා දිශානති පෙළගැස්ම.") : "HTF (1H) ප්‍රවණතා දිශානති පෙළගැස්ම."}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Reasoning tabs */}
                        <div className="flex flex-col gap-4">
                          <div className="border-t border-[#1E2235] pt-5">
                            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5 mb-2">
                              <svg className="w-4 h-4 text-[#10B981]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                              </svg>
                              Technical Reasoning
                            </h4>
                            <div className="bg-[#141626]/50 p-4 rounded-xl border border-[#1E2235] text-xs leading-relaxed text-gray-300 font-mono">
                              {(() => {
                                const parsed = parseTextWithTranslation(sbResult.reasoning || "");
                                return (
                                  <div className="flex flex-col gap-3">
                                    <div className="whitespace-pre-wrap">{parsed.english}</div>
                                    {parsed.sinhala && (
                                      <div className="mt-2 pt-3 border-t border-[#1E2235]/60 flex flex-col gap-2">
                                        <span className="text-[9px] font-bold text-indigo-400 tracking-wider uppercase bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20 font-sans self-start">
                                          සිංහල පරිවර්තනය • Sinhala Translation
                                        </span>
                                        <div className="text-gray-300 leading-relaxed font-sans text-[12px] bg-[#0E101A]/60 p-3 rounded-lg border border-[#1E2235]/80">
                                          <div className="whitespace-pre-wrap font-normal leading-relaxed">{parsed.sinhala}</div>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                );
                              })()}
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Setup Invalidation
                              </h4>
                              <div className="bg-[#141626]/30 p-3.5 rounded-xl border border-[#1E2235]/40 text-[11px] leading-relaxed text-gray-400 font-mono">
                                {(() => {
                                  const parsed = parseTextWithTranslation(sbResult.invalidation || "");
                                  return (
                                    <div className="flex flex-col gap-3.5">
                                      <div className="whitespace-pre-wrap">{parsed.english}</div>
                                      {parsed.sinhala && (
                                        <div className="mt-1 pt-2 border-t border-[#1E2235]/40 flex flex-col gap-1.5">
                                          <span className="text-[8px] font-bold text-indigo-400 tracking-wider uppercase font-sans">සිංහල</span>
                                          <div className="text-gray-400 font-sans text-[11px] whitespace-pre-wrap bg-[#0E101A]/40 p-2.5 rounded-lg border border-[#1E2235]/40">{parsed.sinhala}</div>
                                        </div>
                                      )}
                                    </div>
                                  );
                                })()}
                              </div>
                            </div>

                            <div>
                              <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                                Risk Mitigation
                              </h4>
                              <div className="bg-[#141626]/30 p-3.5 rounded-xl border border-[#1E2235]/40 text-[11px] leading-relaxed text-gray-400 font-mono">
                                {(() => {
                                  const parsed = parseTextWithTranslation(sbResult.risk_notes || "");
                                  return (
                                    <div className="flex flex-col gap-3.5">
                                      <div className="whitespace-pre-wrap">{parsed.english}</div>
                                      {parsed.sinhala && (
                                        <div className="mt-1 pt-2 border-t border-[#1E2235]/40 flex flex-col gap-1.5">
                                          <span className="text-[8px] font-bold text-indigo-400 tracking-wider uppercase font-sans">සිංහල</span>
                                          <div className="text-gray-400 font-sans text-[11px] whitespace-pre-wrap bg-[#0E101A]/40 p-2.5 rounded-lg border border-[#1E2235]/40">{parsed.sinhala}</div>
                                        </div>
                                      )}
                                    </div>
                                  );
                                })()}
                              </div>
                            </div>
                          </div>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </section>
        ) : activeView === "smc" ? (
                  <section className="flex flex-col gap-6 w-full animate-fadeIn" id="smc-method-section">
                {/* Header Banner */}
                <div className="bg-[#11131F]/90 border border-emerald-500/30 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full filter blur-3xl pointer-events-none" />
                  <div className="flex flex-col gap-1.5 z-10">
                    <div className="flex items-center gap-2">
                      <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold px-2.5 py-0.5 rounded font-mono uppercase tracking-wider">
                        SMC MASTER ENGINE
                      </span>
                      <span className="text-xs text-gray-400 font-mono">• Smart Money Concepts Specification</span>
                    </div>
                    <h2 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
                      Smart Money Concepts (SMC Method) Analysis ⚡
                    </h2>
                    <p className="text-xs text-gray-300 max-w-3xl leading-relaxed">
                      Institutional Market Structure Mapping, Inducement (IDM) Sweeps, Break of Structure (BOS) Body Closes, 
                      and Order Block / Fair Value Gap Mitigation under 50% Equilibrium Zone constraints.
                    </p>
                  </div>
                </div>

                {/* Form Controls and Analytics Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                  {/* Left Control Panel */}
                  <div className="lg:col-span-5 bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 shadow-xl flex flex-col gap-5">
                    <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2 font-mono">
                      <span>⚙️</span> SMC Market Structure Controls
                    </h3>

                    {/* Symbol Selection */}
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Trading Symbol</label>
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={smcSymbol}
                          onChange={(e) => setSmcSymbol(e.target.value.toUpperCase())}
                          className="bg-[#141626] border border-[#1E2235] rounded-xl px-3.5 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono w-full"
                          placeholder="e.g. BTCUSDT, ETHUSDT"
                        />
                        <button
                          type="button"
                          onClick={() => handleRunSmcAnalysis(false)}
                          className="bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/40 text-xs font-bold px-3 py-2 rounded-xl transition-all font-mono whitespace-nowrap cursor-pointer"
                        >
                          Fetch Price
                        </button>
                      </div>
                    </div>

                    {/* Timeframe & HTF Trend Selection */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">Execution Timeframe</label>
                        <select
                          value={smcTimeframe}
                          onChange={(e) => {
                              const val = e.target.value;
                              setSmcTimeframe(val);
                              if (val === "1m") {
                                setSmcStrategyModel("sniper_entry");
                              }
                            }}
                          className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                        >
                          <option value="1m">1m (Scalp Entry)</option>
                          <option value="3m">3m (Scalp Entry)</option>
                          <option value="5m">5m (Intraday Entry)</option>
                          <option value="15m">15m (Primary Structure)</option>
                          <option value="1h">1h (HTF Reference)</option>
                        </select>
                      </div>
                      <div className="flex flex-col gap-1.5">
                        <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">1H HTF Trend</label>
                        <select
                          value={smcHtfTrend}
                          onChange={(e) => setSmcHtfTrend(e.target.value)}
                          className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                        >
                          <option value="BULLISH">BULLISH (Auto Selected)</option>
                          <option value="BEARISH">BEARISH (Auto Selected)</option>
                        </select>
                      </div>
                    </div>

                    {/* SMC Market Structure Checkboxes */}
                    {/* SMC Strategy Model Selection */}
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">SMC Strategy Model</label>
                      <select
                        value={smcStrategyModel}
                        onChange={(e) => setSmcStrategyModel(e.target.value)}
                        className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                      >
                        <option value="double_mitigation">PO3 Double Mitigation Reversal Model (Crypto Roots)</option>
                        <option value="sniper_entry">1m Sniper Entry Model (The Trading Geek)</option>
                      </select>
                    </div>

                    <div className="flex flex-col gap-2.5 bg-[#141626]/40 p-4 rounded-xl border border-[#1E2235]">
                      <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider font-mono flex items-center justify-between">
                        <span>{smcStrategyModel === "double_mitigation" ? "SMC Double Mitigation Reversal Rules" : "SMC 1m Sniper Entry Rules"}</span>
                        <span className="text-[9px] text-gray-400 font-normal">YouTube Tutorial Sync</span>
                      </span>

                      {smcStrategyModel === "double_mitigation" ? (
                        <>
                          {/* Rule 1 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1">
                            <input
                              type="checkbox"
                              checked={true}
                              readOnly
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500 opacity-60"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 1: HTF Trend Alignment & POI Mitigation</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: HTF Trend එක සහ 1H/15m POI කලාපය සනාථ වීම</span>
                            </div>
                          </label>

                          {/* Rule 2 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={true}
                              readOnly
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500 opacity-60"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 2: First Mitigation Lockout (Ignore Entry)</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: පළමු මිටිගේෂන් එකෙන් පසු ආක්‍රමණශීලී ලෙස එන්ට්‍රි නොගෙන සිටීම (Ignore)</span>
                            </div>
                          </label>

                          {/* Rule 3 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={smcLiquidityPoolsSwept}
                              onChange={(e) => setSmcLiquidityPoolsSwept(e.target.checked)}
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 3: Second Mitigation Test (Double Tap Re-test)</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: මිල දෙවන වරටත් POI කලාපය re-test කිරීම සනාථ වීම</span>
                            </div>
                          </label>

                          {/* Rule 4 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={smcInducementSwept}
                              onChange={(e) => setSmcInducementSwept(e.target.checked)}
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 4: 1m Rejection Wick Confirmation (Wick &gt;= 35%)</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: 1m chart එකෙහි Rejection Wick එකක් පිහිටුවීම</span>
                            </div>
                          </label>

                          {/* Rule 5 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={smcSwingValidated}
                              onChange={(e) => setSmcSwingValidated(e.target.checked)}
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 5: 1m MSS/CHoCH Shift with Displacement</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: 1m MSS (Market Structure Shift) සහ displacement එකක් සනාථ වීම</span>
                            </div>
                          </label>

                          {/* Rule 6 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={smcLtfChoch}
                              onChange={(e) => setSmcLtfChoch(e.target.checked)}
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 6: FVG / OB Pullback Limit Entry Set</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: FVG / OB Pullback මට්ටමේ Limit Entry එකක් පිහිටුවීම</span>
                            </div>
                          </label>
                        </>
                      ) : (
                        <>
                          {/* Rule 1 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1">
                            <input
                              type="checkbox"
                              checked={true}
                              readOnly
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500 opacity-60"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 1: HTF 1H & 15m Trend Alignment</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: 1H Trend එක Uptrend නම් 15m Trend එකද Uptrend විය යුතුය</span>
                            </div>
                          </label>

                          {/* Rule 2 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={true}
                              readOnly
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500 opacity-60"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 2: 15m Downtrend Pullback Filter</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: 15m Down වුවහොත්, 1m downtrend pullback එක ඔස්සේ (Sell) හෝ 1m නැවත Up වන තෙක් බලා සිටීම</span>
                            </div>
                          </label>

                          {/* Rule 3 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={smcLiquidityPoolsSwept}
                              onChange={(e) => setSmcLiquidityPoolsSwept(e.target.checked)}
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 3: 1m Liquidity Wick Sweep (Stop Loss Hunt)</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: සීමාන්තික මිල මට්ටමේ ඇති Stop Loss සූරා දැමීම (Wick Sweep)</span>
                            </div>
                          </label>

                          {/* Rule 4 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={smcSwingValidated}
                              onChange={(e) => setSmcSwingValidated(e.target.checked)}
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 4: 1m CHoCH/MSS Shift with Displacement</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: 1m ප්‍රස්ථාරයේ අවසාන swing මට්ටම candle body එකකින් බිඳ වැටීම</span>
                            </div>
                          </label>

                          {/* Rule 5 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={smcLtfChoch}
                              onChange={(e) => setSmcLtfChoch(e.target.checked)}
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 5: FVG / OB Pullback Limit Order Setup</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: FVG සීමාවේ හෝ OB මධ්‍ය ලක්ෂ්‍යයේ Limit Order එක පිහිටුවීම</span>
                            </div>
                          </label>

                          {/* Rule 6 */}
                          <label className="flex items-center gap-3 cursor-pointer select-none py-1 border-t border-[#1E2235]/40 mt-1 pt-2">
                            <input
                              type="checkbox"
                              checked={true}
                              readOnly
                              className="w-4 h-4 rounded text-emerald-600 bg-[#141626] border-[#1E2235] focus:ring-emerald-500 opacity-60"
                            />
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-white">Rule 6: Tight Stop Loss & 10-15 Minutes Max Hold</span>
                              <span className="text-[9px] text-emerald-400/80 font-mono">සිංහල පරිවර්තනය: Stop Loss එක manipulation extreme එකෙන් ඔබ්බට තබා විනාඩි 10-15ක් රඳවා ගැනීම</span>
                            </div>
                          </label>
                        </>                      )}
                    </div>

                    {/* PO3 Phase Selection */}
                    <div className="flex flex-col gap-1.5">
                      <label className="text-[10px] font-bold text-gray-400 uppercase tracking-wider font-mono">PO3 Institutional AMD Phase</label>
                      <select
                        value={smcPo3Phase}
                        onChange={(e) => setSmcPo3Phase(e.target.value)}
                        className="bg-[#141626] border border-[#1E2235] rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
                      >
                        <option value="ACCUMULATION">Accumulation Phase (Asia Range Tight Consolidations)</option>
                        <option value="MANIPULATION">Manipulation Phase (False Wick Sweep Above/Below Open)</option>
                        <option value="DISTRIBUTION">Distribution Phase (Expansion Towards Draw on Liquidity)</option>
                      </select>
                    </div>

                    {/* Buttons */}
                    <div className="grid grid-cols-2 gap-3 mt-2">
                      <button
                        type="button"
                        onClick={() => handleRunSmcAnalysis(true)}
                        disabled={smcLoading}
                        className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs py-3 px-4 rounded-xl transition-all shadow-lg shadow-emerald-600/20 flex items-center justify-center gap-2 cursor-pointer"
                      >
                        {smcLoading ? "Analyzing..." : "Run SMC Analysis ⚡"}
                      </button>

                      <button
                        type="button"
                        onClick={handleLogSmcTrade}
                        disabled={logLoading || !smcResult}
                        className="bg-teal-600/20 hover:bg-teal-600/30 border border-teal-500/30 text-teal-400 font-bold text-xs py-3 px-4 rounded-xl transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-40"
                      >
                        {logLoading ? "Logging..." : "Log SMC Trade 📈"}
                      </button>
                    </div>

                    {/* TradingView Live Chart for SMC Method */}
                    <div className="bg-[#141626]/60 border border-emerald-500/30 rounded-xl p-4 flex flex-col gap-2 h-[520px] mt-2 relative">
                      <div className="flex justify-between items-center px-1">
                        <span className="text-[10px] font-semibold text-emerald-400 uppercase tracking-widest font-mono flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                          TradingView Live SMC Chart ({smcSymbol})
                        </span>
                        <a
                          href={`https://www.tradingview.com/chart/?symbol=${getTradingViewSymbol(smcSymbol)}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[10px] text-emerald-400 hover:text-emerald-300 transition-colors font-semibold flex items-center gap-1 font-mono bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20"
                        >
                          Open in TradingView ↗
                        </a>
                      </div>
                      <div className="flex-1 w-full rounded-lg overflow-hidden border border-[#1E2235]/40 bg-black/40 relative">
                        <iframe
                          id="tradingview-smc-chart-widget"
                          src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview-smc-chart-widget&symbol=${getTradingViewSymbol(smcSymbol)}&interval=${getIntervalForTradingView(smcTimeframe)}&theme=dark&style=1&timezone=America%2FNew_York&hide_volume=false`}
                          className="w-full h-full border-none"
                          allowFullScreen
                        />
                      </div>
                    </div>
                  </div>

                                    {/* Right Results & Visualizer Panel */}
                  <div className="lg:col-span-7 flex flex-col gap-5">
                    {/* Main Single-Coin Analysis Details */}
                    {smcResult ? (
                      <>
                        {/* Live Strategy Confluences Checklist */}
                        <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-xl p-5 flex flex-col gap-3">
                          <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono flex justify-between items-center">
                            <span>📊 Live Confluences & Confidence Tracker ({smcSymbol})</span>
                            <span className={`px-2 py-0.5 rounded text-[10px] ${smcResult.confidence >= 80 ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-rose-500/10 text-rose-400 border border-rose-500/20"}`}>
                              {smcResult.confidence}% Confirmed
                            </span>
                          </h4>
                          
                          {/* Progress Bar */}
                          <div className="w-full bg-[#141626] rounded-full h-2.5 overflow-hidden border border-[#1E2235]">
                            <div 
                              className={`h-full transition-all duration-300 ${smcResult.confidence >= 80 ? "bg-emerald-500" : "bg-indigo-500"}`}
                              style={{ width: `${smcResult.confidence}%` }}
                            />
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] font-mono mt-2">
                            <div className="flex items-center justify-between p-2 rounded bg-black/20 border border-[#1E2235]/40">
                              <span className="text-gray-400">1. Trend Alignment</span>
                              <span className="text-emerald-400 font-bold">+20% (Met)</span>
                            </div>
                            <div className="flex items-center justify-between p-2 rounded bg-black/20 border border-[#1E2235]/40">
                              <span className="text-gray-400">2. Discount/Premium Zone</span>
                              <span className={smcResult.zone_type === "DISCOUNT" ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                                {smcResult.zone_type === "DISCOUNT" ? "+20% (Met)" : "0% (Failed)"}
                              </span>
                            </div>
                            <div className="flex items-center justify-between p-2 rounded bg-black/20 border border-[#1E2235]/40">
                              <span className="text-gray-400">3. Daily Open Relation</span>
                              <span className={smcResult.daily_open_relation === "BELOW_OPEN" ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                                {smcResult.daily_open_relation === "BELOW_OPEN" ? "+15% (Met)" : "0% (Failed)"}
                              </span>
                            </div>
                            <div className="flex items-center justify-between p-2 rounded bg-black/20 border border-[#1E2235]/40">
                              <span className="text-gray-400">4. Liquidity Pools Swept</span>
                              <span className={smcLiquidityPoolsSwept ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                                {smcLiquidityPoolsSwept ? "+15% (Met)" : "0% (Failed)"}
                              </span>
                            </div>
                            <div className="flex items-center justify-between p-2 rounded bg-black/20 border border-[#1E2235]/40">
                              <span className="text-gray-400">5. 1m Rejection Wick</span>
                              <span className={smcSwingValidated ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                                {smcSwingValidated ? "+15% (Met)" : "0% (Failed)"}
                              </span>
                            </div>
                            <div className="flex items-center justify-between p-2 rounded bg-black/20 border border-[#1E2235]/40">
                              <span className="text-gray-400">6. LTF MSS Shift with FVG</span>
                              <span className={smcLtfChoch ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                                {smcLtfChoch ? "+15% (Met)" : "0% (Failed)"}
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Warning/Success Banner */}
                        {!smcResult.is_valid && (
                          <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl p-3.5 text-xs font-mono flex items-center gap-2">
                            <span>⚠️</span>
                            <span>
                              <strong>SMC Setup Locked:</strong> Confirmation rate is {smcResult.confidence}% (less than the mandatory 70% threshold). Entry parameters are suppressed from active logging.
                              <br />
                              <span className="text-[10px] text-rose-300/80">සිංහල පරිවර්තනය: උපාය මාර්ගික අනුකූලතාවය {smcResult.confidence}% ක් වන බැවින් (අවම 70% ට වඩා අඩු) ඇතුල්වීම් අවහිර කර ඇත.</span>
                            </span>
                          </div>
                        )}
                        {smcResult.is_valid && (
                          <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl p-3.5 text-xs font-mono flex items-center gap-2 animate-pulse">
                            <span>✅</span>
                            <span>
                              <strong>SMC Setup Active:</strong> 70% minimum confirmation reached ({smcResult.confidence}%). Limit order is ready!
                              <br />
                              <span className="text-[10px] text-emerald-300/80">සිංහල පරිවර්තනය: අවම 70% සීමාව පසු කර ඇති බැවින් (තහවුරු කිරීම: {smcResult.confidence}%) ඇතුල්වීම වලංගු වේ!</span>
                            </span>
                          </div>
                        )}

                        {/* Summary Bar */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-xl p-4 flex flex-col gap-1.5">
                            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">Setup Status</span>
                            <div className="flex items-center gap-2">
                              <span className={`w-2.5 h-2.5 rounded-full ${smcResult.is_valid ? "bg-emerald-400 animate-ping" : "bg-rose-500"}`} />
                              <span className={`text-xs font-bold font-mono ${smcResult.is_valid ? "text-emerald-400" : "text-rose-400"}`}>
                                {smcResult.is_valid ? "VALID SMC SETUP" : "SETUP LOCKED"}
                              </span>
                            </div>
                          </div>

                          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-xl p-4 flex flex-col gap-1.5">
                            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">Confidence Rating</span>
                            <span className={`text-sm font-bold font-mono ${smcResult.confidence >= 70 ? "text-emerald-400" : "text-rose-400"}`}>
                              {smcResult.confidence}% CONFIRMED
                            </span>
                          </div>

                          <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-xl p-4 flex flex-col gap-1.5">
                            <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">Matrix Zone</span>
                            <span className="text-xs font-bold text-indigo-400 font-mono">
                              {smcResult.zone_type} ({smcResult.daily_open_relation})
                            </span>
                          </div>
                        </div>

                        {/* Trade Parameters Cards */}
                        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                          <div className="bg-[#11131F]/90 border border-indigo-500/30 rounded-xl p-3.5 flex flex-col gap-1">
                            <span className="text-[9px] font-bold text-indigo-400 uppercase font-mono">Symbol</span>
                            <span className="text-xs font-bold text-white font-mono">
                              🪙 {smcSymbol.toUpperCase()}
                            </span>
                          </div>
                          <div className={`bg-[#11131F]/90 border ${smcResult.is_valid ? "border-emerald-500/30" : "border-rose-500/30"} rounded-xl p-3.5 flex flex-col gap-1`}>
                            <span className={`text-[9px] font-bold ${smcResult.is_valid ? "text-emerald-400" : "text-rose-400"} uppercase font-mono`}>Entry Price</span>
                            <span className="text-xs font-bold text-white font-mono">
                              {smcResult.entry_price_area}
                            </span>
                          </div>
                          <div className="bg-[#11131F]/90 border border-rose-500/30 rounded-xl p-3.5 flex flex-col gap-1">
                            <span className="text-[9px] font-bold text-rose-400 uppercase font-mono">Stop Loss</span>
                            <span className="text-xs font-bold text-rose-400 font-mono">
                              {smcResult.is_valid ? `$${Number(smcResult.stop_loss_level).toFixed(2)}` : "N/A"}
                            </span>
                          </div>
                          <div className="bg-[#11131F]/90 border border-teal-500/30 rounded-xl p-3.5 flex flex-col gap-1">
                            <span className="text-[9px] font-bold text-teal-400 uppercase font-mono">Target TP</span>
                            <span className="text-xs font-bold text-teal-400 font-mono">
                              {smcResult.is_valid ? `$${Number(smcResult.tp2_target).toFixed(2)}` : "N/A"}
                            </span>
                          </div>
                          <div className="bg-[#11131F]/90 border border-indigo-500/30 rounded-xl p-3.5 flex flex-col gap-1">
                            <span className="text-[9px] font-bold text-indigo-400 uppercase font-mono">Target RR</span>
                            <span className="text-xs font-bold text-indigo-300 font-mono">
                              1:4.00 RR
                            </span>
                          </div>
                        </div>

                        {/* Reasoning & Sinhala Translation */}
                        <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-xl p-5 flex flex-col gap-4 font-mono">
                          <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                            <span>🧠</span> Technical Analysis & Sinhala Translation (සිංහල පරිවර්තනය)
                          </h4>
                          <div className="bg-[#07080E] p-4 rounded-xl border border-[#1E2235] text-xs leading-relaxed text-gray-300 whitespace-pre-wrap">
                            {smcResult.reasoning}
                          </div>
                          <div className="bg-[#07080E] p-4 rounded-xl border border-[#1E2235] text-xs leading-relaxed text-rose-300 whitespace-pre-wrap">
                            {smcResult.invalidation}
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-12 flex flex-col items-center justify-center gap-3 text-center min-h-[250px]">
                        <span className="text-3xl">⚡</span>
                        <h3 className="text-sm font-bold text-white font-mono">SMC Method Analysis Ready</h3>
                        <p className="text-xs text-gray-400 max-w-md">
                          Select your symbol, timeframe, and structural confluences, then click "Run SMC Analysis" to generate actionable setups.
                        </p>
                      </div>
                    )}

                    {/* SMC Active Monitor Watchlist (Always Visible) */}
                    <div className="bg-[#11131F]/90 border border-emerald-500/30 rounded-2xl p-5 shadow-xl flex flex-col gap-4">
                      <div className="flex justify-between items-center border-b border-[#1E2235] pb-3">
                        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2 font-mono">
                          <span>📊</span> SMC Active Monitor Watchlist
                        </h3>
                        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 font-bold px-2.5 py-0.5 rounded border border-emerald-500/20 font-mono">
                          {monitoredCoins.length} Active Tracks
                        </span>
                      </div>

                      {monitoredCoins.length === 0 ? (
                        <div className="flex flex-col items-center justify-center gap-3 py-16 text-center">
                          <span className="text-3xl animate-pulse">📡</span>
                          <h4 className="text-xs font-bold text-white font-mono">Watchlist is Empty</h4>
                          <p className="text-[11px] text-gray-400 max-w-sm font-mono leading-relaxed">
                            Search a coin on the left, check your initial confluences, and click "Run SMC Analysis ⚡" to add it here. The bot will automatically track prices and update confluences locally every 5 seconds!
                          </p>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {monitoredCoins.map((coin) => {
                            const params = getCoinParameters(coin);
                            const liveAction = coin.htfTrend === "BULLISH" ? "Buy Limit" : "Sell Limit";
                            const liveEntryArea = params.is_valid ? `${liveAction} at ${params.entry_price.toFixed(2)}` : "No Entry (Confidence < 70%)";

                            return (
                              <div key={coin.id} className={`bg-[#0E101A]/85 border ${params.is_valid ? 'border-emerald-500/50' : 'border-[#1E2235]'} rounded-xl p-4 flex flex-col gap-3 relative shadow-lg`}>
                                {/* Card Header */}
                                <div className="flex justify-between items-center border-b border-[#1E2235]/60 pb-2">
                                  <div className="flex items-center gap-2">
                                    <span className="text-sm font-extrabold text-white font-mono">🪙 {coin.symbol.toUpperCase()}</span>
                                    <span className="text-[10px] bg-[#1E2235] text-indigo-300 font-bold px-1.5 py-0.5 rounded font-mono">{coin.timeframe}</span>
                                    <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded font-mono ${coin.htfTrend === 'BULLISH' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                      {coin.htfTrend}
                                    </span>
                                  </div>
                                  <button 
                                    onClick={() => setMonitoredCoins(monitoredCoins.filter(c => c.id !== coin.id))}
                                    className="text-gray-500 hover:text-rose-400 font-bold text-xs p-1 cursor-pointer transition-colors"
                                    title="Remove from monitoring"
                                  >
                                    ❌
                                  </button>
                                </div>

                                {/* Live Status Row */}
                                <div className="flex justify-between items-center text-[10px] font-mono">
                                  <span className="text-gray-400">Live Price:</span>
                                  <span className="font-extrabold text-white animate-pulse">${coin.currentPrice.toFixed(2)}</span>
                                </div>

                                {/* Progress Bar & Confidence Rating */}
                                <div className="flex flex-col gap-1">
                                  <div className="flex justify-between items-center text-[9px] font-mono">
                                    <span className="text-gray-500">Confidence Rating:</span>
                                    <span className={`font-bold ${params.is_valid ? 'text-emerald-400' : 'text-rose-400'}`}>{params.confidence}% CONFIRMED</span>
                                  </div>
                                  <div className="w-full bg-[#141626] rounded-full h-2 overflow-hidden border border-[#1E2235]">
                                    <div 
                                      className={`h-full transition-all duration-300 ${params.is_valid ? "bg-emerald-500" : "bg-indigo-500"}`}
                                      style={{ width: `${params.confidence}%` }}
                                    />
                                  </div>
                                </div>

                                {/* Status Badge */}
                                <div className="flex items-center justify-between">
                                  <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">Setup Status</span>
                                  {params.is_valid ? (
                                    <span className="text-[10px] bg-emerald-500/15 text-emerald-400 font-extrabold border border-emerald-500/30 px-2.5 py-0.5 rounded-full animate-bounce font-mono flex items-center gap-1">
                                      🎯 Ready to Entry
                                    </span>
                                  ) : (
                                    <span className="text-[10px] bg-rose-500/10 text-rose-400 font-bold border border-rose-500/20 px-2 py-0.5 rounded-full font-mono">
                                      🔒 Setup Locked
                                    </span>
                                  )}
                                </div>

                                {/* Entry Models Grid */}
                                <div className="bg-[#07080E]/80 p-3 rounded-lg border border-[#1E2235]/60 text-[11px] font-mono flex flex-col gap-2">
                                  <div className="flex justify-between items-center text-[9px] text-gray-500 border-b border-[#1E2235]/40 pb-1.5 uppercase tracking-wider font-extrabold">
                                    <span>Execution Levels</span>
                                    <span className="text-indigo-400">1:4.00 RR</span>
                                  </div>
                                  
                                  {/* Entry Price */}
                                  <div className="flex justify-between items-center bg-black/15 px-2 py-1 rounded">
                                    <span className="text-gray-400">Entry Price (OB Limit):</span>
                                    <span className="text-emerald-400 font-extrabold">
                                      {params.is_valid ? `$${params.entry_price.toFixed(2)}` : "🔒 Locked"}
                                    </span>
                                  </div>

                                  {/* Stop Loss */}
                                  <div className="flex justify-between items-center bg-rose-950/10 border border-rose-500/10 px-2 py-1 rounded">
                                    <span className="text-rose-400/90 font-medium">Stop Loss (SL):</span>
                                    <span className="text-rose-400 font-extrabold">${params.stop_loss.toFixed(2)}</span>
                                  </div>

                                  {/* Take Profit */}
                                  <div className="flex justify-between items-center bg-indigo-950/10 border border-indigo-500/10 px-2 py-1 rounded">
                                    <span className="text-indigo-300 font-medium">Take Profit (TP):</span>
                                    <span className="text-indigo-400 font-extrabold">${params.take_profit.toFixed(2)}</span>
                                  </div>

                                  {/* Risk to Reward */}
                                  <div className="flex justify-between items-center bg-black/20 px-2 py-1 rounded text-[10px]">
                                    <span className="text-gray-500">Risk-to-Reward:</span>
                                    <span className="text-indigo-300 font-bold">1:4.00 RR Target</span>
                                  </div>
                                </div>

                                {/* 1-Click Action Button */}
                                <button
                                  disabled={!params.is_valid || logLoading}
                                  onClick={async () => {
                                    setLogLoading(true);
                                    try {
                                      const res = await fetch("http://127.0.0.1:8000/api/trades/log", {
                                        method: "POST",
                                        headers: { "Content-Type": "application/json" },
                                        body: JSON.stringify({
                                          symbol: coin.symbol.toUpperCase(),
                                          direction: coin.htfTrend,
                                          entry_price: params.entry_price,
                                          stop_loss: params.stop_loss,
                                          take_profit: params.take_profit,
                                          confidence: params.confidence,
                                          strategy_type: "SMC"
                                        })
                                      });
                                      if (res.ok) {
                                        alert(`🎯 SMC trade for ${coin.symbol.toUpperCase()} executed/logged successfully!`);
                                        setMonitoredCoins(monitoredCoins.filter(c => c.id !== coin.id));
                                        const resHist = await fetch("http://127.0.0.1:8000/api/trades/history");
                                        if (resHist.ok) {
                                          const histData = await resHist.json();
                                          setTradeHistory(histData);
                                        }
                                      }
                                    } catch (err) {
                                      console.error("Error logging watchlist trade:", err);
                                    } finally {
                                      setLogLoading(false);
                                    }
                                  }}
                                  className={`w-full py-2 rounded-lg font-bold text-xs font-mono transition-all cursor-pointer ${
                                    params.is_valid 
                                      ? "bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/20 animate-pulse" 
                                      : "bg-gray-800 text-gray-500 border border-gray-700 disabled:opacity-50"
                                  }`}
                                >
                                  {params.is_valid ? "🎯 Execute Limit Entry ⚡" : "🔒 Locked (<80% Confirmed)"}
                                </button>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
            {/* Trade History & Strategy Performance Dashboard */}

            <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-6 shadow-xl flex flex-col gap-6 mt-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#1E2235] pb-4">
                <div className="flex flex-col gap-1">
                  <h3 className="text-base font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    Trade Performance Journal 📈
                  </h3>
                  <p className="text-xs text-gray-400">
                    Track executing setup performance. Outcomes auto-resolve via Binance market price.
                    <br />
                    <span className="text-[10px] text-indigo-400/80 font-mono">
                      සිංහල පරිවර්තනය: ගනුදෙනු ලොගය සහ ප්‍රතිඵල ස්වයංක්‍රීයව Binance මිල මඟින් යාවත්කාලීන වේ.
                    </span>
                  </p>
                </div>
                
                {/* Glow Win Rate Badge */}
                {(() => {
                  const completedTrades = tradeHistory.filter(t => t.status === "WIN" || t.status === "LOSS");
                  const winsCount = tradeHistory.filter(t => t.status === "WIN").length;
                  const winRate = completedTrades.length > 0 
                    ? ((winsCount / completedTrades.length) * 100).toFixed(1) + "%" 
                    : "0.0%";
                  return (
                    <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-xl p-3.5 flex flex-col items-center gap-1 min-w-[140px] shadow-[0_0_15px_rgba(99,102,241,0.1)]">
                      <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest font-mono">Win Rate</span>
                      <span className="text-2xl font-bold text-white font-mono">{winRate}</span>
                    </div>
                  );
                })()}
              </div>

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-[#141626]/40 border border-[#1E2235]/60 rounded-xl p-4 flex flex-col gap-1.5 items-center">
                  <span className="text-[9px] font-bold text-gray-500 uppercase tracking-wider font-mono">Total Logged</span>
                  <span className="text-lg font-bold text-white font-mono">{tradeHistory.length}</span>
                </div>
                <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-4 flex flex-col gap-1.5 items-center">
                  <span className="text-[9px] font-bold text-emerald-400 uppercase tracking-wider font-mono">Wins 🏆</span>
                  <span className="text-lg font-bold text-emerald-400 font-mono">{tradeHistory.filter(t => t.status === "WIN").length}</span>
                </div>
                <div className="bg-rose-500/5 border border-rose-500/20 rounded-xl p-4 flex flex-col gap-1.5 items-center">
                  <span className="text-[9px] font-bold text-rose-400 uppercase tracking-wider font-mono">Losses ❌</span>
                  <span className="text-lg font-bold text-rose-400 font-mono">{tradeHistory.filter(t => t.status === "LOSS").length}</span>
                </div>
                <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 flex flex-col gap-1.5 items-center">
                  <span className="text-[9px] font-bold text-amber-400 uppercase tracking-wider font-mono">Pending ⏳</span>
                  <span className="text-lg font-bold text-amber-400 font-mono">{tradeHistory.filter(t => t.status === "PENDING").length}</span>
                </div>
              </div>

              {/* Logged Trades Table */}
              {tradeHistory.length === 0 ? (
                <div className="bg-[#141626]/20 border border-[#1E2235]/40 rounded-xl p-8 text-center text-xs text-gray-500 font-mono">
                  No trades logged in the journal yet. Click "Log Trade" on active setups above to record them.
                </div>
              ) : (
                <div className="overflow-x-auto border border-[#1E2235]/60 rounded-xl bg-black/20">
                  <table className="w-full text-left border-collapse text-xs font-mono">
                    <thead>
                      <tr className="border-b border-[#1E2235] bg-[#141626]/60 text-gray-400">
                        <th className="p-3 text-[10px] uppercase font-bold tracking-wider">Date & Time</th>
                        <th className="p-3 text-[10px] uppercase font-bold tracking-wider">Symbol</th>
                        <th className="p-3 text-[10px] uppercase font-bold tracking-wider">Type</th>
                        <th className="p-3 text-[10px] uppercase font-bold tracking-wider">Entry</th>
                        <th className="p-3 text-[10px] uppercase font-bold tracking-wider">SL</th>
                        <th className="p-3 text-[10px] uppercase font-bold tracking-wider">TP</th>
                        <th className="p-3 text-[10px] uppercase font-bold tracking-wider">Status</th>
                        <th className="p-3 text-[10px] uppercase font-bold tracking-wider text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tradeHistory.map((trade: any) => (
                        <tr key={trade.id} className="border-b border-[#1E2235]/40 hover:bg-[#141626]/20 transition-all">
                          <td className="p-3 text-gray-400">
                            {new Date(trade.timestamp ? (trade.timestamp.endsWith('Z') || trade.timestamp.includes('+') ? trade.timestamp : trade.timestamp + 'Z') : "").toLocaleString()}
                          </td>
                          <td className="p-3 text-white font-bold">
                            <div className="flex flex-col gap-0.5">
                              <div className="flex items-center gap-1.5">
                                <span>{trade.symbol}</span>
                                {livePrices[trade.symbol.toUpperCase()] !== undefined && (
                                  <span className="text-[10px] text-emerald-400 font-semibold animate-pulse">
                                    • ${livePrices[trade.symbol.toUpperCase()].toFixed(2)}
                                  </span>
                                )}
                              </div>
                              {trade.confidence !== undefined && trade.confidence !== null && trade.confidence > 0 && (
                                <span className="text-[9px] font-extrabold text-indigo-400 font-mono">
                                  {trade.confidence}% Conf.
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="p-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              trade.direction === "BULLISH" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                            }`}>
                              {trade.direction === "BULLISH" ? "LONG" : "SHORT"}
                            </span>
                          </td>
                          <td 
                            onClick={() => handleEditTradeField(trade, "entry_price", "Entry")}
                            className="p-3 text-gray-300 hover:text-white hover:underline cursor-pointer select-none decoration-dotted"
                            title="Click to edit Entry price"
                          >
                            ${trade.entry_price.toFixed(2)}
                          </td>
                          <td 
                            onClick={() => handleEditTradeField(trade, "stop_loss", "Stop Loss")}
                            className="p-3 text-rose-400 hover:text-rose-300 hover:underline cursor-pointer select-none decoration-dotted"
                            title="Click to edit Stop Loss price"
                          >
                            ${trade.stop_loss.toFixed(2)}
                          </td>
                          <td 
                            onClick={() => handleEditTradeField(trade, "take_profit", "Take Profit")}
                            className="p-3 text-emerald-400 hover:text-emerald-300 hover:underline cursor-pointer select-none decoration-dotted"
                            title="Click to edit Take Profit price"
                          >
                            ${trade.take_profit.toFixed(2)}
                          </td>
                          <td className="p-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              trade.status === "WIN"
                                ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                                : trade.status === "LOSS"
                                  ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                                  : trade.status === "ACTIVE"
                                    ? "bg-indigo-500/15 text-indigo-300 border border-indigo-500/30 animate-pulse"
                                    : trade.status === "INVALIDATED"
                                      ? "bg-orange-500/10 text-orange-400 border border-orange-500/20"
                                      : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                            }`}>
                              {trade.status}
                            </span>
                          </td>
                          <td className="p-3 text-right flex items-center justify-end gap-2">
                            <select
                              value={trade.status}
                              onChange={(e) => handleUpdateTradeStatus(trade.id, e.target.value)}
                              className="bg-[#141626] border border-[#1E2235] text-[10px] text-gray-300 rounded px-1 py-0.5 focus:outline-none focus:border-[#6366F1] font-mono cursor-pointer"
                            >
                              <option value="PENDING">PENDING ⏳</option>
                              <option value="ACTIVE">ACTIVE ⚡</option>
                              <option value="RUNNING">RUNNING 🏃‍♂️</option>
                              <option value="WIN">WIN 🏆</option>
                              <option value="LOSS">LOSS ❌</option>
                              <option value="INVALIDATED">INVALIDATED ❌</option>
                            </select>
                            
                            <button
                              onClick={() => handleDeleteTrade(trade.id)}
                              className="text-rose-400/70 hover:text-rose-400 transition-colors p-1"
                              title="Delete from journal"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                              </svg>
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
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
                <div className="flex justify-between items-center">
                  <label className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider">Timeframe</label>
                  <span className="text-[8px] bg-indigo-500/10 text-indigo-400 font-bold font-mono px-1.5 py-0.5 rounded border border-indigo-500/20 animate-pulse">
                    M1 LOCKED (STRATEGY RULE)
                  </span>
                </div>
                <div className="flex bg-[#141626] border border-[#1E2235] rounded-xl p-1 gap-1">
                  {timeframes.map((tf) => {
                    const isSelected = selectedTimeframe === tf || tf === "1m";
                    return (
                      <button
                        key={tf}
                        id={`tf-${tf}`}
                        disabled={tf !== "1m"}
                        onClick={() => setSelectedTimeframe(tf)}
                        className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                          tf === "1m"
                            ? "bg-[#6366F1] text-white shadow-md shadow-indigo-500/10"
                            : "text-gray-600 cursor-not-allowed opacity-35"
                        }`}
                      >
                        {tf}
                      </button>
                    );
                  })}
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
            <div className="flex justify-between items-center px-1">
              <span className="text-[10px] font-semibold text-gray-500 uppercase tracking-widest font-mono">TradingView Live Chart</span>
              <a
                href={`https://www.tradingview.com/chart/?symbol=BINANCE:${selectedSymbol}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] text-indigo-400 hover:text-indigo-300 transition-colors font-semibold flex items-center gap-1 font-mono"
              >
                Open in TradingView ↗
              </a>
            </div>
            <div className="flex-1 w-full rounded-xl overflow-hidden border border-[#1E2235]/60 bg-black/40">
              <iframe
                id="tradingview-chart-widget"
                src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview-chart-widget&symbol=BINANCE%3A${selectedSymbol}&interval=${getIntervalForTradingView(selectedTimeframe)}&theme=dark&style=1&timezone=America%2FNew_York&hide_volume=true`}
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
                <div className="text-sm leading-relaxed text-gray-300 font-mono bg-[#141626]/50 p-4 rounded-xl border border-[#1E2235]">
                  {renderFieldText(currentAnalysis.reasoning, "reasoning")}
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
                  <div className="text-xs leading-relaxed text-gray-400 font-mono bg-[#141626]/30 p-3.5 rounded-xl border border-[#1E2235]/40 mt-1">
                    {renderFieldText(currentAnalysis.invalidation, "invalidation")}
                  </div>
                </div>

                {/* Risk Warning & Management */}
                <div className="bg-[#11131F]/90 border border-[#1E2235] rounded-2xl p-5 shadow-xl flex flex-col gap-3">
                  <h4 className="text-xs font-semibold tracking-wider text-amber-400 uppercase flex items-center gap-1.5">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Risk Mitigation Guidelines
                  </h4>
                  <div className="text-xs leading-relaxed text-gray-400 font-mono bg-[#141626]/30 p-3.5 rounded-xl border border-[#1E2235]/40 mt-1">
                    {renderFieldText(currentAnalysis.risk_notes, "risk_notes")}
                  </div>
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
                <a
                  href="https://aistudio.google.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[10px] text-indigo-400 hover:text-indigo-300 font-semibold mt-1.5 self-start flex items-center gap-1 font-mono transition-colors"
                >
                  Check API Limits & Usage ↗
                </a>

                {/* API Key Status Feedback */}
                <div 
                  className="border rounded-xl p-3 flex flex-col gap-1 text-[11px] font-mono mt-3"
                  style={{
                    borderColor: 
                      geminiStatus.status === "VALID" ? "rgba(16, 185, 129, 0.2)" :
                      geminiStatus.status === "INVALID" ? "rgba(239, 68, 68, 0.3)" :
                      geminiStatus.status === "HIGH_DEMAND" ? "rgba(245, 158, 11, 0.3)" :
                      geminiStatus.status === "MISSING" ? "rgba(107, 114, 128, 0.2)" :
                      "rgba(59, 130, 246, 0.2)",
                    backgroundColor: 
                      geminiStatus.status === "VALID" ? "rgba(16, 185, 129, 0.05)" :
                      geminiStatus.status === "INVALID" ? "rgba(239, 68, 68, 0.05)" :
                      geminiStatus.status === "HIGH_DEMAND" ? "rgba(245, 158, 11, 0.05)" :
                      geminiStatus.status === "MISSING" ? "rgba(107, 114, 128, 0.05)" :
                      "rgba(59, 130, 246, 0.05)",
                    color: 
                      geminiStatus.status === "VALID" ? "#34D399" :
                      geminiStatus.status === "INVALID" ? "#F87171" :
                      geminiStatus.status === "HIGH_DEMAND" ? "#FBBF24" :
                      geminiStatus.status === "MISSING" ? "#9CA3AF" :
                      "#60A5FA"
                  }}
                >
                  <div className="flex items-center gap-1.5 font-bold uppercase text-[10px]">
                    <span className={`w-1.5 h-1.5 rounded-full ${
                      geminiStatus.status === "VALID" ? "bg-emerald-500 animate-pulse" :
                      geminiStatus.status === "INVALID" ? "bg-rose-500" :
                      geminiStatus.status === "HIGH_DEMAND" ? "bg-amber-500 animate-bounce" :
                      geminiStatus.status === "MISSING" ? "bg-gray-500" :
                      "bg-blue-500"
                    }`}></span>
                    Connection Status: {geminiStatus.status}
                  </div>
                  <p className="text-[10px] text-gray-300 font-medium leading-normal mt-0.5">
                    {geminiStatus.details}
                  </p>
                </div>
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
