"""
Spatial Touch REST API Module

Provides HTTP endpoints for controlling the application from external clients
like the Flutter settings app.
"""

from .server import APIServer, APIServerConfig, create_api_app

__all__ = ["APIServer", "APIServerConfig", "create_api_app"]
