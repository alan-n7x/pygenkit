# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.4] - 2026-07-05

### Fixed

- Corrected module detection for projects using a `src/` layout.
- Ignored `.egg-info`, virtual environments, build directories, and caches during module detection.
- Detected PyPI publishing actions inside any GitHub Actions workflow file.
- Removed false health warnings for `__version__` and PyPI publishing workflows.

## [0.2.3] - 2026-07-05

### Added

- Published PyGenKit package metadata.
- Added project health checks.
- Added inspection and validation workflow.

### Changed

- Improved README presentation and project documentation.
