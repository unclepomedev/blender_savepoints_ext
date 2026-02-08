# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from pathlib import Path

import bpy

_local_core = None
_core_available = False
_injected_sys_paths = []

_vendor_path = Path(__file__).parent.parent / "vendor"
_vendor_core_path = _vendor_path / "savepoints"

if (_vendor_core_path / "__init__.py").exists():
    print(f"[SavePoints Ext] Dev mode detected. Loading core from: {_vendor_path}")

    _wheels_path = _vendor_core_path / "wheels"
    if _wheels_path.exists():
        for wheel_file in _wheels_path.glob("*.whl"):
            wheel_str = str(wheel_file)
            if wheel_str not in sys.path:
                sys.path.insert(0, wheel_str)
                _injected_sys_paths.append(wheel_str)
                print(f"[SavePoints Ext] Loaded dependency wheel: {wheel_file.name}")

    vendor_str = str(_vendor_path)
    if vendor_str not in sys.path:
        sys.path.insert(0, vendor_str)
        _injected_sys_paths.append(vendor_str)

    try:
        import savepoints

        _local_core = savepoints
        _core_available = True
    except Exception as e:
        print(f"[SavePoints Ext] Failed to load local core: {e}")
        import traceback

        traceback.print_exc()

else:
    try:
        import savepoints

        _core_available = True
    except ImportError:
        _core_available = False

if _core_available:
    try:
        from . import operators, panel

        _ext_modules = [
            operators,
            panel,
        ]
    except ImportError as e:
        print(f"[SavePoints Ext] Error importing extension modules: {e}")
        _ext_modules = []
        _core_available = False
else:
    _ext_modules = []


def register():
    if not _core_available:

        def draw_error(self, _context):
            self.layout.label(text="SavePoints Core is missing or failed to load!", icon="ERROR")
            self.layout.label(text="Please install 'SavePoints' main addon first.")
            self.layout.label(text="Check console for dependency errors.")

        bpy.context.window_manager.popup_menu(draw_error, title="SavePoints Error", icon="CANCEL")
        raise RuntimeError("SavePoints Core is required but not found/loaded.")

    if _local_core:
        try:
            _local_core.register()
        except Exception as ex:
            print(f"[SavePoints Ext] Local Core register error: {ex}")
            raise

    registered = []
    for mod in _ext_modules:
        try:
            mod.register()
            registered.append(mod)
        except Exception as ex:
            print(f"[SavePoints Ext] Register error in {mod.__name__}: {ex}")
            for rmod in reversed(registered):
                try:
                    rmod.unregister()
                except Exception as ex:
                    print(f"[SavePoints Ext] ext unregister error: {ex}")
                    pass
            if _local_core:
                try:
                    _local_core.unregister()
                except Exception as ex:
                    print(f"[SavePoints Ext] local_core unregister error: {ex}")
                    pass
            raise


def unregister():
    for mod in reversed(_ext_modules):
        try:
            mod.unregister()
        except Exception as ex:
            print(f"[SavePoints Ext] Unregister error: {ex}")

    if _local_core:
        try:
            _local_core.unregister()
        except Exception as ex:
            print(f"[SavePoints Ext] Local Core unregister error: {ex}")

    if _injected_sys_paths:
        for path in _injected_sys_paths:
            if path in sys.path:
                try:
                    sys.path.remove(path)
                except ValueError:
                    pass
        _injected_sys_paths.clear()
