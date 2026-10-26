"""Refresh the first acoustic song's reading lyrics and VTT from its timed JSON.

Run from the repository root: python scripts/build_lyric_assets.py
"""
from pathlib import Path
from bs4 import BeautifulSoup
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'captions' / 'before-the-morning-preview.json'
READER = ROOT / 'preview-songs' / '01.html'
VTT = ROOT / 'captions' / 'before-the-morning-preview.vtt'


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    return f'{milliseconds // 3_600_000:02}:{milliseconds // 60_000 % 60:02}:{milliseconds // 1000 % 60:02}.{milliseconds % 1000:03}'


def main():
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    cues = data['cues']
    if not cues:
        raise ValueError('Caption file has no cues')
    for index, cue in enumerate(cues):
        if not isinstance(cue['text'], str) or not cue['text'].strip():
            raise ValueError(f'Cue {index + 1} has no lyric text')
        if cue['start'] < 0 or cue['end'] <= cue['start']:
            raise ValueError(f'Cue {index + 1} has invalid times')
        if index and cue['start'] < cues[index - 1]['end']:
            raise ValueError(f'Cue {index + 1} overlaps the previous cue')
    vtt = 'WEBVTT\n\nNOTE Draft captions for listening review.\n\n'
    vtt += '\n\n'.join(f"{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}" for c in cues) + '\n'
    VTT.write_text(vtt, encoding='utf-8')

    soup = BeautifulSoup(READER.read_text(encoding='utf-8'), 'html.parser')
    box = soup.select_one('#synchronized-lyrics')
    if box is None:
        raise ValueError('Reading page is missing #synchronized-lyrics')
    box.clear()
    for cue in cues:
        stanza = soup.new_tag('p', attrs={'class': 'lyric-stanza'})
        for index, line in enumerate(cue['text'].split('\n')):
            if index:
                stanza.append(soup.new_tag('br'))
            stanza.append(line)
        box.append(stanza)
    READER.write_text(str(soup), encoding='utf-8')
    print(f'Refreshed {len(cues)} cues in the reading page and WebVTT file.')


if __name__ == '__main__':
    main()
