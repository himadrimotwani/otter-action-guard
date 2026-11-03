#!/usr/bin/env python3
"""
OtterActionGuard Web Dashboard
Run: python3 app.py
Visit: http://localhost:8080 in your browser.

Zero-dependency, standalone local dashboard to interactively test meeting transcripts,
view AI Agent Chain-of-Thought deliberation, and inspect MCP tool payloads.
"""

import http.server
import json
import urllib.parse
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
            OtterActionGuard <span class="text-xs bg-blue-500/20 text-blue-400 font-semibold px-2 py-0.5 rounded-full border border-blue-500/30">AI Meeting Agent</span>
          </h1>
          <p class="text-xs text-slate-400">Meeting-to-Action Disambiguation & Gated MCP Tool Dispatch</p>
        </div>
      </div>
      <div class="flex items-center gap-3 text-xs">
        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Engine Ready (Zero Dependencies)
        </span>
        <a href="https://github.com/himadrimotwani/otter-action-guard" target="_blank" class="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition">
          <i class="fa-brands fa-github mr-1"></i> GitHub
        </a>
      </div>
    </div>
  </header>

  <!-- Main Grid -->
  <main class="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
    
    <!-- Left Column: Input & Controls (5 cols) -->
    <div class="lg:col-span-5 space-y-6">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div class="flex items-center justify-between mb-3">
          <label class="text-sm font-semibold text-slate-200">Select Meeting Scenario</label>
          <span class="text-xs text-slate-400">Presets</span>
        </div>
        <div class="grid grid-cols-2 gap-2 mb-4">
          <button onclick="loadSample(0)" class="text-left p-2.5 rounded-xl bg-slate-800 hover:bg-blue-600/20 hover:border-blue-500/50 border border-slate-700/60 transition text-xs">
            <div class="font-medium text-slate-200">👟 Nike Sourcing Sync</div>
            <div class="text-[11px] text-slate-400 truncate">Supply chain & supplier negotiation</div>
          </button>
          <button onclick="loadSample(1)" class="text-left p-2.5 rounded-xl bg-slate-800 hover:bg-blue-600/20 hover:border-blue-500/50 border border-slate-700/60 transition text-xs">
            <div class="font-medium text-slate-200">🚀 Tech Arch Review</div>
            <div class="text-[11px] text-slate-400 truncate">MCP connectors & Redis infra</div>
          </button>
        </div>

        <div class="mb-3">
          <div class="flex justify-between items-center mb-1.5">
            <label class="text-xs font-semibold text-slate-300">Transcript Input (with ASR speech artifacts)</label>
            <span class="text-[11px] text-slate-400" id="turnCountLabel">8 turns</span>
          </div>
          <textarea id="transcriptInput" rows="10" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono focus:outline-none focus:border-blue-500 leading-relaxed resize-y"></textarea>
        </div>

        <button onclick="runAnalysis()" id="analyzeBtn" class="w-full py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm transition shadow-lg shadow-blue-600/30 flex items-center justify-center gap-2">
          <i class="fa-solid fa-wand-magic-sparkles"></i> Run AI Agent Disambiguation
        </button>
      </div>

      <!-- Quick Metrics Summary -->
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
    </div>

    <!-- Right Column: Results & MCP Payloads (7 cols) -->
    <div class="lg:col-span-7 space-y-6">
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

  <script>
    const SAMPLES = [
      {
        title: "Nike Global Sourcing Sync",
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
        title: "Otter AI Agent Architecture Sync",
        transcript: `[00:10] Alex (Tech Lead): Let's review the em see pee server connector rollouts for Jira and Salesforce.
[00:30] Priya (Backend SWE): I will deploy the rate-limiter updates to staging by Friday.
[00:55] Alex (Tech Lead): Could we potentially bypass the cache on retry requests?
[01:20] Jordan (Infra): Only if Redis memory utilization stays below 75% under benchmark load.
[01:45] Priya (Backend SWE): Somebody needs to update the staging environment secrets before we run the load test.`
      }
    ];

    function loadSample(idx) {
      document.getElementById('transcriptInput').value = SAMPLES[idx].transcript;
      updateTurnCount();
    }

    function updateTurnCount() {
      const lines = document.getElementById('transcriptInput').value.trim().split('\\n').filter(l => l.trim().length > 0);
      document.getElementById('turnCountLabel').innerText = lines.length + ' turns';
    }

    document.getElementById('transcriptInput').addEventListener('input', updateTurnCount);
    loadSample(0);

    async function runAnalysis() {
      const text = document.getElementById('transcriptInput').value;
      const btn = document.getElementById('analyzeBtn');
      btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Reasoning & Disambiguating...';
      btn.disabled = true;

      try {
        const resp = await fetch('/api/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ transcript: text })
        });
        const data = await resp.json();
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

      document.getElementById('metricReady').innerText = data.ready_count;
      document.getElementById('metricBlocked').innerText = data.blocked_count;
      document.getElementById('metricClarify').innerText = data.clarification_count;
      document.getElementById('metricSpeech').innerText = data.speech_corrections_made;
      document.getElementById('executionBadge').innerText = `${data.actions.length} Actions Evaluated`;

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
            <div class="text-slate-400 text-[11px]">
              Assigned: <strong class="text-slate-200">${act.assigned_to || 'None (Unowned)'}</strong>
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
                result = guard.process_transcript(raw_text)
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
