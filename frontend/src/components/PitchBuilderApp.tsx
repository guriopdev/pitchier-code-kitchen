"use client";

import React, { useState } from "react";
import {
  Layers,
  Terminal,
  Download,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  ArrowUpRight,
  Check,
  AlertCircle,
  HelpCircle,
  TrendingUp,
  Shield,
  BarChart3,
  PieChart,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { SAMPLE_PITCH_DECK } from "@/lib/sample-deck";
import { generateClientSideDeck } from "@/lib/deck-synthesizer";
import { exportDeckToPptxClient } from "@/lib/pptx-client-exporter";
import { PitchDeck, Slide } from "@/types/deck";
import { SlideChartVisualizer } from "@/components/SlideChartVisualizer";

export default function PitchBuilderApp() {
  const [deck, setDeck] = useState<PitchDeck>(SAMPLE_PITCH_DECK);
  const [currentSlideIndex, setCurrentSlideIndex] = useState<number>(0);
  const [viewMode, setViewMode] = useState<"slide" | "critique">("slide");
  const [activeTab, setActiveTab] = useState<"viewport" | "editor">("viewport");
  const [isSynthesizing, setIsSynthesizing] = useState<boolean>(false);

  // Form input state
  const [companyName, setCompanyName] = useState<string>("Sentient Ledger");
  const [rawNotes, setRawNotes] = useState<string>(
    "We are building in-memory transaction screening for FedNow and instant payment rails. Legacy fraud solutions take minutes or hours; we do it in 6.4ms inside banking VPCs without egressing PII. Signed 3 pilots with $380k in pipeline ARR. Targeting $2.5M Seed round."
  );
  const [targetRound, setTargetRound] = useState<string>("Seed");
  const [targetAmount, setTargetAmount] = useState<string>("$2,500,000");

  const currentSlide: Slide = deck.slides[currentSlideIndex];

  const handleNext = () => {
    if (currentSlideIndex < deck.slides.length - 1) {
      setCurrentSlideIndex((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentSlideIndex > 0) {
      setCurrentSlideIndex((prev) => prev - 1);
    }
  };

  const handleExportPptx = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/pitch/export/pptx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(deck),
      });

      if (!response.ok) {
        throw new Error("Backend export unavailable");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${deck.company_name.toLowerCase().replace(/\s+/g, "_")}_pitch_deck.pptx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch {
      // Direct client-side PowerPoint synthesis when backend is offline
      await exportDeckToPptxClient(deck);
    }
  };

  const handleSynthesize = async () => {
    setIsSynthesizing(true);
    try {
      const response = await fetch("http://localhost:8000/api/v1/pitch/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_name: companyName,
          raw_notes: rawNotes,
          target_round: targetRound,
          target_amount: targetAmount,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.deck) {
          setDeck(data.deck);
          setCurrentSlideIndex(0);
          return;
        }
      }
      throw new Error("Backend response not ok");
    } catch {
      // Intelligent client-side synthesis directly parsing user notes & business models
      const clientDeck = generateClientSideDeck(
        companyName,
        rawNotes,
        targetRound,
        targetAmount
      );
      setDeck(clientDeck);
      setCurrentSlideIndex(0);
    } finally {
      setIsSynthesizing(false);
      setActiveTab("viewport");
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f9f7f2] text-[#18181b]">
      {/* Modern Top Navigation Bar */}
      <header className="border-b border-[#e4decf]/80 bg-[#f9f7f2]/90 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3.5">
            <div className="w-8 h-8 rounded-lg bg-[#18181b] flex items-center justify-center text-xs font-mono font-bold text-[#f9f7f2] shadow-sm">
              PB
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-semibold text-sm tracking-tight text-[#18181b]">
                  Startup Pitch Builder
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-medium bg-[#efebe1] text-[#71717a] border border-[#e4decf]">
                  AlloyDB · Gemini 2.5
                </span>
              </div>
              <p className="text-[11px] text-[#71717a]">
                Institutional 10-Slide Deck Engine
              </p>
            </div>
          </div>

          {/* Segmented Pill Tabs */}
          <div className="flex items-center p-1 rounded-full bg-[#f3efe6] border border-[#e4decf]">
            <button
              onClick={() => setActiveTab("viewport")}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                activeTab === "viewport"
                  ? "bg-white text-[#18181b] shadow-sm font-semibold"
                  : "text-[#71717a] hover:text-[#18181b]"
              }`}
            >
              Deck Canvas
            </button>
            <button
              onClick={() => setActiveTab("editor")}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                activeTab === "editor"
                  ? "bg-white text-[#18181b] shadow-sm font-semibold"
                  : "text-[#71717a] hover:text-[#18181b]"
              }`}
            >
              Founder Stream
            </button>
          </div>

          {/* Action Suite with Rounded Buttons */}
          <div className="flex items-center space-x-2.5">
            <button
              onClick={handleExportPptx}
              className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-medium border border-[#e4decf] bg-white hover:bg-[#f3efe6] text-[#3f3f46] hover:text-[#18181b] transition-all shadow-sm"
            >
              <Download className="w-3.5 h-3.5 text-[#71717a]" />
              <span>Export .pptx</span>
            </button>
            <button
              onClick={handleSynthesize}
              disabled={isSynthesizing}
              className="inline-flex items-center space-x-1.5 px-4 py-1.5 rounded-lg text-xs bg-[#18181b] text-white hover:bg-[#27272a] font-medium transition-all shadow-sm disabled:opacity-50"
            >
              <span>{isSynthesizing ? "Synthesizing..." : "Stress-Test Deck"}</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 flex flex-col">
        {activeTab === "editor" ? (
          /* Founder Note Stream Dashboard */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 rounded-2xl border border-[#e4decf] bg-white p-7 shadow-sm space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-[#18181b] tracking-tight">
                  Founder Input Canvas
                </h2>
                <p className="text-xs text-[#71717a] mt-1 leading-relaxed">
                  Drop unstructured founder notes, transcripts, or competitor URLs. Vertex AI Gemini 2.5 extracts key mechanisms, removes promotional fluff, and constructs the 10-slide narrative.
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-[#3f3f46] mb-1.5">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full bg-[#fcfbfa] border border-[#e4decf] rounded-xl px-4 py-2.5 text-sm text-[#18181b] focus:border-[#c2410c] focus:bg-white focus:outline-none transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-[#3f3f46] mb-1.5">
                    Raw Thoughts, Transcripts & Data Points
                  </label>
                  <textarea
                    rows={8}
                    value={rawNotes}
                    onChange={(e) => setRawNotes(e.target.value)}
                    className="w-full bg-[#fcfbfa] border border-[#e4decf] rounded-xl p-4 text-sm text-[#18181b] font-mono leading-relaxed resize-none focus:border-[#c2410c] focus:bg-white focus:outline-none transition-colors"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-[#3f3f46] mb-1.5">
                      Target Financing Stage
                    </label>
                    <input
                      type="text"
                      value={targetRound}
                      onChange={(e) => setTargetRound(e.target.value)}
                      className="w-full bg-[#fcfbfa] border border-[#e4decf] rounded-xl px-4 py-2.5 text-sm text-[#18181b] focus:border-[#c2410c] focus:bg-white focus:outline-none transition-colors"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-[#3f3f46] mb-1.5">
                      Capital Ask Target
                    </label>
                    <input
                      type="text"
                      value={targetAmount}
                      onChange={(e) => setTargetAmount(e.target.value)}
                      className="w-full bg-[#fcfbfa] border border-[#e4decf] rounded-xl px-4 py-2.5 text-sm text-[#18181b] focus:border-[#c2410c] focus:bg-white focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                <div className="pt-3">
                  <button
                    onClick={handleSynthesize}
                    disabled={isSynthesizing}
                    className="w-full py-3 rounded-xl bg-[#18181b] text-white hover:bg-[#27272a] text-sm font-medium transition-all shadow-sm"
                  >
                    {isSynthesizing ? "Synthesizing Deck with Gemini 2.5..." : "Compile 10-Slide Canonical Deck"}
                  </button>
                </div>
              </div>
            </div>

            {/* Architecture Constraints Panel */}
            <div className="lg:col-span-4 space-y-4">
              <div className="rounded-2xl border border-[#e4decf] bg-white p-6 shadow-sm space-y-2.5">
                <div className="flex items-center space-x-2 text-xs font-semibold text-[#15803d]">
                  <ShieldCheck className="w-4 h-4" />
                  <span className="uppercase tracking-wider">Zero Buzzword Policy</span>
                </div>
                <p className="text-xs text-[#71717a] leading-relaxed">
                  Strictly banned: &quot;revolutionary&quot;, &quot;game-changing&quot;, &quot;paradigm shift&quot;, &quot;disruptive&quot;. Every statement requires an operational mechanism and verifiable unit economics.
                </p>
              </div>

              <div className="rounded-2xl border border-[#e4decf] bg-white p-6 shadow-sm space-y-2.5">
                <div className="flex items-center space-x-2 text-xs font-semibold text-[#18181b]">
                  <Layers className="w-4 h-4 text-[#c2410c]" />
                  <span className="uppercase tracking-wider">AlloyDB HNSW Vector Grounding</span>
                </div>
                <p className="text-xs text-[#71717a] leading-relaxed">
                  Grounded against benchmark winning venture decks indexed in AlloyDB using pgvector HNSW cosine distance.
                </p>
              </div>
            </div>
          </div>
        ) : (
          /* Presentation Viewport */
          <div className="flex-1 flex flex-col space-y-5">
            {/* Top Deck Info Bar */}
            <div className="flex items-center justify-between px-1">
              <div className="flex items-center space-x-3 text-xs">
                <span className="font-semibold text-[#18181b]">{deck.company_name}</span>
                <span className="text-[#d5ccba]">•</span>
                <span className="text-[#71717a] truncate max-w-lg">{deck.one_liner}</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="px-2.5 py-1 rounded-full bg-white border border-[#e4decf] text-xs font-medium text-[#3f3f46] shadow-sm">
                  Round: {deck.target_round}
                </span>
                <span className="px-2.5 py-1 rounded-full bg-white border border-[#e4decf] text-xs font-mono font-semibold text-[#18181b] shadow-sm tabular-nums">
                  Ask: {deck.target_amount}
                </span>
              </div>
            </div>

            {/* 16:9 Presentation Canvas (Modern Rounded Card Container) */}
            <div className="relative w-full min-h-[580px] lg:aspect-[16/9] rounded-3xl border border-[#e4decf] bg-white shadow-sm flex flex-col justify-between p-6 sm:p-8 lg:p-10 overflow-hidden">
              {/* Slide Meta Bar */}
              <div className="flex items-center justify-between border-b border-[#f0ebe1] pb-4">
                <div className="flex items-center space-x-3">
                  <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-[#f3efe6] text-[#18181b] border border-[#e4decf]">
                    {String(currentSlide.slide_number).padStart(2, "0")} / 10
                  </span>
                  <span className="text-xs font-mono font-medium text-[#71717a] uppercase tracking-wider">
                    {currentSlide.slide_type.replace("_", " ")}
                  </span>
                </div>

                {/* View Mode Toggle Pill */}
                <div className="flex items-center p-1 rounded-full bg-[#f3efe6] border border-[#e4decf]">
                  <button
                    onClick={() => setViewMode("slide")}
                    className={`px-3.5 py-1 rounded-full text-xs font-medium transition-all ${
                      viewMode === "slide"
                        ? "bg-white text-[#18181b] font-semibold shadow-sm"
                        : "text-[#71717a] hover:text-[#18181b]"
                    }`}
                  >
                    Slide View
                  </button>
                  <button
                    onClick={() => setViewMode("critique")}
                    className={`px-3.5 py-1 rounded-full text-xs font-medium transition-all ${
                      viewMode === "critique"
                        ? "bg-white text-[#b45309] font-semibold shadow-sm"
                        : "text-[#71717a] hover:text-[#b45309]"
                    }`}
                  >
                    Partner Critique
                  </button>
                </div>
              </div>

              {/* Slide Body */}
              <div className="flex-1 flex flex-col justify-center py-4 my-auto overflow-y-auto max-h-full">
                <AnimatePresence mode="wait">
                  {viewMode === "slide" ? (
                    <motion.div
                      key={`slide-${currentSlide.slide_number}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
                      className="space-y-4"
                    >
                      <div>
                        <h1 className="text-xl sm:text-2xl lg:text-3xl font-semibold text-[#18181b] tracking-tight leading-tight max-w-4xl">
                          {currentSlide.headline}
                        </h1>
                        {currentSlide.subtitle && (
                          <p className="text-xs sm:text-sm text-[#71717a] mt-1 font-normal">
                            {currentSlide.subtitle}
                          </p>
                        )}
                      </div>

                      {/* Content Grid */}
                      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 pt-0.5 items-start">
                        {/* Key Takeaway Statements */}
                        <div className="lg:col-span-7 space-y-2.5">
                          {currentSlide.key_points.map((point, idx) => (
                            <div
                              key={idx}
                              className="flex items-start space-x-3 p-3.5 rounded-xl border border-[#e4decf]/70 bg-[#faf8f4] hover:bg-[#f5f1e8] transition-colors"
                            >
                              <span className="text-xs font-mono font-semibold text-[#c2410c] mt-0.5 px-1.5 py-0.5 rounded bg-[#ffedd5]/60 flex-shrink-0">
                                0{idx + 1}
                              </span>
                              <p className="text-xs sm:text-sm text-[#27272a] leading-relaxed">
                                {point}
                              </p>
                            </div>
                          ))}
                        </div>

                        {/* Metric Cards & Visualizations Callout Column */}
                        <div className="lg:col-span-5 space-y-3">
                          {/* Interactive Pie / Bar Chart Visualizer */}
                          {currentSlide.chart && (
                            <SlideChartVisualizer chart={currentSlide.chart} />
                          )}

                          {/* Metric Cards (Compact grid if chart is present, stacked if not) */}
                          <div className={`grid ${currentSlide.chart ? "grid-cols-2 sm:grid-cols-3 lg:grid-cols-2" : "grid-cols-1 sm:grid-cols-3 lg:grid-cols-1"} gap-2`}>
                            {currentSlide.metrics.map((m, idx) => (
                              <div
                                key={idx}
                                className="p-3 rounded-xl border border-[#e4decf] bg-[#f9f7f2]"
                              >
                                <div className="text-[10px] font-mono font-medium text-[#71717a] uppercase tracking-wider truncate">
                                  {m.label}
                                </div>
                                <div className="text-lg sm:text-xl font-bold font-mono text-[#18181b] tracking-tight tabular-nums mt-0.5">
                                  {m.value}
                                </div>
                                {m.context && (
                                  <div className="text-[11px] text-[#71717a] mt-0.5 truncate">
                                    {m.context}
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>

                          {/* Institutional Strategic Analysis Card */}
                          {currentSlide.analysis && (
                            <div className="rounded-xl border border-[#e4decf] bg-[#f3efe6]/80 p-3 space-y-2">
                              <div className="flex items-center justify-between border-b border-[#e4decf]/80 pb-1">
                                <div className="flex items-center space-x-1.5 text-[10px] font-mono font-semibold text-[#18181b] uppercase">
                                  <TrendingUp className="w-3 h-3 text-[#c2410c]" />
                                  <span>Strategic Analysis</span>
                                </div>
                                {currentSlide.analysis.moat_rating && (
                                  <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-[#18181b] text-white font-medium">
                                    {currentSlide.analysis.moat_rating} Moat
                                  </span>
                                )}
                              </div>

                              <div className="space-y-1 text-xs text-[#27272a] leading-relaxed">
                                <div>
                                  <span className="font-semibold text-[#18181b]">Takeaway: </span>
                                  <span className="text-[11px]">{currentSlide.analysis.strategic_takeaway}</span>
                                </div>
                                {currentSlide.analysis.unit_economics_verdict && (
                                  <div className="text-[10px] text-[#71717a] font-mono bg-white/70 p-1.5 rounded-lg border border-[#e4decf]/50">
                                    <span className="font-semibold text-[#18181b]">Economics: </span>
                                    {currentSlide.analysis.unit_economics_verdict}
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ) : (
                    /* Partner Critique Modal / View */
                    <motion.div
                      key={`critique-${currentSlide.slide_number}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
                      className="space-y-4"
                    >
                      <div className="rounded-xl border border-[#e4decf] bg-[#f9f7f2] p-3 text-xs font-mono flex items-center justify-between">
                        <span className="text-[#18181b] font-semibold">
                          TERMINAL DIALOGUE // TIER-1 VENTURE PARTNER EVALUATION
                        </span>
                        <span className="text-[#71717a] font-medium">
                          TARGET: SLIDE {String(currentSlide.slide_number).padStart(2, "0")}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* Strengths */}
                        <div className="rounded-xl border border-[#bbf7d0] bg-[#f0fdf4] p-4 space-y-3">
                          <div className="flex items-center space-x-2 border-b border-[#bbf7d0] pb-2 text-xs font-semibold text-[#15803d]">
                            <Check className="w-3.5 h-3.5" />
                            <span className="uppercase tracking-wider">Signals (Pass)</span>
                          </div>
                          <ul className="space-y-2">
                            {currentSlide.investor_critique.strengths.map((item, i) => (
                              <li key={i} className="text-xs text-[#166534] leading-relaxed">
                                • {item}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Red Flags */}
                        <div className="rounded-xl border border-[#fecdd3] bg-[#fff1f2] p-4 space-y-3">
                          <div className="flex items-center space-x-2 border-b border-[#fecdd3] pb-2 text-xs font-semibold text-[#be123c]">
                            <AlertCircle className="w-3.5 h-3.5" />
                            <span className="uppercase tracking-wider">Friction Points (Fail)</span>
                          </div>
                          <ul className="space-y-2">
                            {currentSlide.investor_critique.red_flags.map((item, i) => (
                              <li key={i} className="text-xs text-[#9f1239] leading-relaxed">
                                • {item}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Grilling Questions */}
                        <div className="rounded-xl border border-[#fed7aa] bg-[#fff7ed] p-4 space-y-3">
                          <div className="flex items-center space-x-2 border-b border-[#fed7aa] pb-2 text-xs font-semibold text-[#c2410c]">
                            <HelpCircle className="w-3.5 h-3.5" />
                            <span className="uppercase tracking-wider">Diligence Interrogation</span>
                          </div>
                          <ul className="space-y-2">
                            {currentSlide.investor_critique.hard_questions.map((item, i) => (
                              <li key={i} className="text-xs text-[#9a3412] leading-relaxed">
                                • {item}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Viewport Bottom Bar: Founder Script & Controls */}
              <div className="border-t border-[#f0ebe1] pt-4 flex items-center justify-between">
                <div className="max-w-2xl">
                  <span className="text-[11px] font-mono text-[#71717a] uppercase tracking-wider block mb-0.5 font-semibold">
                    Founder Voiceover (30-45s)
                  </span>
                  <p className="text-xs text-[#52525b] italic truncate">
                    &quot;{currentSlide.speaker_notes}&quot;
                  </p>
                </div>

                <div className="flex items-center space-x-1.5 p-1 rounded-xl bg-[#f3efe6] border border-[#e4decf]">
                  <button
                    onClick={handlePrev}
                    disabled={currentSlideIndex === 0}
                    className="p-1.5 rounded-lg text-[#71717a] hover:text-[#18181b] hover:bg-white disabled:opacity-25 transition-all"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="text-xs font-mono px-2 text-[#18181b] font-semibold">
                    {String(currentSlideIndex + 1).padStart(2, "0")} / 10
                  </span>
                  <button
                    onClick={handleNext}
                    disabled={currentSlideIndex === deck.slides.length - 1}
                    className="p-1.5 rounded-lg text-[#71717a] hover:text-[#18181b] hover:bg-white disabled:opacity-25 transition-all"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Rounded Rectangular 10-Slide Step Dock */}
            <div className="grid grid-cols-5 sm:grid-cols-10 gap-2 pt-1">
              {deck.slides.map((s, idx) => (
                <button
                  key={s.slide_number}
                  onClick={() => {
                    setCurrentSlideIndex(idx);
                    setViewMode("slide");
                  }}
                  className={`p-2.5 rounded-xl text-left border transition-all ${
                    currentSlideIndex === idx
                      ? "border-[#18181b] bg-white text-[#18181b] shadow-sm font-semibold ring-1 ring-[#18181b]"
                      : "border-[#e4decf] bg-[#f3efe6]/60 text-[#71717a] hover:border-[#d5ccba] hover:bg-white hover:text-[#18181b]"
                  }`}
                >
                  <div className="text-[10px] font-mono mb-1 text-[#a1a1aa]">
                    {String(s.slide_number).padStart(2, "0")}
                  </div>
                  <div className="text-[11px] font-medium truncate capitalize">
                    {s.slide_type.replace("_", " ")}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Modern Minimalist Footer */}
      <footer className="border-t border-[#e4decf] py-5 bg-[#f9f7f2] mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between text-xs font-mono text-[#71717a]">
          <div>STARTUP PITCH BUILDER · OPEN SOURCE ARCHITECTURE</div>
          <div>FASTAPI · CLOUD RUN · ALLOYDB HNSW · GEMINI 2.5</div>
        </div>
      </footer>
    </div>
  );
}
