"""
Google Analytics 4 Report
Site: AiKuleana.com
Property ID: (set below after you find it)
Credentials: .gsc-credentials/laptoplane-blogspot-autoposter-c7da82883623.json

SETUP:
  1. Enable "Google Analytics Data API" in Google Cloud Console
     (project: laptoplane-blogspot-autoposter)
  2. In GA4 Admin > Property Access Management, add:
     claude-test-sa@laptoplane-blogspot-autoposter.iam.gserviceaccount.com
     as Viewer
  3. Find your GA4 Property ID (numeric, not the G- measurement ID):
     GA4 Admin > Property Settings > Property ID (top right)
  4. Set PROPERTY_ID below to that number

USAGE:
  python ga_report.py                          # summary (default)
  python ga_report.py --report summary         # overall stats
  python ga_report.py --report pages           # top pages
  python ga_report.py --report sources         # traffic sources
  python ga_report.py --report devices         # device breakdown
  python ga_report.py --report countries       # top countries
  python ga_report.py --report all             # all reports
  python ga_report.py --days 7                 # last 7 days (default: 28)
  python ga_report.py --report pages --limit 20
"""

import argparse
from datetime import date, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest, OrderBy
)
from google.oauth2 import service_account

# --- Config ---
KEY_FILE    = ".gsc-credentials/laptoplane-blogspot-autoposter-c7da82883623.json"
PROPERTY_ID = "544041015"
SCOPES      = ["https://www.googleapis.com/auth/analytics.readonly"]


def get_client():
    if not PROPERTY_ID:
        print("ERROR: Set PROPERTY_ID in ga_report.py first.")
        print("Find it at: GA4 Admin > Property Settings > Property ID")
        raise SystemExit(1)
    creds = service_account.Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    return BetaAnalyticsDataClient(credentials=creds)


def run_report(client, dimensions, metrics, days, limit, order_by_metric=0):
    dr = DateRange(start_date=f"{days}daysAgo", end_date="yesterday")
    dims = [Dimension(name=d) for d in dimensions]
    mets = [Metric(name=m) for m in metrics]
    order = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=metrics[order_by_metric]),
                     desc=True)]
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=dims,
        metrics=mets,
        date_ranges=[dr],
        order_bys=order,
        limit=limit,
    )
    return client.run_report(request)


def date_label(days):
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return f"{start} to {end}"


# --- Reports ---

def report_summary(client, days, limit):
    dr = DateRange(start_date=f"{days}daysAgo", end_date="yesterday")
    request = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        metrics=[
            Metric(name="sessions"),
            Metric(name="totalUsers"),
            Metric(name="newUsers"),
            Metric(name="screenPageViews"),
            Metric(name="averageSessionDuration"),
            Metric(name="bounceRate"),
            Metric(name="engagedSessions"),
        ],
        date_ranges=[dr],
    )
    response = client.run_report(request)
    if not response.rows:
        print("No data available.")
        return

    r = response.rows[0]
    vals = [m.value for m in r.metric_values]
    sessions = int(vals[0])
    users = int(vals[1])
    new_users = int(vals[2])
    pageviews = int(vals[3])
    avg_duration = float(vals[4])
    bounce_rate = float(vals[5]) * 100
    engaged = int(vals[6])
    engagement_rate = (engaged / sessions * 100) if sessions else 0
    mins = int(avg_duration) // 60
    secs = int(avg_duration) % 60

    label = date_label(days)
    print(f"\n{'='*50}")
    print(f"  SUMMARY  |  {label}")
    print(f"{'='*50}")
    print(f"  Sessions          : {sessions:,}")
    print(f"  Total Users       : {users:,}")
    print(f"  New Users         : {new_users:,}")
    print(f"  Page Views        : {pageviews:,}")
    print(f"  Avg Duration      : {mins}m {secs}s")
    print(f"  Bounce Rate       : {bounce_rate:.1f}%")
    print(f"  Engagement Rate   : {engagement_rate:.1f}%")
    print(f"{'='*50}\n")


