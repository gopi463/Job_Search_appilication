import streamlit as st
import pandas as pd
import numpy as np
from jobspy import scrape_jobs
from utils import (
    clean_and_normalize_jobs,
    generate_site_distribution_chart,
    generate_top_companies_chart,
    generate_job_type_chart,
    generate_salary_distribution_chart
)
import io

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobSpy Intelligence Center",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Outfit:wght@600;700;800&display=swap');

/* Apply modern base styles */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    color: #F1F5F9;
}

/* Deep Space Premium Dark Background */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1E1B4B 0%, #0B0F19 60%, #05070F 100%);
    background-attachment: fixed;
}

/* Premium Glassmorphic Header Container */
.header-container {
    background: linear-gradient(135deg, rgba(30, 27, 75, 0.45) 0%, rgba(49, 16, 66, 0.45) 50%, rgba(15, 23, 42, 0.45) 100%);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    padding: 2.2rem 2.5rem;
    border-radius: 20px;
    border: 1px solid rgba(139, 92, 246, 0.25);
    margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.05);
    position: relative;
    overflow: hidden;
}

.header-container::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(167, 139, 250, 0.08) 0%, transparent 60%);
    pointer-events: none;
}

.header-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    color: #F8FAFC;
    margin: 0;
    letter-spacing: -0.03em;
    background: linear-gradient(to right, #FFFFFF 30%, #C084FC 80%, #6366F1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.header-subtitle {
    color: #C084FC;
    font-size: 1.1rem;
    margin-top: 0.5rem;
    margin-bottom: 0;
    font-weight: 400;
    opacity: 0.9;
    letter-spacing: 0.02em;
}

/* Premium Glassmorphic Metric Cards */
.metric-card {
    background: rgba(30, 41, 59, 0.35);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    padding: 1.5rem 1.2rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.05);
}

.metric-card:hover {
    transform: translateY(-5px);
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 12px 30px rgba(99, 102, 241, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.1);
}

.metric-title {
    color: #94A3B8;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0;
}

.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    margin-top: 0.5rem;
    margin-bottom: 0;
    line-height: 1.1;
    font-family: 'Outfit', sans-serif;
}

/* Detail Card Styling */
.detail-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    padding: 1.6rem;
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.detail-header {
    font-size: 1.4rem;
    font-weight: 800;
    color: #F8FAFC;
    margin-bottom: 0.3rem;
    line-height: 1.3;
    font-family: 'Outfit', sans-serif;
}

.detail-meta {
    font-size: 0.95rem;
    color: #94A3B8;
    margin-bottom: 1rem;
}

