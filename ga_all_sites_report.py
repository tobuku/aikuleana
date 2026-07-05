"""
GA4 All-Sites Report
Queries all accessible GA4 properties and generates an HTML dashboard.
Output: Desktop/ga-all-sites-report.html

Usage:
  python ga_all_sites_report.py              # 28-day default
  python ga_all_sites_report.py --days 14
  python ga_all_sites_report.py --days 90
"""

import argparse
import os
import sys
from datetime import datetime, timedelta

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest
)
from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
from google.oauth2 import service_account

# --- Config ---
KEY_FILE = os.path.join(os.path.dirname(__file__),
    ".gsc-credentials/laptoplane-blogspot-autoposter-c7da82883623.json")
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
OUTPUT = os.path.expanduser("~/Desktop/ga-all-sites-report.html")


def get_clients():
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    admin = AnalyticsAdminServiceClient(credentials=creds)
    data = BetaAnalyticsDataClient(credentials=creds)
    return admin, data


def discover_properties(admin):
    props = []
    for summary in admin.list_account_summaries():
        for prop in summary.property_summaries:
            pid = prop.property.split("/")[-1]
            props.append({"id": pid, "name": prop.display_name, "account": summary.display_name})
    return props


def run_summary(data, pid, start, end):
    """Get sessions, users, pageviews, bounce rate, avg session duration."""
    try:
        resp = data.run_report(RunReportRequest(
            property=f"properties/{pid}",
            date_ranges=[DateRange(start_date=start, end_date=end)],
            metrics=[
                Metric(name="sessions"),
                Metric(name="totalUsers"),
                Metric(name="screenPageViews"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="newUsers"),
            ],
        ))
        if resp.rows:
            r = resp.rows[0]
            return {
                "sessions": int(r.metric_values[0].value),
                "users": int(r.metric_values[1].value),
                "pageviews": int(r.metric_values[2].value),
                "bounce": float(r.metric_values[3].value),
                "avg_duration": float(r.metric_values[4].value),
                "new_users": int(r.metric_values[5].value),
            }
        return {"sessions": 0, "users": 0, "pageviews": 0, "bounce": 0, "avg_duration": 0, "new_users": 0}
    except Exception as e:
        return {"error": str(e)}


def run_top_pages(data, pid, start, end, limit=5):
    try:
        resp = data.run_report(RunReportRequest(
            property=f"properties/{pid}",
            date_ranges=[DateRange(start_date=start, end_date=end)],
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews"), Metric(name="totalUsers")],
            limit=limit,
        ))
        pages = []
        for row in resp.rows:
            pages.append({
                "path": row.dimension_values[0].value,
                "views": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
            })
        return pages
    except:
        return []


def run_sources(data, pid, start, end, limit=5):
    try:
        resp = data.run_report(RunReportRequest(
            property=f"properties/{pid}",
            date_ranges=[DateRange(start_date=start, end_date=end)],
            dimensions=[Dimension(name="sessionSource")],
            metrics=[Metric(name="sessions"), Metric(name="totalUsers")],
            limit=limit,
        ))
        sources = []
        for row in resp.rows:
            sources.append({
                "source": row.dimension_values[0].value,
                "sessions": int(row.metric_values[0].value),
                "users": int(row.metric_values[1].value),
            })
        return sources
    except:
        return []


def fmt_duration(secs):
    m, s = divmod(int(secs), 60)
    return f"{m}m {s}s"


def build_html(results, days):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_sessions = sum(r["summary"].get("sessions", 0) for r in results if "error" not in r.get("summary", {}))
    total_users = sum(r["summary"].get("users", 0) for r in results if "error" not in r.get("summary", {}))
    total_pageviews = sum(r["summary"].get("pageviews", 0) for r in results if "error" not in r.get("summary", {}))

    rows_html = ""
    detail_html = ""

    # Sort by sessions descending
    results.sort(key=lambda x: x.get("summary", {}).get("sessions", 0), reverse=True)

    for i, r in enumerate(results):
        s = r.get("summary", {})
        if "error" in s:
            rows_html += f'<tr class="err"><td>{r["name"]}</td><td colspan="5" class="error">{s["error"][:80]}</td></tr>\n'
            continue

        bounce_class = "good" if s["bounce"] < 0.5 else ("warn" if s["bounce"] < 0.7 else "bad")
        rows_html += f'''<tr>
  <td><a href="#detail-{i}">{r["name"]}</a></td>
  <td>{s["sessions"]:,}</td>
  <td>{s["users"]:,}</td>
  <td>{s["pageviews"]:,}</td>
  <td class="{bounce_class}">{s["bounce"]:.1%}</td>
  <td>{fmt_duration(s["avg_duration"])}</td>
</tr>
'''
        # Detail section
        pages_rows = ""
        for p in r.get("pages", []):
            pages_rows += f'<tr><td>{p["path"]}</td><td>{p["views"]:,}</td><td>{p["users"]:,}</td></tr>\n'

        sources_rows = ""
        for src in r.get("sources", []):
            sources_rows += f'<tr><td>{src["source"]}</td><td>{src["sessions"]:,}</td><td>{src["users"]:,}</td></tr>\n'

        detail_html += f'''
<div class="detail" id="detail-{i}">
  <h3>{r["name"]} <span class="account">({r["account"]})</span></h3>
  <div class="cols">
    <div>
      <h4>Top Pages</h4>
      <table class="sub"><tr><th>Path</th><th>Views</th><th>Users</th></tr>
      {pages_rows if pages_rows else '<tr><td colspan="3">No data</td></tr>'}
      </table>
    </div>
    <div>
      <h4>Traffic Sources</h4>
      <table class="sub"><tr><th>Source</th><th>Sessions</th><th>Users</th></tr>
      {sources_rows if sources_rows else '<tr><td colspan="3">No data</td></tr>'}
      </table>
    </div>
  </div>
</div>
'''

    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GA4 All Sites Report</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui,-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;padding:24px;line-height:1.5}}
