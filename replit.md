# Overview

The MAJESTIC Punishment Stacker is a Python-based GUI application designed for automated stacking and escalation of gaming punishments. It processes punishment commands like `/ajail`, `/ban`, `/warn`, and `/hardban`, automatically consolidating multiple infractions for the same player and escalating punishments based on severity and frequency. The application features a modern Tkinter-based interface with multiple themes and flexible configuration options for moderation teams.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Architecture
- **Single-file monolithic design**: The main application logic resides in `punishment_stacker.py` with minimal dependencies
- **Desktop-first approach**: Built primarily for Windows desktop environments with GUI fallback detection for web-based platforms like Replit
- **Configuration-driven logic**: All punishment rules, limits, and escalation formulas are configurable through the `PunishmentStackerConfig` class

## GUI Framework
- **Tkinter-based interface**: Uses Python's built-in Tkinter library for cross-platform compatibility
- **Theme system**: Supports multiple visual themes (dark, classic, majestic) with customizable color schemes
- **Responsive layout**: Uses grid-based layout management for consistent appearance across screen sizes

## Data Processing Pipeline
- **Command parsing**: Regular expressions extract player IDs, durations, reasons, and moderator information from text commands
- **Stacking logic**: Groups punishments by player ID and applies escalation rules based on total duration and violation types
- **Output generation**: Produces consolidated punishment commands with merged reasons and calculated durations

## Business Logic Components
- **Escalation engine**: Automatically converts jail time to bans/warnings based on configurable thresholds
- **Reason consolidation**: Merges multiple infractions with intelligent date and moderator grouping
- **Violation limits**: Enforces specific limits for different violation types (ПГО categories)
- **Multi-formula support**: Supports linear, exponential, and custom escalation formulas

## File Management
- **Text-based I/O**: Reads commands from `.txt` files and outputs processed results
- **Configuration persistence**: Saves and loads settings in JSON format
- **Sample data included**: Ships with test and real command examples for demonstration

## Error Handling
- **Graceful degradation**: Falls back to console mode when GUI is unavailable
- **Input validation**: Validates command format and provides warnings for malformed entries
- **Exception management**: Comprehensive error handling with user-friendly messages

# External Dependencies

## Core Dependencies
- **Python 3.7+**: Minimum Python version requirement
- **tkinter**: Built-in GUI framework (standard library)
- **tkinter.ttk**: Enhanced widgets for modern appearance (standard library)
- **re**: Regular expression processing (standard library)
- **json**: Configuration serialization (standard library)
- **os**: File system operations (standard library)

## Development Tools
- **PyInstaller**: Optional dependency for creating standalone executables
- **typing**: Type hints for better code documentation (standard library)

## Runtime Environment
- **Desktop environment**: Requires windowing system for GUI functionality
- **File system access**: Needs read/write permissions for configuration and data files
- **Console fallback**: Can operate in text mode when GUI is unavailable

## Distribution Format
- **Source files**: Distributed as Python source code for maximum compatibility
- **Executable option**: Can be compiled to standalone `.exe` using PyInstaller
- **Cross-platform**: Compatible with Windows, Linux, and macOS desktop environments

Note: The application is designed to be self-contained with no external service dependencies or network requirements.