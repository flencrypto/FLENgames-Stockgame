"""
FLENgames Stock Prediction Game — Streamlit Edition
Palantir-inspired dark UI
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timedelta, timezone
from typing import Any

import requests
import streamlit as st

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="FLEN Stock Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# PALANTIR-INSPIRED CSS
# ──────────────────────────────────────────────────────────────

PALANTIR_CSS = """
<style>
  /* ── Global reset & fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&family=Inter:wght@300;400;600;700&display=swap');

  html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0a0a !important;
    color: #e0e0e0 !important;
    font-family: 'Inter', sans-serif !important;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background-color: #0f0f0f !important;
    border-right: 1px solid #1e1e1e !important;
  }
  [data-testid="stSidebar"] * { color: #c8c8c8 !important; }
  [data-testid="stSidebar"] .stRadio label { font-size: 0.85rem !important; letter-spacing: 0.08em; }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Top bar title ── */
  .pln-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 0 8px 0;
    border-bottom: 1px solid #1e1e1e;
    margin-bottom: 28px;
  }
  .pln-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.35rem;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: 0.06em;
  }
  .pln-logo span { color: #00d4aa; }
  .pln-tagline {
    font-size: 0.72rem;
    color: #555;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-left: auto;
  }

  /* ── Metric cards ── */
  .pln-metric-row { display: flex; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }
  .pln-metric {
    flex: 1;
    min-width: 140px;
    background: #111;
    border: 1px solid #1e1e1e;
    padding: 18px 20px;
    position: relative;
  }
  .pln-metric::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: #00d4aa;
  }
  .pln-metric-label {
    font-size: 0.68rem;
    color: #555;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 8px;
    font-family: 'JetBrains Mono', monospace;
  }
  .pln-metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #fff;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
  }
  .pln-metric-value.positive { color: #00d4aa; }
  .pln-metric-value.negative { color: #ff4d4d; }

  /* ── Section headers ── */
  .pln-section {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #555;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    border-bottom: 1px solid #1a1a1a;
    padding-bottom: 8px;
    margin-bottom: 18px;
  }

  /* ── Data table ── */
  .pln-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
  .pln-table th {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #555;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    text-align: left;
    padding: 8px 12px;
    border-bottom: 1px solid #1a1a1a;
    font-weight: 400;
  }
  .pln-table td {
    padding: 10px 12px;
    border-bottom: 1px solid #141414;
    color: #c8c8c8;
    vertical-align: middle;
  }
  .pln-table tr:hover td { background: #141414; }
  .pln-table .badge-up {
    background: rgba(0,212,170,0.12);
    color: #00d4aa;
    border: 1px solid rgba(0,212,170,0.3);
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
  }
  .pln-table .badge-down {
    background: rgba(255,77,77,0.12);
    color: #ff6b6b;
    border: 1px solid rgba(255,77,77,0.3);
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
  }
  .pln-table .badge-win {
    background: rgba(0,212,170,0.12);
    color: #00d4aa;
    border: 1px solid rgba(0,212,170,0.3);
    padding: 2px 8px;
    font-size: 0.72rem;
  }
  .pln-table .badge-loss {
    background: rgba(255,77,77,0.12);
    color: #ff6b6b;
    border: 1px solid rgba(255,77,77,0.3);
    padding: 2px 8px;
    font-size: 0.72rem;
  }
  .pln-table .badge-pending {
    background: rgba(255,200,0,0.1);
    color: #ffd700;
    border: 1px solid rgba(255,200,0,0.25);
    padding: 2px 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
  }
  .pln-table .mono { font-family: 'JetBrains Mono', monospace; }

  /* ── Streamlit widget overrides ── */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div {
    background-color: #111 !important;
    border: 1px solid #2a2a2a !important;
    color: #e0e0e0 !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
  }
  .stTextInput > div > div > input:focus,
  .stNumberInput > div > div > input:focus {
    border-color: #00d4aa !important;
    box-shadow: 0 0 0 1px #00d4aa !important;
  }
  label[data-testid="stWidgetLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #555 !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: transparent !important;
    border: 1px solid #00d4aa !important;
    color: #00d4aa !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 8px 20px !important;
    transition: all 0.15s;
  }
  .stButton > button:hover {
    background: #00d4aa !important;
    color: #0a0a0a !important;
  }
  .stButton > button:active { transform: scale(0.97); }

  /* ── Alert boxes ── */
  .pln-alert {
    border-left: 3px solid #00d4aa;
    background: rgba(0,212,170,0.06);
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #c8c8c8;
    margin-bottom: 16px;
  }
  .pln-alert-error {
    border-left: 3px solid #ff4d4d;
    background: rgba(255,77,77,0.06);
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #c8c8c8;
    margin-bottom: 16px;
  }
  .pln-alert-warn {
    border-left: 3px solid #ffd700;
    background: rgba(255,215,0,0.06);
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #c8c8c8;
    margin-bottom: 16px;
  }

  /* ── Rank table ── */
  .rank-1 .pln-rank-num { color: #ffd700; }
  .rank-2 .pln-rank-num { color: #c0c0c0; }
  .rank-3 .pln-rank-num { color: #cd7f32; }
  .pln-rank-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    font-weight: 700;
    color: #555;
    min-width: 24px;
    display: inline-block;
  }

  /* ── Radio button overrides ── */
  .stRadio > div { flex-direction: row !important; gap: 12px; }
  .stRadio > div label {
    background: #111 !important;
    border: 1px solid #2a2a2a !important;
    padding: 6px 16px !important;
    cursor: pointer;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #888 !important;
    letter-spacing: 0.1em;
  }
  .stRadio > div label:has(input:checked) {
    border-color: #00d4aa !important;
    color: #00d4aa !important;
    background: rgba(0,212,170,0.08) !important;
  }

  /* ── Scrollbars ── */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: #0a0a0a; }
  ::-webkit-scrollbar-thumb { background: #2a2a2a; }

  /* ── Divider ── */
  hr { border-color: #1a1a1a !important; }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    background: #111 !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #888 !important;
    letter-spacing: 0.1em;
  }
  .streamlit-expanderContent {
    background: #0f0f0f !important;
    border: 1px solid #1e1e1e !important;
    border-top: none !important;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1e1e1e !important;
    gap: 0 !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: #555 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 10px 20px !important;
    border-radius: 0 !important;
  }
  .stTabs [aria-selected="true"] {
    color: #00d4aa !important;
    border-bottom: 2px solid #00d4aa !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab-panel"] { padding: 24px 0 0 0 !important; }
</style>
"""

st.markdown(PALANTIR_CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────

# The demo key is the same one documented publicly in README.md.
# For production use, set ALPHAVANTAGE_API_KEY in your environment or
# add it under [alphavantage] in your Streamlit secrets file:
#   [alphavantage]
#   api_key = "YOUR_KEY_HERE"
_DEMO_API_KEY = "8HE88K05447IY34U"
AV_BASE = "https://www.alphavantage.co/query"
API_TIMEOUT_SECONDS = 8


def _default_api_key() -> str:
    """Return API key from Streamlit secrets, env var, or the public demo key."""
    try:
        return st.secrets["alphavantage"]["api_key"]
    except (KeyError, AttributeError, FileNotFoundError):
        pass
    return os.environ.get("ALPHAVANTAGE_API_KEY", _DEMO_API_KEY)

# ──────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────


def _init_state() -> None:
    defaults: dict[str, Any] = {
        "username": "Player1",
        "api_key": _default_api_key(),
        "predictions": [],
        "league": {},
        "next_id": 1,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()

# ──────────────────────────────────────────────────────────────
# DATE HELPERS
# ──────────────────────────────────────────────────────────────


def _next_market_day(ref: date | None = None) -> date:
    ref = ref or date.today()
    result = ref + timedelta(days=1)
    while result.weekday() >= 5:
        result += timedelta(days=1)
    return result


def _next_friday(ref: date | None = None) -> date:
    ref = ref or date.today()
    days_ahead = 4 - ref.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return ref + timedelta(days=days_ahead)


def _fmt(d: date) -> str:
    return d.strftime("%a, %b %d %Y")


# ──────────────────────────────────────────────────────────────
# ALPHA VANTAGE HELPERS
# ──────────────────────────────────────────────────────────────


def _av_search(keyword: str, api_key: str) -> list[dict]:
    try:
        resp = requests.get(
            AV_BASE,
            params={"function": "SYMBOL_SEARCH", "keywords": keyword, "apikey": api_key},
            timeout=API_TIMEOUT_SECONDS,
        )
        data = resp.json()
        return data.get("bestMatches", [])
    except Exception:
        return []


def _av_quote(symbol: str, api_key: str) -> dict | None:
    try:
        resp = requests.get(
            AV_BASE,
            params={"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": api_key},
            timeout=API_TIMEOUT_SECONDS,
        )
        data = resp.json()
        return data.get("Global Quote") or None
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────
# SCORING
# ──────────────────────────────────────────────────────────────


def _calc_s1(predictions: list[dict]) -> int:
    total = 0
    for p in predictions:
        if p["status"] != "resolved":
            continue
        if p["open_price"] is None or p["close_price"] is None:
            continue
        actual = "up" if p["close_price"] > p["open_price"] else "down"
        total += 1 if p["prediction"] == actual else -1
    return total


def _calc_s2(predictions: list[dict]) -> float:
    total = 0.0
    for p in predictions:
        if p["status"] != "resolved":
            continue
        if p["open_price"] is None or p["close_price"] is None:
            continue
        if p["open_price"] == 0:
            continue
        change_pct = (p["close_price"] - p["open_price"]) / p["open_price"] * 100
        total += change_pct if p["prediction"] == "up" else -change_pct
    return total


def _outcome(p: dict) -> str | None:
    if p["status"] != "resolved":
        return None
    if p["open_price"] is None or p["close_price"] is None:
        return None
    actual = "up" if p["close_price"] > p["open_price"] else "down"
    return "win" if p["prediction"] == actual else "loss"


# ──────────────────────────────────────────────────────────────
# UI HELPERS
# ──────────────────────────────────────────────────────────────


def _badge(text: str, kind: str) -> str:
    return f'<span class="badge-{kind}">{text}</span>'


def _metric_card(label: str, value: str, css_class: str = "") -> str:
    return f"""
    <div class="pln-metric">
      <div class="pln-metric-label">{label}</div>
      <div class="pln-metric-value {css_class}">{value}</div>
    </div>
    """


def _section(title: str) -> None:
    st.markdown(f'<div class="pln-section">{title}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────


def _render_header() -> None:
    st.markdown(
        """
        <div class="pln-header">
          <div class="pln-logo">FLEN<span>GAMES</span> · STOCK PREDICTION</div>
          <div class="pln-tagline">Real-time intelligence platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.65rem;'
            'color:#555;letter-spacing:0.18em;text-transform:uppercase;'
            'margin-bottom:20px;padding-bottom:8px;border-bottom:1px solid #1a1a1a;">'
            "SYSTEM CONFIG</div>",
            unsafe_allow_html=True,
        )

        username = st.text_input("Username", value=st.session_state["username"], key="sb_user")
        if username:
            st.session_state["username"] = username

        api_key = st.text_input(
            "Alpha Vantage API Key",
            value=st.session_state["api_key"],
            type="password",
            key="sb_key",
        )
        if api_key:
            st.session_state["api_key"] = api_key

        st.markdown("<hr>", unsafe_allow_html=True)

        # Export / Import
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.65rem;'
            'color:#555;letter-spacing:0.18em;text-transform:uppercase;'
            'margin-bottom:12px;">DATA EXPORT / IMPORT</div>',
            unsafe_allow_html=True,
        )

        export_data = {
            "predictions": st.session_state["predictions"],
            "pointsS1": _calc_s1(st.session_state["predictions"]),
            "pointsS2": round(_calc_s2(st.session_state["predictions"]), 4),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }
        st.download_button(
            "Export My Data",
            data=json.dumps(export_data, indent=2),
            file_name=f"{st.session_state['username']}_predictions.json",
            mime="application/json",
        )

        uploaded = st.file_uploader("Import Data (JSON)", type=["json"], key="import_file")
        if uploaded:
            try:
                imported = json.load(uploaded)
                preds = imported.get("predictions", [])
                # Basic validation
                valid = [
                    p
                    for p in preds
                    if isinstance(p, dict)
                    and "symbol" in p
                    and "prediction" in p
                    and "period" in p
                ]
                st.session_state["predictions"] = valid
                st.session_state["next_id"] = max((p.get("id", 0) for p in valid), default=0) + 1
                st.markdown(
                    f'<div class="pln-alert">✓ Imported {len(valid)} predictions.</div>',
                    unsafe_allow_html=True,
                )
            except Exception as exc:
                st.markdown(
                    f'<div class="pln-alert-error">✗ Import failed: {exc}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<hr>", unsafe_allow_html=True)
        s1 = _calc_s1(st.session_state["predictions"])
        s2 = _calc_s2(st.session_state["predictions"])
        total = len(st.session_state["predictions"])
        resolved = sum(1 for p in st.session_state["predictions"] if p["status"] == "resolved")

        st.markdown(
            f"""
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.72rem;
            color:#555;letter-spacing:0.1em;">
              <div style="margin-bottom:8px;">
                <span style="color:#888;">USER&nbsp;&nbsp;&nbsp;</span>
                <span style="color:#e0e0e0;">{st.session_state['username']}</span>
              </div>
              <div style="margin-bottom:8px;">
                <span style="color:#888;">S1 PTS&nbsp;</span>
                <span style="color:{'#00d4aa' if s1 >= 0 else '#ff4d4d'};">{s1:+d}</span>
              </div>
              <div style="margin-bottom:8px;">
                <span style="color:#888;">S2 PTS&nbsp;</span>
                <span style="color:{'#00d4aa' if s2 >= 0 else '#ff4d4d'};">{s2:+.2f}%</span>
              </div>
              <div>
                <span style="color:#888;">PREDS&nbsp;&nbsp;</span>
                <span style="color:#e0e0e0;">{resolved}/{total}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────
# TAB: PREDICT
# ──────────────────────────────────────────────────────────────


def _tab_predict() -> None:
    _section("NEW PREDICTION")

    col_search, col_period = st.columns([2, 1])

    with col_search:
        symbol_input = st.text_input(
            "Stock Symbol or Keyword",
            placeholder="e.g. AAPL, Tesla, MSFT",
            key="pred_symbol",
        )

    with col_period:
        period = st.radio("Period", ["Day", "Week"], key="pred_period", horizontal=True)

    # Live stock quote
    quote_data: dict | None = None
    if symbol_input and len(symbol_input) >= 1:
        clean_symbol = symbol_input.strip().upper()

        # Symbol search suggestions
        if len(clean_symbol) >= 2 and not re.match(r"^[A-Z]{1,5}$", clean_symbol):
            with st.spinner("Searching symbols..."):
                matches = _av_search(clean_symbol, st.session_state["api_key"])
            if matches:
                options = [
                    f"{m.get('1. symbol', '')} — {m.get('2. name', '')}" for m in matches[:6]
                ]
                selected = st.selectbox("Select Symbol", options, key="pred_match")
                if selected:
                    clean_symbol = selected.split(" — ")[0]

        # Fetch live quote
        with st.spinner(f"Fetching quote for {clean_symbol}…"):
            quote_data = _av_quote(clean_symbol, st.session_state["api_key"])

        if quote_data and quote_data.get("05. price"):
            price = float(quote_data.get("05. price", 0))
            change = float(quote_data.get("09. change", 0))
            change_pct = quote_data.get("10. change percent", "0%").replace("%", "")
            try:
                change_pct_f = float(change_pct)
            except ValueError:
                change_pct_f = 0.0
            pos = change >= 0
            st.markdown(
                f"""
                <div class="pln-metric-row">
                  {_metric_card("SYMBOL", quote_data.get("01. symbol", clean_symbol))}
                  {_metric_card("PRICE", f"${price:,.2f}", "positive" if pos else "negative")}
                  {_metric_card("CHANGE", f"{change:+.2f}", "positive" if pos else "negative")}
                  {_metric_card("CHANGE %", f"{change_pct_f:+.2f}%", "positive" if pos else "negative")}
                  {_metric_card("VOLUME", quote_data.get("06. volume", "—"))}
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif symbol_input:
            st.markdown(
                '<div class="pln-alert-warn">⚠ No live data available — check symbol or API key.</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    _section("DIRECTION FORECAST")

    direction_col, launch_col = st.columns([1, 1])
    with direction_col:
        direction = st.radio(
            "Predicted Direction",
            ["UP ▲", "DOWN ▼"],
            key="pred_direction",
            horizontal=True,
        )

    with launch_col:
        st.markdown("<br>", unsafe_allow_html=True)
        launch = st.button("⟩ LAUNCH PREDICTION", key="pred_launch")

    if launch:
        sym = (symbol_input or "").strip().upper()
        if not sym:
            st.markdown(
                '<div class="pln-alert-error">✗ Enter a stock symbol.</div>',
                unsafe_allow_html=True,
            )
        else:
            dir_val = "up" if direction.startswith("UP") else "down"
            period_val = "day" if period == "Day" else "week"
            target = _next_market_day() if period_val == "day" else _next_friday()

            pred: dict[str, Any] = {
                "id": st.session_state["next_id"],
                "symbol": sym,
                "prediction": dir_val,
                "period": period_val,
                "made_at": datetime.now(timezone.utc).isoformat(),
                "target_date": target.isoformat(),
                "open_price": None,
                "close_price": None,
                "status": "pending",
                "user": st.session_state["username"],
            }
            st.session_state["predictions"].insert(0, pred)
            st.session_state["next_id"] += 1
            dir_icon = "▲" if dir_val == "up" else "▼"
            st.markdown(
                f'<div class="pln-alert">✓ Prediction launched: <strong>{sym}</strong> '
                f'{dir_icon} by {_fmt(target)}</div>',
                unsafe_allow_html=True,
            )

    # ── Pending predictions ──
    pending = [p for p in st.session_state["predictions"] if p["status"] == "pending"]
    if not pending:
        return

    st.markdown("<br>", unsafe_allow_html=True)
    _section(f"PENDING PREDICTIONS ({len(pending)})")

    for idx, pred in enumerate(pending):
        with st.expander(
            f"{pred['symbol']}  ·  {pred['prediction'].upper()}  ·  {pred['period'].upper()}  ·  Target {pred['target_date']}"
        ):
            r1, r2, r3 = st.columns(3)
            with r1:
                open_p = st.number_input(
                    "Open Price",
                    min_value=0.0,
                    step=0.01,
                    format="%.4f",
                    key=f"open_{pred['id']}",
                )
            with r2:
                close_p = st.number_input(
                    "Close Price",
                    min_value=0.0,
                    step=0.01,
                    format="%.4f",
                    key=f"close_{pred['id']}",
                )
            with r3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("RESOLVE", key=f"resolve_{pred['id']}"):
                    if open_p > 0 and close_p > 0:
                        # Find and update in session state
                        for sp in st.session_state["predictions"]:
                            if sp["id"] == pred["id"]:
                                sp["open_price"] = open_p
                                sp["close_price"] = close_p
                                sp["status"] = "resolved"
                                break
                        st.rerun()
                    else:
                        st.warning("Enter valid open and close prices.")

            if st.button("✕ Delete", key=f"del_{pred['id']}"):
                st.session_state["predictions"] = [
                    p for p in st.session_state["predictions"] if p["id"] != pred["id"]
                ]
                st.rerun()


# ──────────────────────────────────────────────────────────────
# TAB: HISTORY
# ──────────────────────────────────────────────────────────────


def _tab_history() -> None:
    resolved = [p for p in st.session_state["predictions"] if p["status"] == "resolved"]
    pending = [p for p in st.session_state["predictions"] if p["status"] == "pending"]

    s1 = _calc_s1(st.session_state["predictions"])
    s2 = _calc_s2(st.session_state["predictions"])
    wins = sum(1 for p in resolved if _outcome(p) == "win")
    losses = len(resolved) - wins

    s1_cls = "positive" if s1 >= 0 else "negative"
    s2_cls = "positive" if s2 >= 0 else "negative"

    _section("PERFORMANCE SUMMARY")
    st.markdown(
        f"""
        <div class="pln-metric-row">
          {_metric_card("SYSTEM 1", f"{s1:+d} pts", s1_cls)}
          {_metric_card("SYSTEM 2", f"{s2:+.2f}%", s2_cls)}
          {_metric_card("WINS", str(wins), "positive")}
          {_metric_card("LOSSES", str(losses), "negative" if losses else "")}
          {_metric_card("PENDING", str(len(pending)))}
          {_metric_card("WIN RATE", f"{(wins/len(resolved)*100):.0f}%" if resolved else "N/A")}
        </div>
        """,
        unsafe_allow_html=True,
    )

    _section("PREDICTION HISTORY")
    all_preds = st.session_state["predictions"]
    if not all_preds:
        st.markdown(
            '<div class="pln-alert-warn">No predictions yet. Go to Predict to get started.</div>',
            unsafe_allow_html=True,
        )
        return

    rows_html = ""
    for p in all_preds:
        outcome = _outcome(p)
        dir_badge = _badge(p["prediction"].upper(), p["prediction"])
        if outcome == "win":
            out_badge = _badge("WIN", "win")
        elif outcome == "loss":
            out_badge = _badge("LOSS", "loss")
        else:
            out_badge = _badge("PENDING", "pending")

        open_str = f"${p['open_price']:,.4f}" if p["open_price"] is not None else "—"
        close_str = f"${p['close_price']:,.4f}" if p["close_price"] is not None else "—"
        made_at = p.get("made_at", "")[:10]
        target = p.get("target_date", "")

        rows_html += f"""
        <tr>
          <td class="mono">{p['symbol']}</td>
          <td>{dir_badge}</td>
          <td class="mono">{p['period'].upper()}</td>
          <td class="mono">{made_at}</td>
          <td class="mono">{target}</td>
          <td class="mono">{open_str}</td>
          <td class="mono">{close_str}</td>
          <td>{out_badge}</td>
        </tr>
        """

    st.markdown(
        f"""
        <table class="pln-table">
          <thead>
            <tr>
              <th>Symbol</th><th>Direction</th><th>Period</th>
              <th>Made At</th><th>Target</th>
              <th>Open</th><th>Close</th><th>Outcome</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑 Clear All History"):
        st.session_state["predictions"] = []
        st.rerun()


# ──────────────────────────────────────────────────────────────
# TAB: LEAGUE
# ──────────────────────────────────────────────────────────────


def _tab_league() -> None:
    _section("LEAGUE MANAGEMENT")

    # Add current user's data to league
    current_user = st.session_state["username"]
    if current_user:
        st.session_state["league"][current_user] = {
            "predictions": st.session_state["predictions"],
            "pointsS1": _calc_s1(st.session_state["predictions"]),
            "pointsS2": round(_calc_s2(st.session_state["predictions"]), 4),
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        }

    # Import competitor data
    with st.expander("IMPORT COMPETITOR DATA"):
        st.markdown(
            '<div class="pln-alert" style="margin-top:8px;">Paste or upload a competitor\'s '
            "exported JSON to add them to your league.</div>",
            unsafe_allow_html=True,
        )
        comp_json = st.text_area(
            "Paste JSON",
            height=120,
            placeholder='{"predictions": [...], "pointsS1": 5, "pointsS2": 12.3, "updatedAt": "..."}',
            key="league_json",
        )
        comp_name = st.text_input("Competitor Username", key="league_name")
        if st.button("ADD TO LEAGUE", key="league_add"):
            if not comp_name:
                st.markdown(
                    '<div class="pln-alert-error">✗ Enter a username.</div>',
                    unsafe_allow_html=True,
                )
            else:
                try:
                    data = json.loads(comp_json)
                    preds = data.get("predictions", [])
                    s1 = (
                        _calc_s1(preds) if preds else data.get("pointsS1", 0)
                    )
                    s2 = (
                        _calc_s2(preds) if preds else data.get("pointsS2", 0.0)
                    )
                    st.session_state["league"][comp_name] = {
                        "predictions": preds,
                        "pointsS1": s1,
                        "pointsS2": round(s2, 4),
                        "updatedAt": data.get("updatedAt", datetime.now(timezone.utc).isoformat()),
                    }
                    st.markdown(
                        f'<div class="pln-alert">✓ Added {comp_name} to league.</div>',
                        unsafe_allow_html=True,
                    )
                except Exception as exc:
                    st.markdown(
                        f'<div class="pln-alert-error">✗ Parse error: {exc}</div>',
                        unsafe_allow_html=True,
                    )

    st.markdown("<br>", unsafe_allow_html=True)

    league = st.session_state["league"]
    if not league:
        st.markdown(
            '<div class="pln-alert-warn">No league data yet. Your data will appear here '
            "after making predictions.</div>",
            unsafe_allow_html=True,
        )
        return

    # Sort by S1 then S2
    sorted_entries = sorted(
        league.items(),
        key=lambda kv: (-kv[1]["pointsS1"], -kv[1]["pointsS2"]),
    )

    _section("LEADERBOARD — SYSTEM 1 (BINARY)")
    rows_html = ""
    for rank, (uname, entry) in enumerate(sorted_entries, 1):
        s1 = entry["pointsS1"]
        s2 = entry["pointsS2"]
        pred_count = len(entry.get("predictions", []))
        resolved_count = sum(
            1 for p in entry.get("predictions", []) if p.get("status") == "resolved"
        )
        is_you = uname == current_user
        rank_class = f"rank-{rank}" if rank <= 3 else ""
        s1_color = "#00d4aa" if s1 >= 0 else "#ff4d4d"
        s2_color = "#00d4aa" if s2 >= 0 else "#ff4d4d"
        you_badge = (
            ' <span style="color:#ffd700;font-size:0.65rem;letter-spacing:0.1em;">YOU</span>'
            if is_you
            else ""
        )
        rows_html += f"""
        <tr class="{rank_class}">
          <td><span class="pln-rank-num">#{rank}</span></td>
          <td class="mono" style="color:#e0e0e0;">{uname}{you_badge}</td>
          <td class="mono" style="color:{s1_color};font-weight:700;">{s1:+d}</td>
          <td class="mono" style="color:{s2_color};">{s2:+.2f}%</td>
          <td class="mono" style="color:#555;">{resolved_count}/{pred_count}</td>
        </tr>
        """

    st.markdown(
        f"""
        <table class="pln-table">
          <thead>
            <tr>
              <th>Rank</th><th>User</th>
              <th>System 1 (pts)</th><th>System 2 (%)</th>
              <th>Resolved / Total</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    # Remove a competitor
    st.markdown("<br>", unsafe_allow_html=True)
    others = [u for u in league if u != current_user]
    if others:
        with st.expander("REMOVE A COMPETITOR"):
            to_remove = st.selectbox("Select user to remove", others, key="league_remove_sel")
            if st.button("REMOVE", key="league_remove_btn"):
                del st.session_state["league"][to_remove]
                st.rerun()


# ──────────────────────────────────────────────────────────────
# TAB: MARKET DATA
# ──────────────────────────────────────────────────────────────


def _tab_market() -> None:
    _section("LIVE MARKET LOOKUP")

    sym = st.text_input(
        "Stock Symbol",
        placeholder="e.g. AAPL",
        key="market_sym",
    ).strip().upper()

    if sym and st.button("FETCH QUOTE", key="market_fetch"):
        with st.spinner(f"Fetching {sym}…"):
            q = _av_quote(sym, st.session_state["api_key"])
        if q and q.get("05. price"):
            price = float(q.get("05. price", 0))
            change = float(q.get("09. change", 0))
            change_pct_raw = q.get("10. change percent", "0%").replace("%", "")
            try:
                change_pct = float(change_pct_raw)
            except ValueError:
                change_pct = 0.0
            pos = change >= 0
            high = float(q.get("03. high", 0))
            low = float(q.get("04. low", 0))
            prev_close = float(q.get("08. previous close", 0))

            st.markdown(
                f"""
                <div class="pln-metric-row">
                  {_metric_card("SYMBOL", q.get("01. symbol", sym))}
                  {_metric_card("PRICE", f"${price:,.2f}", "positive" if pos else "negative")}
                  {_metric_card("CHANGE", f"{change:+.2f}", "positive" if pos else "negative")}
                  {_metric_card("CHANGE %", f"{change_pct:+.2f}%", "positive" if pos else "negative")}
                  {_metric_card("HIGH", f"${high:,.2f}")}
                  {_metric_card("LOW", f"${low:,.2f}")}
                  {_metric_card("PREV CLOSE", f"${prev_close:,.2f}")}
                  {_metric_card("VOLUME", q.get("06. volume", "—"))}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="pln-alert-warn">⚠ No data returned. Check symbol or API key.</div>',
                unsafe_allow_html=True,
            )

    _section("SYMBOL SEARCH")
    kw = st.text_input("Search keyword", placeholder="e.g. Tesla, Apple, Microsoft", key="mkt_kw")
    if kw and st.button("SEARCH", key="mkt_search"):
        with st.spinner("Searching…"):
            matches = _av_search(kw, st.session_state["api_key"])
        if matches:
            rows_html = ""
            for m in matches:
                rows_html += f"""
                <tr>
                  <td class="mono">{m.get("1. symbol", "")}</td>
                  <td>{m.get("2. name", "")}</td>
                  <td class="mono">{m.get("3. type", "")}</td>
                  <td class="mono">{m.get("4. region", "")}</td>
                  <td class="mono">{m.get("8. currency", "")}</td>
                  <td class="mono">{float(m.get("9. matchScore", 0)):.2f}</td>
                </tr>
                """
            st.markdown(
                f"""
                <table class="pln-table">
                  <thead>
                    <tr>
                      <th>Symbol</th><th>Name</th><th>Type</th>
                      <th>Region</th><th>Currency</th><th>Score</th>
                    </tr>
                  </thead>
                  <tbody>{rows_html}</tbody>
                </table>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="pln-alert-warn">No results found.</div>',
                unsafe_allow_html=True,
            )


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────


def main() -> None:
    _render_header()
    _render_sidebar()

    tab_predict, tab_history, tab_league, tab_market = st.tabs(
        ["PREDICT", "HISTORY", "LEAGUE", "MARKET DATA"]
    )

    with tab_predict:
        _tab_predict()

    with tab_history:
        _tab_history()

    with tab_league:
        _tab_league()

    with tab_market:
        _tab_market()


if __name__ == "__main__":
    main()
