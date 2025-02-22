"""
OPSGENIE ALERTS REPORT GENERATOR

This script generates a report of OpsGenie alerts within a given time range.
Output can be generated as Markdown or as nicely formatted terminal output.

Usage Example:
    export OPSGENIE_API_KEY="your-api-key"
    uv run opsg.py --start-time "12-02-2025T14:00:00" --days 7 > opsg.md
"""

from datetime import datetime, timedelta, timezone
import os
import argparse
import re

from tabulate import tabulate  # For terminal output
from opsgenie_sdk import ApiClient, AlertApi, Configuration
from opsgenie_sdk.rest import ApiException


def build_query(args: argparse.Namespace) -> str:
    """Build the Opsgenie query string based on CLI arguments."""
    if args.start_time:
        if args.days is None:
            raise ValueError("--days is required when --start-time is provided")
        start_dt = datetime.strptime(args.start_time, "%d-%m-%YT%H:%M:%S")
        start_dt = start_dt.replace(tzinfo=timezone.utc)
        end_dt = start_dt + timedelta(days=args.days)
        query = (
            f'createdAt > "{start_dt.strftime("%d-%m-%YT%H:%M:%S")}" '
            f'and createdAt < "{end_dt.strftime("%d-%m-%YT%H:%M:%S")}"'
        )
    else:
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        query = f'createdAt > "{seven_days_ago.strftime("%d-%m-%YT%H:%M:%S")}"'
    return query


def create_api_client() -> AlertApi:
    """Create and return an AlertApi instance using the OPSGENIE_API_KEY environment variable."""
    configuration = Configuration()
    configuration.api_key['Authorization'] = os.getenv('OPSGENIE_API_KEY')
    if not os.getenv('OPSGENIE_API_KEY'):
        raise ValueError("Environment variable OPSGENIE_API_KEY is not set.")
    api_client = ApiClient(configuration)
    return AlertApi(api_client=api_client)


def fetch_alerts(api_instance: AlertApi, query: str, limit: int = 100) -> list:
    """Fetch all alerts from Opsgenie that match the given query, paginating as needed."""
    alerts = []
    offset = 0
    while True:
        response = api_instance.list_alerts(
            query=query,
            limit=limit,
            offset=offset,
            sort='createdAt',
            order='asc'
        )
        if not response.data:
            break
        alerts.extend(response.data)
        offset += limit
        if len(response.data) < limit:
            break
    return alerts


def process_alerts(alerts: list) -> tuple:
    """
    Process alerts into data tables.

    Returns:
        alerts_data: list of [Trigger Date, Priority, Alert Message, Resolved Time, Open Duration]
        summary_data: list of [Priority, Total Count, Out-of-hours Count]
        token_summary_data: list of [First Alert Token, Count]
    """
    alerts_data = []
    priority_count = {}
    out_of_hours_count = {}
    message_token_count = {}

    # Patterns to remove certain strings from the alert message.
    remove_patterns = [
        r"\[Prometheus\]: \[FIRING:.*\] ",
        r"kubernetes-service-endpoints",
        r"crate",
        r"prod",
        r"kubernetes-nodes",
        r"stable",
        r"\(metrics promethe",
    ]

    for alert in alerts:
        created_at_str = alert.created_at.strftime('%Y-%m-%d %H:%M')
        raw_message = alert.message
        for pattern in remove_patterns:
            raw_message = re.sub(pattern, "", raw_message)
        message = raw_message.strip()  # Adjust truncation here if necessary

        # Count first token from message
        tokens = message.split()
        first_token = tokens[0] if tokens else ""
        message_token_count[first_token] = message_token_count.get(first_token, 0) + 1

        # Determine resolved values and open duration
        if alert.report.close_time:
            resolved_dt = alert.created_at + timedelta(milliseconds=alert.report.close_time)
            resolved_time = resolved_dt.strftime('%Y-%m-%d %H:%M')
            open_duration_str = str(resolved_dt - alert.created_at).split('.')[0]
        else:
            resolved_time = 'Open'
            open_duration_str = '-'

        priority = alert.priority if alert.priority else 'Not Specified'
        priority_count[priority] = priority_count.get(priority, 0) + 1

        if alert.created_at.hour >= 22 or alert.created_at.hour < 8:
            out_of_hours_count[priority] = out_of_hours_count.get(priority, 0) + 1

        alerts_data.append([created_at_str, priority, message, resolved_time, open_duration_str])

    # Prepare summary data for priorities and out-of-hours count.
    summary_data = []
    for prio, total in priority_count.items():
        outside = out_of_hours_count.get(prio, 0)
        summary_data.append([prio, total, outside])

    # Prepare summary data for the first token occurrences.
    token_summary_data = []
    for token, count in sorted(message_token_count.items()):
        token_summary_data.append([token, count])

    # Sort alerts by creation time.
    alerts_data.sort(key=lambda row: row[0])
    return alerts_data, summary_data, token_summary_data


def generate_markdown(alerts_data: list, summary_data: list, token_summary_data: list, query: str) -> str:
    """Generate Markdown output for the alerts report."""
    md = (f"## Opsgenie Alerts Report ({query})\n\n"
          "| Trigger Date       | Prty           | Alert Message                              | Resolved Time    | Open Duration |\n"
          "|--------------------|----------------|--------------------------------------------|------------------|---------------|\n")
    md += "\n".join([f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |" for row in alerts_data])
    md += "\n\n## Alert Type Summary\n\n"
    md += ("| Priority Level     | Count | Out-of-hours |\n"
           "|--------------------|-------|--------------|\n")
    md += "\n".join([f"| {row[0]} | {row[1]} | {row[2]} |" for row in summary_data])
    md += "\n\n## Alert Message Summary\n\n"
    md += ("| Alert Token       | Count |\n"
           "|-------------------|-------|\n")
    md += "\n".join([f"| {row[0]} | {row[1]} |" for row in token_summary_data])
    return md


def generate_text_output(alerts_data: list, summary_data: list, token_summary_data: list) -> None:
    """Print formatted terminal output for the alerts report."""
    print("Formatted Terminal Output:\n")
    print(tabulate(alerts_data, headers=["Trigger Date", "Priority", "Alert Message", "Resolved Time", "Open Duration"], tablefmt="grid"))
    print("\nAlert Type Summary:")
    print(tabulate(summary_data, headers=["Priority Level", "Count", "Out-of-hours"], tablefmt="grid"))
    print("\nAlert Message Summary:")
    print(tabulate(token_summary_data, headers=["Alert Token", "Count"], tablefmt="grid"))


def main() -> None:
    """Main entry point for the Opsgenie alerts report generator."""
    try:
        args = parse_cli_args()
        query = build_query(args)
        api_instance = create_api_client()
        alerts = fetch_alerts(api_instance, query)
        alerts_data, summary_data, token_summary_data = process_alerts(alerts)

        if args.format == "md":
            md_output = generate_markdown(alerts_data, summary_data, token_summary_data, query)
            print("Markdown Output:\n")
            print(md_output)
        else:
            generate_text_output(alerts_data, summary_data, token_summary_data)

    except ApiException as api_e:
        print(f"Opsgenie API exception: {api_e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
