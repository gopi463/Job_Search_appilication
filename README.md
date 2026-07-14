# 🔍 JobSpy Intelligence Center

A premium **Streamlit** web application for scraping, filtering, analyzing, and exporting job postings from multiple platforms simultaneously using [`python-jobspy`](https://github.com/speedyapply/JobSpy).

---

## 🌟 Features

- **Multi-platform scraping** — LinkedIn, Indeed, Glassdoor, ZipRecruiter, Google Jobs
- **Domain / site selection** — choose which job boards to search
- **Job posting age filter** — Last 24h, 3 days, 1 week, 1 month, or Anytime
- **Interactive results table** — filter by keyword across title, company, location, and description
- **Full job description viewer** — inline detail panel with direct link to the original posting
- **Market intelligence dashboard** — 4 interactive Plotly charts:
  - Platform distribution (donut chart)
  - Top hiring companies (bar chart)
  - Employment type breakdown
  - Salary range comparison (annualized USD)
- **Export** — Download results as CSV or Excel
- **Proxy support** — add HTTP/S proxies to bypass rate limits
- **Premium dark-mode UI** — glassmorphism design with smooth hover animations

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/gopi463/Job_Search_appilication.git
cd Job_Search_appilication
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** `python-jobspy` pins `numpy==1.26.3` in its metadata but works fine with numpy 2.x. Install without deps if you hit compilation issues:
> ```bash
> pip install python-jobspy --no-deps
> pip install tls-client "markdownify>=0.13.1,<0.14.0"
> ```

### 3. Run the app
```bash
python -m streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 🖥️ Usage

1. Enter a **Job Title** (e.g. `Python Developer`) and **Location** (e.g. `Remote`)
2. Select the **job boards** you want to search
3. Set the **posting age** to filter recent listings
4. Optionally configure **Advanced Settings** (remote filter, country, proxies)
5. Click **🚀 Start Scraping**
6. Browse results, inspect descriptions, and download as CSV/Excel

---

## 🛡️ Rate Limit Tips

| Platform | Rate Limit Risk | Tips |
|---|---|---|
| LinkedIn | 🔴 High | Use proxies; enable fetch desc only when needed |
| Indeed | 🟡 Medium | Works best with small result counts (10–15) |
| ZipRecruiter | 🟢 Low | Most reliable, recommended for testing |
| Google Jobs | 🟢 Low | Aggregates many boards, great coverage |
| Glassdoor | 🟡 Medium | Shares Indeed backend, needs country set |

---

## 📁 Project Structure

```
Job_Search_appilication/
├── app.py            # Main Streamlit application
├── utils.py          # Data cleaning & Plotly chart generators
├── requirements.txt  # Python dependencies
└── README.md
```

---

## 📦 Requirements

- Python **3.10+**
- streamlit >= 1.30.0
- python-jobspy >= 1.1.40
- pandas >= 2.0.0
- plotly >= 5.18.0
- openpyxl >= 3.1.2

---

## 📄 License

MIT License — feel free to use and modify.
