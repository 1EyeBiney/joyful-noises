"""Build the original-edition album and reading pages from the archived long page."""
from copy import deepcopy
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
archive = ROOT / 'scripts' / 'original-long-page.txt'
source = BeautifulSoup((archive if archive.exists() else ROOT / 'original.html').read_text(encoding='utf-8'), 'html.parser')
acoustic = BeautifulSoup((ROOT / 'acoustic.html').read_text(encoding='utf-8'), 'html.parser')
reader_template = BeautifulSoup((ROOT / 'preview-songs' / '02.html').read_text(encoding='utf-8'), 'html.parser')
articles = source.select('article.track')
assert len(articles) == 13
blurbs = [
    'Praise can begin before circumstances improve because God is faithful through the night.',
    'God remains near to weary hearts and breathes life into what feels dry.',
    'Jesus calls us by name and invites us to follow before we see the whole road.',
    'Nothing can separate believers from God’s love in Christ.',
    'Jesus remains faithful while plans and circumstances change.',
    'Learn to hear Jesus’ voice through the noise and follow Him.',
    'When the world shakes, God calls us to be still and remember who He is.',
    'Come honestly to Jesus and receive His rest, mercy, and grace.',
    'The same hands that made creation touched the rejected, served, were pierced, and hold us securely.',
    'The risen Jesus gives living hope today and a future resurrection.',
    'Christ lives in believers, shaping how we love and serve in ordinary life.',
    'Jesus is the Way; we ask Him to make His love visible through us.',
    'Praise the risen Jesus through present pain, with hope of life with Him forever.',
]

# Keep the existing original page as the source of its song descriptions, Scripture,
# reflections, and lyrics. Running this script after replacement requires that archive.
if not archive.exists():
    archive.write_text(str(source), encoding='utf-8')

page = deepcopy(acoustic)
page.body['class'] = ['lyric-preview', 'original-edition']
page.body['data-edition'] = 'original'
page.select_one('link[href^="css/lyric-preview.css"]')['href'] = 'css/lyric-preview.css?v=5'
page.select_one('script[src^="js/lyric-preview.js"]')['src'] = 'js/lyric-preview.js?v=6'
page.title.string = 'Original electronic album | A Series of Joyful Noises'
page.select_one('.site-header a[href="acoustic.html"]').attrs.pop('aria-current', None)
page.select_one('.site-header a[href="original.html"]')['aria-current'] = 'page'
intro = page.select_one('.album-intro')
intro.select_one('.eyebrow').string = 'Original Electronic Edition'
intro.h1.string = 'Turn it up.'
intro.select_one('p:not(.eyebrow)').string = 'Progressive trance, electronic textures, and breakbeats carry these songs with motion and release.'
intro.select_one('a[download]')['href'] = 'downloads/a-series-of-joyful-noises-original.zip'
stage = page.select_one('.listening-stage')
stage.img['src'] = 'images/original-cover.png'
stage.img['alt'] = 'Golden sunrise over dark blue water beneath dramatic purple clouds.'
stage.select_one('#stage-title').string = 'Before the Morning'
stage.select_one('#stage-version').string = 'Original Electronic Edition'
stage.select_one('.caption-note').string = 'Timed lyrics are drafts awaiting listening review.'
stage.select_one('#stage-reader')['href'] = 'original-songs/01.html'
playlist = page.select_one('.playlist')
playlist.select_one('#track-list').string = 'The original album'
playlist.select_one('.playlist-heading p').string = '13 songs · about 72 minutes'
song_list = playlist.select_one('.song-list')
song_list.clear()
reader_dir = ROOT / 'original-songs'
reader_dir.mkdir(exist_ok=True)

