/* ============================================================
   docs.js
   Loads the Markdown docs pages from docs/docs/v1 and renders
   them into the docs section of the static site.
============================================================ */

const DOC_FILES = {
  overview: 'docs/v1/intro.md',
  'getting-started': 'docs/v1/getting-started.md',
  authentication: 'docs/v1/authentication.md',
  'api-guide': 'docs/v1/api.md',
  workflow: 'docs/v1/whole-workflow.md',
  faq: 'docs/v1/faq.md',
};

function renderMarkdownInto(docsBody, markdown) {
  if (typeof marked === 'undefined') {
    docsBody.innerHTML = '<p style="color:var(--text-muted);padding:24px 0;">Markdown renderer unavailable.</p>';
    return;
  }

  docsBody.innerHTML = marked.parse(markdown);

  if (typeof hljs !== 'undefined') {
    docsBody.querySelectorAll('pre code').forEach(block => {
      hljs.highlightElement(block);
    });
  }
}

window.loadDoc = async function (pageId, clickedEl) {
  const docsBody = document.getElementById('docsBody');
  if (!docsBody) return;

  document.querySelectorAll('.docs-nav-item').forEach(el => {
    el.classList.remove('active');
  });
  if (clickedEl) clickedEl.classList.add('active');

  docsBody.innerHTML = `
    <div class="docs-loading">
      <div class="spinner"></div>
      Loading…
    </div>`;

  const url = DOC_FILES[pageId];
  if (!url) {
    docsBody.innerHTML = '<p style="color:var(--text-muted);padding:24px 0;">Page not found.</p>';
    return;
  }

  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Not found');
    }
    const markdown = await response.text();
    renderMarkdownInto(docsBody, markdown);
  } catch (error) {
    docsBody.innerHTML = `
      <p style="color:var(--text-muted);padding:24px 0;">
        Could not load this page. Make sure the Markdown file exists at <code>${url}</code>.
      </p>`;
  }
};

document.addEventListener('DOMContentLoaded', async () => {
  const docsBody = document.getElementById('docsBody');
  if (!docsBody) return;

  const firstItem = document.querySelector('.docs-nav-item');
  if (firstItem) {
    firstItem.classList.add('active');
  }

  try {
    const response = await fetch(DOC_FILES.overview);
    if (!response.ok) {
      throw new Error('Not found');
    }
    const markdown = await response.text();
    renderMarkdownInto(docsBody, markdown);
  } catch (error) {
    docsBody.innerHTML = `
      <p style="color:var(--text-muted);padding:24px 0;">
        Could not load the overview page.
      </p>`;
  }
});