/* Badges with neon hues */
.badge {
    display: inline-block;
    padding: 0.35em 0.8em;
    font-size: 0.75rem;
    font-weight: 700;
    border-radius: 8px;
    margin-right: 0.5rem;
    margin-bottom: 0.4rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    letter-spacing: 0.01em;
}
.badge-site   { background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%); color: #F1F5F9; border: 1px solid rgba(59, 130, 246, 0.3); }
.badge-type   { background: linear-gradient(135deg, #047857 0%, #065F46 100%); color: #F1F5F9; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-remote { background: linear-gradient(135deg, #6D28D9 0%, #5B21B6 100%); color: #F1F5F9; border: 1px solid rgba(139, 92, 246, 0.3); }
.badge-salary { background: linear-gradient(135deg, #B45309 0%, #92400E 100%); color: #F1F5F9; border: 1px solid rgba(245, 158, 11, 0.3); }

/* Description Scrollbox */
.detail-body {
    font-size: 0.95rem;
    color: #E2E8F0;
    line-height: 1.7;
    background: rgba(15, 23, 42, 0.6);
    padding: 1.2rem;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    max-height: 440px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}

/* Custom Scrollbar for detail body */
.detail-body::-webkit-scrollbar {
    width: 6px;
}
.detail-body::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
}
.detail-body::-webkit-scrollbar-thumb {
    background: rgba(139, 92, 246, 0.4);
    border-radius: 3px;
}
.detail-body::-webkit-scrollbar-thumb:hover {
    background: rgba(139, 92, 246, 0.6);
}

/* Divider styling */
hr { border-color: rgba(255, 255, 255, 0.08); }

/* Sidebar Premium styling */
section[data-testid="stSidebar"] {
    background: #090D1A;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Premium tab selection styles */
button[data-baseweb="tab"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #94A3B8 !important;
    transition: all 0.2s ease !important;
}
button[data-baseweb="tab"]:hover {
    color: #C084FC !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #F8FAFC !important;
    border-bottom-color: #8B5CF6 !important;
}

/* Streamlit Native Expander styling override */
.streamlit-expanderHeader {
    background-color: rgba(30, 41, 59, 0.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🔍 JobSpy Intelligence Center</h1>
    <p class="header-subtitle">Aggregate, analyze, and explore job postings from LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google Jobs &amp; more in real time.</p>
</div>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
for key, default in [
    ('raw_jobs',        None),
    ('cleaned_jobs',    None),
    ('selected_job_idx', None),
    ('scrape_status',   ''),
    ('scrape_details',  None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

def has_data():
    d = st.session_state['cleaned_jobs']
    return d is not None and isinstance(d, pd.DataFrame) and not d.empty

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("### ⚙️ Search Configuration")

search_term = st.sidebar.text_input(
    "Job Title / Keywords", value="Software Engineer",
    placeholder="e.g. Python Developer"
)
location = st.sidebar.text_input(
    "Location", value="Remote",
    placeholder="e.g. San Francisco, CA or Remote"
)

SITE_MAP = {
    "LinkedIn":     "linkedin",
    "Indeed":       "indeed",
    "Glassdoor":    "glassdoor",
    "ZipRecruiter": "zip_recruiter",
    "Google Jobs":  "google",
    "Naukri":       "naukri",
    "Bayt":         "bayt",
    "BdJobs":       "bdjobs",
}
selected_sites = st.sidebar.multiselect(
    "Job Boards / Domains to Scrape",
    options=list(SITE_MAP.keys()),
    default=["LinkedIn", "Indeed"],
    help="LinkedIn and Indeed are highly responsive. Glassdoor, ZipRecruiter, and Google Jobs may require proxies or specific queries."
)
jobspy_sites = [SITE_MAP[s] for s in selected_sites]

age_option = st.sidebar.selectbox(
    "Job Posting Age (Max)",
    options=["Anytime", "Last 24 Hours", "Last 3 Days", "Last Week", "Last Month"],
    index=0
)
AGE_MAP = {"Anytime": None, "Last 24 Hours": 24, "Last 3 Days": 72, "Last Week": 168, "Last Month": 720}
hours_old = AGE_MAP[age_option]

results_wanted = st.sidebar.slider("Results per Platform", min_value=5, max_value=100, value=15, step=5)

# ── Advanced Settings — all variables defined before expander closes ──────────
is_remote        = False
country_indeed   = "usa"
linkedin_fetch   = False
proxies_list     = None

with st.sidebar.expander("🛠️ Advanced Settings"):
    is_remote = st.checkbox("Remote Jobs Only", value=False)

    country_raw = st.selectbox(
        "Indeed Country",
        options=["USA", "UK", "Canada", "India", "Germany", "Australia", "France"],
        index=0
    )
    country_indeed = country_raw.lower()

    linkedin_fetch = st.checkbox(
        "Fetch Full LinkedIn Descriptions",
        value=False,
        help="Makes one extra request per job — much slower and risks rate-limits."
    )

    proxies_raw = st.text_area(
        "HTTP/S Proxies (one per line, optional)",
        placeholder="http://user:pass@host:port\nhttp://ip:port",
        help="Helps bypass IP-based rate-limits on LinkedIn/Indeed."
    )
    if proxies_raw.strip():
        proxies_list = [p.strip() for p in proxies_raw.splitlines() if p.strip()]

st.sidebar.markdown("---")
scrape_clicked = st.sidebar.button("🚀 Start Scraping", type="primary", use_container_width=True)

# ── Scraper Execution ─────────────────────────────────────────────────────────
if scrape_clicked:
    if not jobspy_sites:
        st.sidebar.error("❌ Select at least one job board.")
    else:
        st.session_state['scrape_status'] = ''
        st.session_state['scrape_details'] = {}
        status_box = st.empty()
        
        all_dfs = []
        scrape_details = {}
        
        progress_text = st.empty()
        
        for idx, site in enumerate(jobspy_sites):
            site_display = [k for k, v in SITE_MAP.items() if v == site][0]
            progress_text.info(f"⏳ [{idx+1}/{len(jobspy_sites)}] Scraping **{site_display}** for '{search_term}'…")
            
            try:
                # Build specific args for each site
                site_args = {
                    "site_name":       [site],
                    "search_term":     search_term,
                    "results_wanted":  results_wanted,
                    "country_indeed":  country_indeed,
                    "is_remote":       is_remote,
                }
                if location.strip():
                    site_args["location"] = location.strip()
                if hours_old is not None:
                    site_args["hours_old"] = hours_old
                if site == "linkedin":
                    site_args["linkedin_fetch_description"] = linkedin_fetch
                if proxies_list:
                    site_args["proxies"] = proxies_list

                import time
                start_time = time.time()
                site_df = scrape_jobs(**site_args)
                duration = time.time() - start_time

                if site_df is not None and not site_df.empty:
                    all_dfs.append(site_df)
                    scrape_details[site_display] = {
                        "status": "success",
                        "count": len(site_df),
                        "message": f"Retrieved {len(site_df)} jobs in {duration:.1f}s."
                    }
                else:
                    scrape_details[site_display] = {
                        "status": "warning",
                        "count": 0,
                        "message": "No listings found. The query might be too narrow, or anti-bot challenge was active."
                    }
            except Exception as exc:
                err_str = str(exc)
                if "403" in err_str or "forbidden" in err_str.lower():
                    msg = "Blocked (403 Forbidden). Cloudflare protected - proxy required."
                elif "429" in err_str or "too many requests" in err_str.lower():
                    msg = "Rate limited (429 Too Many Requests). Try spacing out searches."
                elif "406" in err_str or "not acceptable" in err_str.lower():
                    msg = "Challenge active (406 Verification/reCAPTCHA required)."
                else:
                    msg = f"Failed: {err_str}"
                
                scrape_details[site_display] = {
                    "status": "error",
                    "count": 0,
                    "message": msg
                }
            
            # Short sleep to prevent heavy spikes
            time.sleep(1.2)
            
        progress_text.empty()
        st.session_state['scrape_details'] = scrape_details

        if all_dfs:
            raw_df = pd.concat(all_dfs, ignore_index=True)
            st.session_state['raw_jobs']         = raw_df
            st.session_state['cleaned_jobs']     = clean_and_normalize_jobs(raw_df)
            st.session_state['selected_job_idx'] = st.session_state['cleaned_jobs'].index[0]
            
            success_list = [s for s, d in scrape_details.items() if d["status"] == "success"]
            st.session_state['scrape_status']    = f"✅ Found **{len(raw_df)}** job listings from: {', '.join(success_list)}!"
        else:
            st.session_state['raw_jobs']         = None
            st.session_state['cleaned_jobs']     = None
            st.session_state['selected_job_idx'] = None
            st.session_state['scrape_status']    = "⚠️ No results found. All selected job boards returned empty or failed."

        if st.session_state['scrape_status']:
            msg = st.session_state['scrape_status']
            if msg.startswith("✅"):
                status_box.success(msg)
            elif msg.startswith("⚠️"):
                status_box.warning(msg)
            else:
                status_box.error(msg)
                st.info("💡 Tip: Reduce results, deselect LinkedIn/Indeed, or add proxies.")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_search, tab_analytics, tab_guide = st.tabs([
    "🔍 Job Board & Search",
    "📊 Insights & Dashboard",
    "📖 User Guide & Tips",
])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — JOB BOARD & SEARCH
# ════════════════════════════════════════════════════════════════════════════════
with tab_search:
    # ── Scrape Status Details Dashboard ───────────────────────────────────────
    if st.session_state.get('scrape_details'):
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        cols = st.columns(len(st.session_state['scrape_details']))
        for col, (site, details) in zip(cols, st.session_state['scrape_details'].items()):
            status = details["status"]
            count = details["count"]
            msg = details["message"]
            
            if status == "success":
                border_color = "#10B981"  # Emerald
                bg_gradient = "linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.3) 100%)"
                status_badge = "🟢 Success"
                badge_color = "#34D399"
            elif status == "warning":
                border_color = "#F59E0B"  # Amber
                bg_gradient = "linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(120, 53, 4, 0.3) 100%)"
                status_badge = "🟡 Empty"
                badge_color = "#FBBF24"
            else:  # error
                border_color = "#EF4444"  # Rose
                bg_gradient = "linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.3) 100%)"
                status_badge = "🔴 Blocked / Error"
                badge_color = "#F87171"
            
            with col:
                st.markdown(f"""
                <div style="
                    background: {bg_gradient};
                    border: 1px solid {border_color};
                    border-radius: 12px;
                    padding: 1rem;
                    height: 100%;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                ">
                    <div style="font-weight: 700; font-size: 1.1rem; color: #F1F5F9; margin-bottom: 0.25rem;">{site}</div>
                    <div style="display: inline-block; font-size: 0.75rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 4px; background: rgba(0,0,0,0.25); color: {badge_color}; margin-bottom: 0.5rem;">{status_badge}</div>
                    <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.3;">{msg}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if not has_data():
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem; background:#1E293B;
                    border-radius:16px; border:1px dashed #475569; margin-top:1rem;">
            <h2 style="color:#94A3B8; font-weight:500;">No Search Results Yet</h2>
            <p style="color:#64748B; font-size:1.05rem; max-width:480px; margin:.5rem auto 0 auto;">
                Configure your search in the sidebar and click <b>🚀 Start Scraping</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df = st.session_state['cleaned_jobs']

        # ── Metric cards ──────────────────────────────────────────────────────
        total_jobs       = len(df)
        # Safely count remote jobs (column may be object/bool/NaN)
        remote_jobs      = df['is_remote'].apply(lambda v: bool(v) if pd.notna(v) else False).sum()
        unique_companies = df['company'].nunique()

        salary_df        = df[df['annual_avg'].notna()]
        median_salary    = f"${salary_df['annual_avg'].median():,.0f}" if not salary_df.empty else "N/A"

        mc1, mc2, mc3, mc4 = st.columns(4)
        for col, title, val, color in [
            (mc1, "Total Postings",    total_jobs,       "#38BDF8"),
            (mc2, "Remote Listings",   remote_jobs,      "#C084FC"),
            (mc3, "Unique Companies",  unique_companies, "#34D399"),
            (mc4, "Median Salary",     median_salary,    "#FBBF24"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <p class="metric-title">{title}</p>
                    <p class="metric-value" style="color:{color};">{val}</p>
                </div>
                """, unsafe_allow_html=True)

        st.write("---")

        # ── Filter row + Export ───────────────────────────────────────────────
        fc, ec = st.columns([3, 1])
        with fc:
            text_filter = st.text_input(
                "🔎 Filter results (title · company · location · description)", "",
                key="internal_filter"
            )
        with ec:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            csv_buf = io.StringIO()
            df.to_csv(csv_buf, index=False)
            xl_buf = io.BytesIO()
            with pd.ExcelWriter(xl_buf, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Jobs')
            ex1, ex2 = st.columns(2)
            slug = search_term.replace(' ', '_').lower()
            with ex1:
                st.download_button("📄 CSV",   csv_buf.getvalue(), f"jobs_{slug}.csv",
                                   "text/csv", use_container_width=True)
            with ex2:
                st.download_button("📊 Excel", xl_buf.getvalue(),  f"jobs_{slug}.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)

        # ── Apply text filter (NaN-safe) ──────────────────────────────────────
        filtered_df = df.copy()
        if text_filter.strip():
            q = text_filter.strip().lower()
            def safe_contains(series, q):
                return series.fillna('').astype(str).str.lower().str.contains(q, na=False)
            mask = (
                safe_contains(filtered_df['title'],          q) |
                safe_contains(filtered_df['company'],        q) |
                safe_contains(filtered_df['clean_location'], q) |
                safe_contains(filtered_df['description'],    q)
            )
            filtered_df = filtered_df[mask]

        # ── Split view: listings table ← → detail panel ───────────────────────
        left_col, right_col = st.columns([3, 2])

        with left_col:
            st.markdown("#### 📋 Job Listings")

            if filtered_df.empty:
                st.info("No listings matched your filter.")
            else:
                indices = filtered_df.index.tolist()

                # Build display labels
                def make_label(idx):
                    r = filtered_df.loc[idx]
                    return f"{r['title']}  |  {r['company']}  ({r['site_formatted']})"

                labels = [make_label(i) for i in indices]

                # Resolve current selection safely
                cur = st.session_state['selected_job_idx']
                if cur in indices:
                    default_idx = indices.index(cur)
                else:
                    default_idx = 0

                chosen_label = st.selectbox(
                    "Select a listing to view full details →",
                    options=labels,
                    index=default_idx,
                    key="job_selector"
                )
                chosen_idx = indices[labels.index(chosen_label)]
                st.session_state['selected_job_idx'] = chosen_idx

                # Visible table columns
                disp = filtered_df[[
                    'site_formatted', 'title', 'company',
                    'clean_location', 'clean_job_type', 'salary_display'
                ]].copy()
                disp.columns = ['Board', 'Title', 'Company', 'Location', 'Type', 'Salary']
                st.dataframe(disp, use_container_width=True, height=440)

        # ── Detail Panel ──────────────────────────────────────────────────────
        with right_col:
            st.markdown("#### 🗂️ Posting Details")
            sel = st.session_state['selected_job_idx']

            if sel is not None and sel in df.index:
                job = df.loc[sel]

                # Header card
                is_rem = bool(job['is_remote']) if pd.notna(job['is_remote']) else False
                remote_badge = "<span class='badge badge-remote'>🏠 Remote</span>" if is_rem else ""
                salary_val = str(job['salary_display']) if pd.notna(job.get('salary_display')) else 'N/A'

                st.markdown(f"""
                <div class="detail-card">
                    <div class="detail-header">{job['title']}</div>
                    <div class="detail-meta">
                        🏢 <b>{job['company']}</b> &nbsp;·&nbsp; 📍 {job['clean_location']}
                    </div>
                    <div>
                        <span class="badge badge-site">{job['site_formatted']}</span>
                        <span class="badge badge-type">{job['clean_job_type']}</span>
                        {remote_badge}
                        <span class="badge badge-salary">💰 {salary_val}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # "View original" button
                job_url = str(job['job_url']) if pd.notna(job.get('job_url')) else ''
                if job_url and job_url.startswith('http'):
                    st.link_button(
                        f"🌐 Open on {job['site_formatted']}",
                        url=job_url,
                        use_container_width=True,
                        type="primary"
                    )

                # ── Description display ───────────────────────────────────────
                st.markdown("**📄 Job Description:**")
                raw_desc = job.get('description', '')

                # Safely convert to string and check for real content
                if raw_desc is None or (isinstance(raw_desc, float) and np.isnan(raw_desc)):
                    desc = ''
                else:
                    desc = str(raw_desc).strip()

                if desc and desc.lower() not in ('none', 'nan', 'n/a', ''):
                    # Render as markdown (jobspy often returns markdown-formatted text)
                    with st.container():
                        st.markdown(
                            f'<div class="detail-body">{desc}</div>',
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown("""
                    <div class="detail-body" style="color:#64748B; font-style:italic;
                                text-align:center; padding:2rem 0;">
                        No description available for this listing.<br><br>
                        <b>Tips to get descriptions:</b><br>
                        • Enable <i>Fetch Full LinkedIn Descriptions</i> for LinkedIn jobs<br>
                        • Indeed &amp; ZipRecruiter usually include descriptions automatically<br>
                        • Click "Open on [Board]" to view the full posting online
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Select a job from the dropdown above to see full details here.")

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — INSIGHTS & ANALYTICS
# ════════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    if not has_data():
        st.markdown("""
        <div style="text-align:center; padding:4rem 2rem; background:#1E293B;
                    border-radius:16px; border:1px dashed #475569; margin-top:1rem;">
            <h2 style="color:#94A3B8; font-weight:500;">No Data to Visualize</h2>
            <p style="color:#64748B; font-size:1.05rem; max-width:480px; margin:.5rem auto 0 auto;">
                Analytics charts will appear here after a successful scrape.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        adf = st.session_state['cleaned_jobs']
        st.markdown("### 📊 Market Intelligence Dashboard")

        r1c1, r1c2 = st.columns(2)
        r2c1, r2c2 = st.columns(2)

        with r1c1:
            st.plotly_chart(generate_site_distribution_chart(adf),  use_container_width=True)
        with r1c2:
            st.plotly_chart(generate_top_companies_chart(adf, 10),   use_container_width=True)
        with r2c1:
            st.plotly_chart(generate_job_type_chart(adf),            use_container_width=True)
        with r2c2:
            sal_fig = generate_salary_distribution_chart(adf)
            if sal_fig:
                st.plotly_chart(sal_fig, use_container_width=True)
            else:
                st.markdown("""
                <div style="border:1px solid #334155; border-radius:12px; height:350px;
                            display:flex; flex-direction:column; justify-content:center;
                            align-items:center; background:#1E293B; padding:2rem;">
                    <h4 style="color:#94A3B8; margin:0; text-align:center;">No Salary Data</h4>
                    <p style="color:#64748B; font-size:.88rem; text-align:center;
                              max-width:300px; margin-top:.5rem;">
                        Most listings don't publish salary ranges. Try Indeed or ZipRecruiter
                        which tend to include more compensation details.
                    </p>
                </div>
                """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — USER GUIDE
# ════════════════════════════════════════════════════════════════════════════════
with tab_guide:
    st.markdown("""
    ### 📖 User Guide & Scraping Tips

    #### ⚙️ Input Reference

    | Field | Description |
    |---|---|
    | **Job Title / Keywords** | Role or tech stack (e.g. `Data Engineer`, `React Developer`) |
    | **Location** | City, state, country, or `Remote` |
    | **Job Boards** | Platforms to search — select multiple for broad coverage |
    | **Job Posting Age** | Only return jobs posted within the selected window |
    | **Results per Platform** | How many listings to request *from each* selected board |
    | **Remote Jobs Only** | Filters to remote-flagged postings only |
    | **Fetch Full LinkedIn Descriptions** | Slower but retrieves full description text |

    #### 🗂️ About Job Descriptions
    - **Indeed / ZipRecruiter / Google Jobs** usually return descriptions automatically.
    - **LinkedIn** only returns a snippet by default — enable *Fetch Full LinkedIn Descriptions* to get full text (slower).
    - **Glassdoor** may return partial descriptions depending on scraper access.
    - If no description appears, click **"Open on [Board]"** to read the full posting directly.

    #### 🛡️ Dealing with Rate Limits (Empty Results / 403 Errors)

    - **Lower your results count** — start with 10–15 results per platform.
    - **Avoid LinkedIn / Indeed initially** — try Google Jobs or ZipRecruiter first.
    - **Use proxies** — add HTTP/S proxies in Advanced Settings to rotate IPs.
    - **Space out your searches** — wait a few minutes between scrapes.
    - **Try different locations** — some boards block requests that look too broad.

    #### 📤 Exporting Results
    Use the **CSV** and **Excel** download buttons in the Job Board tab to export all scraped listings.
    """)

