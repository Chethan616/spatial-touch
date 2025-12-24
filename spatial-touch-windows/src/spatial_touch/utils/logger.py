"""
Logger Module

Provides structured logging configuration for Spatial Touch.
Supports file and console output with rotation.
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# Default log format
DEFAULT_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Module-level logger cache
_loggers: dict[str, logging.Logger] = {}


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True,
    format_string: Optional[str] = None,
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 3
) -> logging.Logger:
    """Configure logging for Spatial Touch.
    
    Sets up logging with optional file output and console output.
    Uses rotating file handler to manage log file size.
    
    Args:
        level: Log level ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        log_file: Path to log file (None for no file logging)
        console: Whether to log to console
        format_string: Custom log format string
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Root logger instance
        
    Example:
        >>> setup_logging(level="DEBUG", log_file="logs/app.log")
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    # Get root logger for the package
    root_logger = logging.getLogger("spatial_touch")
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        format_string or DEFAULT_FORMAT,
        datefmt=DEFAULT_DATE_FORMAT
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger("mediapipe").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    if name not in _loggers:
        # Ensure it's under our namespace
        if not name.startswith("spatial_touch"):
            name = f"spatial_touch.{name}"
        _loggers[name] = logging.getLogger(name)
    
    return _loggers[name]


class PerformanceLogger:
    """Logger for performance metrics.
    
    Tracks timing and performance data with structured output.
    
    Example:
        >>> perf = PerformanceLogger("processing")
        >>> perf.start()
        >>> # ... do work ...
        >>> perf.end()  # Logs duration
    """
    
    def __init__(self, operation: str, logger: Optional[logging.Logger] = None) -> None:
        """Initialize performance logger.
        
        Args:
            operation: Name of the operation being tracked
            logger: Logger instance (creates one if not provided)
        """
        self.operation = operation
        self.logger = logger or get_logger("performance")
        self._start_time: Optional[float] = None
        self._samples: list[float] = []
        self._max_samples = 100
    
    def start(self) -> None:
        """Start timing."""
        import time
        self._start_time = time.perf_counter()
    
    def end(self, log: bool = True) -> float:
        """End timing and optionally log.
        
        Args:
            log: Whether to log the duration
            
        Returns:
            Duration in milliseconds
        """
        import time
        
        if self._start_time is None:
            return 0.0
        
        duration = (time.perf_counter() - self._start_time) * 1000  # ms
        self._samples.append(duration)
        
        # Keep only recent samples
        if len(self._samples) > self._max_samples:
            self._samples = self._samples[-self._max_samples:]
        
        if log:
            self.logger.debug(
                "%s completed in %.2f ms (avg: %.2f ms)",
                self.operation,
                duration,
                self.average
            )
        
        self._start_time = None
        return duration
    
    @property
    def average(self) -> float:
        """Get average duration in milliseconds."""
        if not self._samples:
            return 0.0
        return sum(self._samples) / len(self._samples)
    
    @property
    def min(self) -> float:
        """Get minimum duration."""
        return min(self._samples) if self._samples else 0.0
    
    @property
    def max(self) -> float:
        """Get maximum duration."""
        return max(self._samples) if self._samples else 0.0
    
    def report(self) -> dict:
        """Get performance report.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            "operation": self.operation,
            "samples": len(self._samples),
            "average_ms": self.average,
            "min_ms": self.min,
            "max_ms": self.max,
        }


class ContextLogger:
    """Context manager for logging with timing.
    
    Example:
        >>> with ContextLogger("processing frame", logger):
        ...     process_frame()
        # Logs: "processing frame completed in X.XX ms"
    """
    
    def __init__(
        self, 
        message: str, 
        logger: Optional[logging.Logger] = None,
        level: int = logging.DEBUG
    ) -> None:
        """Initialize context logger.
        
        Args:
            message: Log message
            logger: Logger instance
            level: Log level
        """
        self.message = message
        self.logger = logger or get_logger("context")
        self.level = level
        self._start_time: Optional[float] = None
    
    def __enter__(self) -> ContextLogger:
        """Enter context."""
        import time
        self._start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit context and log."""
        import time
        
        duration = (time.perf_counter() - self._start_time) * 1000
        
        if exc_type:
            self.logger.error(
                "%s failed after %.2f ms: %s",
                self.message, duration, exc_val
            )
        else:
            self.logger.log(
                self.level,
                "%s completed in %.2f ms",
                self.message, duration
            )


def log_exception(
    logger: logging.Logger,
    message: str,
    exc: Exception,
    include_traceback: bool = True
) -> None:
    """Log an exception with optional traceback.
    
    Args:
        logger: Logger instance
        message: Context message
        exc: Exception to log
        include_traceback: Whether to include full traceback
    """
    if include_traceback:
        logger.exception("%s: %s", message, exc)
    else:
        logger.error("%s: %s", message, exc)
