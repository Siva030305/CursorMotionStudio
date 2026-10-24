========================================================================
                      CURSOR MOTION STUDIO v1.0.0
========================================================================
A lightweight, offline desktop application for Windows 10 and Windows 11.
Provides 5 bounded cursor movement modes, configurable countdown timer,
emergency stop mechanisms, and an independent Technology Stack display.

------------------------------------------------------------------------
1. FEATURES
------------------------------------------------------------------------
• 5 Specialized Cursor Movement Modes:
    1. Shake Mode      : Rapid, small jitter oscillation around anchor.
    2. Random Mode     : Randomized organic wander bounded by radius.
    3. Circle Mode     : Smooth continuous circular trajectory.
    4. Gentle Mode     : Subtle, breathing drift.
    5. Horizontal Mode : Side-to-side sweep along the horizontal axis.

• Safety & Motion Boundaries:
    - Initial maximum radius: strictly capped at 15 pixels (default: 6px).
    - Hard clamped to keep the cursor within screen boundaries.
    - Zero simulated clicks or keystrokes: pure safe coordinate motion.
    - Emergency Stop: Press [ESC] or push cursor to any screen corner.

• Configurable Countdown Timer:
    - Adjustable from 1 to 120 minutes.
    - Real-time digital MM:SS countdown with progress tracking.
    - Automatically stops cursor movement when timer reaches 00:00.

• Dedicated Technology Stack Display:
    - Displayed as a separate, independent card in the user interface.
    - Highlights: Python, PySide6, PyAutoGUI, and PyInstaller.

• Ultra-Compact Form Factor:
    - Tailored to approximately 325 × 540 pixels (matching Windows Calculator).
    - Modern dark theme with high contrast and DPI scaling safety.

• 100% Offline:
    - Zero telemetry, zero internet connection required, zero cloud servers.

------------------------------------------------------------------------
2. RUNNING THE APPLICATION
------------------------------------------------------------------------
Option A: Running Portable Executable (No Python Required)
---------------------------------------------------------
1. Extract "CursorMotionStudio-Portable.zip" (or open dist/exe/).
2. Double-click "CursorMotionStudio.exe".
3. The application will launch immediately without any setup.

Option B: Running from Python Source
------------------------------------
1. Ensure Python 3.10+ is installed on your system.
2. Install dependencies:
       pip install -r requirements.txt
3. Launch the application:
       python main.py

------------------------------------------------------------------------
3. BUILDING STANDALONE EXECUTABLE (.EXE & .ZIP)
------------------------------------------------------------------------
To rebuild the standalone executable and portable ZIP package:
1. Run:
       build.bat
2. The output files will be created in:
       dist/exe/CursorMotionStudio.exe
       dist/CursorMotionStudio-Portable.zip

------------------------------------------------------------------------
4. KEYBOARD SHORTCUTS & EMERGENCY STOP
------------------------------------------------------------------------
• [ESC]            : Immediately stops cursor movement.
• Screen Corners   : Moving the cursor to any of the 4 screen corners
                     triggers PyAutoGUI FailSafe to immediately stop motion.

========================================================================
(C) 2026 Cursor Motion Studio. Developed for offline Windows environments.
========================================================================
