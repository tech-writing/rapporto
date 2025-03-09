"""
Aggregated, chronological change log across multiple projects.

References:
- zt.manticore.ext.changes
"""

import copy
import glob
import logging
import os
import re
import sys
import typing as t
from collections import namedtuple
from operator import attrgetter
from pathlib import Path

from .util import rest_header, walk_projects

HACKS: t.Dict[str, t.Dict[str, str]] = {
    "project_aliases": {
        # 'from': 'to',
    }
}

Segment = namedtuple("Segment", "date, version, author, text")
Change = namedtuple("Change", "date, name, version, author, text")


logger = logging.getLogger(__name__)


class ChangesFileReader:
    def __init__(self, changes_file_path):
        self.changes_file_path = changes_file_path

    def expand_roles(self, line):
        """
        Expand strings like 'BUG-XXXX' to ':bug:`BUG-XXXX`'.
        For using with the `sphinx.ext.extlinks` extension.
        """
        expansions = [("BUG", ":bug:")]
        for expansion in expansions:
            symbol = expansion[0]
            role = expansion[1]
            if (
                "{symbol}-".format(**locals()) in line
                and "{role}`{symbol}-".format(**locals()) not in line
            ):
                line = re.sub(
                    r"{symbol}-(\d+)".format(**locals()),
                    r"{role}`{symbol}-\1`".format(**locals()),
                    line,
                )
        return line

    def lines(self):
        for line in Path(self.changes_file_path).read_text().splitlines():
            yield self.expand_roles(line)


class ChangesFileSegmentizer:
    """CHANGES file parser and segmentizer. Uses regexes and a little state machine."""

    def __init__(self, reader):
        self.reader = reader
        self.date_patterns = [
            r"(?P<year>\d{4})[/-](?P<month>\d{2})[/-](?P<day>\d{2})?",
            r"(?P<day>\d{2})[/-](?P<month>\d{2})[/-](?P<year>\d{4})?",
        ]
        self.header_patterns = []
        self.suffix_pattern = r"""
            (?:\s?\(?v?
                (?P<version>[-.0-9]+)
            \)?)?
            (?:\s\[(?P<author>\D+?)\])?
            :?
        """
        for date_pattern in self.date_patterns:
            pattern = date_pattern + self.suffix_pattern
            # print pattern
            self.header_patterns.append(re.compile(pattern, re.VERBOSE))
        self.date_tpl = "%(year)s-%(month)s-%(day)s"
        self.date_tpl = "%(version)s"

    def _match_header(self, line):
        for header_pattern in self.header_patterns:
            m = header_pattern.match(line)
            if m:
                return m
        return None

    def get_entries(self):
        state_header = False
        state_inblock = False

        # initialize data variables
        date = None
        version = None
        author = None
        block: t.List[str] = []

        def response():
            # yield out response entry
            segment = Segment(date, version, author, "\n".join(block))
            # print segment
            return segment

        for line in self.reader.lines():
            # if not line: continue
            line = line.rstrip()

            # check line for "date & version" pattern
            m = self._match_header(line)
            if m:
                if state_inblock:
                    # yield out finished block
                    yield response()

                    # reset for next iteration
                    date = None
                    version = None
                    author = None
                    block = []

                # compute normalized change entry attributes
                payload = m.groupdict()
                date = "%(year)s-%(month)s-%(day)s" % payload
                version = payload["version"]
                author = payload["author"]
                state_header = True
                continue

            if state_header:
                # skip reST title underlines
                if line.startswith("=" * 5) or line.startswith("-" * 5):
                    continue

                # switch state to block content aggregation
                else:
                    state_header = False
                    state_inblock = True

            # aggregate block content
            if state_inblock:
                block.append(line)

        # yield out last block
        yield response()


