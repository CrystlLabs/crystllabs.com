(() => {
  const path = location.pathname.toLowerCase();
  const body = document.body;
  if (!body) return;

  const nested = /\/(apps|blog|telegram|discord)\//.test(path);
  const root = nested ? '..' : '.';
  const isHome = /\/(index\.html)?$/.test(path) && !/\/(telegram|discord)\//.test(path);
  const pageClass = path.includes('/apps/') ? 'crystl-app'
    : path.includes('/blog/') ? 'crystl-article'
    : path.endsWith('/blogs.html') ? 'crystl-journal'
    : path.endsWith('/personnel.html') ? 'crystl-studio'
    : path.endsWith('/contact.html') ? 'crystl-contact'
    : /(privacy|terms|data-deletion)\.html$/.test(path) ? 'crystl-reading'
    : path.endsWith('/projects.html') ? 'crystl-projects'
    : isHome ? 'crystl-home' : 'crystl-interior';
  body.classList.add(pageClass, 'crystl-enhanced');

  const url = (value) => `${root}/${value}`;
  const links = [
    ['Projects', 'projects.html'],
    ['Journal', 'blogs.html'],
    ['Studio', 'personnel.html'],
    ['Contact', 'contact.html']
  ];

  const nav = document.querySelector('body > nav');
  if (nav) {
    const lang = nav.querySelector('#langSelect');
    nav.className = 'crystl-nav';

    const brand = document.createElement('a');
    brand.className = 'crystl-brand';
    brand.href = url('index.html');
    brand.setAttribute('aria-label', 'Crystl Labs home');
    brand.innerHTML = `<img src="${url('assets/crystl-mark.svg')}" alt=""><span class="crystl-wordmark">Crystl Labs</span>`;

    const primary = document.createElement('div');
    primary.className = 'crystl-nav-links';
    primary.setAttribute('aria-label', 'Primary navigation');
    links.forEach(([label, href]) => {
      const a = document.createElement('a');
      a.href = url(href);
      a.textContent = label;
      if (path.endsWith(`/${href}`) || (href === 'projects.html' && path.includes('/apps/')) || (href === 'blogs.html' && path.includes('/blog/'))) a.setAttribute('aria-current', 'page');
      primary.appendChild(a);
    });

    const tools = document.createElement('div');
    tools.className = 'crystl-nav-tools';
    tools.innerHTML = '<span class="crystl-status">Seoul · Online</span>';
    if (lang) tools.appendChild(lang);

    nav.replaceChildren(brand, primary, tools);
  }

  const menuButton = document.querySelector('body > button[onclick*="toggleMenu"]');
  if (menuButton) {
    menuButton.className = 'crystl-menu-button';
    menuButton.setAttribute('aria-label', 'Open navigation');
  }

  const sidebar = document.getElementById('sidebar');
  if (sidebar) {
    sidebar.innerHTML = `<nav class="crystl-mobile-menu" aria-label="Mobile navigation">
      ${links.map(([label, href]) => `<a href="${url(href)}">${label}</a>`).join('')}
      <a href="${url('privacy.html')}">Privacy</a>
      <small>Independent · Seoul · Online<br>Elegant worlds, deeply simulated.</small>
    </nav>`;
  }

  const ambient = document.createElement('div');
  ambient.className = 'crystl-ambient';
  ambient.setAttribute('aria-hidden', 'true');
  body.prepend(ambient);

  if (isHome) buildImpossibleWindow();
  else buildPocketWorld();

  const revealTargets = document.querySelectorAll('main > div > section, main article > section, #appGrid > *, #heatGrid > *, #siteGrid > *');
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const reveal = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        reveal.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: .08 });
    revealTargets.forEach((element, index) => {
      element.classList.add('crystl-reveal');
      element.style.transitionDelay = `${Math.min(index % 4, 3) * 55}ms`;
      reveal.observe(element);
    });
  } else {
    revealTargets.forEach((element) => element.classList.add('is-visible'));
  }

  document.querySelectorAll('#sidebar a').forEach((link) => link.addEventListener('click', () => {
    if (innerWidth >= 768) return;
    sidebar.classList.add('-translate-x-full');
    document.getElementById('sidebarBackdrop')?.classList.add('hidden');
  }));

  if (!document.querySelector('meta[http-equiv="refresh"]')) {
    const footer = document.createElement('footer');
    footer.className = 'crystl-footer';
    footer.innerHTML = `<span>Crystl Labs · Seoul</span><nav aria-label="Legal navigation">
      <a href="${url('privacy.html')}">Privacy</a>
      <a href="${url('terms.html')}">Terms</a>
      <a href="${url('data-deletion.html')}">Data deletion</a>
      <a href="mailto:dev@crystllabs.com">dev@crystllabs.com</a>
    </nav>`;
    body.appendChild(footer);
  }

  function buildImpossibleWindow() {
    const shell = document.querySelector('main > div:first-child');
    const hero = shell?.querySelector('header');
    if (!shell || !hero || shell.querySelector('.crystl-portal')) return;

    const portal = document.createElement('div');
    portal.className = 'crystl-portal';
    portal.setAttribute('aria-label', 'Featured Crystl Labs worlds');
    portal.innerHTML = `<div class="portal-aperture">
      <div class="portal-void" aria-hidden="true"></div>
      <a class="portal-plane portal-plane--one" href="${url('apps/bent-fc.html')}">
        <img src="${url('apps/bent-fc.png')}" alt=""><span>Bent FC</span><small>World 01 · Football</small>
      </a>
      <a class="portal-plane portal-plane--two" href="${url('apps/dork.html')}">
        <img src="${url('apps/dork.png')}" alt=""><span>DORK</span><small>World 02 · Audio</small>
      </a>
      <a class="portal-plane portal-plane--three" href="${url('apps/mise.html')}">
        <img src="${url('apps/mise.png')}" alt=""><span>Mise</span><small>World 03 · Kitchen</small>
      </a>
    </div><span class="portal-index">Drag your gaze · Enter a world</span>`;
    hero.insertAdjacentElement('afterend', portal);

    if (!matchMedia('(pointer: fine)').matches || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    portal.addEventListener('pointermove', (event) => {
      const rect = portal.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - .5;
      const y = (event.clientY - rect.top) / rect.height - .5;
      portal.style.setProperty('--ry', `${x * 5}deg`);
      portal.style.setProperty('--rx', `${y * -4}deg`);
    });
    portal.addEventListener('pointerleave', () => {
      portal.style.setProperty('--ry', '0deg');
      portal.style.setProperty('--rx', '0deg');
    });
  }

  function buildPocketWorld() {
    const main = document.querySelector('main');
    if (!main || main.querySelector('.page-pocket-world')) return;

    let images;
    if (pageClass === 'crystl-app') {
      const current = document.getElementById('apIcon')?.getAttribute('src');
      images = [current || url('assets/crystl-mark.svg')];
    } else if (['crystl-projects','crystl-journal'].includes(pageClass)) {
      images = [url('apps/bent-fc.png'), url('apps/dork.png'), url('apps/mise.png')];
    } else {
      images = [url('assets/crystl-mark.svg')];
    }

    const pocket = document.createElement('div');
    pocket.className = 'page-pocket-world';
    pocket.setAttribute('aria-hidden', 'true');
    pocket.innerHTML = images.map((src) => `<span class="pocket-shell"><img src="${src}" alt=""></span>`).join('');
    main.prepend(pocket);
  }
})();
