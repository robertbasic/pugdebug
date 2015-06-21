# Change Log

## [Unreleased][unrealeased]
### Added
 - Display current project name in window title

### Changed
 - Use mono fonts in sub-windows

### Fixed
 - Fix for GTK critical errors on Ubuntu
 - Do not jump to top of the file every time a debugging session starts
 - Updating settings now updates current project's settings as well
 - Deleting current project doesn't break pugdebug any more
 - Breakpoints do not dissapear any more when debugging multiple requests

### Removed

## [1.0.0-beta.1] - 2015-06-10

### Added
 - Simple build file for Windows

### Fixed
 - Tries debugging requests even when the XDEBUG_SESSION_START param is not set

## [1.0.0-beta] - 2015-06-07
### Added
 - Set debugger features during an active debugging session
 - Confirm deleting a project
 - Improved support for debugging multiple requests
 - Added the change log file

### Changed
 - Set debugger features in the post_start action

### Fixed
 - Non-existent file after mapping
