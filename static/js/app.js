/**
 * AI Agent Dashboard — Frontend Application
 * Handles pipeline execution via SSE, UI state, and rendering.
 */

// ── State ──
const state = {
    isRunning: false,
    activeTab: 'planning',
    stages: {
        planning:    { status: 'idle', output: '' },
        development: { status: 'idle', output: '' },
        testing:     { status: 'idle', output: '' },
        review:      { status: 'idle', output: '' },
    },
    history: [],
};

const STAGE_ORDER = ['planning', 'development', 'testing', 'review'];
const STAGE_META = {
    planning:    { icon: '📋', label: 'Planning',    title: 'Development Plan',   panelIcon: '📋' },
    development: { icon: '💻', label: 'Development', title: 'Generated Code',     panelIcon: '💻' },
    testing:     { icon: '🧪', label: 'Testing',     title: 'Test Report',        panelIcon: '🧪' },
    review:      { icon: '🔍', label: 'Review',      title: 'Final Reviewed Code', panelIcon: '🔍' },
};

// ── DOM refs ──
const els = {};

function initRefs() {
    els.ideaInput       = document.getElementById('idea-input');
    els.runBtn          = document.getElementById('run-btn');
    els.btnText         = document.getElementById('btn-text');
    els.btnIcon         = document.getElementById('btn-icon');
    els.progressBar     = document.getElementById('progress-bar');
    els.progressFill    = document.getElementById('progress-fill');
    els.progressText    = document.getElementById('progress-text');
    els.progressPercent = document.getElementById('progress-percent');
    els.historyGrid     = document.getElementById('history-grid');
    els.toastContainer  = document.getElementById('toast-container');
    els.statusDot       = document.getElementById('status-dot');
    els.statusText      = document.getElementById('status-text');
}

// ── Initialization ──
document.addEventListener('DOMContentLoaded', () => {
    initRefs();
    bindEvents();
    loadHistory();
    setActiveTab('planning');
});

function bindEvents() {
    els.runBtn.addEventListener('click', startPipeline);
    els.ideaInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            startPipeline();
        }
    });

    // Quick idea buttons
    document.querySelectorAll('.quick-idea').forEach(btn => {
        btn.addEventListener('click', () => {
            els.ideaInput.value = btn.textContent.trim();
            els.ideaInput.focus();
        });
    });

    // Output tabs
    document.querySelectorAll('.output-tab').forEach(tab => {
        tab.addEventListener('click', () => setActiveTab(tab.dataset.stage));
    });

    // Pipeline stage clicks
    document.querySelectorAll('.pipeline-stage').forEach(stage => {
        stage.addEventListener('click', () => setActiveTab(stage.dataset.stage));
    });
}

// ── Pipeline Execution ──
function startPipeline() {
    const idea = els.ideaInput.value.trim();
    if (!idea || state.isRunning) return;

    state.isRunning = true;
    resetStages();
    updateRunButton(true);
    showProgress(true);
    updateProgress(0, 'Initializing pipeline...');

    // Try to connect to the backend SSE endpoint. If it fails, fall back
    // to a client-side simulation so the dashboard remains usable.
    let evtSource;
    try {
        evtSource = new EventSource(`/api/run?idea=${encodeURIComponent(idea)}`);
    } catch (e) {
        // EventSource constructor may throw in some environments
        simulatePipeline(idea);
        return;
    }

    // If the server doesn't respond quickly, fallback to simulation.
    const connectionTimeout = setTimeout(() => {
        try { evtSource.close(); } catch (e) {}
        if (state.isRunning) simulatePipeline(idea);
    }, 1500);

    evtSource.onopen = () => {
        clearTimeout(connectionTimeout);
    };

    evtSource.onmessage = (event) => {
        clearTimeout(connectionTimeout);
        const data = JSON.parse(event.data);
        handleSSEEvent(data);
    };

    evtSource.onerror = () => {
        clearTimeout(connectionTimeout);
        try { evtSource.close(); } catch (e) {}
        if (state.isRunning) {
            // Fall back to simulation if backend is unreachable
            simulatePipeline(idea);
        }
    };
}

