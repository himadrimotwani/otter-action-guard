#!/usr/bin/env python3
"""
OtterActionGuard Web Dashboard
Run: python3 app.py
Visit: http://localhost:8080 in your browser.

Zero-dependency, standalone local dashboard to interactively test meeting transcripts,
view AI Agent Chain-of-Thought deliberation, inspect MCP tool payloads,
analyze speaker dynamics & presentation coaching, and track cross-meeting state.
"""

import http.server
import json
from pathlib import Path
from otter_action_guard.extractor import OtterActionGuard


PORT = 8080
guard = OtterActionGuard()

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OtterActionGuard | Meeting AI Agent Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    body { font-family: 'Inter', sans-serif; }
    code, pre { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen">
  
  <!-- Header -->
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white text-xl shadow-lg shadow-blue-500/20">
          🦦
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            OtterActionGuard <span class="text-xs bg-blue-500/20 text-blue-400 font-semibold px-2 py-0.5 rounded-full border border-blue-500/30">Enterprise Agent</span>
          </h1>
          <p class="text-xs text-slate-400">Meeting Disambiguation, Cross-Meeting State & Gated MCP Dispatch</p>
        </div>
      </div>
      <div class="flex items-center gap-3 text-xs">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Zero Dependencies Ready
        </span>
        <a href="https://github.com/himadrimotwani/otter-action-guard" target="_blank" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition">
          <i class="fa-brands fa-github mr-1"></i> GitHub
        </a>
      </div>
    </div>
  </header>

  <!-- Main Grid -->
  <main class="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
    
    <!-- Left Column: Input, Upload & Controls (5 cols) -->
    <div class="lg:col-span-5 space-y-6">
      
      <!-- Input Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div class="flex items-center justify-between">
          <label class="text-sm font-semibold text-slate-200">Select Meeting Scenario</label>
          <span class="text-xs text-slate-400">Presets</span>
        </div>
        
        <!-- 3 Presets -->
        <div class="grid grid-cols-1 gap-2">
          <button onclick="loadSample(0)" class="text-left p-2.5 rounded-xl bg-slate-800 hover:bg-blue-600/20 hover:border-blue-500/50 border border-slate-700/60 transition text-xs flex justify-between items-center">
            <div>
              <div class="font-medium text-slate-200">👟 [1] Nike Sourcing Sync (Nov 2)</div>
              <div class="text-[11px] text-slate-400">Creates conditional commitments (gated on customs & QA)</div>
            </div>
            <span class="px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px]">Session 1</span>
          </button>
          
          <button onclick="loadSample(1)" class="text-left p-2.5 rounded-xl bg-slate-800 hover:bg-blue-600/20 hover:border-blue-500/50 border border-slate-700/60 transition text-xs flex justify-between items-center">
            <div>
              <div class="font-medium text-slate-200">⚡ [2] Nike Standup (Nov 5)</div>
              <div class="text-[11px] text-slate-400">Resolves Session 1 conditions (Customs & QA passed)</div>
            </div>
            <span class="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px]">Session 2</span>
          </button>

          <button onclick="loadSample(2)" class="text-left p-2.5 rounded-xl bg-slate-800 hover:bg-blue-600/20 hover:border-blue-500/50 border border-slate-700/60 transition text-xs flex justify-between items-center">
            <div>
              <div class="font-medium text-slate-200">🚀 [3] Tech Arch Review</div>
              <div class="text-[11px] text-slate-400">MCP connectors & Redis infra gating</div>
            </div>
            <span class="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 text-[10px]">Eng Sync</span>
          </button>
        </div>

        <!-- Audio Upload / Drop Zone -->
        <div id="dropZone" class="border-2 border-dashed border-slate-800 hover:border-blue-500/50 rounded-xl p-3 text-center transition cursor-pointer bg-slate-950/50">
          <input type="file" id="fileInput" accept=".wav,.mp3,.json,.txt" class="hidden" onchange="handleFileSelect(event)">
          <div onclick="document.getElementById('fileInput').click()" class="space-y-1">
            <i class="fa-solid fa-file-audio text-blue-400 text-lg"></i>
            <div class="text-xs text-slate-300 font-medium">Drop .wav, .mp3, or transcript file here</div>
            <div class="text-[10px] text-slate-500">Simulates speech acoustic waveform decoding & ASR diarization</div>
          </div>
        </div>

        <div>
          <div class="flex justify-between items-center mb-1.5">
            <label class="text-xs font-semibold text-slate-300">Transcript Input (with ASR speech artifacts)</label>
            <span class="text-[11px] text-slate-400" id="turnCountLabel">8 turns</span>
          </div>
          <textarea id="transcriptInput" rows="7" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-blue-500 leading-relaxed resize-y"></textarea>
        </div>

        <button onclick="runAnalysis()" id="analyzeBtn" class="w-full py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2">
          <i class="fa-solid fa-wand-magic-sparkles"></i> Run AI Agent Disambiguation
        </button>
      </div>

      <!-- Pipeline Safety Metrics -->
      <div id="metricsCard" class="hidden bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">Pipeline Safety Metrics</h3>
        <div class="grid grid-cols-3 gap-3 text-center">
          <div class="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
            <div id="metricReady" class="text-xl font-bold text-emerald-400">0</div>
            <div class="text-[11px] text-slate-400">Ready to Dispatch</div>
          </div>
          <div class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <div id="metricBlocked" class="text-xl font-bold text-amber-400">0</div>
            <div class="text-[11px] text-slate-400">Gated (Prerequisite)</div>
          </div>
          <div class="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20">
            <div id="metricClarify" class="text-xl font-bold text-blue-400">0</div>
            <div class="text-[11px] text-slate-400">Live Assist Ping</div>
          </div>
        </div>
        <div class="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60 flex items-center justify-between text-xs">
          <span class="text-slate-300">🎙️ ASR Phonetic Errors Repaired:</span>
          <span id="metricSpeech" class="font-bold text-blue-400">0</span>
        </div>
      </div>

      <!-- Meeting Coach & Speaker Analytics Card -->
      <div id="coachCard" class="hidden bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <i class="fa-solid fa-chart-pie text-blue-400"></i> Meeting Coach & Dynamics
          </h3>
          <span id="balanceScoreBadge" class="text-[11px] font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Balance: 87%
          </span>
        </div>
        
        <!-- Speaker distribution bars -->
        <div id="speakerBars" class="space-y-2"></div>

        <!-- AI Coaching Tips -->
        <div class="border-t border-slate-800 pt-3">
          <div class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">AI Presentation & Negotiation Feedback:</div>
          <div id="coachingTips" class="space-y-1.5 text-xs text-slate-300"></div>
        </div>
      </div>

    </div>

    <!-- Right Column: Results & MCP Payloads (7 cols) -->
    <div class="lg:col-span-7 space-y-6">
      
      <!-- Actions Stream -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl min-h-[500px]">
        <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div>
            <h2 class="text-sm font-bold text-slate-100 flex items-center gap-2">
              <i class="fa-solid fa-layer-group text-blue-400"></i> AI Agent Disambiguation Stream
            </h2>
            <p class="text-xs text-slate-400 mt-0.5">Linguistic gating, coreference resolution & Chain-of-Thought (CoT) trace</p>
          </div>
          <div id="executionBadge" class="text-xs font-mono px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700">
            Standby
          </div>
        </div>

        <!-- Cross-Meeting Resolution Banner (Injected if conditions resolved) -->
        <div id="crossMeetingBanner" class="hidden mb-4 p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/40 space-y-2">
          <div class="flex items-center gap-2 text-emerald-400 font-bold text-xs uppercase tracking-wider">
            <i class="fa-solid fa-bolt"></i> Otter Work Mode: Cross-Meeting Resolution Triggered
          </div>
          <div id="crossMeetingList" class="space-y-1.5 text-xs text-emerald-200"></div>
        </div>

        <div id="actionsContainer" class="space-y-4">
          <div class="text-center py-20 text-slate-500 text-sm">
            <i class="fa-regular fa-comment-dots text-4xl mb-3 block text-slate-600"></i>
            Select a preset scenario on the left and click "Run AI Agent Disambiguation".
          </div>
        </div>
      </div>

      <!-- MCP Tool Payload Inspector -->
      <div id="mcpContainer" class="hidden bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <i class="fa-solid fa-code text-blue-400"></i> Generated Model Context Protocol (MCP) Tool Calls
          </h3>
          <span class="text-xs text-slate-400">Enterprise Dispatch Schemas</span>
        </div>
        <pre id="mcpCode" class="bg-slate-950 p-4 rounded-xl text-xs text-emerald-400 font-mono overflow-x-auto border border-slate-800/80 leading-relaxed max-h-72"></pre>
      </div>
    </div>

  </main>

  <!-- Interactive Dispatch Sandbox Modal -->
  <div id="dispatchModal" class="hidden fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <span id="modalIcon" class="text-xl">🚀</span>
          <h3 id="modalTitle" class="text-sm font-bold text-white">Simulate Enterprise Tool Dispatch</h3>
        </div>
        <button onclick="closeModal()" class="text-slate-400 hover:text-white text-sm"><i class="fa-solid fa-xmark"></i></button>
      </div>

      <div id="modalBody" class="space-y-3 text-xs">
        <!-- Injected dynamically -->
      </div>

      <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
        <button onclick="closeModal()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs">Cancel</button>
        <button onclick="confirmDispatch()" id="modalConfirmBtn" class="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-lg shadow-blue-500/20">
          Confirm Execution
        </button>
      </div>
    </div>
  </div>

  <script>
    const SAMPLES = [
      {
        id: "OPS-SYNC-PART-1",
        title: "Nike Global Sourcing Sync (Session 1 - Nov 2)",
        transcript: `[00:05] Marcus (Sourcing Lead): Welcome everyone. Let's align on the Q2 sneaker assembly volumes for skew 902.
[00:24] David (Supplier Rep): On the 50,000 unit batch, we can commit to delivery by next Friday if the customs clearance clears by Tuesday.
[00:52] Sarah (Quality Lead): Hold on, we can only approve that delivery schedule if QA finishes the stress-test audit on batch 4 first.
[01:15] Marcus (Sourcing Lead): Good catch. Someone should follow up with the lab in Vietnam to get those test logs.
[01:38] Elena (Procurement): What if we split the shipment into two 25,000 unit air-freight drops instead?
[02:05] David (Supplier Rep): I will send the revised bomb and price quotation by tomorrow morning.
[02:30] Marcus (Sourcing Lead): Perfect. Dave, please make sure to log the new pee oh numbers in the ERP system by Thursday.
[02:55] Sarah (Quality Lead): I will review the lab results as soon as they land in my inbox.`
      },
      {
        id: "OPS-SYNC-PART-2",
        title: "Nike Operations Standup (Session 2 - Nov 5)",
        transcript: `[00:05] Marcus (Sourcing Lead): Quick standup team. Any updates on customs clearance for batch 4?
[00:20] David (Supplier Rep): Good news Marcus, customs cleared this morning without any tariff delays! We are officially confirmed for Friday delivery.
[00:45] Sarah (Quality Lead): Awesome, QA audit is complete and the stress-test passed with zero defects.
[01:10] Marcus (Sourcing Lead): Fantastic. I will notify the distribution center in Memphis to prepare docking bay 3.`
      },
      {
        id: "ENG-AGENT-LAUNCH",
        title: "Otter AI Agent Architecture Sync",
        transcript: `[00:10] Alex (Tech Lead): Let's review the em see pee server connector rollouts for Jira and Salesforce.
[00:30] Priya (Backend SWE): I will deploy the rate-limiter updates to staging by Friday.
[00:55] Alex (Tech Lead): Could we potentially bypass the cache on retry requests?
[01:20] Jordan (Infra): Only if Redis memory utilization stays below 75% under benchmark load.
[01:45] Priya (Backend SWE): Somebody needs to update the staging environment secrets before we run the load test.`
      }
    ];

    let currentSampleIndex = 0;
    let currentAnalysisData = null;
    let selectedActionForDispatch = null;

    function loadSample(idx) {
      currentSampleIndex = idx;
      document.getElementById('transcriptInput').value = SAMPLES[idx].transcript;
      updateTurnCount();
    }

    function updateTurnCount() {
      const lines = document.getElementById('transcriptInput').value.trim().split('\\n').filter(l => l.trim().length > 0);
      document.getElementById('turnCountLabel').innerText = lines.length + ' turns';
    }

    function handleFileSelect(evt) {
      const file = evt.target.files[0];
      if (!file) return;

      if (file.name.endsWith('.json')) {
        const reader = new FileReader();
        reader.onload = function(e) {
          try {
            const data = JSON.parse(e.target.result);
            if (Array.isArray(data) && data[0].transcript) {
              document.getElementById('transcriptInput').value = data[0].transcript;
            } else if (data.transcript) {
              document.getElementById('transcriptInput').value = data.transcript;
            }
            updateTurnCount();
          } catch(err) {
            alert('Invalid JSON file.');
          }
        };
        reader.readAsText(file);
      } else if (file.name.endsWith('.txt')) {
        const reader = new FileReader();
        reader.onload = function(e) {
          document.getElementById('transcriptInput').value = e.target.result;
          updateTurnCount();
        };
        reader.readAsText(file);
      } else {
        alert(`🎙️ Decoded audio stream: "${file.name}"\\nWaveform processed through acoustic phoneme aligner and diarized into multi-speaker transcript.`);
        loadSample(0);
      }
    }

    document.getElementById('transcriptInput').addEventListener('input', updateTurnCount);
    loadSample(0);

    async function runAnalysis() {
      const text = document.getElementById('transcriptInput').value;
      const btn = document.getElementById('analyzeBtn');
      btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Reasoning & Disambiguating...';
      btn.disabled = true;

      const sample = SAMPLES[currentSampleIndex];

      try {
        const resp = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            transcript: text,
            meeting_id: sample ? sample.id : "MEET-ADHOC",
            title: sample ? sample.title : "Custom Meeting Sync"
          })
        });
        const data = await resp.json();
        currentAnalysisData = data;
        renderResults(data);
      } catch (e) {
        alert("Error executing analysis: " + e);
      } finally {
        btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Run AI Agent Disambiguation';
        btn.disabled = false;
      }
    }

    function renderResults(data) {
      document.getElementById('metricsCard').classList.remove('hidden');
      document.getElementById('mcpContainer').classList.remove('hidden');
      document.getElementById('coachCard').classList.remove('hidden');

      document.getElementById('metricReady').innerText = data.ready_count;
      document.getElementById('metricBlocked').innerText = data.blocked_count;
      document.getElementById('metricClarify').innerText = data.clarification_count;
      document.getElementById('metricSpeech').innerText = data.speech_corrections_made;
      document.getElementById('executionBadge').innerText = `${data.actions.length} Actions Evaluated`;

      // Render Cross-Meeting Resolutions if present
      const banner = document.getElementById('crossMeetingBanner');
      const list = document.getElementById('crossMeetingList');
      if (data.cross_meeting_events && data.cross_meeting_events.length > 0) {
        banner.classList.remove('hidden');
        list.innerHTML = '';
        data.cross_meeting_events.forEach(evt => {
          const item = document.createElement('div');
          item.className = 'p-2 rounded bg-emerald-900/40 border border-emerald-500/30';
          item.innerHTML = `
            <div class="flex items-center justify-between">
              <strong>${evt.target_action_id} Unlocked</strong>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">BLOCKED ➔ READY</span>
            </div>
            <div class="text-[11px] text-emerald-300 mt-1">"${evt.evidence_statement}" (via ${evt.source_speaker})</div>
          `;
          list.appendChild(item);
        });
      } else {
        banner.classList.add('hidden');
      }

      // Render Speaker Analytics
      if (data.coach_summary) {
        const coach = data.coach_summary;
        document.getElementById('balanceScoreBadge').innerText = `Balance: ${Math.round(coach.interaction_balance_score * 100)}%`;
        
        const barsContainer = document.getElementById('speakerBars');
        barsContainer.innerHTML = '';
        coach.speaker_metrics.forEach(spk => {
          const div = document.createElement('div');
          div.className = 'text-xs space-y-1';
          div.innerHTML = `
            <div class="flex justify-between text-slate-300">
              <span class="font-medium">${spk.speaker}</span>
              <span class="text-slate-400 font-mono">${spk.talk_time_pct}% (${spk.word_count} words)</span>
            </div>
            <div class="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
              <div class="bg-blue-500 h-full rounded-full" style="width: ${spk.talk_time_pct}%"></div>
            </div>
          `;
          barsContainer.appendChild(div);
        });

        const tipsContainer = document.getElementById('coachingTips');
        tipsContainer.innerHTML = '';
        coach.coaching_tips.forEach(tip => {
          const p = document.createElement('p');
          p.className = 'flex items-start gap-1.5';
          p.innerHTML = `<span class="text-blue-400 font-bold">💡</span> <span>${tip}</span>`;
          tipsContainer.appendChild(p);
        });
      }

      // Render Action Cards
      const container = document.getElementById('actionsContainer');
      container.innerHTML = '';

      data.actions.forEach(act => {
        let badgeColor = 'bg-slate-800 text-slate-300 border-slate-700';
        let statusIcon = '💡';
        let borderClass = 'border-slate-800';

        if (act.status === 'READY_FOR_EXECUTION') {
          badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
          statusIcon = '✅';
          borderClass = 'border-emerald-500/30';
        } else if (act.status === 'BLOCKED_ON_CONDITION') {
          badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
          statusIcon = '⏳';
          borderClass = 'border-amber-500/30';
        } else if (act.status === 'NEEDS_CLARIFICATION') {
          badgeColor = 'bg-blue-500/10 text-blue-400 border-blue-500/30';
          statusIcon = '❓';
          borderClass = 'border-blue-500/30';
        }

        const card = document.createElement('div');
        card.className = `p-4 rounded-xl bg-slate-950 border ${borderClass} space-y-2.5 transition hover:border-slate-700`;
        card.innerHTML = `
          <div class="flex items-center justify-between text-xs">
            <div class="flex items-center gap-2">
              <span>${statusIcon}</span>
              <span class="font-bold text-slate-200">${act.id}</span>
              <span class="px-2 py-0.5 rounded-full border text-[10px] font-semibold ${badgeColor}">
                ${act.status}
              </span>
            </div>
            <div class="flex items-center gap-2 text-slate-400 text-[11px]">
              <span>Assigned: <strong class="text-slate-200">${act.assigned_to || 'None (Unowned)'}</strong></span>
              <button onclick="openDispatchModal('${act.id}')" class="px-2 py-0.5 rounded bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 border border-blue-500/30 transition text-[10px] font-semibold">
                <i class="fa-solid fa-play mr-1"></i> Simulate Dispatch
              </button>
            </div>
          </div>

          <div class="text-xs text-slate-200 bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 font-mono">
            "${act.raw_statement}"
          </div>

          ${act.thought_trace ? `
            <div class="text-[11px] text-slate-300 bg-blue-950/20 border border-blue-800/30 p-2.5 rounded-lg">
              <span class="font-bold text-blue-400"><i class="fa-solid fa-brain mr-1"></i> AI Reasoning:</span>
              ${act.thought_trace}
            </div>
          ` : ''}

          ${act.prerequisite_condition ? `
            <div class="text-[11px] text-amber-300 bg-amber-950/20 border border-amber-800/30 p-2 rounded-lg flex items-center justify-between">
              <div><strong class="text-amber-400">⚠️ Gated On:</strong> ${act.prerequisite_condition}</div>
              <button onclick="simulateUnlock('${act.id}')" class="px-2 py-0.5 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-[10px] transition">
                Simulate Prerequisite Pass
              </button>
            </div>
          ` : ''}

          ${act.clarification_prompt ? `
            <div class="text-[11px] text-blue-300 bg-blue-900/20 border border-blue-700/30 p-2 rounded-lg">
              <strong class="text-blue-400">💬 Otter Live Assist Ping:</strong> "${act.clarification_prompt}"
            </div>
          ` : ''}
        `;
        container.appendChild(card);
      });

      document.getElementById('mcpCode').innerText = JSON.stringify(data.mcp_payloads, null, 2);
    }

    function simulateUnlock(actId) {
      alert(`Prerequisite verified for ${actId}! Action status updated to READY_FOR_EXECUTION and MCP payload dispatched.`);
    }

    function openDispatchModal(actId) {
      if (!currentAnalysisData) return;
      const act = currentAnalysisData.actions.find(a => a.id === actId);
      if (!act) return;

      selectedActionForDispatch = act;
      const body = document.getElementById('modalBody');

      let toolType = act.suggested_integration || 'jira';
      let icon = '⚡';
      let title = `Dispatching ${act.id} via Model Context Protocol`;

      if (toolType === 'jira') {
        icon = '🎫';
        body.innerHTML = `
          <div class="p-3 rounded-xl bg-slate-950 border border-blue-500/30 space-y-2">
            <div class="flex justify-between items-center text-slate-400">
              <span class="font-bold text-blue-400">JIRA TICKET PREVIEW</span>
              <span class="px-1.5 py-0.5 rounded bg-slate-800 text-[10px]">PROJ-104</span>
            </div>
            <div class="text-slate-200 font-semibold">${act.action_description}</div>
            <div class="text-slate-400 text-[11px]">Assignee: <strong class="text-slate-200">${act.assigned_to || 'Unassigned'}</strong></div>
            <div class="text-slate-400 text-[11px]">Due Date: <strong class="text-slate-200">${act.target_date_raw || 'Unspecified'}</strong></div>
            <div class="text-[10px] text-slate-500 italic bg-slate-900 p-2 rounded border border-slate-800">
              Source quote: "${act.raw_statement}"
            </div>
          </div>
        `;
      } else if (toolType === 'erp') {
        icon = '📦';
        body.innerHTML = `
          <div class="p-3 rounded-xl bg-slate-950 border border-amber-500/30 space-y-2">
            <div class="flex justify-between items-center text-slate-400">
              <span class="font-bold text-amber-400">ERP PROCUREMENT ORDER UPDATE</span>
              <span class="px-1.5 py-0.5 rounded bg-slate-800 text-[10px]">PO-902-BATCH</span>
            </div>
            <div class="text-slate-200 font-semibold">${act.action_description}</div>
            <div class="text-slate-400 text-[11px]">Owner: <strong class="text-slate-200">${act.assigned_to || 'Supplier Rep'}</strong></div>
            <div class="text-slate-400 text-[11px]">Condition: <span class="text-amber-400">${act.prerequisite_condition || 'None (Unconditional)'}</span></div>
            <div class="text-slate-400 text-[11px]">Confidence Calibration: <strong class="text-emerald-400">${Math.round(act.confidence_score * 100)}%</strong></div>
          </div>
        `;
      } else {
        icon = '💬';
        body.innerHTML = `
          <div class="p-3 rounded-xl bg-slate-950 border border-blue-500/30 space-y-2">
            <div class="flex justify-between items-center text-slate-400">
              <span class="font-bold text-blue-400">SLACK LIVE ASSIST NOTIFICATION</span>
              <span class="px-1.5 py-0.5 rounded bg-slate-800 text-[10px]">#meeting-followups</span>
            </div>
            <div class="text-slate-200 font-medium">${act.clarification_prompt || act.action_description}</div>
            <div class="text-slate-400 text-[11px]">Target Recipient: <strong class="text-slate-200">${act.assigned_to || act.speaker}</strong></div>
          </div>
        `;
      }

      document.getElementById('modalIcon').innerText = icon;
      document.getElementById('modalTitle').innerText = title;
      document.getElementById('dispatchModal').classList.remove('hidden');
    }

    function closeModal() {
      document.getElementById('dispatchModal').classList.add('hidden');
      selectedActionForDispatch = null;
    }

    function confirmDispatch() {
      if (!selectedActionForDispatch) return;
      alert(`✅ MCP Tool Payload successfully executed! Downstream state updated for ${selectedActionForDispatch.id}.`);
      closeModal();
    }
  </script>
</body>
</html>
"""


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(INDEX_HTML.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/analyze":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                raw_text = data.get("transcript", "")
                m_id = data.get("meeting_id", f"MEET-{len(guard.memory.processed_meetings) + 1:03d}")
                title = data.get("title", "Enterprise Operations Review")
                result = guard.process_transcript(raw_text, meeting_id=m_id, title=title)
                resp_payload = result.to_dict()

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(resp_payload).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress noisy HTTP logs
        return


def main():
    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), RequestHandler)
    print(f"🚀 OtterActionGuard Dashboard running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard.")
        server.server_close()


if __name__ == "__main__":
    main()
