# CHANGELOG


## v1.1.0 (2025-03-24)

### Features

- Add download badge
  ([`f0c14d1`](https://github.com/yeonhee7935/py-screen-grab/commit/f0c14d11362ab5a09c72ab48b4fedfa247abb59d))

- Add github workflows
  ([`8c7f0cb`](https://github.com/yeonhee7935/py-screen-grab/commit/8c7f0cb5f8f10d8c489a9796d43977393541a2b9))

- Add github workflows
  ([`d47fa5c`](https://github.com/yeonhee7935/py-screen-grab/commit/d47fa5cf950f8b2ba6c7d304ee9dafdc20269a8d))

- Add preview option during recording
  ([`1b6952b`](https://github.com/yeonhee7935/py-screen-grab/commit/1b6952b42bd17bbc665dde75e9907dc1c15d66de))

allowing users to choose whether to display a preview while recording

- Adjust ROI settings to fit within screen dimensions
  ([`c19fb60`](https://github.com/yeonhee7935/py-screen-grab/commit/c19fb6033f5f9118821e97a7c4e884e96ad619c1))

- Added checks to ensure the region of interest (ROI) coordinates and dimensions are within the
  primary monitor's boundaries.

- Extract constants for roi offset
  ([`6afcd1c`](https://github.com/yeonhee7935/py-screen-grab/commit/6afcd1cd1491b634b651ea9cb828a620e08fb6f5))

### Refactoring

- Add build_command
  ([`b7b12af`](https://github.com/yeonhee7935/py-screen-grab/commit/b7b12af42c1e5aa8758026f5e4d639dc9a600bca))

- Add compensation values for window decorations
  ([`2e4484c`](https://github.com/yeonhee7935/py-screen-grab/commit/2e4484c8d85844dcb1cbba83de3e4108b2eb16e1))

- Adjust roi offset
  ([`07db044`](https://github.com/yeonhee7935/py-screen-grab/commit/07db0440252b5e1ad4e003d2091172ee6a7cc0d6))

- Change test code
  ([`9d682e8`](https://github.com/yeonhee7935/py-screen-grab/commit/9d682e84dd09d9bd16d08c27905f1254ac41df90))

- Setup dependencies in ci
  ([`af6bbc7`](https://github.com/yeonhee7935/py-screen-grab/commit/af6bbc7130b87bd42ebeba72d37af389082e72a8))

- Setup dependencies in ci
  ([`2eb2184`](https://github.com/yeonhee7935/py-screen-grab/commit/2eb2184c2a35f32b74edca3b4939e060860fb86c))


## v1.0.0 (2025-03-20)

### Bug Fixes

- Exclude tests folder from build artifacts
  ([`1250841`](https://github.com/yeonhee7935/py-screen-grab/commit/1250841760520bffee9c54eed6cb39f0c1de9f00))

- Updated find_packages() to exclude tests and tests.* - Added MANIFEST.in to ensure tests folder is
  not included - Cleaned old build artifacts before rebuilding

- Improve preview window behavior - Fix preview window overlapping issue - Add window size
  limitation (30% of screen) - Move preview window to bottom-right corner - Add automatic window
  resizing for large screens - Add 'q' key to stop recording
  ([`23b40c9`](https://github.com/yeonhee7935/py-screen-grab/commit/23b40c99d189b1e766b7beb60f86767d3b957b5b))

### Features

- Add CLI interface - Add interactive command-line interface with monitor selection, custom region
  support, and recording options
  ([`e295b4e`](https://github.com/yeonhee7935/py-screen-grab/commit/e295b4e303cc4a3c0cc21ce204f2d38e7b18a009))

- Implement core screen recording functionality - Add ScreenGrabber class with screen capture,
  preview and recording features
  ([`0477bac`](https://github.com/yeonhee7935/py-screen-grab/commit/0477bac4dde5249e7679f10fd5cff8246873c980))

- Initial commit
  ([`f3fa938`](https://github.com/yeonhee7935/py-screen-grab/commit/f3fa93822150e68f901907fb2b957c1823ddeea8))

- Initialize project structure - Create basic project structure with setup.py, requirements.txt, and
  README.md
  ([`3a945d3`](https://github.com/yeonhee7935/py-screen-grab/commit/3a945d33a70a1ebeff732dfbac71bf71c05c1b3c))

### Refactoring

- Enable constructor params
  ([`956df35`](https://github.com/yeonhee7935/py-screen-grab/commit/956df358131453ce26ccec8bdcdb389d3e488db9))

- Update README
  ([`80fa046`](https://github.com/yeonhee7935/py-screen-grab/commit/80fa04668e9632b40eabfeb04058c875d4eba0a6))
