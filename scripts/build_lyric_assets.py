"""Refresh all acoustic reading lyrics and WebVTT files from the timed JSON.

Run from the repository root: python scripts/build_lyric_assets.py
"""
from pathlib import Path
from bs4 import BeautifulSoup
import json

ROOT = Path(__file__).resolve().parents[1]
CAPTIONS = ROOT / 'captions'


def timestamp(seconds):
    milliseconds = round(seconds * 1000)
    return f'{milliseconds // 3_600_000:02}:{milliseconds // 60_000 % 60:02}:{milliseconds // 1000 % 60:02}.{milliseconds % 1000:03}'


def build(source):
    data = json.loads(source.read_text(encoding='utf-8'))
    recording = Path(data['recording'])
    number = int(recording.stem.split('-', 1)[0])
    reader = ROOT / 'preview-songs' / f'{number:02}.html'
    vtt = source.with_suffix('.vtt')
    cues = data['cues']
    if not cues:
        raise ValueError(f'{source.name} has no cues')
    for index, cue in enumerate(cues):
        if not isinstance(cue['text'], str) or not cue['text'].strip():
            raise ValueError(f'{source.name}: cue {index + 1} has no lyric text')
        if cue['start'] < 0 or cue['end'] <= cue['start']:
            raise ValueError(f'{source.name}: cue {index + 1} has invalid times')
        if index and cue['start'] < cues[index - 1]['end']:
            raise ValueError(f'{source.name}: cue {index + 1} overlaps the previous cue')
    note = 'Verified against the recording.' if 'Verified' in data['status'] else 'Draft captions for listening review.'
    body = '\n\n'.join(f"{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}" for c in cues)
    vtt.write_text(f'WEBVTT\n\nNOTE {note}\n\n{body}\n', encoding='utf-8')

    soup = BeautifulSoup(reader.read_text(encoding='utf-8'), 'html.parser')
    box = soup.select_one('#synchronized-lyrics') or soup.select_one('.lyrics')
    if box is None:
        raise ValueError(f'{reader.name} is missing its lyric container')
    box['id'] = 'synchronized-lyrics'
    box.clear()
    for cue in cues:
        stanza = soup.new_tag('p', attrs={'class': 'lyric-stanza'})
        for index, line in enumerate(cue['text'].split('\n')):
            if index:
                stanza.append(soup.new_tag('br'))
            stanza.append(line)
        box.append(stanza)
    if number > 1 and not soup.select_one('.lyric-draft-note'):
        heading = next((h for h in soup.select('h2') if h.get_text(' ', strip=True) == 'Lyrics'), None)
        if heading is None:
            raise ValueError(f'{reader.name} is missing its Lyrics heading')
        note_tag = soup.new_tag('p', attrs={'class': 'lyric-draft-note'})
        note_tag.string = 'Timed lyrics are a draft and need listening review against this recording.'
        heading.insert_after(note_tag)
    reader.write_text(str(soup), encoding='utf-8')
    return number, len(cues)


def main():
    sources = sorted(CAPTIONS.glob('*.json'))
    built = [build(source) for source in sources]
    if len(built) != 13 or sorted(number for number, _ in built) != list(range(1, 14)):
        raise ValueError('Expected timed lyrics for all 13 tracks')
    print('Refreshed ' + ', '.join(f'{number:02}: {count} cues' for number, count in built))


if __name__ == '__main__':
    main()