h1{{font-size:1.8rem;margin-bottom:4px}}
.meta{{color:#94a3b8;margin-bottom:20px;font-size:.9rem}}
.totals{{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap}}
.totals .card{{background:#1e293b;border-radius:8px;padding:16px 24px;min-width:160px}}
.totals .card .num{{font-size:1.8rem;font-weight:700;color:#38bdf8}}
.totals .card .label{{font-size:.8rem;color:#94a3b8;text-transform:uppercase}}
table{{width:100%;border-collapse:collapse;margin-bottom:24px}}
th{{text-align:left;padding:10px 12px;background:#1e293b;color:#94a3b8;font-size:.8rem;text-transform:uppercase;letter-spacing:.5px}}
td{{padding:10px 12px;border-bottom:1px solid #1e293b}}
tr:hover{{background:#1e293b}}
a{{color:#38bdf8;text-decoration:none}}
a:hover{{text-decoration:underline}}
.good{{color:#4ade80}}.warn{{color:#fbbf24}}.bad{{color:#f87171}}
.error{{color:#f87171;font-size:.85rem}}
.detail{{background:#1e293b;border-radius:8px;padding:20px;margin-bottom:16px}}
.detail h3{{margin-bottom:12px;font-size:1.1rem}}
.detail .account{{color:#64748b;font-weight:normal;font-size:.9rem}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
@media(max-width:768px){{.cols{{grid-template-columns:1fr}}.totals{{flex-direction:column}}}}
.sub{{font-size:.9rem}}
.sub th{{background:#0f172a}}
h4{{margin-bottom:8px;color:#94a3b8;font-size:.85rem;text-transform:uppercase}}
</style></head><body>
<h1>GA4 All Sites Report</h1>
<p class="meta">Generated {today} / Last {days} days</p>
<div class="totals">
  <div class="card"><div class="num">{total_sessions:,}</div><div class="label">Total Sessions</div></div>
  <div class="card"><div class="num">{total_users:,}</div><div class="label">Total Users</div></div>
  <div class="card"><div class="num">{total_pageviews:,}</div><div class="label">Total Pageviews</div></div>
  <div class="card"><div class="num">{len(results)}</div><div class="label">Properties</div></div>
</div>
<table>
<tr><th>Property</th><th>Sessions</th><th>Users</th><th>Pageviews</th><th>Bounce Rate</th><th>Avg Duration</th></tr>
{rows_html}
</table>
<h2 style="margin-bottom:16px">Site Details</h2>
{detail_html}
</body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=28)
    args = parser.parse_args()

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    print(f"GA4 All-Sites Report / {args.days} days ({start_date} to {end_date})")
    print("=" * 60)

    admin, data = get_clients()
    print("Discovering properties...")
    props = discover_properties(admin)
    print(f"Found {len(props)} properties.\n")

    results = []
    for p in props:
        print(f"  {p['name']}...", end=" ", flush=True)
        summary = run_summary(data, p["id"], start_date, end_date)
        pages = run_top_pages(data, p["id"], start_date, end_date)
        sources = run_sources(data, p["id"], start_date, end_date)

        result = {"name": p["name"], "account": p["account"], "id": p["id"],
                  "summary": summary, "pages": pages, "sources": sources}
        results.append(result)

        if "error" in summary:
            print(f"ERROR")
        else:
            print(f"{summary['sessions']} sessions, {summary['users']} users")

    # Terminal summary
    print("\n" + "=" * 60)
    print(f"{'Property':<30} {'Sessions':>10} {'Users':>10} {'PV':>10}")
    print("-" * 60)
    for r in sorted(results, key=lambda x: x["summary"].get("sessions", 0), reverse=True):
        s = r["summary"]
        if "error" in s:
            print(f"{r['name']:<30} {'ERROR':>10}")
        else:
            print(f"{r['name']:<30} {s['sessions']:>10,} {s['users']:>10,} {s['pageviews']:>10,}")

    # HTML report
    html = build_html(results, args.days)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nHTML report saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
