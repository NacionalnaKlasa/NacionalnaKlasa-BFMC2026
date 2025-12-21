# BFMC 2026

Repository used by team **NacionalnaKlasa**

# Logger Library

A thread-safe Python logging library with color-coded console output and automatic file logging.

## Features

- **Thread-safe logging** with internal queue management
- **Color-coded console output** (INFO, WARNING, ERROR)
- **Automatic file logging** to timestamped log files
- **Non-blocking logging** with background thread processing
- **Multiple log levels** with flexible API

## Installation

Copy the `Logger` directory to your project:

```
your_project/
├── Logger/
│   ├── Color.py
│   ├── Logger.py
│   ├── Logger_Base.py
│   └── Queue.py
└── main.py
```

## Quick Start

```python
from Logger.Logger import Logger

# Initialize the logger
Logger()

# Log messages
Logger.logi("This is an info message")
Logger.logw("This is a warning message")
Logger.loge("This is an error message")

# Stop the logger when done
Logger.stop()
```

## Usage

### Basic Logging

The library provides three convenience methods for different log levels:

```python
Logger.logi("Information message")    # INFO level - white text
Logger.logw("Warning message")        # WARNING level - yellow text
Logger.loge("Error message")          # ERROR level - red text
```

### Generic Log Method

You can also use the generic `log()` method with a log level parameter:

```python
# Using integer log levels
Logger.log("Info message", 0)      # INFO
Logger.log("Warning message", 1)   # WARNING
Logger.log("Error message", 2)     # ERROR

# Using string log levels
Logger.log("Info message", "INFO")
Logger.log("Warning message", "WARNING")
Logger.log("Error message", "ERROR")
```

### Complete Example

```python
from Logger.Logger import Logger
import time

# Initialize logger
running = True
Logger()

services = [Logger]

counter = 0
while running:
    try:
        Logger.logi("Processing iteration...")
        time.sleep(2)

        # Alternate between log levels
        Logger.log("Dynamic log message", counter % 3)
        counter += 1

    except KeyboardInterrupt:
        running = False
        for service in reversed(services):
            try:
                print("Stopping service: " + str(service))
                service.stop()
            except Exception as e:
                print(f"Error stopping service: {e}")
```

## Log Files

The logger automatically creates log files in the `./logs/` directory with the following naming convention:

```
logger-YYYY-MM-DD_HH-MM-SS.txt
```

Example: `logger-2024-12-10_14-30-45.txt`

### File Configuration

You can customize the log file location and naming in `Logger_Base.py`:

```python
Log_file_path = "./logs/"           # Directory for log files
Log_file_name_prefix = "logger-"    # Prefix for log files
Log_file_name_sufix = ".txt"        # File extension
```

## Log Levels

| Level | Integer | String | Color | Description |
|-------|---------|--------|-------|-------------|
| INFO | 0 | "INFO" | White | General information |
| WARNING | 1 | "WARNING" | Yellow | Warning messages |
| ERROR | 2 | "ERROR" | Red | Error messages |

## Thread Safety

The logger uses internal queues and threading locks to ensure thread-safe operation. Multiple threads can log messages simultaneously without conflicts.

### How It Works

1. Log messages are added to priority queues (ERROR > WARNING > INFO)
2. A background thread processes messages from queues
3. Messages are written to both console (with colors) and log file
4. Thread synchronization ensures no message loss

## Best Practices

1. **Initialize once**: Call `Logger()` only once at application startup
2. **Stop gracefully**: Always call `Logger.stop()` before exiting
3. **Use try-except**: Wrap your main loop to ensure proper cleanup
4. **Check return values**: Log methods return `True` on success

```python
if Logger.logi("Important message"):
    # Message queued successfully
    pass
```

## API Reference

### Initialization

```python
Logger()
```

Initializes the logger, creates the background thread, and sets up log files.

### Logging Methods

```python
Logger.logi(msg: str) -> bool
```
Logs an INFO level message.

```python
Logger.logw(msg: str) -> bool
```
Logs a WARNING level message.

```python
Logger.loge(msg: str) -> bool
```
Logs an ERROR level message.

```python
Logger.log(msg: str, log_level: int|str) -> bool
```
Logs a message with specified log level (0-2 or "INFO"/"WARNING"/"ERROR").

### Cleanup

```python
Logger.stop()
```
Stops the background thread and closes log files. Always call this before application exit.

## Troubleshooting

### Log directory not created

If you see a warning about the log directory not existing, the logger will automatically create it. Ensure your application has write permissions.

### Messages not appearing

- Check that `Logger()` was called to initialize
- Verify the background thread is running
- Ensure `Logger.stop()` hasn't been called prematurely

### Thread not stopping

Make sure to call `Logger.stop()` in your exception handlers and cleanup code.

## License

This library is provided as-is for educational and commercial use.