class ChangesAggregator:
    """Aggregates and holds all global changes. Provides a sorted activity stream of changes."""

    def __init__(self, project_path, summary_path):
        # configuration data
        self.filename_choices = ["CHANGES.rst", "CHANGES.txt", "CHANGES"]
        self.project_path = project_path
        self.summary_path = summary_path

        # volatile data
        self.changes = set()
        self.projects = set()

    def walk_projects_changes_files(self):
        """Scans all main level directories in the projects directory for a 'CHANGES.rst' file"""
        for project in walk_projects(self.project_path):
            possible_files = glob.glob(project.path + "/*") + glob.glob(project.path + "/*/*")
            changes_files_found = [
                changes_file
                for changes_file in possible_files
                if os.path.basename(changes_file) in self.filename_choices
            ]
            if not changes_files_found:
                yield project
            for changes_file_found in changes_files_found:
                project_ready = copy.deepcopy(project)
                project_ready.changes_file = changes_file_found
                yield project_ready

    def normalize_project_name(self, project_name):
        for alias, name in HACKS.get("project_aliases", {}).items():
            project_name = project_name.replace(alias, name)
        return project_name

    def read_changes_file(self, project):
        """Read 'CHANGES.rst', segmentize into change entries and store in memory"""
        # print changes_file_path
        # project_name = self.normalize_project_name(project.name)
        if not project.changes_file:
            return
        cfs = ChangesFileSegmentizer(ChangesFileReader(project.changes_file))
        for entry in cfs.get_entries():
            entry = Change(entry.date, project.name, entry.version, entry.author, entry.text)
            self.changes.add(entry)

    def compute_changes(self):
        # scan for CHANGES files
        for project in self.walk_projects_changes_files():
            project.name = self.normalize_project_name(project.name)
            self.projects.add(project)
            self.read_changes_file(project)

        logger.info(f"Processing projects: {self.projects}")

        # process change entries
        self.changes = sorted(self.changes, key=attrgetter("date", "name", "version"))  # type: ignore[assignment]

    def get_change_title(self, change, short=False):
        if short:
            change_name = change.name or ""
            change_version = change.version or ""
            return change_name + " " + change_version
        else:
            change_header = "%(date)s :ref:`%(name)s <%(name)s>`" % change._asdict()
            if change.version:
                change_header += " " + change.version
            if change.author:
                change_header += " [author: " + change.author + "]"
            return change_header

    def get_change_message(self, change):
        message = ""
        if change.date is None or change.date == "":
            message += ".. note:: Date missing\n"
        # if change.version is None or change.version == '':
        #    message += '.. note:: Version missing'
        if change.text is None or change.text == "":
            message += ".. note:: Change text is empty"
        return message

    def write_summary_rst(self):
        summary_file = os.path.join(self.summary_path, "changes.rst")
        summary_path = os.path.dirname(summary_file)
        if not os.path.exists(summary_path):
            os.makedirs(summary_path)
        project_names = [project.name for project in self.projects]
        project_names.sort()
        f = open(summary_file, "w")
        f.write(rest_header("Release notes", "zt.manticore.ext.changes"))
        f.write("\n.. include:: ../global/manticore-links.rst\n\n")
        f.write(
            "Aggregated release notes across all projects ``CHANGES.rst`` "
            "in reverse chronological order as an activity stream.\n\n"
        )
        f.write("project names: ")
        f.write(", ".join(project_names))
        f.write("\n\n")
        f.write(self.get_timeline_widget())
        f.write("\n\n\n")

        changes = copy.copy(self.changes)
        changes = reversed(list(changes))  # type: ignore[assignment]
        for change in changes:
            title = self.get_change_title(change)
            f.write(title + "\n")
            f.write("-" * len(title) + "\n")
            f.write(self.sanitize_change_text(change.text) + "\n")
            f.write(self.get_change_message(change))
            f.write("\n\n")

        f.close()

    def get_timeline_widget(self):
        return ".. seealso:: :doc:`timeline`"
        timeline_widget = """
----

Timeline data: :download:`changes.js`.

.. raw:: html

    <!-- Include Simile Timeline Widget -->
    <iframe src="../_static/timeline/timeline.html" width="100%" height="400" style="border: 0px; overflow: visible">
        <p>Changes timeline</p>
    </iframe>

----
        """  # noqa: E501
        return timeline_widget

    def write_summary_js(self):
        summary = """var timeline_data = {
    'dateTimeFormat': 'iso8601',
    'wikiURL': "http://manticore.example.net/summary/changes.html",
    'wikiSection': "project changes",
    'events': [
        %(events)s
    ]
}
        """

        """
        'events': [
            {'start': '2009-12-13',
            'title': 'Barfusserkirche',
            'description': 'by Lyonel Feininger, American/German Painter, 1871-1956',
            'image': 'http://images.allposters.com/images/AWI/NR096_b.jpg',
            'link': 'http://www.allposters.com/-sp/Barfusserkirche-1924-Posters_i1116895_.htm'
            },
        ]
        """
        event_template = """
        {
            'start': '%(start_date)s',
            'title': '%(title)s',
            'description': '%(description)s',
            'image': '%(image)s',
            'link': '%(link)s'
        },
        """

        def sanitize_js(text):
            return text.replace("'", '"').replace("\n-", "<br/><br/>-").replace("\n", "<br/>")

        events = []
        changes = copy.copy(self.changes)

        for change in changes:
            start_date = change.date
            if not start_date:
                continue
            title = sanitize_js(self.get_change_title(change, short=True))
            description = sanitize_js(self.sanitize_change_text(change.text))
            image = ""  # TODO
            link = ""  # TODO
            description += sanitize_js(self.get_change_message(change))
            # print locals()
            events.append(event_template % locals())

        summary_file = os.path.join(self.summary_path, "changes.js")
        summary_path = os.path.dirname(summary_file)
        if not os.path.exists(summary_path):
            os.makedirs(summary_path)
        f = open(summary_file, "w")
        f.write(summary % {"events": "".join(events)})
        f.close()

    def sanitize_change_text(self, text):
        lines = []
        for line in text.split("\n"):
            if re.match("^[-=]+$", line.strip()):
                continue
            lines.append(line)
        return "\n".join(lines)

    def run(self):
        self.compute_changes()
        self.write_summary_rst()
        self.write_summary_js()


def aggregate():
    logger.info("Computing aggregated CHANGES and summarizing in reStructuredText format")
    source_path = sys.argv[1]
    summary_path = sys.argv[2]
    ca = ChangesAggregator(source_path, summary_path)
    logger.info("Output path will be '%s'" % ca.summary_path)
    ca.run()
    # pprint(ca.changes)
    logger.info("Ready: Found %s changes in %s projects" % (len(ca.changes), len(ca.projects)))
