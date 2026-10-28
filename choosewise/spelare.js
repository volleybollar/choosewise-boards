/* =====================================================================
   SPELAREN för Choosewise-boards (förhandsvisning i webbläsaren)

   Varje board bygger en GSAP-tidslinje och lämnar den till Tavla.start().
   Spelaren:
   - skalar boarden så att den får plats i fönstret,
   - visar en startknapp (webbläsaren spelar bara ljud efter ett klick),
   - spelar ljuden på rätt tid och sparar dem i en lista, så att exporten
     senare kan lägga samma ljud i filmen,
   - tangenter: mellanslag spelar om, K visar eller döljer kamerazonen.
   ===================================================================== */

window.Tavla = (function () {
  // Ljudkartan: samma filer och nivåer som Choosewise i grafikramverket
  // (AI-OS/brands/choosewise/grafik/ljud.json). 1 = oförändrad nivå.
  var LJUD = {
    landa:  { fil: 'klick.wav',   niva: 0.35 },  // ett tal eller märke landar
    skriv:  { fil: 'tangent.wav', niva: 0.51 },  // text skrivs fram
    lager:  { fil: 'lager.wav',   niva: 0.22 },  // ett lager dras isär
    glid:   { fil: 'sus.wav',     niva: 0.29 }   // något färdas en lång sträcka
  };
  var ljudmapp = '../ljud/';
  var ljudlista = [];  // [{ tid, ljud }] för exporten

  // Lägger ett ljud på tidslinjen vid en viss tid (sekunder).
  function ljud(tl, tid, namn) {
    ljudlista.push({ tid: tid, ljud: namn });
    tl.call(function () {
      var l = LJUD[namn];
      var a = new Audio(ljudmapp + l.fil);
      a.volume = l.niva;
      a.play().catch(function () {});
    }, null, tid);
  }

  // Skalar boarden (1920 × 1080) så att den ryms i fönstret.
  function skala() {
    var s = Math.min(innerWidth / 1920, innerHeight / 1080);
    var b = document.querySelector('.cw');
    b.style.transform = 'scale(' + s + ')';
    b.style.transformOrigin = '0 0';
    document.body.style.width = 1920 * s + 'px';
    document.body.style.height = 1080 * s + 'px';
  }

  function start(tl) {
    window.tavla = { tl: tl, ljud: ljudlista };  // exporten läser härifrån
    document.body.style.margin = '0';
    document.body.style.background = '#000';
    addEventListener('resize', skala);
    skala();

    // Kamerazonen syns i förhandsvisningen.
    var zon = document.createElement('div');
    zon.className = 'kamerazon';
    zon.textContent = 'Borumi';
    document.querySelector('.cw').appendChild(zon);

    // Startknappen.
    var knapp = document.createElement('button');
    knapp.textContent = '▶ Spela med ljud';
    knapp.style.cssText = 'position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);' +
      'font:600 28px -apple-system,sans-serif;padding:20px 36px;border-radius:999px;border:0;' +
      'background:#C2793A;color:#fff;cursor:pointer;z-index:99';
    knapp.onclick = function () { knapp.remove(); tl.restart(); };
    document.body.appendChild(knapp);

    addEventListener('keydown', function (e) {
      if (e.code === 'Space') { e.preventDefault(); if (knapp.isConnected) knapp.remove(); tl.restart(); }
      if (e.key === 'k' || e.key === 'K') document.body.classList.toggle('dolj-kamera');
    });
  }

  return { start: start, ljud: ljud };
})();