for number, article in enumerate(articles, 1):
    title = article.h2.get_text(' ', strip=True)
    description = blurbs[number-1]
    old_button = article.select_one('.play-track')
    recording = old_button['data-src']
    slug = Path(recording).stem
    row = BeautifulSoup(f'<li class="song-row" id="track-{number}"></li>', 'html.parser').li
    number_tag = page.new_tag('div', attrs={'class': 'song-number', 'aria-hidden': 'true'})
    number_tag.string = f'{number:02}'
    row.append(number_tag)
    copy = page.new_tag('div', attrs={'class': 'song-copy'})
    heading = page.new_tag('h3')
    hidden = page.new_tag('span', attrs={'class': 'sr-only'})
    hidden.string = f'Track {number}: '
    heading.append(hidden)
    heading.append(title)
    copy.append(heading)
    blurb = page.new_tag('p')
    blurb.string = description
    copy.append(blurb)
    links = page.new_tag('div', attrs={'class': 'song-links'})
    link = page.new_tag('a', href=f'original-songs/{number:02}.html', target='_blank', rel='noopener')
    link.append('Lyrics and story')
    sr = page.new_tag('span', attrs={'class': 'sr-only'})
    sr.string = f' for {title} (opens a new tab)'
    link.append(sr)
    links.append(link)
    link = page.new_tag('a', href=recording, download='')
    link.append('Download MP3')
    sr = page.new_tag('span', attrs={'class': 'sr-only'})
    sr.string = f' of {title}'
    link.append(sr)
    links.append(link)
    marker = page.new_tag('span', attrs={'class': 'playing-marker', 'hidden': ''})
    marker.string = 'Now playing'
    links.append(marker)
    copy.append(links)
    row.append(copy)
    button = page.new_tag('button', attrs={'type': 'button', 'class': 'play-track', 'data-index': str(number-1),
                                           'data-src': recording, 'data-captions': f'captions/original/{slug}.json',
                                           'data-title': title})
    icon = page.new_tag('span', attrs={'aria-hidden': 'true'})
    icon.string = '▶ '
    button.append(icon)
    button.append('Play')
    sr = page.new_tag('span', attrs={'class': 'sr-only'})
    sr.string = f' {title}'
    button.append(sr)
    row.append(button)
    song_list.append(row)

    reader = deepcopy(reader_template)
    reader.body['class'] = ['lyric-preview', 'reader-page', 'original-edition']
    reader.select_one('link[href^="../css/lyric-preview.css"]')['href'] = '../css/lyric-preview.css?v=5'
    reader.title.string = f'{title} | Original album lyrics'
    reader.select_one('.site-header .brand')['href'] = '../original.html'
    reader.select_one('main > .eyebrow').string = 'Original Electronic Edition'
    reader_article = deepcopy(article)
    reader_article.h2.name = 'h1'
    listen = next(h for h in reader_article.select('h3') if h.get_text(' ', strip=True) == 'Listen')
    listen.find_next_sibling('p').decompose()
    listen.decompose()
    for heading in reader_article.select('h3'):
        heading.name = 'h2'
    for heading in reader_article.select('h4'):
        heading.name = 'h3'
    back = reader_article.select_one('a[href="#track-list-title"]')
    if back:
        back.parent.decompose()
    lyrics_heading = next(h for h in reader_article.select('h2') if h.get_text(' ', strip=True) == 'Lyrics')
    note = reader.new_tag('p', attrs={'class': 'lyric-draft-note'})
    note.string = 'Timed lyrics are a draft and need listening review against this recording.'
    lyrics_heading.insert_after(note)
    reader_article.select_one('.lyrics')['id'] = 'synchronized-lyrics'
    reader.select_one('main article.track').replace_with(reader_article)
    for link in reader.select('a[href^="../acoustic.html"]'):
        link['href'] = '../original.html'
    (reader_dir / f'{number:02}.html').write_text(str(reader), encoding='utf-8')

story = page.select_one('#collection-story')
story.select_one('summary').string = 'How the original album came together'
body = story.select_one('.story-body')
body.clear()
for paragraph in source.select_one('.collection-story').select('p'):
    body.append(deepcopy(paragraph))
(ROOT / 'original.html').write_text(str(page), encoding='utf-8')
print('Built original album layout and 13 reading pages.')
