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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark background override */
.stApp {
    background: #0A0F1E;
}

/* Header */
.header-container {
    background: linear-gradient(135deg, #1E1B4B 0%, #311042 55%, #0F172A 100%);
    padding: 2.5rem 2.8rem;
    border-radius: 18px;
    border: 1px solid rgba(139, 92, 246, 0.3);
    margin-bottom: 1.5rem;
    box-shadow: 0 0 40px rgba(139, 92, 246, 0.15);
}
.header-title {
    font-family: 'Outfit', 'Inter', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    color: #F8FAFC;
    margin: 0;
    letter-spacing: -0.02em;
}
.header-subtitle {
    color: #C084FC;
    font-size: 1.05rem;
    margin-top: 0.4rem;
    margin-bottom: 0;
    font-weight: 400;
    opacity: 0.88;
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(145deg, #1E293B, #162032);
    padding: 1.25rem 1rem;
    border-radius: 14px;
    border: 1px solid #334155;
    text-align: center;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    border-color: #6366F1;
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.2);
}
.metric-title {
    color: #94A3B8;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    margin-top: 0.4rem;
    margin-bottom: 0;
    line-height: 1.1;
}

/* Detail Card */
.detail-card {
    background: #1E293B;
    padding: 1.4rem;
    border-radius: 14px;
    border: 1px solid #334155;
    margin-bottom: 0.8rem;
}
.detail-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: #F1F5F9;
    margin-bottom: 0.2rem;
    line-height: 1.3;
}
.detail-meta {
    font-size: 0.88rem;
    color: #94A3B8;
    margin-bottom: 0.8rem;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 0.28em 0.65em;
    font-size: 0.72rem;
    font-weight: 700;
    border-radius: 6px;
    margin-right: 0.4rem;
    margin-bottom: 0.3rem;
}
.badge-site   { background-color: #2563EB; color: white; }
.badge-type   { background-color: #059669; color: white; }
.badge-remote { background-color: #7C3AED; color: white; }
.badge-salary { background-color: #D97706; color: white; }

/* Description box */
.detail-body {
    font-size: 0.9rem;
    color: #CBD5E1;
    line-height: 1.65;
    background: #0F172A;
    padding: 1rem 1.1rem;
    border-radius: 10px;
    border: 1px solid #1E293B;
    max-height: 420px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}

/* Divider */
hr { border-color: #1E293B; }

/* Sidebar tweaks */
section[data-testid="stSidebar"] {
    background: #0D1526;
    border-right: 1px solid #1E293B;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🔍 JobSpy Intelligence Center</h1>
    <p class="header-subtitle">Aggregate, analyze, and explore job postings from LinkedIn, Indeed, Glassdoor, ZipRecruiter &amp; Google Jobs in real time.</p>
</div>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
for key, default in [
    ('raw_jobs',        None),
    ('cleaned_jobs',    None),
    ('selected_job_idx', None),
    ('scrape_status',   ''),
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
}
selected_sites = st.sidebar.multiselect(
    "Job Boards / Domains to Scrape",
    options=list(SITE_MAP.keys()),
    default=["Indeed", "ZipRecruiter", "Google Jobs"],
    help="LinkedIn and Indeed may block without proxies. Google Jobs is most reliable."
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
        status_box = st.empty()

        with st.spinner(f"⏳ Scraping **{search_term}** in **{location}** across {', '.join(selected_sites)}…"):
            try:
                scrape_args = {
                    "site_name":       jobspy_sites,
                    "search_term":     search_term,
                    "results_wanted":  results_wanted,
                    "country_indeed":  country_indeed,
                    "is_remote":       is_remote,
                }
                if location.strip():
                    scrape_args["location"] = location.strip()
                if hours_old is not None:
                    scrape_args["hours_old"] = hours_old
                if "linkedin" in jobspy_sites:
                    scrape_args["linkedin_fetch_description"] = linkedin_fetch
                if proxies_list:
                    scrape_args["proxies"] = proxies_list

                raw_df = scrape_jobs(**scrape_args)

                if raw_df is not None and not raw_df.empty:
                    st.session_state['raw_jobs']         = raw_df
                    st.session_state['cleaned_jobs']     = clean_and_normalize_jobs(raw_df)
                    st.session_state['selected_job_idx'] = st.session_state['cleaned_jobs'].index[0]
                    st.session_state['scrape_status']    = f"✅ Found **{len(raw_df)}** job listings!"
                else:
                    st.session_state['raw_jobs']         = None
                    st.session_state['cleaned_jobs']     = None
                    st.session_state['selected_job_idx'] = None
                    st.session_state['scrape_status']    = "⚠️ No results found. Try different keywords or locations."

            except Exception as exc:
                st.session_state['raw_jobs']         = None
                st.session_state['cleaned_jobs']     = None
                st.session_state['selected_job_idx'] = None
                st.session_state['scrape_status']    = f"❌ Error: {exc}"

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

