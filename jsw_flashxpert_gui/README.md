# JSW FlashXpert - lightweight portable exe build

This folder packages `jsw_gui.py` (the ECU flashing GUI) into a single
portable Windows `.exe` with PyInstaller.

## Why the previous build was ~500MB

The app itself is tiny. It only uses:

- stdlib: `tkinter`, `ctypes`, `threading`, `time`, `os`, `sys`, `traceback`,
  `subprocess`, `zlib`
- one small pure-Python third-party package: `intelhex`

`PCANBasic.py` talks to the CAN driver via
`ctypes.windll.LoadLibrary("PCANBasic")` at **runtime** - the DLL is not
imported by Python and PyInstaller never bundles it. (The PEAK PCAN driver
must simply be installed on whatever machine runs the exe, same as before.)

None of that adds up to 500MB. A build that size means PyInstaller was run
inside a non-isolated interpreter (system Python with lots of packages
installed globally, or an Anaconda/Miniconda environment) and it picked up
unrelated heavy packages - numpy, pandas, matplotlib, PyQt, scipy, etc. -
that happened to be importable in that environment, or `--add-data` pointed
at a folder that included a full venv/site-packages by accident.

The fix is not code changes, it's building from a **clean, isolated
virtual environment** that only has this app's actual dependencies
installed, which is what `build.bat` and `jsw_flashxpert.spec` do here.

## Build (on Windows)

1. Install Python 3.10+ from python.org (not Anaconda) if you don't have it.
2. Open a plain `cmd`/PowerShell in this folder (do **not** use an Anaconda
   prompt, and do **not** run this from a venv/conda env that already has
   other packages installed).
3. Run:

   ```
   build.bat
   ```

   This creates a fresh `.venv`, installs only `intelhex` + `pyinstaller`,
   and builds via `jsw_flashxpert.spec`.
4. The exe is at `dist\JSW_FlashXpert.exe`. It's a single portable file -
   copy it anywhere, no installer needed.

Expect roughly **15-25 MB**, not 500MB.

## Optional: shrink further with UPX

PyInstaller will use UPX automatically if it's on your `PATH`, compressing
the exe further (usually another 30-50%):

1. Download UPX from https://github.com/upx/upx/releases (Windows zip).
2. Extract it and add the folder to your `PATH`, or drop `upx.exe` into this
   project folder.
3. Re-run `build.bat`.

If UPX isn't present, PyInstaller just skips compression - the build still
succeeds, it's only a little bigger.

## If your build is still huge

Almost always caused by building from the wrong Python:

- Run `where python` / `where pip` before building and make sure they point
  inside `.venv`, not `C:\ProgramData\Anaconda3\...` or a global install.
- Run `pip list` inside the activated `.venv` right after `pip install -r
  requirements.txt` - it should show only `intelhex`, `pyinstaller`, and
  their few small transitive deps. If you see numpy/pandas/scipy/etc. there,
  something leaked into the venv (e.g. it wasn't created with `--clear`, or
  you used `python -m venv --system-site-packages`) - delete `.venv` and
  recreate it.
- Check `build\JSW_FlashXpert\warn-JSW_FlashXpert.txt` after a build - it
  lists every module PyInstaller decided to include; anything unexpected in
  there points at the culprit.
