(()=>{
'use strict';
const root=document.querySelector('#album-player');if(!root)return;
const audio=root.querySelector('audio'),status=document.querySelector('#now-playing'),toggle=root.querySelector('[data-action=playpause]');
const buttons=[...document.querySelectorAll('.play-track')],windowText=document.querySelector('#lyric-window'),stageTitle=document.querySelector('#stage-title'),stageVersion=document.querySelector('#stage-version'),stageLabel=document.querySelector('#stage-label'),reader=document.querySelector('#stage-reader'),seek=document.querySelector('#seek'),clock=document.querySelector('#time-readout'),error=document.querySelector('#play-error');
let current=-1,cues=[],lastText='',requestId=0,loading=false;
const time=s=>{s=Number.isFinite(s)?Math.max(0,s):0;return Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0')};
function showText(text){if(text===lastText)return;lastText=text;windowText.replaceChildren();const p=document.createElement('p');text.split('\n').forEach((line,i)=>{if(i)p.append(document.createElement('br'));p.append(document.createTextNode(line))});windowText.append(p)}
function updateLyrics(){if(current<0)return;if(loading){showText('Loading lyrics…');return}if(!cues.length){showText('The timed lyrics could not be loaded.\nYou can still listen to the album.');return}const cue=cues.find(c=>audio.currentTime>=c.start&&audio.currentTime<c.end);showText(cue?cue.text:'Instrumental')}
function updateTime(){const duration=Number.isFinite(audio.duration)?audio.duration:0;seek.max=duration||100;seek.value=Math.min(audio.currentTime||0,duration||100);clock.textContent=time(audio.currentTime)+' / '+time(duration);seek.setAttribute('aria-valuetext',time(audio.currentTime)+' of '+time(duration));updateLyrics()}
function updateToggle(){const playing=!audio.paused&&!audio.ended;toggle.textContent=playing?'Pause':'Play';buttons.forEach((b,i)=>{b.closest('.song-row').classList.toggle('is-playing',i===current);const marker=b.closest('.song-row').querySelector('.playing-marker');marker.hidden=i!==current;marker.textContent=playing?'Now playing':'Selected'})}
async function play(){try{await audio.play();error.hidden=true}catch(e){if(e.name==='AbortError')return;error.textContent='Playback was interrupted. Use Play to continue.';error.hidden=false}}
async function load(i){if(i<0||i>=buttons.length)return;const token=++requestId;current=i;const b=buttons[i];const original=document.body.dataset.edition==='original';cues=[];loading=true;audio.src=b.dataset.src;status.textContent='Now playing: '+b.dataset.title;document.title=b.dataset.title+' | A Series of Joyful Noises';stageTitle.textContent=original?b.dataset.title:i===0?'Before the Morning':b.dataset.title;stageVersion.textContent=original?'Original Electronic Edition':i===0?'Gentle Slide Remix':'Acoustic and Worship Edition';stageLabel.textContent='Track '+String(i+1).padStart(2,'0')+' of 13';reader.href=(original?'original-songs/':'preview-songs/')+String(i+1).padStart(2,'0')+'.html';error.hidden=true;showText('Loading lyrics…');updateToggle();play();try{const response=await fetch(b.dataset.captions,{cache:'no-store'});if(!response.ok)throw Error('Captions unavailable');const data=await response.json();if(token!==requestId)return;cues=data.cues;loading=false;updateLyrics()}catch{if(token===requestId){loading=false;showText('The timed lyrics could not be loaded.\nYou can still listen to the album.')}}}
buttons.forEach((b,i)=>b.addEventListener('click',()=>load(i)));
root.querySelector('[data-action=previous]').addEventListener('click',()=>load(Math.max(0,current-1)));
root.querySelector('[data-action=rewind]').addEventListener('click',()=>{audio.currentTime=Math.max(0,audio.currentTime-15);updateTime()});
toggle.addEventListener('click',()=>{if(current<0)load(0);else if(audio.paused)play();else audio.pause()});
root.querySelector('[data-action=next]').addEventListener('click',()=>load(Math.min(buttons.length-1,current+1)));
seek.addEventListener('input',()=>{if(Number.isFinite(audio.duration)){audio.currentTime=Number(seek.value);updateTime()}});
for(const event of ['timeupdate','seeked','loadedmetadata'])audio.addEventListener(event,updateTime);
for(const event of ['play','pause'])audio.addEventListener(event,updateToggle);
audio.addEventListener('ended',()=>{updateToggle();if(current<buttons.length-1)load(current+1)});
audio.addEventListener('error',()=>{error.textContent='This recording could not be loaded. Try Play again or choose another song.';error.hidden=false});
function sizeDock(){const height=root.getBoundingClientRect().height;document.body.classList.toggle('player-static',height>window.innerHeight*.45);document.documentElement.style.setProperty('--player-space',(height+24)+'px')}
new ResizeObserver(sizeDock).observe(root);window.addEventListener('resize',sizeDock);sizeDock();
})();
