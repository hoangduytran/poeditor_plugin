Here’s a step-by-step design for your menu system refactor:

1. **Move Menu Logic to MainAppWindow:**
   - Relocate all menu creation, action instantiation, and signal connection logic from `POEditorWindow` to `MainAppWindow`.
   - `MainAppWindow` will own the menu bar and manage all QActions.

2. **Remove Preferences Menu:**
   - Omit any menu or submenu labeled “Preferences” or similar.
   - All settings should be accessed via the “Settings” system.

3. **Menu Context and Activation:**
   - On application start, only “File” > “Open” is enabled; all other actions (Save, Save As, Edit, etc.) are disabled.
   - When a `POEditorWindow` instance is created and set as active, enable all actions that affect the document (Save, Save As, Edit, etc.).
   - When no editor is active, revert to only “Open” being enabled.

4. **Menu Structure Example:**
   - File
     - Open (always enabled)
     - Save (enabled only with active editor)
     - Save As... (enabled only with active editor)
     - Close (enabled only with active editor)
     - Exit/Quit
   - Edit
     - Undo, Redo, Cut, Copy, Paste, etc. (enabled only with active editor)
   - View, Tools, etc. (as needed, enabled contextually)
   - Settings (if you want a menu entry for it, otherwise omit)

5. **Implementation Details:**
   - Store all QActions as attributes of `MainAppWindow`.
   - When a `POEditorWindow` is created or closed, call a method in `MainAppWindow` to update the enabled/disabled state of actions.
   - Use signals/slots or direct method calls to communicate editor activation/deactivation.

6. **Submenu Handling:**
   - Submenus (e.g., Edit > Find/Replace) should be created in `MainAppWindow` and enabled/disabled as above.

7. **No Preferences Menu:**
   - Ensure there is no “Preferences” or “Options” menu; all such functionality should be under “Settings” or handled elsewhere.
