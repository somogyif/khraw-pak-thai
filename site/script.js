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
    function openLb(src, cap){
      lbImg.src = src; lbImg.alt = cap || '';
      lbCap.textContent = cap || '';
      lb.classList.add('open'); lb.setAttribute('aria-hidden','false');
    }
    function closeLb(){ lb.classList.remove('open'); lb.setAttribute('aria-hidden','true'); lbImg.src=''; }
    document.querySelectorAll('.mi-thumb').forEach(function(t){
      t.addEventListener('click', function(){ openLb(t.src, t.getAttribute('data-cap')); });
    });
    lb.addEventListener('click', function(e){ if(e.target !== lbImg) closeLb(); });
    document.addEventListener('keydown', function(e){ if(e.key === 'Escape') closeLb(); });
  }

  // Nyelvváltás (HU alap, EN a data-en attribútumból)
  var langBtn = document.getElementById('langToggle');
  function setLang(lang){
    document.querySelectorAll('[data-en]').forEach(function(el){
      if(!el.hasAttribute('data-hu')) el.setAttribute('data-hu', el.innerHTML);
      el.innerHTML = (lang === 'en') ? el.getAttribute('data-en') : el.getAttribute('data-hu');
    });
    document.documentElement.lang = (lang === 'en') ? 'en' : 'hu';
    if(langBtn) langBtn.textContent = (lang === 'en') ? 'HU' : 'EN';
    try{ localStorage.setItem('kpt-lang', lang); }catch(e){}
    updateOpen(lang);
  }
  var saved = 'hu';
  try{ saved = localStorage.getItem('kpt-lang') || 'hu'; }catch(e){}
  if(langBtn){
    langBtn.addEventListener('click', function(){
      var next = (document.documentElement.lang === 'en') ? 'hu' : 'en';
      setLang(next);
    });
  }
  setLang(saved);
})();
