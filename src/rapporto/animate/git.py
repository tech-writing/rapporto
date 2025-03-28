"""
Render video of VCS repository commit history using Gource, with audio.

Prerequisites::

    apt-get install --yes ffmpeg gource mp3wrap
    brew install ffmpeg gource mp3wrap

Synopsis::

    rapporto animate git \
        --name acme \
        --path ~/dev/sandbox/acme \
        --audio '/home/foobar/music/Beastie boys/Suco De Tangerina.mp3'

References:
- https://gource.io/
- https://github.com/acaudwell/Gource
- zt.manticore.ext.gource
"""

# Relax linter.
# `subprocess` call: check for execution of untrusted input
# Starting a process with a shell, possible injection detected
# ruff: noqa: S603,S605
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import time


class GourceRenderer:
    """Renders project history using 'gource'."""

    def __init__(
        self,
        source_path,
        target_path,
        overwrite=False,
        audio=None,
        start_date=None,
        stop_date=None,
        time_lapse=False,
    ):
        self.project_path = source_path
        self.output_path = target_path

        self.start_date = start_date
        self.stop_date = stop_date

        # configuration data
        self.gource_cmd_tpl = """
            gource \\
                --title "%(title)s" --key \\
                --viewport 1280x720 \\
                --multi-sampling \\
                --hide bloom  \\
                --output-ppm-stream - \\
%(date_options)s  \\
%(speed_options)s  \\
                --stop-at-end \\
                --max-user-speed 250 \\
                --user-scale 1.5 \\
                --user-font-size 18 \\
                %(path)s \\
        """

        # --disable-auto-rotate \\

        # options
        self.overwrite = overwrite
        self.audio = audio
        self.time_lapse = time_lapse

    def get_gource_command(self, path: str, title: str):
        date_options = ""
        if self.start_date is not None:
            date_options += f"                --start-date '{self.start_date}' \\\n"
        if self.stop_date is not None:
            date_options += f"                --stop-date '{self.stop_date}' \\\n"
        else:
            date_options += "                --stop-at-end \\\n"
        # --stop-at-time 1

        speed_options = "                --seconds-per-day 5 --time-scale 1.5 \\\n"
        if self.time_lapse:
            speed_options = "                --seconds-per-day 2.5 --time-scale 2 \\\n"
        speed_options += "                --file-idle-time 20 --max-file-lag 2.5 \\\n"

        gource_options = {
            "path": path,
            "title": title,
            "date_options": date_options,
            "speed_options": speed_options,
        }
        command = self.gource_cmd_tpl % gource_options
        return command

    def choose_background_song(self):
        # TODO: enhance song picker (e.g. random or mapped selection from a directory)
        if self.audio and os.path.isfile(self.audio):
            return self.audio
        elif os.path.isfile(os.environ.get("GOURCE_AUDIO", "")):
            return os.environ.get("GOURCE_AUDIO")
        return None

    def process_project(self, path: str, name: str):
        print("=" * 42)
        print("Processing project '%s'" % name)
        print("=" * 42)

        video_file = self.create_video(path, self.output_path, name)
        if not video_file:
            print("ERROR: video could not be created")
            return False

        mi = MediaInfo(video_file)
        if "video" in mi.get_streams():
            print("INFO: Video:    ", video_file)
            print("INFO: Duration: ", mi.duration)

        else:
            print("ERROR: video '%s' could not be recorded" % video_file)
            os.unlink(video_file)
            video_file = None
            return False

        return True

    def create_video(self, project_path, video_path, video_filename):
        vr = VideoRecorder(video_path, video_filename)
        if vr.exists() and not self.overwrite:
            print("INFO: Video exists and --overwrite is not given, will skip further processing.")
            return vr.get_video_file()

        print("-" * 42)
        print("Creating video '%s'" % vr.get_video_file())
        cmd = (
            self.get_gource_command(path=project_path, title=video_filename)
            + " | \\"
            + vr.get_command()
        )
        print("command:", cmd)
        print("-" * 42)

        if run_command(cmd):
            video_file = vr.get_video_file()

            audio_file = self.choose_background_song()
            if audio_file:
                mixer = VideoAudioMixer(video_file, audio_file)
                mixer.extend_audio()
                mixer.run()

            return video_file
        return None


class MediaInfo:
    """
    Duration: 00:00:01.73, start: 0.000000, bitrate: 662 kb/s
      Stream #0.0(und): Video: h264, yuv420p, 1024x768, 651 kb/s, 60 fps, 59.94 tbr, 60 tbn, 120 tbc
    """

    def __init__(self, mediafile):
        self.mediafile = mediafile
        self.raw = ""
        self.duration = ""
        self.streams = []
        self.read_info()
        self.parse_info()

    def read_info(self):
        cmd = "ffprobe -i '%s'" % self.mediafile
        print("MediaInfo ffmpeg command:", cmd)
        output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT).decode("utf-8")
        # print("MediaInfo output:", output)
        self.raw = output

    def parse_info(self):
        r_duration = re.compile(".*Duration: ([.:0-9]+)")
        r_stream = re.compile(".*Stream .*: (Video|Audio)")
        for line in self.raw.split("\n"):
            m = r_duration.match(line)
            if m:
                self.duration = m.group(1)
            m = r_stream.match(line)
            if m:
                self.streams.append(m.group(1).lower())

    def get_duration(self):
        return self.duration

    def get_streams(self):
        return self.streams


