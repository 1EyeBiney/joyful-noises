# Timed lyrics pilot

`before-the-morning-preview.json` is the editable source for the first acoustic song's timed lyrics. Each cue has a start time, end time, and the text to show. The album preview reads this file when track 1 starts. The lyric text does not announce itself to screen readers; the current song title still does.

After any wording or timing change, run `python scripts/build_lyric_assets.py` from the repository root. This refreshes `preview-songs/01.html` and the WebVTT caption file from the JSON. Publish those three files together. No layout or playback change is needed for a caption correction.

These captions were machine aligned and reconciled with a source lyric sheet. They still need a listening check against the Gentle Slide recording before being treated as final. If the MP3 is replaced with a different performance, realign its cues to the new recording.
