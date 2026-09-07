# test-toy-greet-plugin — the in-container scratch project

This folder is the **scratch working directory** where we actually install and exercise the
toy plugin **inside the dev container**. The plugin *source* lives one level up in
`../toy-greet-plugin/`; this folder is just a clean place to run `/greet` and let it act,
kept separate from the plugin source.

- **Dev container setup, lifecycle, and VS Code commands:** see `../DEVCONTAINER.md`.
- **The toy plugin being tested:** `../toy-greet-plugin/`.

## The test flow (summary — exact `/plugin` commands verified in Chunk 8)
Inside the container (`devcontainer exec --workspace-folder . bash`, or a VS Code container
terminal), from `/workspaces/expt-skill-wotkflow-agent`:

1. Log in once: `claude` → interactive OAuth (persists via the named volume).
2. Register the local marketplace that points at `toy-greet-plugin/` (needs a `marketplace.json`).
3. `/plugin install` the toy, then run `/greet` and watch the two approval gates fire.
4. Iterate: edit `../toy-greet-plugin/commands/greet.md` on the Mac (live in the container),
   reload, re-run.

## Why a container at all
Installing a plugin writes into `~/.claude`. Doing it in the container keeps your **Mac's
`~/.claude` untouched** and gives a disposable, resettable environment — the correct blast
radius for a workflow that (in the real product) writes and commits code.
