"""Tests for the model selection UI flow."""

import pytest
from PyQt6.QtWidgets import QComboBox, QPushButton
from PyQt6.QtCore import Qt

from imagen_desktop.ui.features.generation.forms.model_selector import ModelSelector
from imagen_desktop.ui.dialogs.model_manager import ModelManagerDialog


@pytest.mark.ui
def test_model_selector_initialization(qtbot, mocker):
    """Test that ModelSelector initializes correctly with default models."""
    # Mock the model data
    mock_models = [
        {"name": "Test Model 1", "id": "model1", "version": "1.0"},
        {"name": "Test Model 2", "id": "model2", "version": "2.0"}
    ]
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_available_models",
        return_value=mock_models
    )
    
    # Create the model selector widget
    model_selector = ModelSelector()
    qtbot.addWidget(model_selector)
    
    # Get the combobox from the model selector
    combo_box = model_selector.findChild(QComboBox)
    assert combo_box is not None, "ComboBox not found in ModelSelector"
    
    # Check that models are loaded
    assert combo_box.count() == len(mock_models), f"Expected {len(mock_models)} models, got {combo_box.count()}"
    
    # Check model names are correctly displayed
    for i, model in enumerate(mock_models):
        assert combo_box.itemText(i) == model["name"], f"Model name mismatch at index {i}"


@pytest.mark.ui
def test_model_selection_change(qtbot, mocker):
    """Test that changing the selected model emits the correct signal."""
    # Mock the model data
    mock_models = [
        {"name": "Test Model 1", "id": "model1", "version": "1.0"},
        {"name": "Test Model 2", "id": "model2", "version": "2.0"}
    ]
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_available_models",
        return_value=mock_models
    )
    
    # Create the model selector widget
    model_selector = ModelSelector()
    qtbot.addWidget(model_selector)
    
    # Get the combobox from the model selector
    combo_box = model_selector.findChild(QComboBox)
    
    # Create a signal spy to check if model_changed signal is emitted
    with qtbot.waitSignal(model_selector.model_changed) as signal_spy:
        # Change the selection
        combo_box.setCurrentIndex(1)
    
    # Check that the signal was emitted with the correct model ID
    assert signal_spy.args[0] == mock_models[1]["id"], "Signal emitted with incorrect model ID"


@pytest.mark.ui
def test_open_model_manager_dialog(qtbot, mocker):
    """Test that clicking the manage button opens the model manager dialog."""
    # Mock the model data
    mock_models = [
        {"name": "Test Model 1", "id": "model1", "version": "1.0"}
    ]
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_available_models",
        return_value=mock_models
    )
    
    # Mock the model manager dialog 
    mock_dialog = mocker.patch("imagen_desktop.ui.dialogs.model_manager.ModelManagerDialog")
    mock_dialog.return_value.exec.return_value = True
    
    # Create the model selector widget
    model_selector = ModelSelector()
    qtbot.addWidget(model_selector)
    
    # Find the manage button
    manage_button = None
    for button in model_selector.findChildren(QPushButton):
        if button.text() == "Manage Models":
            manage_button = button
            break
    
    assert manage_button is not None, "Manage Models button not found"
    
    # Click the manage button
    qtbot.mouseClick(manage_button, Qt.MouseButton.LeftButton)
    
    # Verify that the dialog was created and shown
    mock_dialog.assert_called_once()
    mock_dialog.return_value.exec.assert_called_once()


@pytest.mark.ui
def test_model_manager_dialog(qtbot, mocker):
    """Test the model manager dialog functionality."""
    # Mock the model data
    mock_models = [
        {"name": "Test Model 1", "id": "model1", "version": "1.0"},
        {"name": "Test Model 2", "id": "model2", "version": "2.0"}
    ]
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_available_models",
        return_value=mock_models
    )
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_model_details",
        return_value={"name": "Test Model 1", "description": "A test model", "owner": "test-user"}
    )
    
    # Create the dialog
    dialog = ModelManagerDialog()
    qtbot.addWidget(dialog)
    
    # Check that the dialog shows the correct number of models
    assert dialog.model_list.count() == len(mock_models), "Dialog should show all models"
    
    # Select a model and check that details are displayed
    with qtbot.waitSignal(dialog.model_list.currentItemChanged):
        dialog.model_list.setCurrentRow(0)
    
    # Check that details are shown for the selected model
    assert "Test Model 1" in dialog.model_details.toPlainText(), "Model name should be in details"
    assert "A test model" in dialog.model_details.toPlainText(), "Model description should be in details"