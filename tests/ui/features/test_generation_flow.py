"""Tests for the image generation UI flow."""

import pytest
from PyQt6.QtWidgets import QLineEdit, QPushButton, QProgressBar, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from imagen_desktop.ui.features.generation.generation_form import GenerationForm
from imagen_desktop.ui.features.generation.forms.prompt_input import PromptInput
from imagen_desktop.ui.features.generation.forms.model_selector import ModelSelector
from imagen_desktop.ui.features.generation.forms.generation_params import GenerationParams
from imagen_desktop.core.models.generation import GenerationStatus


@pytest.mark.ui
def test_generation_form_initialization(qtbot, mocker):
    """Test that GenerationForm initializes correctly with all expected components."""
    # Mock the API client
    mocker.patch("imagen_desktop.api.client.ReplicateClient")
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_available_models",
        return_value=[{"name": "Test Model", "id": "model1", "version": "1.0"}]
    )
    
    # Create the generation form
    form = GenerationForm()
    qtbot.addWidget(form)
    
    # Check that main components exist
    assert form.findChild(PromptInput) is not None, "Prompt input not found"
    assert form.findChild(ModelSelector) is not None, "Model selector not found"
    assert form.findChild(GenerationParams) is not None, "Generation parameters not found"
    
    # Check that generate button exists
    generate_button = None
    for button in form.findChildren(QPushButton):
        if "Generate" in button.text():
            generate_button = button
            break
    
    assert generate_button is not None, "Generate button not found"


@pytest.mark.ui
def test_generation_flow(qtbot, mocker):
    """Test the end-to-end image generation flow."""
    # Mock the API client
    mock_client = mocker.patch("imagen_desktop.api.client.ReplicateClient").return_value
    mock_client.generate_image.return_value = "dummy-prediction-id"
    
    # Mock the prediction manager
    mock_prediction_manager = mocker.patch("imagen_desktop.api.prediction_manager.PredictionManager").return_value
    mock_prediction_manager.start_polling.return_value = None
    
    # Mock the model manager
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_available_models",
        return_value=[{"name": "Test Model", "id": "model1", "version": "1.0"}]
    )
    
    # Create the generation form
    form = GenerationForm()
    qtbot.addWidget(form)
    
    # Find key components
    prompt_input = form.findChild(PromptInput)
    prompt_field = prompt_input.findChild(QLineEdit)
    generate_button = None
    for button in form.findChildren(QPushButton):
        if "Generate" in button.text():
            generate_button = button
            break
    
    # Set a prompt
    qtbot.keyClicks(prompt_field, "A beautiful mountain landscape")
    
    # Click generate
    qtbot.mouseClick(generate_button, Qt.MouseButton.LeftButton)
    
    # Check that the API was called with the right parameters
    mock_client.generate_image.assert_called_once()
    call_args = mock_client.generate_image.call_args[0]
    assert call_args[0] == "model1", "Wrong model ID passed to generate_image"
    assert "A beautiful mountain landscape" in call_args[1], "Prompt not passed correctly"
    
    # Check that prediction polling was started
    mock_prediction_manager.start_polling.assert_called_once()


@pytest.mark.ui
def test_generation_progress_updates(qtbot, mocker):
    """Test that generation progress updates correctly."""
    # Mock the API client and prediction manager
    mock_client = mocker.patch("imagen_desktop.api.client.ReplicateClient").return_value
    mock_client.generate_image.return_value = "dummy-prediction-id"
    
    # Mock the model manager
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_available_models",
        return_value=[{"name": "Test Model", "id": "model1", "version": "1.0"}]
    )
    
    # Create the generation form
    form = GenerationForm()
    qtbot.addWidget(form)
    
    # Find the progress bar
    progress_bar = form.findChild(QProgressBar)
    assert progress_bar is not None, "Progress bar not found"
    
    # Find the status label
    status_label = None
    for label in form.findChildren(QLabel):
        if "Status" in label.text():
            status_label = label
            break
    
    assert status_label is not None, "Status label not found"
    
    # Simulate generation started
    form.update_generation_status({"status": GenerationStatus.PROCESSING, "progress": 25})
    
    # Check that UI reflects the processing state
    assert progress_bar.value() == 25, "Progress bar should show 25%"
    assert "Processing" in status_label.text(), "Status should show Processing"
    
    # Simulate generation completed
    form.update_generation_status({"status": GenerationStatus.COMPLETED, "progress": 100})
    
    # Check that UI reflects the completed state
    assert progress_bar.value() == 100, "Progress bar should show 100%"
    assert "Completed" in status_label.text(), "Status should show Completed"


@pytest.mark.ui
def test_generation_error_handling(qtbot, mocker):
    """Test error handling in the generation flow."""
    # Mock the API client to raise an exception
    mock_client = mocker.patch("imagen_desktop.api.client.ReplicateClient").return_value
    mock_client.generate_image.side_effect = Exception("API Error")
    
    # Mock the model manager
    mocker.patch(
        "imagen_desktop.api.model_manager.ReplicateModelManager.get_available_models",
        return_value=[{"name": "Test Model", "id": "model1", "version": "1.0"}]
    )
    
    # Mock the error dialog
    mock_error_dialog = mocker.patch("PyQt6.QtWidgets.QMessageBox.critical")
    
    # Create the generation form
    form = GenerationForm()
    qtbot.addWidget(form)
    
    # Find key components
    prompt_input = form.findChild(PromptInput)
    prompt_field = prompt_input.findChild(QLineEdit)
    generate_button = None
    for button in form.findChildren(QPushButton):
        if "Generate" in button.text():
            generate_button = button
            break
    
    # Set a prompt
    qtbot.keyClicks(prompt_field, "A beautiful mountain landscape")
    
    # Click generate
    qtbot.mouseClick(generate_button, Qt.MouseButton.LeftButton)
    
    # Check that error dialog was shown
    mock_error_dialog.assert_called_once()
    assert "API Error" in mock_error_dialog.call_args[0][1], "Error message should contain the exception message"