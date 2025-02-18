import argparse
import logging
import os
import re
import sys
from datetime import datetime

import requests
from slack_sdk import WebClient as SlackClient
from slack_sdk.errors import SlackApiError


class SlackThreadExporter:
    def __init__(self, token):
        self.client = SlackClient(token)
        self.user_cache = {}

    def resolve_user_id(self, user_id):
        """
        Resolve a Slack user ID to a username.

        :param user_id: Slack user ID (e.g., 'U01S5H7RRGB')
        :return: Username string (e.g., '@john.doe') or the original mention if unresolved
        """
        if user_id in self.user_cache:
            logging.debug(f"User ID {user_id} found in cache.")
            return self.user_cache[user_id]

        try:
            user_info = self.client.users_info(user=user_id)
            if user_info["ok"]:
                username = f"@{user_info['user']['name']}"  # Using 'name' for @username format
                self.user_cache[user_id] = username
                logging.debug(f"Resolved user ID {user_id} to username {username}.")
                return username
            else:
                logging.error(f"Failed to resolve user ID {user_id}: {user_info['error']}")
                return f"<@{user_id}>"  # Return original mention if failed
        except SlackApiError as e:
            logging.error(
                f"Slack API error when resolving user ID {user_id}: {e.response['error']}"
            )
            return f"<@{user_id}>"  # Return original mention if exception occurs

    def replace_user_mentions(self, text):
        """
        Replace Slack user mentions in the format <@USERID> with @username in bold.

        :param text: Original message text
        :return: Text with user mentions replaced by bold usernames
        """
        pattern = re.compile(r"<@([A-Z0-9]+)>")  # Matches patterns like <@U01S5H7RRGB>
        matches = pattern.findall(text)
        logging.debug(f"Found user mentions: {matches}")
        for user_id in matches:
            username = self.resolve_user_id(user_id)
            text = text.replace(f"<@{user_id}>", f"**{username}**")
            logging.debug(f"Replaced <@{user_id}> with **{username}**")
        return text

    def export_thread(self, slack_link, output_dir="slack_export"):
        """
        Export a Slack thread to markdown.

        :param slack_link: Slack thread URL
        :param output_dir: Directory to save exported files
        """
        logging.info(f"Starting export for Slack link: {slack_link}")

        # Parse link to get channel and thread details
        try:
            channel_id, thread_ts = self._parse_slack_link(slack_link)
            logging.debug(f"Parsed channel ID: {channel_id}, Thread Timestamp: {thread_ts}")
        except ValueError as ve:
            logging.error(f"Error parsing Slack link: {ve}")
            return

        # Fetch channel name
        try:
            channel_info = self.client.conversations_info(channel=channel_id)
            channel_name = channel_info["channel"]["name"]
            logging.debug(f"Fetched channel name: {channel_name}")
        except SlackApiError as e:
            logging.error(f"Error fetching channel info: {e.response['error']}")
            return

        # Fetch thread messages
        try:
            thread_replies = self.client.conversations_replies(channel=channel_id, ts=thread_ts)
            logging.debug(f"Fetched {len(thread_replies['messages'])} messages in thread.")
        except SlackApiError as e:
            logging.error(f"Error fetching thread: {e.response['error']}")
            return

        # Get the title from the first message
        title = thread_replies["messages"][0].get("text", "")[:20]
        logging.debug(f"Extracted title from first message: {title}")

        # Create output directories
        os.makedirs(output_dir, exist_ok=True)
        attachments_dir = os.path.join(output_dir, "attachments")
        os.makedirs(attachments_dir, exist_ok=True)
        logging.debug(f"Created output directories: {output_dir} and {attachments_dir}")

        # Generate sanitized filename
        sanitized_channel_name = self._sanitize_filename(channel_name)
        sanitized_title = self._sanitize_filename(title)
        sanitized_ts = datetime.fromtimestamp(float(thread_ts)).strftime("%y-%m-%d-%H_%M")
        filename_md = f"{sanitized_channel_name}_{sanitized_title}_{sanitized_ts}.md"
        logging.debug(f"Generated markdown filename: {filename_md}")

        # Markdown content
        markdown_content = []
        file_counter = 1

        # Process each message in the thread
        for message in thread_replies["messages"]:
            # Parse message details
            user_id = message.get("user", "")
            if user_id:
                username = self.resolve_user_id(user_id)
            else:
                username = "System"  # For messages like system messages without a user ID
                logging.debug("Message without user ID detected. Marked as 'System'.")

            timestamp = datetime.fromtimestamp(float(message["ts"])).strftime("%Y-%m-%d %H:%M:%S")
            markdown_content.append(f"### {username} - {timestamp}")
            logging.debug(f"Added header for message by {username} at {timestamp}.")

            # Process message text with formatting
            text = message.get("text", "")
            text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
            text = text.replace("```", "\n```")
            logging.debug(f"Processed message text: {text}")

            # Replace user mentions with usernames (formatted in bold)
            text = self.replace_user_mentions(text)
            logging.debug(f"Replaced user mentions in text: {text}")

            # Check if the message is from Opsgenie and format accordingly
            logging.debug(f"Checking if message is from Opsgenie: {username}")
            if "opsgenie" in username.lower():
                logging.debug("Identified as Opsgenie message.")
                # Check if the message has attachments or blocks
                if "attachments" in message:
                    for attachment in message["attachments"]:
                        if "text" in attachment:
                            text += "\n" + attachment["text"]
                            logging.debug("Appended attachment text from Opsgenie message.")
                if "blocks" in message:
                    for block in message["blocks"]:
                        if "text" in block and "text" in block["text"]:
                            text += "\n" + block["text"]["text"]
                            logging.debug("Appended block text from Opsgenie message.")
                text = self._format_opsgenie_message(text)
                logging.debug(f"Formatted Opsgenie message text: {text}")

            markdown_content.append(text)

            # Handle file attachments
            if "files" in message:
                for file_info in message["files"]:
                    original_filename = file_info.get("name", "unnamed")
                    sanitized_filename = self._sanitize_filename(original_filename)
                    basename, extension = os.path.splitext(sanitized_filename)

                    # Create unique filename with sanitized_ts and counter
                    unique_filename = f"{basename}_{sanitized_ts}_{file_counter}{extension}"
                    file_path = os.path.join(attachments_dir, unique_filename)
                    logging.debug(f"Prepared to download file: {unique_filename}")

                    # Download file with authorization
                    headers = {"Authorization": f"Bearer {self.client.token}"}
                    success = self._download_file(
                        file_info.get("url_private_download", ""), file_path, headers
                    )

                    if success:
                        # Add file reference to markdown
                        if file_info.get("mimetype", "").startswith("image/"):
                            markdown_content.append(
                                f"![{unique_filename}](attachments/{unique_filename})"
                            )
                            logging.debug(f"Embedded image in markdown: {unique_filename}")
                        else:
                            markdown_content.append(
                                f"**Attachment:** [Download {unique_filename}](attachments/{unique_filename})"
                            )
                            logging.debug(f"Added attachment link in markdown: {unique_filename}")
                        file_counter += 1  # Increment counter after successful download
                    else:
                        logging.error(f"Failed to download file: {unique_filename}")

            # Handle reactions
            if "reactions" in message:
                reactions_list = []
                for reaction in message["reactions"]:
                    emoji = reaction["name"]
                    users = reaction["users"]
                    # Resolve usernames from user IDs
                    usernames = [self.resolve_user_id(user_id) for user_id in users]
                    # Join usernames with commas
                    usernames_str = ", ".join(usernames)
                    # Add to reactions list
                    reactions_list.append(f":{emoji}: {usernames_str}")
                    logging.debug(f"Processed reaction: :{emoji}: by {usernames_str}")
                # Append reactions section to markdown_content
                if reactions_list:
                    reactions_md = "\n**Reactions:**\n"
                    for reaction_entry in reactions_list:
                        reactions_md += f"- {reaction_entry}\n"
                    markdown_content.append(reactions_md)
                    logging.debug("Appended reactions section to markdown.")

            markdown_content.append("\n---\n")
            logging.debug("Added section separator to markdown.")

        # Write markdown file
        markdown_text = "\n".join(markdown_content)
        markdown_file_path = os.path.join(output_dir, filename_md)
        logging.info(f"Writing markdown file to: {markdown_file_path}")
        try:
            with open(markdown_file_path, "w", encoding="utf-8") as f:
                f.write(markdown_text)
            logging.info(f"Markdown file written successfully to: {markdown_file_path}")
        except Exception as e:
            logging.error(f"Error writing markdown file: {e}")

        logging.info(f"Thread exported successfully to {output_dir}")

    def _format_opsgenie_message(self, text):
        """
        Format Opsgenie message text for markdown export.

        :param text: Original message text
        :return: Formatted message text
        """
        # Replace Opsgenie-specific formatting with markdown formatting
        text = text.replace("h4.", "####")
        text = text.replace("* ", "* ")
        text = text.replace("[", "[").replace("|", "](").replace("]", ")")
        logging.debug(f"Formatted Opsgenie message: {text}")
        return text

    def _parse_slack_link(self, slack_link):
        """
        Parse Slack link to extract channel ID and thread timestamp.

        :param slack_link: Slack thread URL
        :return: Tuple of channel ID and thread timestamp
        """
        # Extract channel ID and thread timestamp using regex
        match = re.search(r"/archives/(\w+)/p(\d+)", slack_link)
        if not match:
            raise ValueError("Invalid Slack link format")

        channel_id = match.group(1)
        thread_ts = f"{match.group(2)[:10]}.{match.group(2)[10:]}"
        logging.debug(f"Extracted channel ID: {channel_id}, Thread TS: {thread_ts}")
        return channel_id, thread_ts

    def _sanitize_filename(self, filename):
        """
        Sanitize filename to remove any invalid characters.

        :param filename: Original filename
        :return: Sanitized filename
        """
        sanitized = "".join(
            [c for c in filename if c.isalpha() or c.isdigit() or c in (" ", ".", "_")]
        ).rstrip()
        logging.debug(f"Sanitized filename from '{filename}' to '{sanitized}'")
        return sanitized

    def _download_file(self, url, path, headers):
        """
        Download file from URL with authorization headers.

        :param url: File URL
        :param path: Path to save the file
        :param headers: Authorization headers
        :return: Boolean indicating success or failure
        """
        if not url:
            logging.error("No download URL provided.")
            return False

        try:
            logging.info(f"Attempting to download file from URL: {url}")
            response = requests.get(url, headers=headers, stream=True)
            logging.debug(f"Response Status Code: {response.status_code}")
            logging.debug(f"Response Headers: {response.headers}")

            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "").lower()
                # logging.debug(f"Content-Type of response: {content_type}")

                if "text/html" in content_type:
                    logging.error(
                        f"Unexpected Content-Type: {content_type}. Possible authentication issue."
                    )
                    return False

                with open(path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                logging.info(f"File downloaded successfully: {path}")
                return True
            else:
                logging.error(f"Failed to download file. Status Code: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Exception occurred while downloading file: {e}")
            return False


# Example usage
def main():
    parser = argparse.ArgumentParser(description="Export a Slack thread to markdown.")
    parser.add_argument("--slack-token", required=False, help="Slack API token")
    parser.add_argument("--slack-link", required=True, help="Slack thread link")
    args = parser.parse_args()

    # Retrieve Slack token from command-line argument or environment variable
    slack_token = args.slack_token or os.getenv("SLACK_TOKEN")

    if not slack_token:
        logging.warning(
            "Slack API token not provided via --slack-token or SLACK_TOKEN environment variable."
        )
        sys.exit(1)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("slack_exporter.log"), logging.StreamHandler()],
    )

    exporter = SlackThreadExporter(args.slack_token)
    exporter.export_thread(args.slack_link)


if __name__ == "__main__":
    main()
