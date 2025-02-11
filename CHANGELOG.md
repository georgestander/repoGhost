# Changelog

All notable changes to RepoGhost will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-02-11

### Changed
- Updated build configuration and housekeeping files
- No functional changes to the package

## [0.2.1] - 2025-02-11

### Added
- Code snippets support in summaries
- Snippets are now stored alongside summaries in the output
- Backward compatibility for reading older cache files without snippets

### Changed
- Modified summarize_chunk to return both summary and snippets
- Updated data structures to store snippets information
- Improved JSON output format to include code snippets

## [0.2.0] - Previous Release

### Added
- Initial public release
- Basic repository summarization
- Chunk-based code analysis
- Cache system for unchanged files
- Progress bar and rich console output
- OpenAI GPT-4 integration

### Changed
- Moved core functionality to separate modules
- Improved error handling and logging
