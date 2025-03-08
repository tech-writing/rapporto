# Animate Git

## About

Render video of VCS repository commit history using [Gource], with audio.

## Prerequisites

Debian Linux.
```shell
apt-get install --yes ffmpeg gource mp3wrap
```

macOS/Homebrew.
```shell
brew install ffmpeg gource mp3wrap
```

## Usage

```shell
rapporto animate git \
  --name "Project ACME" \
  --path "/path/to/acme" \
  --audio "/path/to/audio.mp3"
```

## Examples

### Prepare audio

Get an audio file.
```shell
yt-dlp --extract-audio --format=m4a \
  --output="./var/Beastie boys - Suco De Tangerina.m4a" \
  "https://www.youtube.com/watch?v=lpHWxf5xL0w"
```

Convert file to MP3 format.
```shell
ffmpeg \
  -i "./var/Beastie boys - Suco De Tangerina.m4a" \
  -c:v copy -c:a libmp3lame -q:a 4 \
  "./var/Beastie boys - Suco De Tangerina.mp3"
```

### Basic

Acquire VCS sources.
```shell
git clone https://github.com/acaudwell/Gource ./var/src/gource
```

Render and play video.
```shell
rapporto animate git \
  --name "Gource" \
  --path "./var/src/gource" \
  --audio "./var/Beastie boys - Suco De Tangerina.mp3"
```
```shell
open -a vlc Gource.mp4
```

### Advanced

Render and play video.
```shell
rapporto animate git \
  --name "Gource 2009" \
  --path "./var/src/gource" \
  --audio "./var/Beastie boys - Suco De Tangerina.mp3" \
  --start-date 2009-01-01 \
  --stop-date 2009-12-31 \
  --time-lapse \
  --outdir "./var" \
  --overwrite
```


[Gource]: https://github.com/acaudwell/Gource
