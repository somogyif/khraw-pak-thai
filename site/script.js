/* ===== Khraw Pak Thai – interakciók ===== */
(function(){
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');

  // Mobil menü
  if(toggle){
    toggle.addEventListener('click', function(){
      var open = header.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    header.querySelectorAll('.mobile-nav a').forEach(function(a){
      a.addEventListener('click', function(){
        header.classList.remove('open');
        toggle.setAttribute('aria-expanded','false');
      });
    });
  }

  // Étlap fülek — a markup tab szerepet hirdet, tehát teljesíteni is kell:
  // aria-selected, egyetlen tabstop, és nyílbillentyűs léptetés (WAI-ARIA tabs).
  var tabs = Array.prototype.slice.call(document.querySelectorAll('.menu-tab'));
  var panels = document.querySelectorAll('.menu-panel');
  function selectTab(tab, moveFocus){
    var cat = tab.getAttribute('data-cat');
    tabs.forEach(function(t){
      var on = t === tab;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.setAttribute('tabindex', on ? '0' : '-1');   // egy fül, egy tabstop
    });
    panels.forEach(function(p){ p.classList.toggle('is-active', p.getAttribute('data-cat') === cat); });
    if(moveFocus) tab.focus();
  }
  tabs.forEach(function(tab, i){
    tab.addEventListener('click', function(){ selectTab(tab, false); });
    tab.addEventListener('keydown', function(e){
      var to = null;
      if(e.key === 'ArrowRight' || e.key === 'ArrowDown') to = tabs[(i + 1) % tabs.length];
      else if(e.key === 'ArrowLeft' || e.key === 'ArrowUp') to = tabs[(i - 1 + tabs.length) % tabs.length];
      else if(e.key === 'Home') to = tabs[0];
      else if(e.key === 'End') to = tabs[tabs.length - 1];
      if(to){ e.preventDefault(); selectTab(to, true); }
    });
  });

  // Nyitva / zárva állapot – kétnyelvű
  function updateOpen(lang){
    var el = document.getElementById('openNow');
    if(!el) return;
    // Budapesti idő szerint (a látogató időzónájától függetlenül)
    var h;
    try {
      var parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Budapest', hour12: false, hour: '2-digit' }).formatToParts(new Date());
      h = parseInt(parts.find(function(p){ return p.type === 'hour'; }).value, 10);
    } catch(e) {
      h = new Date().getHours();
    }
    var open = h >= 11 && h < 22;
    if(lang === 'en'){
      el.textContent = open ? '● Open now – until 22:00' : '● Currently closed – opens at 11:00';
    } else {
      el.textContent = open ? '● Most nyitva – 22:00-ig' : '● Jelenleg zárva – nyitás 11:00-kor';
    }
    el.classList.remove('is-open','is-closed');
    el.classList.add(open ? 'is-open' : 'is-closed');
  }

  // Kép nagyító (lightbox) a menü bélyegképeihez
  var lb = document.getElementById('lightbox');
  if(lb){
    var lbImg = lb.querySelector('img');
    var lbCap = lb.querySelector('.lb-cap');
    var lbClose = lb.querySelector('.lb-close');
    var lastFocused = null;
    function openLb(src, cap){
      lastFocused = document.activeElement;
      lbImg.src = src; lbImg.alt = cap || '';
      lbCap.textContent = cap || '';
      lb.classList.add('open'); lb.setAttribute('aria-hidden','false');
      if(lbClose) lbClose.focus();          // a fókusz a panelbe kerül
    }
    function closeLb(){
      if(!lb.classList.contains('open')) return;
      lb.classList.remove('open'); lb.setAttribute('aria-hidden','true');
      lbImg.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
      if(lastFocused && lastFocused.focus) lastFocused.focus();   // vissza oda, ahonnan jött
    }
    // A bélyegkép <img>, tehát alapból nem fókuszálható: gombbá tesszük, hogy
    // billentyűzettel is meg lehessen nyitni. Csak itt, JS-ből — JS nélkül
    // nincs nagyító, és akkor ne is látsszon gombnak.
    var openLabel = document.documentElement.lang === 'en'
      ? 'Open photo: ' : 'Fénykép megnyitása: ';
    document.querySelectorAll('.mi-thumb').forEach(function(t){
      t.setAttribute('role', 'button');
      t.setAttribute('tabindex', '0');
      // A gomb neve mondja meg, mit csinál — az alt egyedül csak a szomszédos
      // sort ismételné meg a képernyőolvasónak.
      t.setAttribute('aria-label', openLabel + (t.alt || ''));
      function open(){ openLb(t.getAttribute('data-full') || t.src, t.alt); }
      t.addEventListener('click', open);
      t.addEventListener('keydown', function(e){
        if(e.key === 'Enter' || e.key === ' '){ e.preventDefault(); open(); }
      });
    });
    lb.addEventListener('click', function(e){ if(e.target !== lbImg) closeLb(); });
    document.addEventListener('keydown', function(e){
      if(e.key === 'Escape'){ closeLb(); return; }
      // Amíg nyitva van, a Tab ne vigye ki a fókuszt a panel mögé.
      if(e.key === 'Tab' && lb.classList.contains('open')){ e.preventDefault(); if(lbClose) lbClose.focus(); }
    });
    if(lbClose) lbClose.addEventListener('click', closeLb);
  }

  // Térkép betöltése csak kérésre — így a Google addig nem kap adatot,
  // és nincs szükség cookie-bannerre.
  var facade = document.getElementById('mapFacade');
  var mapBtn = document.getElementById('mapLoad');
  if (facade && mapBtn) {
    mapBtn.addEventListener('click', function () {
      var frame = document.createElement('iframe');
      frame.title = document.documentElement.lang === 'en'
        ? 'Khraw Pak Thai on the map' : 'Khraw Pak Thai a térképen';
      frame.src = facade.getAttribute('data-src');
      frame.loading = 'lazy';
      frame.referrerPolicy = 'no-referrer-when-downgrade';
      frame.setAttribute('allowfullscreen', '');
      // A térkép idegen tartalom: csak annyit engedünk neki, amennyi a működéséhez kell.
      frame.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox');
      facade.replaceWith(frame);
    });
  }

  // Nyelv: a dokumentum sajátja, és kész. A magyar oldal / , az angol /en/ —
  // két külön, generált dokumentum, a váltó mindkét irányban sima link.
  // Nincs futásidejű fordítás, nincs innerHTML, nincs böngészőben tárolt adat.
  updateOpen(document.documentElement.lang === 'en' ? 'en' : 'hu');
})();
