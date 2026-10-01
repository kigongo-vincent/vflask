<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>vflask | Enterprise Flask app scaffolding</title>
    <style>
      :root {
        --airbnb-red: #ff385c;
        --airbnb-red-dark: #d82d4a;
        --airbnb-ink: #222222;
        --airbnb-muted: #717171;
        --airbnb-line: #ebebeb;
        --airbnb-bg: #f7f7f7;
        --airbnb-card: #ffffff;
        --airbnb-soft: #fff4f5;
        --airbnb-success: #2a9d8f;
        --airbnb-warning: #f4a261;
        --shadow: 0 24px 70px rgba(34, 34, 34, 0.08);
      }

      * { box-sizing: border-box; }

      html {
        scroll-behavior: smooth;
      }

      body {
        margin: 0;
        font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: linear-gradient(180deg, #fff 0%, #f8f8f8 100%);
        color: var(--airbnb-ink);
      }

      a {
        color: inherit;
        text-decoration: none;
      }

      .page {
        max-width: 1200px;
        margin: 0 auto;
        padding: 24px 20px 80px;
      }

      .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 12px 0 24px;
      }

      .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 700;
        letter-spacing: -0.03em;
      }

      .brand-mark {
        display: grid;
        place-items: center;
        width: 36px;
        height: 36px;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--airbnb-red) 0%, #ff7a7a 100%);
        color: white;
        font-size: 18px;
        box-shadow: 0 8px 18px rgba(255, 56, 92, 0.22);
      }

      .nav {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        color: var(--airbnb-muted);
        font-size: 14px;
      }

      .nav a {
        padding: 10px 14px;
        border-radius: 999px;
        transition: 0.2s ease;
      }

      .nav a:hover {
        background: #f3f3f3;
        color: var(--airbnb-ink);
      }

      .hero {
        display: grid;
        grid-template-columns: 1.5fr 0.9fr;
        gap: 24px;
        padding: 28px;
        border-radius: 32px;
        background: linear-gradient(135deg, #fff 0%, #fff5f6 100%);
        border: 1px solid rgba(255, 56, 92, 0.08);
        box-shadow: var(--shadow);
      }

      .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--airbnb-red-dark);
        background: rgba(255, 56, 92, 0.08);
        border: 1px solid rgba(255, 56, 92, 0.08);
        border-radius: 999px;
        padding: 8px 12px;
        font-weight: 700;
      }

      h1 {
        margin: 18px 0 14px;
        font-size: clamp(2.6rem, 5vw, 4.5rem);
        line-height: 0.95;
        letter-spacing: -0.06em;
      }

      .hero p {
        margin: 0;
        max-width: 680px;
        color: var(--airbnb-muted);
        font-size: 1.08rem;
        line-height: 1.75;
      }

      .cta-row {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 24px;
      }

      .button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 14px 20px;
        border-radius: 14px;
        font-weight: 700;
        transition: 0.2s ease;
        border: 1px solid transparent;
      }

      .button.primary {
        background: var(--airbnb-red);
        color: #fff;
        box-shadow: 0 12px 24px rgba(255, 56, 92, 0.22);
      }

      .button.primary:hover {
        background: var(--airbnb-red-dark);
      }

      .button.secondary {
        background: #fff;
        border-color: var(--airbnb-line);
      }

      .mini-panel {
        display: grid;
        gap: 16px;
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(34, 34, 34, 0.06);
        border-radius: 24px;
        padding: 22px;
        backdrop-filter: blur(4px);
      }

      .mini-panel .metric {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        padding: 14px 0;
        border-bottom: 1px solid var(--airbnb-line);
      }

      .mini-panel .metric:last-child {
        border-bottom: none;
      }

      .mini-panel .label {
        color: var(--airbnb-muted);
        font-size: 14px;
      }

      .mini-panel .value {
        font-weight: 800;
        letter-spacing: -0.04em;
        font-size: 1.8rem;
      }

      .section {
        margin-top: 42px;
      }

      .section-header {
        margin-bottom: 18px;
      }

      .section-header h2 {
        margin: 0 0 10px;
        font-size: clamp(1.8rem, 3vw, 2.6rem);
        letter-spacing: -0.05em;
      }

      .section-header p {
        margin: 0;
        color: var(--airbnb-muted);
        max-width: 760px;
        line-height: 1.7;
      }

      .feature-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 18px;
      }

      .feature-card, .panel, .code-card, .table-wrap {
        background: var(--airbnb-card);
        border: 1px solid var(--airbnb-line);
        border-radius: 24px;
        box-shadow: 0 10px 28px rgba(34, 34, 34, 0.04);
      }

      .feature-card {
        padding: 22px;
      }

      .icon-dot {
        display: inline-grid;
        place-items: center;
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: var(--airbnb-soft);
        color: var(--airbnb-red);
        font-weight: 800;
        margin-bottom: 14px;
      }

      .feature-card h3 {
        margin: 0 0 10px;
        font-size: 1.15rem;
      }

      .feature-card p {
        margin: 0;
        line-height: 1.7;
        color: var(--airbnb-muted);
      }

      .panel {
        padding: 22px;
      }

      .code-card {
        overflow: hidden;
      }

      .copy-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #f4f4f4;
        border-bottom: 1px solid var(--airbnb-line);
        padding: 12px 16px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--airbnb-muted);
      }

      .copy-btn {
        border: 1px solid var(--airbnb-line);
        border-radius: 10px;
        background: white;
        padding: 8px 10px;
        cursor: pointer;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }

      pre {
        margin: 0;
        padding: 18px 20px 22px;
        overflow-x: auto;
        font-size: 0.96rem;
        line-height: 1.7;
        background: #0f172a;
        color: #e5eefb;
      }

      .table-wrap {
        overflow: hidden;
      }

      table {
        width: 100%;
        border-collapse: collapse;
      }

      th, td {
        padding: 16px 18px;
        text-align: left;
        vertical-align: top;
        border-bottom: 1px solid var(--airbnb-line);
      }

      th {
        background: #fafafa;
        font-size: 12px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--airbnb-muted);
      }

      td {
        color: var(--airbnb-ink);
        line-height: 1.65;
      }

      td strong {
        letter-spacing: -0.02em;
      }

      .stack {
        display: grid;
        gap: 18px;
      }

      .badge-list {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 16px;
      }

      .badge {
        display: inline-flex;
        align-items: center;
        padding: 9px 12px;
        border-radius: 999px;
        background: #f8f8f8;
        border: 1px solid var(--airbnb-line);
        color: var(--airbnb-ink);
        font-size: 13px;
        font-weight: 600;
      }

      .footer {
        margin-top: 40px;
        padding-top: 22px;
        border-top: 1px solid var(--airbnb-line);
        display: flex;
        justify-content: space-between;
        gap: 16px;
        flex-wrap: wrap;
        color: var(--airbnb-muted);
        font-size: 14px;
      }

      @media (max-width: 960px) {
        .hero {
          grid-template-columns: 1fr;
        }

        .feature-grid {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }

      @media (max-width: 640px) {
        .page {
          padding-left: 14px;
          padding-right: 14px;
        }

        .feature-grid {
          grid-template-columns: 1fr;
        }

        .topbar {
          flex-direction: column;
          align-items: flex-start;
        }
      }
    </style>

  </head>
  <body>
    <div class="page">
      <header class="topbar">
        <div class="brand">
          <div class="brand-mark">v</div>
          <span>vflask</span>
        </div>
        <nav class="nav" aria-label="Main navigation">
          <a href="#quickstart">Quick start</a>
          <a href="#architecture">Architecture</a>
          <a href="#modules">Modules</a>
          <a href="#edgecases">Edge cases</a>
          <a href="#operations">Hosting</a>
          <a href="#reference">CLI</a>
        </nav>
      </header>

      <main>
        <section class="hero">
          <div>
            <span class="eyebrow">Python 3.11+ · Flask 3</span>
            <h1>Build enterprise-grade SaaS apps with vflask.</h1>
            <p>
              vflask scaffolds a production-oriented Flask foundation with typed modules, RBAC,
              migrations, a health-aware local runtime, OpenAPI docs, test coverage, and deployment
              automation. It gives beginners structure and gives teams a maintainable base for real apps.
            </p>
            <div class="cta-row">
              <a class="button primary" href="#quickstart">Start building</a>
              <a class="button secondary" href="#architecture">See architecture</a>
            </div>
          </div>

          <div class="mini-panel" aria-label="Project health overview">
            <div class="metric">
              <div class="label">Default package version</div>
              <div class="value">1.0.0</div>
            </div>
            <div class="metric">
              <div class="label">Generated app stack</div>
              <div class="value">Flask</div>
            </div>
            <div class="metric">
              <div class="label">Included systems</div>
              <div class="value">Auth + DB + API + Tests</div>
            </div>
          </div>
        </section>

        <section class="section">
          <div class="section-header">
            <h2>Why teams use vflask</h2>
            <p>It turns a blank Flask project into a cohesive platform with clear boundaries, generated modules, and clear operational defaults.</p>
          </div>

          <div class="feature-grid">
            <article class="feature-card">
              <div class="icon-dot">01</div>
              <h3>Repeatable structure</h3>
              <p>Generate a consistent app skeleton with app factory, modules, docs, tests, auth, migrations, and deployment workflows.</p>
            </article>
            <article class="feature-card">
              <div class="icon-dot">02</div>
              <h3>Typed CRUD modules</h3>
              <p>Define fields in a single command and generate models, routes, handlers, services, tests, and migrations without boilerplate noise.</p>
            </article>
            <article class="feature-card">
              <div class="icon-dot">03</div>
              <h3>Operational defaults</h3>
              <p>Use Postgres, Redis, health checks, Docker Compose setup, and a production-ready deployment baseline from day one.</p>
            </article>
            <article class="feature-card">
              <div class="icon-dot">04</div>
              <h3>Real-world guardrails</h3>
              <p>Support for JWT auth, OAuth, provider adapters, and edge-case expectations keeps your app closer to production reality.</p>
            </article>
          </div>
        </section>

        <section id="quickstart" class="section">
          <div class="section-header">
            <h2>Quick start</h2>
            <p>Follow this flow to create a clean application, generate modules, and run it locally.</p>
          </div>

          <div class="stack">
            <div class="code-card">
              <div class="copy-row">
                <span>1. Install the CLI</span>
                <button class="copy-btn" data-copy="python -m pip install vflask">Copy</button>
              </div>
              <pre><code>python -m pip install vflask</code></pre>
            </div>

            <div class="code-card">
              <div class="copy-row">
                <span>2. Create a project</span>
                <button class="copy-btn" data-copy="vflask new bookstore

cd bookstore">Copy</button>
</div>
<pre><code>vflask new bookstore
cd bookstore</code></pre>
</div>

            <div class="code-card">
              <div class="copy-row">
                <span>3. Create a typed module</span>
                <button class="copy-btn" data-copy="vflask module create products -f name:string:required -f price:decimal:required -f sku:string:unique -r admin -r editor">Copy</button>
              </div>
              <pre><code>vflask module create products \

-f name:string:required \
 -f price:decimal:required \
 -f sku:string:unique \
 -r admin -r editor</code></pre>
</div>

            <div class="code-card">
              <div class="copy-row">
                <span>4. Run the app</span>
                <button class="copy-btn" data-copy="vflask run">Copy</button>
              </div>
              <pre><code>vflask run</code></pre>
            </div>
          </div>
        </section>

        <section id="architecture" class="section">
          <div class="section-header">
            <h2>Architecture</h2>
            <p>vflask creates a clean application layout that is easy to extend without hiding Flask from you.</p>
          </div>

          <div class="panel">
            <pre><code>app/

auth/ JWT auth and Google OAuth routes
base/ API responses, JSON types, filters, and OpenAPI helpers
integrations/ payment, storage, mail, and OAuth provider adapters
shared/ users, roles, and RBAC primitives
modules/ generated business modules with routes, services, handlers, tests
migrations/ Alembic versions and migration environment
tests/ test fixtures and app-level checks
.github/ CI and deployment workflows
Dockerfile runtime image for the app
compose.yml PostgreSQL + Redis + app orchestration
.env.example local environment template</code></pre>
</div>
</section>

        <section id="modules" class="section">
          <div class="section-header">
            <h2>Module generation model</h2>
            <p>Generate modules from field definitions. Each module includes the logic you need to move from idea to running endpoints quickly.</p>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Module artifact</th>
                  <th>Purpose</th>
                  <th>Why it matters</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>models.py</strong></td>
                  <td>SQLAlchemy model definitions</td>
                  <td>Defines the schema and DB contract</td>
                </tr>
                <tr>
                  <td><strong>routes.py</strong></td>
                  <td>Blueprint routes and HTTP handlers</td>
                  <td>Creates the public API surface</td>
                </tr>
                <tr>
                  <td><strong>services.py</strong></td>
                  <td>Business logic and DB operations</td>
                  <td>Keeps request handlers thin and testable</td>
                </tr>
                <tr>
                  <td><strong>handlers.py</strong></td>
                  <td>Validation and response shaping</td>
                  <td>Protects the API from invalid inputs</td>
                </tr>
                <tr>
                  <td><strong>test_module.py</strong></td>
                  <td>Automated checks for model and API behavior</td>
                  <td>Prevents regressions in generated modules</td>
                </tr>
                <tr>
                  <td><strong>migration.py</strong></td>
                  <td>Alembic migration stub</td>
                  <td>Tracks schema changes in a safe way</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="section">
          <div class="section-header">
            <h2>Field system</h2>
            <p>Use a compact specification to describe the domain model and generate working CRUD patterns.</p>
          </div>
          <div class="panel">
            <pre><code>Supported types:

string, text, integer, float, decimal, boolean, date, datetime, json, uuid

Supported flags:
required, unique, index, nullable, default=value

Examples:
name:string:required
sku:string:unique
price:decimal:required
metadata:json</code></pre>
</div>
</section>

        <section id="edgecases" class="section">
          <div class="section-header">
            <h2>Enterprise edge cases and how to handle them</h2>
            <p>These are the issues teams run into when moving from a demo to a production-grade application.</p>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Scenario</th>
                  <th>Best practice</th>
                  <th>Why it matters</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Missing environment variables</strong></td>
                  <td>Start from <code>.env.example</code>, then copy to <code>.env</code> and fill every required value.</td>
                  <td>Prevents runtime failures and bad secrets in the repo.</td>
                </tr>
                <tr>
                  <td><strong>Database migration drift</strong></td>
                  <td>Use Alembic revisions instead of editing schema directly when the app already runs.</td>
                  <td>Schema changes should be versioned and reviewable.</td>
                </tr>
                <tr>
                  <td><strong>OAuth misconfiguration</strong></td>
                  <td>Set the exact public <code>GOOGLE_REDIRECT_URI</code> and verify the Google email domain.</td>
                  <td>OAuth errors often come from mismatched callback configuration.</td>
                </tr>
                <tr>
                  <td><strong>Local services not ready</strong></td>
                  <td>Use <code>vflask run</code> with Compose support, or run with <code>--no-services</code> when connecting to managed infrastructure.</td>
                  <td>It reduces startup race conditions with Postgres and Redis.</td>
                </tr>
                <tr>
                  <td><strong>Sensitive secrets in a repo</strong></td>
                  <td>Keep production values in a secret manager or CI/CD environment variables.</td>
                  <td>Secrets should never live in source control or generated templates.</td>
                </tr>
                <tr>
                  <td><strong>Repeated package upload</strong></td>
                  <td>Use a valid version tag such as <code>v1.2.3</code> or default to <code>1.0.0</code> for first release.</td>
                  <td>PyPI rejects duplicate package versions; vflask handles the first publish case cleanly.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="operations" class="section">
          <div class="section-header">
            <h2>Testing, deployment, and release automation</h2>
            <p>Build a full app lifecycle that is realistic, safe, and easy to trust.</p>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Stage</th>
                  <th>Command</th>
                  <th>What happens</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Local dev</strong></td>
                  <td><code>vflask run</code></td>
                  <td>Creates or reuses environment config, starts DB services when needed, applies migrations, and launches Flask.</td>
                </tr>
                <tr>
                  <td><strong>Local tests</strong></td>
                  <td><code>pytest -q</code></td>
                  <td>Runs the generated app-level and module-level checks.</td>
                </tr>
                <tr>
                  <td><strong>Watch mode</strong></td>
                  <td><code>vflask watch --project-root .</code></td>
                  <td>Automatically regenerates docs when modules change.</td>
                </tr>
                <tr>
                  <td><strong>Release build</strong></td>
                  <td><code>python -m build</code></td>
                  <td>Produces the wheel and source distribution.</td>
                </tr>
                <tr>
                  <td><strong>Metadata validation</strong></td>
                  <td><code>python -m twine check dist/*</code></td>
                  <td>Validates that the package metadata is publishable.</td>
                </tr>
                <tr>
                  <td><strong>PyPI release</strong></td>
                  <td><code>python -m twine upload --skip-existing dist/*</code></td>
                  <td>Pushes the package; first publish creates the project, later same-version pushes are skipped.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section id="reference" class="section">
          <div class="section-header">
            <h2>CLI reference</h2>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Command</th>
                  <th>Purpose</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>vflask new &lt;project&gt;</code></td>
                  <td>Create a new project scaffold in a target directory.</td>
                </tr>
                <tr>
                  <td><code>vflask module create &lt;name&gt; -f ...</code></td>
                  <td>Create a typed business module with generated CRUD files and tests.</td>
                </tr>
                <tr>
                  <td><code>vflask run --project-root .</code></td>
                  <td>Prepare local services, apply migrations, and run the app.</td>
                </tr>
                <tr>
                  <td><code>vflask run --no-services</code></td>
                  <td>Use your own Postgres and Redis instances instead of Docker Compose.</td>
                </tr>
                <tr>
                  <td><code>vflask watch --project-root .</code></td>
                  <td>Rebuild generated module docs when the project changes.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="section">
          <div class="section-header">
            <h2>Checklist for a production-grade app</h2>
          </div>
          <div class="panel">
            <div class="badge-list">
              <span class="badge">Set secrets in CI/CD</span>
              <span class="badge">Use Alembic for schema changes</span>
              <span class="badge">Run tests before deploy</span>
              <span class="badge">Use managed Postgres</span>
              <span class="badge">Protect OAuth callbacks</span>
              <span class="badge">Use Docker + health checks</span>
              <span class="badge">Keep production env separate</span>
              <span class="badge">Version packages with semver</span>
            </div>
          </div>
        </section>

        <footer class="footer">
          <span>vflask</span>
          <span>Built for teams who want a clean Flask baseline without losing control.</span>
          <span>© <span id="year"></span> vflask</span>
        </footer>
      </main>
    </div>

    <script>
      document.querySelectorAll('.copy-btn').forEach((button) => {
        button.addEventListener('click', async () => {
          const text = button.dataset.copy || '';
          try {
            await navigator.clipboard.writeText(text);
            const previous = button.textContent;
            button.textContent = 'Copied';
            setTimeout(() => (button.textContent = previous), 1200);
          } catch (error) {
            button.textContent = 'Failed';
            setTimeout(() => (button.textContent = 'Copy'), 1200);
          }
        });
      });

      document.getElementById('year').textContent = new Date().getFullYear();
    </script>

  </body>
</html>
