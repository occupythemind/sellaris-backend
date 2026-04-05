/* ============================================================
   main.js — Site-wide JavaScript
   Handles: nav scroll, mobile menu, back-to-top, copy commands,
            smooth scroll, keyboard accessibility.
============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  /* ----------------------------------------------------------
     1. FEATHER ICONS
     Replaces every <i data-feather="..."> with an inline SVG.
     Must run after DOM is fully parsed.
  ---------------------------------------------------------- */
  if (typeof feather !== 'undefined') {
    feather.replace({ 'stroke-width': 1.8 });
  }


  /* ----------------------------------------------------------
     2. COPYRIGHT YEAR
     Inserts the current year so you never forget to update it.
  ---------------------------------------------------------- */
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }


  /* ----------------------------------------------------------
     3. NAV SCROLL EFFECT
     Adds .scrolled class to nav when user scrolls past 40px.
     CSS uses that class to darken the frosted-glass background.
  ---------------------------------------------------------- */
  const navbar = document.getElementById('navbar');
  if (navbar) {
    const onNavScroll = () => {
      navbar.classList.toggle('scrolled', window.scrollY > 40);
    };
    window.addEventListener('scroll', onNavScroll, { passive: true });
  }


  /* ----------------------------------------------------------
     4. MOBILE NAV TOGGLE
     Opens/closes the slide-down mobile menu.
  ---------------------------------------------------------- */
  const hamburger  = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.toggle('open');
      hamburger.classList.toggle('open', isOpen);
      // Update ARIA attribute so screen readers know the state
      hamburger.setAttribute('aria-expanded', String(isOpen));
    });
  }


  /* ----------------------------------------------------------
     5. CLOSE MOBILE MENU on link click
     Exported as a global so inline onclick="closeMenu()" works.
  ---------------------------------------------------------- */
  window.closeMenu = function () {
    if (mobileMenu) mobileMenu.classList.remove('open');
    if (hamburger)  hamburger.classList.remove('open');
    if (hamburger)  hamburger.setAttribute('aria-expanded', 'false');
  };


  /* ----------------------------------------------------------
     6. BACK TO TOP BUTTON
     Appears once the user has scrolled more than 400px.
  ---------------------------------------------------------- */
  const backTop = document.getElementById('back-top');
  if (backTop) {
    window.addEventListener('scroll', () => {
      backTop.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });

    backTop.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }


  /* ----------------------------------------------------------
     7. SMOOTH SCROLL for in-page anchor links
     Offsets by nav height (62px) + a little breathing room.
  ---------------------------------------------------------- */
  const NAV_HEIGHT = 72;

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      const top = target.getBoundingClientRect().top + window.scrollY - NAV_HEIGHT;
      window.scrollTo({ top, behavior: 'smooth' });
      // Close mobile menu if open
      window.closeMenu();
    });
  });


  /* ----------------------------------------------------------
     8. COPY COMMAND BUTTONS
     Each .copy-btn has a data-cmd attribute with the text to copy.
     On click: copies to clipboard, swaps icon to a checkmark,
     then reverts after 1.8s.
  ---------------------------------------------------------- */
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.dataset.cmd;
      if (!cmd || !navigator.clipboard) return;

      navigator.clipboard.writeText(cmd).then(() => {
        const original = btn.innerHTML;
        // Show "copied!" state
        btn.innerHTML = `
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
               stroke="currentColor" stroke-width="2.5">
            <polyline points="20 6 9 17 4 12"/>
          </svg> copied!`;
        btn.style.color = '#16a34a';
        btn.style.borderColor = '#bbf7d0';

        // Revert after 1.8s
        setTimeout(() => {
          btn.innerHTML = original;
          btn.style.color = '';
          btn.style.borderColor = '';
          // Re-run feather for the restored icon
          if (typeof feather !== 'undefined') {
            feather.replace({ 'stroke-width': 1.8 });
          }
        }, 1800);
      });
    });
  });


  /* ----------------------------------------------------------
     9. KEYBOARD ACCESSIBILITY for docs nav items
     Allows pressing Enter or Space to activate a nav item
     (they're <div>s, not <button>s, so we add this manually).
  ---------------------------------------------------------- */
  document.querySelectorAll('.docs-nav-item').forEach(item => {
    item.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        item.click();
      }
    });
  });

}); // end DOMContentLoaded
