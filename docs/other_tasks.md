
# Other Tasks

This is a scratchpad of tasks not yet added to Github issues

## General

- Finish integrating SQLite over the file system storage
    - Retaining images on the file system to be imported etc.

## Settings / Config

- Add a settings window..
- That can maintain the API key
- That can set an output directory or data directory

## Model Manager

- Add details about a selected model
- Show more models

## Generation 

- 
- respect model defaults

### Model Selector

- Add FLUX Schnell to the default list (DONE)

## Gallery

- Add management options (delete, rename, etc.)
- Add information about the generation (model, prompt, parameters, etc.) - maybe in a sidebar

## Carousel

- Move to main window (not separate)
- Fix next/previous buttons

## Testing

- Fix UI test failures:
  - Update tests/ui/features/test_gallery_view.py - QAction import error from PyQt6.QtWidgets
  - Update tests/ui/features/test_model_selection.py - ModelManagerDialog import error
  - Increase test coverage to meet minimum requirements

## Advanced

