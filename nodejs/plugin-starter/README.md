# Plugin Starter (Node.js)

A minimal Quix Portal plugin written in plain Node.js + HTML. Use it as a starting point for building your own plugin: fork it, replace the demo UI in `public/index.html` with your own, and deploy.

## How it works

The Quix Portal hosts a small JavaScript SDK at `/static/sdk/quix-plugin.js`. Drop it into your page with a single `<script>` tag and you get:

- **Auth token relay** — `QuixPlugin.init()` posts `REQUEST_AUTH_TOKEN` to the parent Portal; `QuixPlugin.onToken(fn)` fires your callback with the user's bearer token (and fires immediately for late registrations).
- **Navigation sync** — the SDK patches `history.pushState` / `replaceState` and listens for `popstate` / `hashchange`, so any in-plugin navigation is mirrored into the Portal URL. Deep links and hard refreshes restore the right view.
- **Idempotent** — calling `init()` twice is a no-op.

That's the whole API:

```html
<script src="/static/sdk/quix-plugin.js"></script>
<script>
  QuixPlugin.init().onToken((token) => {
    fetch('/api/whatever', {
      headers: { Authorization: `Bearer ${token}` }
    });
  });
</script>
```

## How it shows up in the Portal

The `library.json` registers the plugin in two ways:

- **`embeddedView`** — the deployment details page renders this app in an iframe by default.
- **`sidebarItem`** — adds a "Plugin Starter" entry to the workspace sidebar.

See the [Plugin System Documentation](https://quix.io/docs/quix-cloud/plugin.html) for the full schema (including `globalItem` for organisation-wide plugins).

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log in and deploy this sample from the Code Samples library. Once it's running, click the "Plugin Starter" entry in the workspace sidebar — the iframe loads and the SDK completes the auth handshake automatically.

### Run locally

```bash
npm install
npm start
```

Then open <http://localhost>. Outside the Portal the SDK script 404s (it's only served from the Portal origin), so the page shows an "SDK not loaded" state — useful for confirming the static UI works, but you need a real Portal embed to exercise the auth + navigation features.

## Files

- `public/index.html` — the plugin UI. Loads the SDK, wires up `init().onToken(...)`, and shows the forwarded query params, the received token's claims, and a navigation-sync demo button. **This is the file you'll customise.**
- `main.js` — minimal Express server that serves `public/`.
- `library.json` — plugin metadata and `DeploySettings.plugin` config.
- `dockerfile` — single-stage Node image, listens on port 80.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.