class VideoRecorder:
    def __init__(self, video_path, video_name):
        self.video_path = video_path
        self.video_name = video_name
        self.video_file = self.get_video_file()

    def get_command(self):
        arguments = self.__dict__.copy()

        # Some remarks about "ffmpeg" options:
        #   - The encoder 'aac' is experimental but experimental codecs are not enabled,
        #     add '-strict -2' if you want to use it.
        command = (
            f"""
            ffmpeg -y \\
                -r 60 \\
                -vcodec ppm -f image2pipe -i - \\
                -vcodec libx264 -pix_fmt yuv420p -preset medium -threads 0 -strict -2 \\
                "{self.video_file}" \\
            """
            % arguments
        )
        return command

    def get_video_file(self):
        return os.path.join(self.video_path, self.video_name + self.get_extension())

    def get_extension(self):
        return ".mp4"

    def exists(self):
        return os.path.exists(self.get_video_file())


class VideoAudioMixer:
    def __init__(self, video_file, audio_file):
        self.video_file = video_file
        self.audio_file = audio_file
        self.duration = None

    def run(self):
        extension = os.path.splitext(self.video_file)[1]
        tmpfile = self.video_file + ".tmp" + extension
        cmd = "ffmpeg -y -i '%s' -i '%s' -vcodec copy -acodec copy -async 1 -shortest '%s'" % (
            self.video_file,
            self.audio_file,
            tmpfile,
        )
        print("VideoAudioMixer ffmpeg command:", cmd)
        output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
        print("VideoAudioMixer ffmpeg output:", output)
        shutil.move(tmpfile, self.video_file)

    def extend_audio(self):
        video_info = MediaInfo(mediafile=self.video_file)
        audio_info = MediaInfo(mediafile=self.audio_file)
        loops = self.get_audio_loops(video_info.duration, audio_info.duration)
        print(f"Repeating audio {loops} times to match length of video")
        self.audio_file = self.loop_audio(times=loops)

    def loop_audio(self, times=2):
        # TODO: remove looped audio file after usage

        name = os.path.basename(self.audio_file)
        audio_files = ('"%s" ' % self.audio_file) * times
        mp3wrap_file = "/tmp/tmp_%s" % name

        if not times or times <= 1:
            shutil.copy(self.audio_file, mp3wrap_file)
            return mp3wrap_file

        # WTF?
        mp3wrap_file_real = mp3wrap_file.replace(".mp3", "_MP3WRAP.mp3")
        if os.path.exists(mp3wrap_file_real):
            os.unlink(mp3wrap_file_real)

        mp3wrap_command = 'mp3wrap "%s" %s' % (mp3wrap_file, audio_files)
        if run_command(mp3wrap_command):
            return mp3wrap_file_real
        return None

    @classmethod
    def get_audio_loops(cls, video_duration, audio_duration):
        """
        d1 = "00:03:16.18"
        d2 = "00:00:06.43"
        >>> get_audio_loops(d1, d2)
        33
        """
        factor = cls.duration_to_seconds(video_duration) / cls.duration_to_seconds(audio_duration)
        loops = math.ceil(factor)
        return loops

    @classmethod
    def duration_to_seconds(cls, duration):
        time_struct = time.strptime(duration, "%H:%M:%S.%f")
        seconds = time_struct.tm_hour * 3600 + time_struct.tm_min * 60 + time_struct.tm_sec
        return seconds


def run_command(command):
    returncode = os.system(command)
    if returncode == 0:
        return True
    else:
        print("ERROR while executing command '%s'" % command)
        return False


def render(args):
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-p", "--path", dest="path", help="path to vcs repository")
    parser.add_option("-o", "--outdir", dest="outdir", help="path to output directory")
    parser.add_option(
        "-n",
        "--name",
        dest="name",
        help="project name (output video basename w/o extension) [optional]",
    )
    parser.add_option("-a", "--audio", dest="audio", type="str", help="path to audio file")
    parser.add_option(
        "-O",
        "--overwrite",
        dest="overwrite",
        action="store_true",
        help="whether to overwrite video files",
    )
    parser.add_option("--start-date", dest="start_date", help="Start at a date and optional time")
    parser.add_option("--stop-date", dest="stop_date", help="Stop at a date and optional time")
    parser.add_option(
        "-t", "--time-lapse", dest="time_lapse", action="store_true", help="run in time-lapse mode"
    )
    (options, args) = parser.parse_args(args=args)

    # Sanity checks.
    if not options.path:
        print("ERROR: Option '--path' is mandatory!")
        sys.exit(1)

    options.path = os.path.abspath(options.path)
    if not os.path.isdir(options.path):
        print("ERROR: Directory '%s' does not exist" % options.path)
        sys.exit(1)

    # Defaults.
    if not options.outdir:
        options.outdir = os.path.abspath(os.path.curdir)

    if not options.name:
        options.name = os.path.basename(options.path)

    print(
        "Rendering project history of single project '%s <%s>' using 'gource'"
        % (options.name, options.path)
    )
    source_path = options.path
    target_path = options.outdir
    gr = GourceRenderer(
        source_path,
        target_path,
        overwrite=options.overwrite,
        audio=options.audio,
        start_date=options.start_date,
        stop_date=options.stop_date,
        time_lapse=options.time_lapse,
    )
    gr.process_project(path=options.path, name=options.name)
