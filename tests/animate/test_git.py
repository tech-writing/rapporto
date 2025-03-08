import tempfile
from urllib.request import urlretrieve

from rapporto.cli import cli


def test_cli_animate_git(cli_runner, tmp_path, caplog):
    """
    CLI test: Invoke `rapporto animate git`.
    """

    outfile = tmp_path / "pygource-testdrive.mp4"
    outfile.unlink(missing_ok=True)

    tmp = tempfile.NamedTemporaryFile(suffix=".mp3")
    urlretrieve("https://download.samplelib.com/mp3/sample-6s.mp3", tmp.name)
    subcommand = f"""
    animate git \
        --name pygource-testdrive \
        --start-date 2025-02-04 20:00:00 \
        --stop-date 2025-02-05 03:00:00 \
        --time-lapse \
        --path . \
        --audio {tmp.name} \
        --outdir {outfile.parent} \
        --overwrite
    """.strip()

    result = cli_runner.invoke(
        cli,
        args=subcommand,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert outfile.exists()

    assert "Processing project" in result.output
    assert "Creating video" in result.output
    assert "Repeating audio" in result.output
    assert f"INFO: Video:     {outfile}" in result.output