// ── Fallback simulator (runs when backend API isn't available) ──
function simulatePipeline(idea) {
    const chunks = {
        planning: [`Plan for: ${idea}\n- Define scope\n- Design API\n- Choose database\n`],
        development: [`# app.py\nfrom flask import Flask\n# ...\n\n# Generated code for: ${idea}\n`],
        testing: [`Test report:\nAll basic checks passed.`],
        review: [`Final reviewed code:\n// small improvements applied`],
    };

    const stages = ['planning', 'development', 'testing', 'review'];

    let i = 0;
    function nextStage() {
        if (i >= stages.length) {
            onPipelineComplete();
            return;
        }
        const stage = stages[i];
        onStageStart(stage, `Simulating ${stage}...`);

        // stream chunks
        let sent = '';
        const stageChunks = chunks[stage] || [`(no output)`];
        let j = 0;
        const t = setInterval(() => {
            const chunk = stageChunks[j++] || '';
            if (chunk) {
                onStageChunk(stage, chunk);
                sent += chunk;
            }
            if (j >= stageChunks.length) {
                clearInterval(t);
                setTimeout(() => {
                    onStageComplete(stage, sent || '(no output)');
                    i++;
                    setTimeout(nextStage, 600);
                }, 300);
            }
        }, 250);
    }

    nextStage();
}

function handleSSEEvent(data) {
    switch (data.type) {
        case 'stage_start':
            onStageStart(data.stage, data.message);
            break;
        case 'stage_complete':
            onStageComplete(data.stage, data.output);
            break;
        case 'stage_chunk':
            onStageChunk(data.stage, data.chunk);
            break;
        case 'stage_skip':
            onStageSkip(data.stage);
            break;
        case 'pipeline_complete':
            onPipelineComplete();
            break;
        case 'pipeline_error':
            onPipelineError(data.message);
            break;
    }
}

function onStageStart(stage, message) {
    state.stages[stage].status = 'running';
    updateStageUI(stage);
    setActiveTab(stage);
    setPanelLoading(stage, message);

    const idx = STAGE_ORDER.indexOf(stage);
    const pct = (idx / 4) * 100;
    updateProgress(pct, message);
}

function onStageChunk(stage, chunk) {
    state.stages[stage].output += chunk;
    renderPanelContent(stage, state.stages[stage].output);
}

function onStageComplete(stage, output) {
    state.stages[stage].status = 'complete';
    state.stages[stage].output = output;
    updateStageUI(stage);
    updateTabStatus(stage, 'complete');
    renderPanelContent(stage, output);

    const idx = STAGE_ORDER.indexOf(stage) + 1;
    const pct = (idx / 4) * 100;
    updateProgress(pct, `${STAGE_META[stage].label} complete`);

    showToast(`${STAGE_META[stage].label} stage complete ✓`, 'success');
}

function onStageSkip(stage) {
    state.stages[stage].status = 'skipped';
    updateStageUI(stage);
    updateTabStatus(stage, 'skipped');
}

function onPipelineComplete() {
    state.isRunning = false;
    updateRunButton(false);
    updateProgress(100, 'Pipeline complete!');
    showToast('🎉 Pipeline completed successfully!', 'success');
    loadHistory();

    setTimeout(() => showProgress(false), 3000);
}

function onPipelineError(message) {
    state.isRunning = false;
    updateRunButton(false);
    showToast(`Pipeline error: ${message}`, 'error');
    showProgress(false);
}

// ── UI Updates ──
function resetStages() {
    STAGE_ORDER.forEach(stage => {
        state.stages[stage] = { status: 'idle', output: '' };
        updateStageUI(stage);
        updateTabStatus(stage, 'idle');
        const body = document.getElementById(`panel-${stage}-body`);
        if (body) {
            body.innerHTML = `
                <div class="panel-body empty">
                    <div class="empty-icon">${STAGE_META[stage].icon}</div>
                    <div class="empty-text">Waiting for pipeline to reach this stage...</div>
                </div>`;
        }
    });
}

function updateRunButton(running) {
    state.isRunning = running;
    if (els.runBtn) els.runBtn.disabled = running;
    if (els.btnText) els.btnText.textContent = running ? 'Running...' : 'Build App';
    if (els.btnIcon) els.btnIcon.textContent = running ? '⏳' : '🚀';
}

function showProgress(visible) {
    if (els.progressBar) els.progressBar.style.display = visible ? 'block' : 'none';
}

function updateProgress(percent, text) {
    if (els.progressFill) els.progressFill.style.width = `${percent}%`;
    if (els.progressPercent) els.progressPercent.textContent = `${Math.round(percent)}%`;
    if (els.progressText) els.progressText.textContent = text;
}

function setActiveTab(stage) {
    state.activeTab = stage;
    document.querySelectorAll('.output-tab, .pipeline-stage').forEach(el => {
        el.classList.toggle('active', el.dataset.stage === stage);
    });
    document.querySelectorAll('.output-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === `panel-${stage}`);
    });
    renderPanelContent(stage, state.stages[stage].output);
}