def report_pages(client, days, limit):
    response = run_report(client,
                          ["pagePath"],
                          ["screenPageViews", "sessions", "averageSessionDuration", "bounceRate"],
                          days, limit)
    if not response.rows:
        print("No page data available.")
        return

    label = date_label(days)
    print(f"\nTop {len(response.rows)} Pages  |  {label}\n")
    print(f"{'#':<4} {'Page':<40} {'Views':>7} {'Sess':>7} {'Dur':>8} {'Bounce':>8}")
    print("-" * 78)
    for i, row in enumerate(response.rows, 1):
        page = row.dimension_values[0].value[:39]
        views = int(row.metric_values[0].value)
        sess = int(row.metric_values[1].value)
        dur = float(row.metric_values[2].value)
        bounce = float(row.metric_values[3].value) * 100
        mins = int(dur) // 60
        secs = int(dur) % 60
        print(f"{i:<4} {page:<40} {views:>7,} {sess:>7,} {mins:>2}m{secs:>02}s {bounce:>7.1f}%")
    print()


def report_sources(client, days, limit):
    response = run_report(client,
                          ["sessionSource"],
                          ["sessions", "totalUsers", "bounceRate"],
                          days, limit)
    if not response.rows:
        print("No source data available.")
        return

    label = date_label(days)
    print(f"\nTop {len(response.rows)} Traffic Sources  |  {label}\n")
    print(f"{'#':<4} {'Source':<35} {'Sessions':>10} {'Users':>8} {'Bounce':>8}")
    print("-" * 68)
    for i, row in enumerate(response.rows, 1):
        src = row.dimension_values[0].value[:34]
        sess = int(row.metric_values[0].value)
        users = int(row.metric_values[1].value)
        bounce = float(row.metric_values[2].value) * 100
        print(f"{i:<4} {src:<35} {sess:>10,} {users:>8,} {bounce:>7.1f}%")
    print()


def report_devices(client, days, limit):
    response = run_report(client,
                          ["deviceCategory"],
                          ["sessions", "totalUsers", "screenPageViews"],
                          days, limit)
    if not response.rows:
        print("No device data available.")
        return

    label = date_label(days)
    total_sess = sum(int(r.metric_values[0].value) for r in response.rows)
    print(f"\nDevice Breakdown  |  {label}\n")
    print(f"{'Device':<15} {'Sessions':>10} {'Users':>8} {'Views':>8} {'Share':>8}")
    print("-" * 52)
    for row in response.rows:
        dev = row.dimension_values[0].value
        sess = int(row.metric_values[0].value)
        users = int(row.metric_values[1].value)
        views = int(row.metric_values[2].value)
        share = (sess / total_sess * 100) if total_sess else 0
        print(f"{dev:<15} {sess:>10,} {users:>8,} {views:>8,} {share:>7.1f}%")
    print()


def report_countries(client, days, limit):
    response = run_report(client,
                          ["country"],
                          ["sessions", "totalUsers"],
                          days, limit)
    if not response.rows:
        print("No country data available.")
        return

    label = date_label(days)
    print(f"\nTop {len(response.rows)} Countries  |  {label}\n")
    print(f"{'#':<4} {'Country':<30} {'Sessions':>10} {'Users':>8}")
    print("-" * 55)
    for i, row in enumerate(response.rows, 1):
        country = row.dimension_values[0].value[:29]
        sess = int(row.metric_values[0].value)
        users = int(row.metric_values[1].value)
        print(f"{i:<4} {country:<30} {sess:>10,} {users:>8,}")
    print()


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="GA4 Report - AiKuleana.com")
    parser.add_argument("--report", choices=["summary", "pages", "sources", "devices", "countries", "all"],
                        default="summary", help="Report type (default: summary)")
    parser.add_argument("--days", type=int, default=28,
                        help="Number of days to look back (default: 28)")
    parser.add_argument("--limit", type=int, default=10,
                        help="Max rows to return (default: 10)")
    args = parser.parse_args()

    print(f"Connecting to GA4 for AiKuleana.com (property {PROPERTY_ID})...")
    client = get_client()
    print("Connected.\n")

    reports = {
        "summary":   report_summary,
        "pages":     report_pages,
        "sources":   report_sources,
        "devices":   report_devices,
        "countries": report_countries,
    }

    if args.report == "all":
        for fn in reports.values():
            fn(client, args.days, args.limit)
    else:
        reports[args.report](client, args.days, args.limit)


if __name__ == "__main__":
    main()
