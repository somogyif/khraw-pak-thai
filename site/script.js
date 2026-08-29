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

  // Étlap fülek
  var tabs = document.querySelectorAll('.menu-tab');
  var panels = document.querySelectorAll('.menu-panel');
  tabs.forEach(function(tab){
    tab.addEventListener('click', function(){
      var cat = tab.getAttribute('data-cat');
      tabs.forEach(function(t){ t.classList.toggle('is-active', t === tab); });
      panels.forEach(function(p){ p.classList.toggle('is-active', p.getAttribute('data-cat') === cat); });
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
    document.querySelectorAll('.mi-thumb').forEach(function(t){
      t.setAttribute('role', 'button');
      t.setAttribute('tabindex', '0');
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

  // Nyelvváltás (HU alap, EN a data-en attribútumból)
  // Biztonság: a szöveget nem nyers innerHTML-ként szúrjuk be, hanem szűrve.
  // Csak ez a néhány, nem interaktív tag és a class attribútum engedélyezett;
  // minden más (script, eseménykezelő, külső forrás) eltávolításra kerül.
  var ALLOWED_TAGS = { BR:1, EM:1, STRONG:1, SMALL:1, SPAN:1, B:1, I:1 };
  var ALLOWED_ATTR = { 'class':1 };

  function sanitizeToFragment(markup){
    var tpl = document.createElement('template');
    tpl.innerHTML = markup || '';   // template = inert párszítás: script nem fut, kép nem töltődik
    (function clean(node){
      var child = node.firstChild;
      while(child){
        var next = child.nextSibling;
        if(child.nodeType === 1){                    // elem
          if(ALLOWED_TAGS[child.tagName]){
            for(var i = child.attributes.length - 1; i >= 0; i--){
              var name = child.attributes[i].name;
              if(!ALLOWED_ATTR[name.toLowerCase()]) child.removeAttribute(name);
            }
            clean(child);
          } else {                                   // nem engedélyezett tag → csak a szövege marad
            child.parentNode.replaceChild(document.createTextNode(child.textContent || ''), child);
          }
        } else if(child.nodeType !== 3){             // megjegyzés stb. → el
          child.parentNode.removeChild(child);
        }
        child = next;
      }
    })(tpl.content);
    return tpl.content;
  }

  function setHtmlSafely(el, markup){
    while(el.firstChild) el.removeChild(el.firstChild);
    el.appendChild(sanitizeToFragment(markup));
  }

  var langBtn = document.getElementById('langToggle');
  function setLang(lang){
    document.querySelectorAll('[data-en]').forEach(function(el){
      if(!el.hasAttribute('data-hu')) el.setAttribute('data-hu', el.innerHTML);
      setHtmlSafely(el, (lang === 'en') ? el.getAttribute('data-en') : el.getAttribute('data-hu'));
    });
    // Az attribútumokat (alt, aria-label) a data-en nem érinti — külön kell váltani,
    // különben angol nézetben magyarul maradna a képek szöveges alternatívája.
    document.querySelectorAll('[alt],[aria-label]').forEach(function(el){
      ['alt','aria-label'].forEach(function(a){
        var en = el.getAttribute('data-en-' + a);
        if(en === null) return;
        if(!el.hasAttribute('data-hu-' + a)) el.setAttribute('data-hu-' + a, el.getAttribute(a) || '');
        el.setAttribute(a, (lang === 'en') ? en : el.getAttribute('data-hu-' + a));
      });
    });
    document.documentElement.lang = (lang === 'en') ? 'en' : 'hu';
    if(langBtn) langBtn.textContent = (lang === 'en') ? 'HU' : 'EN';
    if(langBtn){ try{ localStorage.setItem('kpt-lang', lang); }catch(e){} }
    updateOpen(lang);
  }
  // Az /en/ oldal önálló, angolul generált dokumentum: ott nincs nyelvváltó gomb,
  // és a mentett választás NEM írhatja felül a dokumentum saját nyelvét — különben
  // az angol oldal lang="hu"-t kapna, és a nyitvatartás is magyarul jelenne meg.
  var pageLang = (document.documentElement.lang === 'en') ? 'en' : 'hu';
  if(langBtn){
    try{ pageLang = localStorage.getItem('kpt-lang') || pageLang; }catch(e){}
    langBtn.addEventListener('click', function(){
      var next = (document.documentElement.lang === 'en') ? 'hu' : 'en';
      setLang(next);
    });
  }
  setLang(pageLang);
})();
