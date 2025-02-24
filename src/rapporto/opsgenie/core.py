"""
OPSGENIE ALERTS REPORT GENERATOR

Generate report of Opsgenie alerts within a given time range.
Output formats can be Markdown or nicely formatted terminal output.

Usage Example:
    export OPSGENIE_API_KEY="your-api-key"
    rapporto opsgenie export-alerts --when="-7d"
    rapporto opsgenie export-alerts --start-time "12-02-2025T14:00:00" --days 7 > opsgenie-report.md
"""

import io
import json
import logging
import re
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone

import click
from aika import TimeInterval, TimeIntervalParser
from munch import munchify
from opsgenie_sdk import AlertApi, ApiClient, ApiException, Configuration
from opsgenie_sdk.exceptions import ConfigurationException
from tabulate import tabulate

logger = logging.getLogger(__name__)


class OpsgenieAlertsClient:
    """
    Fetch alert items from Opsgenie API.
    """

    OPSGENIE_DATETIME_FORMAT = "%d-%m-%YT%H:%M:%S"

    def __init__(self, api_key: str, query: str):
        self.api_key = api_key
        self.query = query
        self.api: ApiClient = self.client_factory(self.api_key)

    @classmethod
    def format_interval(cls, interval: TimeInterval):
        """Format the interval for the query expression."""
        expression = f'createdAt >= "{interval.start.strftime(cls.OPSGENIE_DATETIME_FORMAT)}"'
        if interval.end:
            expression += (
                f' and createdAt <= "{interval.end.strftime(cls.OPSGENIE_DATETIME_FORMAT)}"'
            )
        return expression

    @classmethod
    def query_from_cli_options(cls, ctx: click.Context) -> str:
        """Build the Opsgenie query string based on CLI arguments."""
        params = munchify(ctx.params)
        if params.when:
            tr = TimeIntervalParser()
            interval = tr.parse(params.when)
        elif params.start_time:
            if params.days is None:
                raise ValueError("--days is required when --start-time is provided")
            start_dt = datetime.strptime(params.start_time, cls.OPSGENIE_DATETIME_FORMAT)
            start_dt = start_dt.replace(tzinfo=timezone.utc)
            end_dt = start_dt + timedelta(days=params.days)
            interval = TimeInterval(start_dt, end_dt)
        else:
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            interval = TimeInterval(seven_days_ago, None)
        query = cls.format_interval(interval)
        logger.info(f"Using query: {query}")
        return query

    @staticmethod
    def client_factory(api_key: str) -> ApiClient:
        """Create an Opsgenie ApiClient instance."""
        configuration = Configuration()
        configuration.api_key["Authorization"] = api_key
        return ApiClient(configuration)

    def fetch(self, limit: int = 100) -> list:
        """Fetch all alerts from Opsgenie that match the given query, paginating as needed."""
        alerts = []
        offset = 0
        alert_api = AlertApi(api_client=self.api)
        while True:
            response = alert_api.list_alerts(
                query=self.query, limit=limit, offset=offset, sort="createdAt", order="asc"
            )
            if not response.data:
                break
            alerts.extend(response.data)
            offset += limit
            if len(response.data) < limit:
                break
        return alerts


class OpsgenieAlertsReport:
    """
    Report about alert items from Opsgenie.
    """

    def __init__(self, client: OpsgenieAlertsClient) -> None:
        self.client: OpsgenieAlertsClient = client
        self.alerts_data: list
        self.summary_data: list
        self.token_summary_data: list

    def process(self) -> None:
        """
        Process alerts into data tables.

        Returns:
            alerts_data: list of [Trigger Date, Priority, Alert Message, Resolved Time, Open Duration]
            summary_data: list of [Priority, Total Count, Out-of-hours Count]
            token_summary_data: list of [First Alert Token, Count]
        """  # noqa: E501
        alerts_data: list = []
        priority_count: dict = {}
        out_of_hours_count: dict = {}
        message_token_count: dict = {}

        # Patterns to remove certain strings from the alert message.
        remove_patterns = [
            r"\[Prometheus\]: \[FIRING:.*\] ",
            r"kubernetes-service-endpoints",
            r"crate",
            r"prod",
            r"kubernetes-nodes",
            r"stable",
            r"db cloud",
            r"( metrics p)",
            r"\(metrics promethe",
        ]

        try:
            alerts = self.client.fetch()
        except ConfigurationException as e:
            msg = f"Opsgenie configuration error: {e.reason}; {json.loads(e.body)['message']}"
            logger.error(msg)
            raise ValueError(msg) from e
        except ApiException as e:
            msg = f"Opsgenie API error: {e.reason}"
            logger.error(msg)
            raise IOError(msg) from e

        for alert in alerts:
            created_at_str = alert.created_at.strftime("%Y-%m-%d %H:%M")
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
                resolved_time = resolved_dt.strftime("%Y-%m-%d %H:%M")
                open_duration_str = str(resolved_dt - alert.created_at).split(".")[0]
            else:
                resolved_time = "Open"
                open_duration_str = "-"

            priority = alert.priority if alert.priority else "Not Specified"
            priority_count[priority] = priority_count.get(priority, 0) + 1

            if alert.created_at.hour >= 22 or alert.created_at.hour < 8:
                out_of_hours_count[priority] = out_of_hours_count.get(priority, 0) + 1

            alerts_data.append(
                [created_at_str, priority, message, resolved_time, open_duration_str]
            )

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

        self.alerts_data = alerts_data
        self.summary_data = summary_data
        self.token_summary_data = token_summary_data

    def to_markdown(self) -> str:
        """Generate Markdown output."""
        md = (
            f"## Opsgenie Alerts Report ({self.client.query})\n\n"
            "| Trigger Date       | Prty           | Alert Message                              | Resolved Time    | Open Duration |\n"  # noqa: E501
            "|--------------------|----------------|--------------------------------------------|------------------|---------------|\n"
        )
        md += "\n".join(
            [
                f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} |"
                for row in self.alerts_data
            ]
        )
        md += "\n\n## Alert Type Summary\n\n"
        md += (
            "| Priority Level     | Count | Out-of-hours |\n"
            "|--------------------|-------|--------------|\n"
        )
        md += "\n".join([f"| {row[0]} | {row[1]} | {row[2]} |" for row in self.summary_data])
        md += "\n\n## Alert Message Summary\n\n"
        md += "| Alert Token       | Count |\n|-------------------|-------|\n"
        md += "\n".join([f"| {row[0]} | {row[1]} |" for row in self.token_summary_data])
        return md

    def to_text(self) -> str:
        """Generate formatted terminal output."""
        with redirect_stdout(io.StringIO()) as stdout:
            print("Formatted Terminal Output:\n")
            print(
                tabulate(
                    self.alerts_data,
                    headers=[
                        "Trigger Date",
                        "Priority",
                        "Alert Message",
                        "Resolved Time",
                        "Open Duration",
                    ],
                    tablefmt="grid",
                )
            )
            print("\nAlert Type Summary:")
            print(
                tabulate(
                    self.summary_data,
                    headers=["Priority Level", "Count", "Out-of-hours"],
                    tablefmt="grid",
                )
            )
            print("\nAlert Message Summary:")
            print(
                tabulate(self.token_summary_data, headers=["Alert Token", "Count"], tablefmt="grid")
            )
        stdout.seek(0)
        return stdout.read()
