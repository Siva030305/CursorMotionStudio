========================================================================
                      CURSOR MOTION STUDIO v1.3.0
========================================================================
An ultra-smooth, premium desktop application for Windows 10 and 11.
Provides 6 bounded cursor movement modes, a real-time motion preview
canvas, 250 Hz hardware pacing, high-speed multipliers up to 6.0x,
strictly 1-pixel imperceptible micro-shake, human-intervention auto-pause,
and dual glassmorphism themes (Midnight Obsidian & Aurora Platinum).

------------------------------------------------------------------------
1. FEATURES & HIGHLIGHTS
------------------------------------------------------------------------
• 6 Specialized Cursor Movement Modes:
    1. Circle Orbit        : Continuous circular orbital motion.
    2. Horizontal Sweep    : Smooth side-to-side harmonic sweep.
    3. Rapid Shake         : Dynamic high-frequency jitter tremor.
    4. 1-Pixel Micro-Shake : Strictly 1-pixel micro-vibration; 100% imperceptible at distance.
    5. Gentle Drift        : Slow, natural breathing Lissajous drift.
    6. Random Wander       : Multi-octave continuous harmonic drift.

• Real-Time Motion Preview Canvas:
    - 60 FPS simulated trajectory before moving the physical cursor.
    - Concentric safety reference rings (5px, 10px, ±15px limit).
    - Glowing animated cursor vector and fading neon trail.
    - Live HUD telemetry displaying dX, dY, and active speed multiplier.
    - 0 physical clicks / simulated hardware keystrokes.

• Speed Multiplier Engine:
    - 1.0x Standard, 2.0x High, 3.5x Very High, 6.0x Maximum ⚡.
    - 250 Hz hardware pacing loop (4ms tick) with Windows 1ms kernel timer.
    - Dynamic delta-t accumulation: change speeds on-the-fly without jerks.

• Strictly 1-Pixel Imperceptible Micro-Shake:
    - Guaranteed Euclidean displacement never exceeds 1.0 pixel (dx² + dy² <= 1.0).
    - Dominant-axis projection prevents diagonal sqrt(2) ≈ 1.41px integer overshoot.
    - High-frequency micro-oscillation keeps the OS continuously awake.

• Smart Human Intervention Detection & Auto-Pause:
    - Detects when you physically move the mouse.
    - Automatically pauses motion and safely resumes 5 seconds after you finish.

• Safety & Motion Boundaries:
    - Strictly bounded radius (<= 15px max).
    - Clamped 2px away from screen edges to avoid failsafe false-triggers.
    - Emergency Stop: Press [ESC] or push cursor to any screen corner.

• Dual Premium Themes:
    - Midnight Obsidian Luxe (Dark) and Aurora Platinum Glass (Light).

------------------------------------------------------------------------
2. RUNNING THE APPLICATION
------------------------------------------------------------------------
Option A: Running Portable Executable (No Python Required)
---------------------------------------------------------
1. Extract "dist/CursorMotionStudio-Portable.zip" (or open dist/exe/).
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
    build.bat

Outputs:
    - Standalone EXE : dist\exe\CursorMotionStudio.exe
    - Portable ZIP   : dist\CursorMotionStudio-Portable.zip
========================================================================
