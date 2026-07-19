import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def clean_and_normalize_jobs(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and normalizes the raw DataFrame returned by python-jobspy.
    Standardizes column casing, locations, job types, and salary intervals.
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # 1. Normalize column names to lowercase
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    
    # Ensure critical columns exist with default values if missing
    critical_columns = {
        'site': 'unknown',
        'title': 'N/A',
        'company': 'N/A',
        'job_url': '',
        'job_type': 'N/A',
        'interval': 'N/A',
        'min_amount': np.nan,
        'max_amount': np.nan,
        'currency': 'USD',
        'is_remote': False,
        'description': '',
        'city': '',
        'state': '',
        'location': ''
    }
    
    for col, default in critical_columns.items():
        if col not in df.columns:
            df[col] = default

    # 2. Site/Domain name formatting
    site_map = {
        'linkedin': 'LinkedIn',
        'indeed': 'Indeed',
        'glassdoor': 'Glassdoor',
        'zip_recruiter': 'ZipRecruiter',
        'google': 'Google Jobs',
        'bayt': 'Bayt',
        'naukri': 'Naukri',
        'bdjobs': 'BdJobs'
    }
    df['site_formatted'] = df['site'].apply(lambda s: site_map.get(str(s).lower(), str(s).capitalize()))

    # 3. Location normalization
    def _clean_str(val):
        """Return clean string or empty string — never 'nan'."""
        if val is None:
            return ''
        s = str(val).strip()
        return '' if s.lower() in ('nan', 'none', 'n/a') else s

    def format_location(row):
        city  = _clean_str(row['city']  if 'city'  in row.index else '')
        state = _clean_str(row['state'] if 'state' in row.index else '')
        loc   = _clean_str(row['location'] if 'location' in row.index else '')

        if city and state:
            return f"{city}, {state}"
        elif city:
            return city
        elif state:
            return state
        elif loc:
            return loc

        try:
            is_rem = bool(row['is_remote']) if pd.notna(row['is_remote']) else False
        except Exception:
            is_rem = False
        if is_rem:
            return "Remote"
        return "Not Specified"

    df['clean_location'] = df.apply(format_location, axis=1)

    # 4. Job type normalization
    def format_job_type(jt):
        if pd.isna(jt):
            return "Not Specified"
        jt_str = str(jt).lower().replace('_', ' ').replace('-', ' ').strip()
        if 'full' in jt_str:
            return 'Full-time'
        elif 'part' in jt_str:
            return 'Part-time'
        elif 'contract' in jt_str:
            return 'Contract'
        elif 'intern' in jt_str:
            return 'Internship'
        elif 'temp' in jt_str:
            return 'Temporary'
        return jt_str.title()
        
    df['clean_job_type'] = df['job_type'].apply(format_job_type)

    # 5. Salary normalization to USD Annual Equivalent (assuming 40hr/wk, 52wk/yr)
    def normalize_to_annual(amount, interval):
        if pd.isna(amount) or pd.isna(interval):
            return np.nan
        
        amount = float(amount)
        interval_str = str(interval).lower()
        
        if 'year' in interval_str:
            return amount
        elif 'month' in interval_str:
            return amount * 12
        elif 'week' in interval_str:
            return amount * 52
        elif 'day' in interval_str:
            return amount * 260
        elif 'hour' in interval_str:
            return amount * 2080  # 40 hours * 52 weeks
        return amount

    # Apply annual conversion
    df['annual_min'] = df.apply(lambda r: normalize_to_annual(r['min_amount'], r['interval']), axis=1)
    df['annual_max'] = df.apply(lambda r: normalize_to_annual(r['max_amount'], r['interval']), axis=1)
    
    # Calculate average annual salary
    df['annual_avg'] = df[['annual_min', 'annual_max']].mean(axis=1)

    # Generate a user-friendly salary string
    def format_salary_text(row):
        min_val = row['min_amount']
        max_val = row['max_amount']
        currency = row['currency'] if pd.notna(row['currency']) else 'USD'
        interval = row['interval']
        
        if pd.isna(min_val) and pd.isna(max_val):
            return "N/A"
        
        curr_symbol = '$' if currency == 'USD' else f"{currency} "
        interval_text = f"/{interval}" if pd.notna(interval) else ""
        
        if pd.notna(min_val) and pd.notna(max_val):
            if min_val == max_val:
                return f"{curr_symbol}{min_val:,.0f}{interval_text}"
            return f"{curr_symbol}{min_val:,.0f} - {curr_symbol}{max_val:,.0f}{interval_text}"
        elif pd.notna(min_val):
            return f"From {curr_symbol}{min_val:,.0f}{interval_text}"
        else:
            return f"Up to {curr_symbol}{max_val:,.0f}{interval_text}"

    df['salary_display'] = df.apply(format_salary_text, axis=1)
    
    return df

# Plotly visualization helper functions
def generate_site_distribution_chart(df: pd.DataFrame):
    """Generates a donut chart for site distribution."""
    site_counts = df['site_formatted'].value_counts().reset_index()
    site_counts.columns = ['Site', 'Count']
    
    fig = px.pie(
        site_counts, 
        values='Count', 
        names='Site', 
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Pastel,
        title="Job Postings by Platform"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        margin=dict(t=40, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

def generate_top_companies_chart(df: pd.DataFrame, top_n: int = 10):
    """Generates a horizontal bar chart for top hiring companies."""
    company_counts = df['company'].value_counts().reset_index()
    company_counts.columns = ['Company', 'Count']
    company_counts = company_counts.head(top_n).sort_values(by='Count', ascending=True)
    
    fig = px.bar(
        company_counts,
        x='Count',
        y='Company',
        orientation='h',
        color='Count',
        color_continuous_scale='Viridis',
        title=f"Top {top_n} Hiring Companies"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        margin=dict(t=40, b=10, l=10, r=10),
        coloraxis_showscale=False
    )
    fig.update_yaxes(title_text="")
    fig.update_xaxes(title_text="Number of Postings")
    return fig

def generate_job_type_chart(df: pd.DataFrame):
    """Generates a bar chart showing employment type distribution."""
    type_counts = df['clean_job_type'].value_counts().reset_index()
    type_counts.columns = ['Job Type', 'Count']
    
    fig = px.bar(
        type_counts,
        x='Job Type',
        y='Count',
        color='Job Type',
        color_discrete_sequence=px.colors.qualitative.Safe,
        title="Job Postings by Employment Type"
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        margin=dict(t=40, b=10, l=10, r=10),
        showlegend=False
    )
    fig.update_xaxes(title_text="")
    fig.update_yaxes(title_text="Count")
    return fig

def generate_salary_distribution_chart(df: pd.DataFrame):
    """Generates a salary range plot for jobs that have salary information."""
    salary_df = df[df['annual_avg'].notna()].copy()
    if salary_df.empty:
        return None
        
    salary_df = salary_df.sort_values(by='annual_avg', ascending=False).head(15)
    
    # We create a Gantt-like or Range-like chart showing min/max bounds
    fig = go.Figure()
    
    # Add Min-Max ranges as error bars or lines
    fig.add_trace(go.Bar(
        y=salary_df['title'] + " (" + salary_df['company'] + ")",
        x=salary_df['annual_max'] - salary_df['annual_min'],
        base=salary_df['annual_min'],
        orientation='h',
        marker=dict(
            color='rgba(58, 71, 205, 0.6)',
            line=dict(color='rgba(58, 71, 205, 1.0)', width=1.5)
        ),
        name='Salary Range (Annualized USD)',
        hovertemplate='<b>%{y}</b><br>Max: $%{x+base:,.0f}<br>Min: $%{base:,.0f}'
    ))
    
    # Add average marker dots
    fig.add_trace(go.Scatter(
        y=salary_df['title'] + " (" + salary_df['company'] + ")",
        x=salary_df['annual_avg'],
        mode='markers',
        marker=dict(color='#FF5722', size=8),
        name='Average Salary',
        hovertemplate='<b>%{y}</b><br>Average: $%{x:,.0f}'
    ))
    
    fig.update_layout(
        title="Top 15 Jobs Salary Ranges (Annualized USD)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#E0E0E0',
        margin=dict(t=45, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        barmode='overlay'
    )
    fig.update_yaxes(title_text="", autorange="reversed")
    fig.update_xaxes(title_text="Annualized Salary (USD)", tickformat="$,.0f")
    return fig

def section_header(title: str, subtitle: str = ""):
    """Renders a styled section header with title and subtitle."""
    import streamlit as st
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h2 style="color: #F8FAFC; margin-bottom: 0.25rem; font-family: 'Outfit', sans-serif; font-weight: 700;">{title}</h2>
        {f'<p style="color: #94A3B8; margin-top: 0; font-size: 1.05rem; font-family: \'Plus Jakarta Sans\', sans-serif;">{subtitle}</p>' if subtitle else ''}
        <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin-top: 1rem; margin-bottom: 1.5rem;">
    </div>
    """, unsafe_allow_html=True)

