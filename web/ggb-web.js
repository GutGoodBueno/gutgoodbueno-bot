/* Gut Good Bueno · bloques dinámicos de gutgoodbueno.com
   Pinta la agenda (#ggb-proximas) y las tarjetas de experiencias (#ggb-experiencias)
   a partir de web/eventos.json y web/experiencias.json de este repositorio. */
(function () {
  if (window.__ggbWeb) return;
  window.__ggbWeb = true;

  var RAW = 'https://raw.githubusercontent.com/GutGoodBueno/gutgoodbueno-bot/main/web/';
  var WA = 'https://wa.me/34659947793?text=';
  var MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var stamp = Math.floor(Date.now() / 6e5); // refresco cada 10 min

  var css = '' +
    '.ggb{--ggb-card:#18181d;--ggb-line:rgba(255,255,255,.12);--ggb-text:#f4f1ec;--ggb-mute:#b9b4ac;--ggb-accent:#e2a03f;font-family:Inter,system-ui,sans-serif;color:var(--ggb-text);max-width:1100px;margin:0 auto;padding:8px 4px;text-align:left}' +
    '.ggb *{box-sizing:border-box}' +
    '.ggb-head{text-align:center;margin-bottom:26px}' +
    '.ggb-kicker{letter-spacing:.3em;text-transform:uppercase;font-size:12px;color:var(--ggb-accent);margin:0 0 8px}' +
    '.ggb-title{font-family:"Dela Gothic One",Inter,sans-serif;font-weight:400;font-size:clamp(24px,4vw,36px);letter-spacing:.06em;text-transform:uppercase;margin:0 0 10px;color:#fff;line-height:1.15}' +
    '.ggb-lead{color:var(--ggb-mute);font-size:15px;line-height:1.5;margin:0 auto;max-width:560px}' +
    '.ggb-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:20px}' +
    '.ggb-card{background:var(--ggb-card);border:1px solid var(--ggb-line);border-radius:14px;overflow:hidden;display:flex;flex-direction:column;transition:transform .2s,box-shadow .2s}' +
    '.ggb-card:hover{transform:translateY(-3px);box-shadow:0 12px 30px rgba(0,0,0,.45)}' +
    '.ggb-media{display:block;position:relative;background:#000;overflow:hidden}' +
    '.ggb-media img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .4s}' +
    '.ggb-card:hover .ggb-media img{transform:scale(1.04)}' +
    '.ggb-media.is-photo{aspect-ratio:3/2}' +
    '.ggb-media.is-poster{aspect-ratio:3/4}' +
    '.ggb-media.is-poster img{object-position:top}' +
    '.ggb-chip{position:absolute;left:12px;bottom:12px;background:rgba(15,15,18,.82);color:#fff;font-size:11px;letter-spacing:.12em;text-transform:uppercase;padding:6px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.25)}' +
    '.ggb-date{position:absolute;top:12px;left:12px;background:var(--ggb-accent);color:#141414;border-radius:10px;padding:6px 10px;text-align:center;line-height:1;font-weight:700;box-shadow:0 4px 14px rgba(0,0,0,.4)}' +
    '.ggb-date b{display:block;font-size:22px}.ggb-date span{font-size:11px;text-transform:uppercase;letter-spacing:.08em}' +
    '.ggb-body{padding:16px 18px 18px;display:flex;flex-direction:column;gap:8px;flex:1}' +
    '.ggb-tag{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ggb-accent);margin:0}' +
    '.ggb-body h3{margin:0;font-size:18px;line-height:1.25;color:#fff;font-weight:700;letter-spacing:0;text-transform:none}' +
    '.ggb-body p{margin:0;color:var(--ggb-mute);font-size:14px;line-height:1.45;letter-spacing:0;text-transform:none}' +
    '.ggb-body .ggb-data{color:var(--ggb-text);font-size:12.5px}' +
    '.ggb-meta{list-style:none;margin:2px 0 0;padding:0;font-size:13.5px;line-height:1.5;color:var(--ggb-text)}' +
    '.ggb-meta li{padding-left:16px;position:relative}.ggb-meta li:before{content:"·";position:absolute;left:5px;color:var(--ggb-accent);font-weight:700}' +
    '.ggb-foot{margin-top:auto;padding-top:10px;display:flex;align-items:center;justify-content:space-between;gap:10px}' +
    '.ggb-price{font-size:20px;font-weight:700;color:#fff;white-space:nowrap}' +
    '.ggb-price small{font-size:11px;font-weight:500;color:var(--ggb-mute);text-transform:uppercase;letter-spacing:.1em;margin-right:3px}' +
    '.ggb-btn{display:inline-block;background:var(--ggb-accent);color:#141414!important;text-decoration:none!important;font-weight:700;font-size:13px;letter-spacing:.06em;text-transform:uppercase;padding:11px 16px;border-radius:999px;white-space:nowrap;transition:transform .15s,background .15s}' +
    '.ggb-btn:hover{transform:translateY(-1px);background:#f0b55a}' +
    '.ggb-btn.is-line{background:transparent;color:var(--ggb-accent)!important;border:1.5px solid var(--ggb-accent)}' +
    '.ggb-btn.is-line:hover{background:rgba(226,160,63,.12)}' +
    '.ggb-private{margin-top:22px;border:1px solid var(--ggb-line);border-radius:14px;padding:18px 20px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;background:linear-gradient(90deg,rgba(226,160,63,.14),rgba(226,160,63,0))}' +
    '.ggb-private b{display:block;color:#fff;font-size:16px;margin-bottom:4px}.ggb-private span{color:var(--ggb-mute);font-size:14px}' +
    '.ggb-empty{grid-column:1/-1;text-align:center;color:var(--ggb-mute);font-size:15px;margin:0}';

  function addCss() {
    if (document.getElementById('ggb-web-css')) return;
    var s = document.createElement('style');
    s.id = 'ggb-web-css';
    s.textContent = css;
    document.head.appendChild(s);
  }

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function hoy() {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }

  function getJSON(name) {
    return fetch(RAW + name + '?v=' + stamp).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    });
  }

  function proximas(el) {
    el.className = 'ggb';
    el.innerHTML =
      '<div class="ggb-head"><p class="ggb-kicker">Agenda</p><h2 class="ggb-title">Próximas actividades</h2>' +
      '<p class="ggb-lead">Rutas, charlas y excursiones con fecha. Plazas limitadas: reserva por WhatsApp.</p></div>' +
      '<div class="ggb-grid"><p class="ggb-empty">Cargando agenda…</p></div>';
    var grid = el.querySelector('.ggb-grid');
    getJSON('eventos.json').then(function (data) {
      var t = hoy();
      var ev = (data.eventos || []).filter(function (e) { return (e.fecha_fin || e.fecha) >= t; })
        .sort(function (a, b) { return a.fecha < b.fecha ? -1 : 1; });
      if (!ev.length) {
        grid.innerHTML = '<p class="ggb-empty">Estamos preparando nuevas fechas. Síguenos en Instagram o escríbenos por WhatsApp para enterarte antes que nadie.</p>';
        return;
      }
      grid.innerHTML = ev.map(function (e) {
        var p = e.fecha.split('-');
        var img = /^https?:/.test(e.cartel) ? e.cartel : RAW + e.cartel;
        var msg = encodeURIComponent('Hola, quiero reservar: ' + e.titulo + ' (' + (e.dia || e.fecha) + ')');
        var meta = '';
        if (e.dia) meta += '<li>' + esc(e.dia) + (e.hora ? ', ' + esc(e.hora) : '') + '</li>';
        if (e.lugar) meta += '<li>' + esc(e.lugar) + '</li>';
        if (e.incluye) meta += '<li>' + esc(e.incluye) + '</li>';
        return '<article class="ggb-card">' +
          '<a class="ggb-media is-poster" href="' + esc(img) + '" target="_blank" rel="noopener" aria-label="Ver cartel de ' + esc(e.titulo) + '">' +
          '<img src="' + esc(img) + '" alt="Cartel: ' + esc(e.titulo) + '" loading="lazy">' +
          '<div class="ggb-date"><b>' + parseInt(p[2], 10) + '</b><span>' + MESES[parseInt(p[1], 10) - 1] + '</span></div></a>' +
          '<div class="ggb-body"><p class="ggb-tag">' + esc(e.tipo) + '</p><h3>' + esc(e.titulo) + '</h3>' +
          (e.subtitulo ? '<p>' + esc(e.subtitulo) + '</p>' : '') +
          '<ul class="ggb-meta">' + meta + '</ul>' +
          '<div class="ggb-foot"><span class="ggb-price">' + esc(e.precio) + '</span>' +
          '<a class="ggb-btn" href="' + WA + msg + '" target="_blank" rel="noopener">Reservar</a></div></div></article>';
      }).join('');
    }).catch(function () {
      grid.innerHTML = '<p class="ggb-empty">No hemos podido cargar la agenda. Escríbenos por WhatsApp al 659 947 793.</p>';
    });
  }

  function experiencias(el) {
    el.className = 'ggb';
    el.innerHTML = '<div class="ggb-grid"><p class="ggb-empty">Cargando experiencias…</p></div>';
    var grid = el.querySelector('.ggb-grid');
    getJSON('experiencias.json').then(function (data) {
      grid.innerHTML = (data.experiencias || []).map(function (x) {
        return '<article class="ggb-card">' +
          '<a class="ggb-media is-photo" href="' + esc(x.enlace) + '" target="_blank" rel="noopener">' +
          '<img src="' + esc(x.imagen) + '" alt="' + esc(x.alt || x.titulo) + '" loading="lazy"><span class="ggb-chip">' + esc(x.etiqueta) + '</span></a>' +
          '<div class="ggb-body"><h3>' + esc(x.titulo) + '</h3><p>' + esc(x.texto) + '</p>' +
          '<p class="ggb-data">' + esc(x.datos) + '</p>' +
          '<div class="ggb-foot"><span class="ggb-price">' + (x.precio_prefijo ? '<small>' + esc(x.precio_prefijo) + '</small>' : '') + esc(x.precio) + '</span>' +
          '<a class="ggb-btn" href="' + esc(x.enlace) + '" target="_blank" rel="noopener">' + esc(x.boton || 'Reservar') + '</a></div></div></article>';
      }).join('');
      if (data.privado) {
        var pv = data.privado;
        var box = document.createElement('div');
        box.className = 'ggb-private';
        box.innerHTML = '<div><b>' + esc(pv.titulo) + '</b><span>' + esc(pv.texto) + '</span></div>' +
          '<a class="ggb-btn is-line" href="' + esc(pv.enlace) + '" target="_blank" rel="noopener">' + esc(pv.boton) + '</a>';
        el.appendChild(box);
      }
    }).catch(function () {
      grid.innerHTML = '<p class="ggb-empty">Consulta nuestras rutas en GetYourGuide o escríbenos por WhatsApp al 659 947 793.</p>';
    });
  }

  function init() {
    addCss();
    var a = document.getElementById('ggb-proximas');
    if (a) proximas(a);
    var b = document.getElementById('ggb-experiencias');
    if (b) experiencias(b);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
