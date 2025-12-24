"""
Spatial Touch - Touchless Computer Control

A Windows background application that enables touchless control of the 
computer using hand gestures captured via the laptop webcam.

Copyright (c) 2024 Spatial Touch Contributors
Licensed under the MIT License
"""

__version__ = "0.1.0"
__author__ = "Spatial Touch Contributors"
__license__ = "MIT"

from spatial_touch.main import SpatialTouchController

__all__ = ["SpatialTouchController", "__version__"]
