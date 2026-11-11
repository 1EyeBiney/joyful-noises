(() => {
  'use strict';
  const key = 'asojn-favorite-recordings';
  const editor = document.querySelector('#favorite-editor');
  const list = document.querySelector('#saved-list');
  const status = document.querySelector('#favorite-status');
  const mode = new URLSearchParams(location.search).get('edit');
  const inputs = [...editor.querySelectorAll('input')];

  function readFavorites() {
    const records = JSON.parse(localStorage.getItem(key) || '[]');
    return new Set(Array.isArray(records) ? records : []);
  }

  function syncEditor() {
    const saved = readFavorites();
    for (const input of inputs) input.checked = saved.has(input.value);
  }

  try {
    if (mode) {
      document.querySelector('#album-player').remove();
      const groups = [...editor.querySelectorAll('fieldset')];
      const group = groups.find(item => item.dataset.album === mode);
      for (const item of groups) item.hidden = !!group && item !== group;
      document.querySelector('h1').textContent = group ? 'Choose favorites' : 'Edit favorites';
      document.querySelector('#favorite-help').textContent = 'Check a song to save it. Uncheck it to remove it. Each change is saved in this browser.';
      const link = document.querySelector('#favorite-link');
      link.href = 'favorites.html';
      link.textContent = 'Play favorites';
      syncEditor();
      editor.hidden = false;
      editor.addEventListener('change', event => {
        const input = event.target;
        try {
          const saved = readFavorites();
          if (input.checked) saved.add(input.value);
          else saved.delete(input.value);
          localStorage.setItem(key, JSON.stringify([...saved]));
          status.textContent = saved.size + (saved.size === 1 ? ' favorite saved.' : ' favorites saved.');
        } catch {
          input.checked = !input.checked;
          status.textContent = 'This browser could not save that change.';
        }
      });
      window.addEventListener('storage', event => {
        if (event.key === key || event.key === null) syncEditor();
      });
    } else {
      const saved = readFavorites();
      for (const row of list.querySelectorAll('[data-recording]')) {
        if (!saved.has(row.dataset.recording)) row.remove();
      }
      for (const section of list.querySelectorAll('section')) {
        if (!section.querySelector('.play-track')) section.remove();
      }
      if (list.querySelector('.play-track')) list.hidden = false;
      else {
        document.querySelector('#album-player').remove();
        status.textContent = 'Your list is empty. Choose Edit favorites to add songs.';
      }
    }
    window.addEventListener('pageshow', event => {
      if (event.persisted) location.reload();
    });
  } catch {
    document.querySelector('#album-player')?.remove();
    status.textContent = 'Favorites storage is unavailable in this browser.';
  }
})();
