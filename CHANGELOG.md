# CHANGELOG


## v1.5.0 (2025-04-17)

### Chores

- Add ROI Type
  ([`538e12e`](https://github.com/yeonhee7935/py-screen-grab/commit/538e12e1be96c4bea686de9e6f197e3f6edb963c))

### Features

- Adds monitor-based ROI configuration to ScreenGrabber
  ([`5330db0`](https://github.com/yeonhee7935/py-screen-grab/commit/5330db0d4df848b7755df6e455989ac8445328df))

Introduces a `set_monitor` method to configure the region of interest (ROI) based on a specific
  monitor. Updates usage in the example code to replace manual ROI setup with monitor-based
  configuration for improved usability and clarity.

### Refactoring

- Rename get_window to get_window_list and update return type; add get_monitor_list function
  ([`c3ba67a`](https://github.com/yeonhee7935/py-screen-grab/commit/c3ba67a6ca6bf1584816b07a7f6568caed8ec722))


## v1.4.0 (2025-04-14)

### Chores

- Add TODO
  ([`14e49f2`](https://github.com/yeonhee7935/py-screen-grab/commit/14e49f2f8581656e602e08d258c2ffeee7468aae))

### Features

- Add init param show_cursor in ScreenGrabber
  ([`f91c681`](https://github.com/yeonhee7935/py-screen-grab/commit/f91c6811da2334bd011b88e033202ee291ecfccf))

- Capture cursor
  ([`04965c1`](https://github.com/yeonhee7935/py-screen-grab/commit/04965c1204800bfdec9c0bfc8b8f01fd0013b352))


## v1.3.3 (2025-04-01)

### Bug Fixes

- Update docstrings for window utility functions to match implementation
  ([`01e60d2`](https://github.com/yeonhee7935/py-screen-grab/commit/01e60d282607450b7f9f85002cf8532797b5ef1d))

- Refined the docstring for `get_window` to accurately describe the return value as a list of window
  names. - Updated the docstring for `get_window_roi` to clearly define the structure and types of
  the returned dictionary. - Ensured consistency between the function behavior and documentation for
  better clarity and usability.

### Chores

- Update README.md
  ([`66b1a75`](https://github.com/yeonhee7935/py-screen-grab/commit/66b1a75e82c52d3a2d4ddd17eede109f3c0c5b3e))


## v1.3.2 (2025-03-28)

### Bug Fixes

- Update run command
  ([`6368f91`](https://github.com/yeonhee7935/py-screen-grab/commit/6368f9170ae49301759693f6aa113720ba00e98f))

### Chores

- Update README.md
  ([`c70354c`](https://github.com/yeonhee7935/py-screen-grab/commit/c70354cc4825d880a3324c368a91df50519ebd8b))

- Update README.md
  ([`e7d58ba`](https://github.com/yeonhee7935/py-screen-grab/commit/e7d58ba74f0f682dccb209239980f7f23819bef1))


## v1.3.1 (2025-03-26)

### Bug Fixes

- Change var name for pyproject.toml(version_variable -> version_variables)
  ([`ba43ffe`](https://github.com/yeonhee7935/py-screen-grab/commit/ba43ffe7a87c57ec28d8565447b81ea1f5eb0d0f))

- Update requirements for package and write README.md for examples
  ([`fc0b204`](https://github.com/yeonhee7935/py-screen-grab/commit/fc0b204acc2c2b50dc4d2db8932db898237fb716))

### Chores

- Add CODE_OF_CONDUCT.md, CONTRIBUTING.md, update README.md
  ([`a12bb91`](https://github.com/yeonhee7935/py-screen-grab/commit/a12bb9163945ac35933e473c79ba747458861ebb))

- Add multi webrtcstream
  ([`070e773`](https://github.com/yeonhee7935/py-screen-grab/commit/070e7733193ade96a90bb884ac1b2dc80609d2c9))

- Update index.py to use WebcamGrabber for streaming
  ([`43015f7`](https://github.com/yeonhee7935/py-screen-grab/commit/43015f7e54382a4975e99af4d0655ee050b81d4e))


## v1.3.0 (2025-03-26)

### Chores

- Update README.md
  ([`9b7975f`](https://github.com/yeonhee7935/py-screen-grab/commit/9b7975f598a6e8f6e537bf4b8695bf0f7bac0763))

### Features

- Implement Real-Time Screen Sharing with WebRTC
  ([`d1c3200`](https://github.com/yeonhee7935/py-screen-grab/commit/d1c3200d6b3f4b48a12f10f26c94f5bcdf8c4465))

Added WebRTCStream class to support real-time streaming Integrated asynchronous streaming
  functionality into ScreenGrabber Implemented reactive frame streaming in RxJS style Managed WebRTC
  connections and ICE candidate handling Added test code and example page

### Refactoring

- Commit for ci/cd
  ([`42f4a7a`](https://github.com/yeonhee7935/py-screen-grab/commit/42f4a7a6457d8181fb4b01a250082e9f019e5228))

- Extract webrtc module(py_screen_grab -> examples)
  ([`b46f138`](https://github.com/yeonhee7935/py-screen-grab/commit/b46f138134d62739bcfe20c2f90f8d2c9a0c1692))


## v1.2.0 (2025-03-25)

### Chores

- Express return value
  ([`e34e414`](https://github.com/yeonhee7935/py-screen-grab/commit/e34e414cb9aad9f6d31314d084428c7c39b1c379))

### Features

- Enable set_window
  ([`88adb83`](https://github.com/yeonhee7935/py-screen-grab/commit/88adb835992e91b2417f49ebcf8f9584ba767304))

### Refactoring

- Install buipip dependencies before build
  ([`89b2775`](https://github.com/yeonhee7935/py-screen-grab/commit/89b27752d61ac74a4e9132fb463711dda41083cc))

- Install buipip dependencies before build
  ([`56fc072`](https://github.com/yeonhee7935/py-screen-grab/commit/56fc072beb6287b1e58b8c9ec5af4ce48a24f063))

- Update screen grabbing methods and improve method chaining
  ([`7c4746a`](https://github.com/yeonhee7935/py-screen-grab/commit/7c4746a9bdf3d678a0d3bd6a2bed9260fe7b4f1b))


## v1.1.0 (2025-03-24)

### Features

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

- Update CI config(workflows)
  ([`32aa88e`](https://github.com/yeonhee7935/py-screen-grab/commit/32aa88eb6f890cc9c4ee58ad6b41094eea85d3e8))

Automatically generated by python-semantic-release

feat: add download badge

1.1.0

refactor: add build_command

refactor: change semantic-release cmd

refactor: delete change log

refactor: add version var in setup.pyy

refactor: upload_to_pypi -> upload_to_repository

refactor: -vv -> version, publish

### Refactoring

- Add compensation values for window decorations
  ([`2e4484c`](https://github.com/yeonhee7935/py-screen-grab/commit/2e4484c8d85844dcb1cbba83de3e4108b2eb16e1))

- Adjust roi offset
  ([`07db044`](https://github.com/yeonhee7935/py-screen-grab/commit/07db0440252b5e1ad4e003d2091172ee6a7cc0d6))

- Build_commmand
  ([`b64aa35`](https://github.com/yeonhee7935/py-screen-grab/commit/b64aa351e612f792b1224426cbe9ca9a3298bf3d))

- Change test code
  ([`9d682e8`](https://github.com/yeonhee7935/py-screen-grab/commit/9d682e84dd09d9bd16d08c27905f1254ac41df90))

- Merge
  ([`94d9bbe`](https://github.com/yeonhee7935/py-screen-grab/commit/94d9bbe62c4e07110abd6e24be8882578daa2222))

- Setup dependencies in ci
  ([`af6bbc7`](https://github.com/yeonhee7935/py-screen-grab/commit/af6bbc7130b87bd42ebeba72d37af389082e72a8))

- Setup dependencies in ci
  ([`2eb2184`](https://github.com/yeonhee7935/py-screen-grab/commit/2eb2184c2a35f32b74edca3b4939e060860fb86c))

- Update pypi-publisher version
  ([`f962698`](https://github.com/yeonhee7935/py-screen-grab/commit/f962698ab33c7656d30585f062f1d0aad7ed1abc))

- Update pypi-publisher version
  ([`5c108ec`](https://github.com/yeonhee7935/py-screen-grab/commit/5c108ec5254a90e221fef7c10067a9f51cd49c32))

- Update pypi-publisher version
  ([`625e614`](https://github.com/yeonhee7935/py-screen-grab/commit/625e61487b784db04dbd1891fbd38797700157e8))

- Update pypi-publisher version
  ([`eb8cba8`](https://github.com/yeonhee7935/py-screen-grab/commit/eb8cba81233ccd33021f6d735f7be0e259bb78ad))

- Update workflow(inline -> plugin)
  ([`1a6bb01`](https://github.com/yeonhee7935/py-screen-grab/commit/1a6bb0117dab62d5064c9be4edc150267417ab07))


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
