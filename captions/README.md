# Timed lyrics for the acoustic album

Each JSON file is the editable source for one recording's timed lyrics. The album page loads the corresponding JSON file when that song starts. The changing words do not announce themselves to screen readers; the current track title still does.

Track 1 was checked against the recording by a sighted reviewer. Tracks 2–13 were aligned locally with speech recognition and reconciled with the existing lyric pages. They need a human listening review before they are marked verified.

After any wording or timing change, run `python scripts/build_lyric_assets.py` from the repository root. It refreshes the full reading page and the WebVTT file from the JSON. Publish the changed JSON, reading page, and VTT together. No layout or playback change is needed for a correction. If a recording is replaced with a different performance, realign its cues to that recording.
