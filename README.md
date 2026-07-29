<!-- Author: SangJeong Kim -->
<!-- Last Modified: 2026-07-29 -->

<div align="center">
  <h1> sjpy </h1>

[sangjung0](https://github.com/sangjung0)

  <br>

<a href="https://github.com/sangjung0/sjpy/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=sangjung0/sjpy" />
</a>

  <br>
  <br>

Personal Python utilities

</div>

---

## Overview

`sjpy` is a small utility package I use across personal research and engineering projects. It is not intended to be a full framework; it collects reusable helpers for file IO, configuration loading, audio conversion, ASR evaluation, async tasks, logging, memory profiling, and small decorator patterns.

The package is kept lightweight and practical. APIs may change as the utilities are adapted for active projects.

## What Is Included

- File helpers for JSON/YAML saving and loading
- Configuration loading from local paths or `CONFIG_PATH`
- Audio helpers for MP4/WAV/PCM conversion, resampling, segmentation, and Opus compression
- ASR and streaming-evaluation helpers, including AL, LAAL, DAL, AP, and average latency
- Async task helpers with callback support
- Logging, memory sampling, statistics, string, archive, and collection utilities
- Small decorators such as singleton and version-check helpers

## Installation

This project targets Python 3.10 or newer.

```bash
git clone https://github.com/sangjung0/sjpy.git
cd sjpy
uv sync
```

For editable local development:

```bash
pip install -e .
```

Some audio utilities require `ffmpeg` to be available on the system path.

## Use as a Git Submodule

Add `sjpy` at the location expected by the parent project's `pyproject.toml`:

```bash
git submodule add https://github.com/sangjung0/sjpy.git modules/sjpy
git submodule update --init --recursive
```

Declare the dependency and its local uv source in the parent project:

```toml
[project]
dependencies = [
    "sjpy",
]

[tool.uv.sources]
sjpy = { path = "modules/sjpy", editable = true }
```

The source path must point to the submodule root containing `pyproject.toml`.

## Development Container

The optional development-only Dockerfile and Compose configuration live in
`.devcontainer`. They provide the GPU-enabled VS Code development environment and
are not runtime images for the library.

Before opening the repository in a Dev Container:

1. Copy `.env.example` to `.env`.
2. Set `CONTAINER_VOLUME` and `AGENTS_PATH` to valid host directories.
3. Confirm that the NVIDIA Container Toolkit is available.
4. Run **Dev Containers: Reopen in Container** from VS Code.

The checked-in `initializeCommand` uses the Windows host script. On a Linux host,
enable the `initialize_command.sh` block in `.devcontainer/devcontainer.json`
instead.

## License

Except for the third-party-derived component identified in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), this project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

The SimulEval-derived latency scoring code is licensed under the Creative Commons Attribution-ShareAlike 4.0 International License. See [LICENSES/CC-BY-SA-4.0](LICENSES/CC-BY-SA-4.0) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