function renderPanelContent(stage, content) {
    const body = document.getElementById(`panel-${stage}-body`);
    if (!body) return;
    body.innerHTML = `<div class="panel-body content"><pre>${escapeHtml(content || 'Waiting for output...')}</pre></div>`;
}

function setPanelLoading(stage, message) {
    const body = document.getElementById(`panel-${stage}-body`);
    if (!body) return;
    body.innerHTML = `
        <div class="panel-body loading">
            <div class="loader"></div>
            <div>${escapeHtml(message)}</div>
        </div>`;
}

function updateStageUI(stage) {
    const stageEl = document.querySelector(`.pipeline-stage[data-stage="${stage}"]`);
    if (!stageEl) return;
    const status = state.stages[stage].status;
    stageEl.classList.toggle('running', status === 'running');
    stageEl.classList.toggle('complete', status === 'complete');
    stageEl.classList.toggle('skipped', status === 'skipped');
    stageEl.dataset.status = status;
    const statusText = stageEl.querySelector('.stage-status-text');
    if (statusText) {
        const statusMap = {
            idle: 'Waiting',
            running: 'Running...',
            complete: 'Done',
            skipped: 'Skipped',
            error: 'Error',
        };
        statusText.textContent = statusMap[status] || '';
    }
}

function updateTabStatus(stage, status) {
    const tab = document.querySelector(`.output-tab[data-stage="${stage}"]`);
    if (!tab) return;
    tab.dataset.status = status;
    tab.classList.toggle('complete', status === 'complete');
    tab.classList.toggle('skipped', status === 'skipped');
}

function showToast(message, type = 'info') {
    if (!els.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${escapeHtml(message)}</span>`;
    els.toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function escapeHtml(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// ── History ──
async function loadHistory() {
    try {
        const res = await fetch('/api/history');
        const data = await res.json();
        state.history = data.runs || [];
        renderHistory();
    } catch {
        // Silently fail
    }
}

function renderHistory() {
    if (!els.historyGrid) return;

    if (state.history.length === 0) {
        els.historyGrid.innerHTML = `
            <div class="panel-body empty" style="grid-column: 1 / -1;">
                <div class="empty-icon">📭</div>
                <div class="empty-text">No pipeline runs yet. Enter an idea above to get started!</div>
            </div>`;
        return;
    }

    els.historyGrid.innerHTML = state.history.map(run => `
        <div class="history-card" onclick="loadHistoryRun('${run.id}')">
            <div class="history-idea">${escapeHtml(run.idea)}</div>
            <div class="history-meta">
                <span>${formatTime(run.started_at)}</span>
                <span class="history-badge ${run.status}">${run.status}</span>
            </div>
        </div>
    `).join('');
}

function loadHistoryRun(runId) {
    const run = state.history.find(r => r.id === runId);
    if (!run || !run.stages) return;

    resetStages();

    Object.entries(run.stages).forEach(([stage, output]) => {
        state.stages[stage] = { status: 'complete', output };
        updateStageUI(stage);
        updateTabStatus(stage, 'complete');
        renderPanelContent(stage, output);
    });

    const firstStage = Object.keys(run.stages)[0];
    if (firstStage) setActiveTab(firstStage);
}

// ── Copy to clipboard ──
function copyPanelContent(stage) {
    const content = state.stages[stage]?.output || '';
    if (!content) return;

    navigator.clipboard.writeText(content).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// ── Toast Notifications ──
function showToast(message, type = 'info') {
    if (!els.toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span><span>${escapeHtml(message)}</span>`;

    els.toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ── Utilities ──
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatTime(isoStr) {
    try {
        const d = new Date(isoStr);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
        return '';
    }
}

function renderMarkdown(text) {
    if (!text) return '';

    // Simple markdown-to-HTML (covers common patterns)
    let html = escapeHtml(text);

    // Code blocks (``` ... ```)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
        return `<pre><code class="language-${lang}">${code.trim()}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Bold & Italic
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Unordered lists
    html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

    // Numbered lists
    html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

    // Line breaks into paragraphs
    html = html.replace(/\n\n/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    html = `<p>${html}</p>`;

    // Clean up empty paragraphs
    html = html.replace(/<p>\s*<\/p>/g, '');
    html = html.replace(/<p>\s*(<h[1-3]>)/g, '$1');
    html = html.replace(/(<\/h[1-3]>)\s*<\/p>/g, '$1');
    html = html.replace(/<p>\s*(<pre>)/g, '$1');
    html = html.replace(/(<\/pre>)\s*<\/p>/g, '$1');
    html = html.replace(/<p>\s*(<ul>)/g, '$1');
    html = html.replace(/(<\/ul>)\s*<\/p>/g, '$1');

    return html;
}
