_CSS = """
/* ── Full-height layout ──────────────────────────────────────── */
html, body {
    height: 100%;
    margin: 0;
}

.container-fluid {
    min-height: 100%;
    display: flex;
    flex-direction: column;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* ── Global page ─────────────────────────────────────────────── */
body {
    background-color: #FFFFFF;
    font-family: 'Segoe UI', system-ui, sans-serif;
    color: #1C1C2E;
}

/* ── Header bar ──────────────────────────────────────────────── */
.bpx-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 28px;
    background: linear-gradient(135deg, #DDD8F0 0%, #E8E3F8 60%, #EDE9F5 100%);
    border-bottom: 2px solid #A896D8;
    height: 120px; 
    color: #2D1F5E;
}

.bpx-header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.bpx-logo {
    height: 100px;
    width: auto;
    opacity: 0.85;
}

.bpx-title-block h1 {
    margin: 0;
    font-size: 2.2rem;
    font-weight: 700;
    color: #2D1F5E;
}

.bpx-title-block p {
    margin: 2px 0 0 0;
    font-size: 0.82rem;
    color: #6B5B9E;
    font-style: italic;
}

.bpx-lab-badge {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    opacity: 0.75;
}

.bpx-lab-badge span {
    font-size: 0.68rem;
    color: #5A4A8A;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Inputs ──────────────────────────────────────────────────── */
.selectize-input, input[type="text"] {
    border: 1px solid #D4C9B0 !important;
    border-radius: 5px !important;
    background: #FFFFFF !important;
}

.selectize-input.focus, input[type="text"]:focus {
    border-color: #4ECDC4 !important;
    box-shadow: 0 0 0 2px rgba(78,205,196,0.18) !important;
}

.selectize-dropdown .active {
    background-color: #1E3A5C !important;
    color: #fff !important;
}

/* ── App layout (sidebar + main) ─────────────────────────────── */
.app-layout {
    display: grid;
    grid-template-columns: 500px 1fr;
    flex: 1 1 auto;
    min-height: calc(100vh - 120px);
}

/* ── Sidebar panel ───────────────────────────────────────────── */
.sidebar-panel {
    background-color: #F5F0E8;
    border-right: 1px solid #E2D9C8;
    padding: 16px;
    overflow-y: auto;
}

.sidebar-panel h5 {
    color: #5C4A2A;
    font-weight: 700;
    font-size: 2rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 4px;
}

.sidebar-panel hr {
    border-color: #E2D9C8;
    margin: 10px 0;
}

.sidebar-panel .selectize-input,
.sidebar-panel input[type="text"] {
    font-size: 2rem;
    padding: 8px 10px !important;
}

.sidebar-panel .selectize-dropdown {
    font-size: 2rem;
}

.sidebar-panel select {
    font-size: 2rem !important;
}

.sidebar-panel .shiny-input-container {
    width: 100% !important;
}

/* ── Main panel ──────────────────────────────────────────────── */
.main-panel {
    padding: 16px;
    overflow-y: auto;
    width: 100%;
}

/* ── Card headers (Power curves / Heatmaps) ──────────────────── */
.card-header {
    font-size: 2rem !important; 
    font-weight: 600;
}

/* Radio button & selectize labels inside cards */
.card .radio label,
.card .selectize-input {
    font-size: 1.3rem;
}

/* ── Card images ─────────────────────────────────────────────── */
.shiny-image-output img {
    width: 100%;
    height: auto;
    max-height: 600px;
    object-fit: contain;
    display: block;
}

/* ── Main panel output ───────────────────────────────────────── */
.shiny-html-output {
    width: 100% !important;
}

/* ── Text output size ───────────────────────────────────────── */
.shiny-text-output {
    font-size: 1.4rem; !important;
}

pre {
    font-size: 2rem !important;
}
"""