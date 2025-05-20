"""Tests for the gallery view UI flow."""

import pytest
from PyQt6.QtWidgets import QLabel, QMenu, QPushButton, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QAction

from imagen_desktop.ui.features.gallery.gallery_view import GalleryView
from imagen_desktop.ui.features.gallery.widgets.product_grid import ProductGrid
from imagen_desktop.ui.features.gallery.widgets.product_strip import ProductStrip
from imagen_desktop.ui.shared.widgets.product_thumbnail import ProductThumbnail
from imagen_desktop.ui.shared.widgets.product_context_menu import ProductContextMenu
from imagen_desktop.core.models.product import Product


@pytest.fixture
def sample_products():
    """Create sample product data for testing."""
    return [
        Product(
            id="product1",
            name="Mountain Landscape",
            description="A beautiful mountain landscape",
            metadata={
                "prompt": "A beautiful mountain landscape",
                "model": "model1",
                "created_at": "2025-05-17T12:00:00Z"
            },
            file_path="/path/to/image1.png"
        ),
        Product(
            id="product2",
            name="Ocean Sunset",
            description="Sunset over the ocean",
            metadata={
                "prompt": "Sunset over the ocean",
                "model": "model1",
                "created_at": "2025-05-17T13:00:00Z"
            },
            file_path="/path/to/image2.png"
        ),
        Product(
            id="product3",
            name="Forest Path",
            description="A path through a dense forest",
            metadata={
                "prompt": "A path through a dense forest",
                "model": "model2",
                "created_at": "2025-05-17T14:00:00Z"
            },
            file_path="/path/to/image3.png"
        )
    ]


@pytest.mark.ui
def test_gallery_view_initialization(qtbot, mocker, sample_products):
    """Test that GalleryView initializes correctly."""
    # Mock the product repository
    mock_repo = mocker.patch("imagen_desktop.data.repositories.product_repository.ProductRepository").return_value
    mock_repo.get_all.return_value = sample_products
    
    # Mock the QPixmap loading
    mocker.patch.object(QPixmap, "load", return_value=True)
    
    # Create the gallery view
    gallery_view = GalleryView()
    qtbot.addWidget(gallery_view)
    
    # Check that both display modes are available
    assert gallery_view.findChild(ProductGrid) is not None, "Product grid not found"
    assert gallery_view.findChild(ProductStrip) is not None, "Product strip not found"
    
    # Wait for the view to load products
    qtbot.wait(100)
    
    # Check that products are loaded
    product_thumbnails = gallery_view.findChildren(ProductThumbnail)
    assert len(product_thumbnails) == len(sample_products), f"Expected {len(sample_products)} thumbnails, got {len(product_thumbnails)}"


@pytest.mark.ui
def test_gallery_view_switching(qtbot, mocker, sample_products):
    """Test switching between grid and strip views."""
    # Mock the product repository
    mock_repo = mocker.patch("imagen_desktop.data.repositories.product_repository.ProductRepository").return_value
    mock_repo.get_all.return_value = sample_products
    
    # Mock the QPixmap loading
    mocker.patch.object(QPixmap, "load", return_value=True)
    
    # Create the gallery view
    gallery_view = GalleryView()
    qtbot.addWidget(gallery_view)
    
    # Get the display mode buttons
    grid_button = None
    strip_button = None
    
    for button in gallery_view.findChildren(QPushButton):
        if button.toolTip() == "Grid View":
            grid_button = button
        elif button.toolTip() == "Strip View":
            strip_button = button
    
    assert grid_button is not None, "Grid view button not found"
    assert strip_button is not None, "Strip view button not found"
    
    # Get the display widgets
    grid_view = gallery_view.findChild(ProductGrid)
    strip_view = gallery_view.findChild(ProductStrip)
    
    # Check that grid view is initially visible and strip view is hidden
    assert grid_view.isVisible(), "Grid view should be initially visible"
    assert not strip_view.isVisible(), "Strip view should be initially hidden"
    
    # Switch to strip view
    qtbot.mouseClick(strip_button, Qt.MouseButton.LeftButton)
    
    # Check that strip view is now visible and grid view is hidden
    assert strip_view.isVisible(), "Strip view should be visible after switching"
    assert not grid_view.isVisible(), "Grid view should be hidden after switching"
    
    # Switch back to grid view
    qtbot.mouseClick(grid_button, Qt.MouseButton.LeftButton)
    
    # Check that grid view is visible and strip view is hidden again
    assert grid_view.isVisible(), "Grid view should be visible after switching back"
    assert not strip_view.isVisible(), "Strip view should be hidden after switching back"


@pytest.mark.ui
def test_product_context_menu(qtbot, mocker, sample_products):
    """Test that right-clicking a product thumbnail shows the context menu."""
    # Mock the product repository
    mock_repo = mocker.patch("imagen_desktop.data.repositories.product_repository.ProductRepository").return_value
    mock_repo.get_all.return_value = sample_products
    
    # Mock the QPixmap loading
    mocker.patch.object(QPixmap, "load", return_value=True)
    
    # Mock the context menu
    mock_menu = mocker.patch("imagen_desktop.ui.shared.widgets.product_context_menu.ProductContextMenu").return_value
    mock_menu.exec.return_value = None
    
    # Create the gallery view
    gallery_view = GalleryView()
    qtbot.addWidget(gallery_view)
    
    # Wait for the view to load products
    qtbot.wait(100)
    
    # Get the first product thumbnail
    thumbnails = gallery_view.findChildren(ProductThumbnail)
    assert len(thumbnails) > 0, "No product thumbnails found"
    
    # Simulate right-click on the thumbnail
    qtbot.mouseClick(thumbnails[0], Qt.MouseButton.RightButton)
    
    # Check that the context menu was shown
    mock_menu.exec.assert_called_once()


@pytest.mark.ui
def test_product_selection(qtbot, mocker, sample_products):
    """Test selecting a product in the gallery."""
    # Mock the product repository
    mock_repo = mocker.patch("imagen_desktop.data.repositories.product_repository.ProductRepository").return_value
    mock_repo.get_all.return_value = sample_products
    
    # Mock the QPixmap loading
    mocker.patch.object(QPixmap, "load", return_value=True)
    
    # Create the gallery view
    gallery_view = GalleryView()
    qtbot.addWidget(gallery_view)
    
    # Wait for the view to load products
    qtbot.wait(100)
    
    # Set up a signal spy to catch the product_selected signal
    with qtbot.waitSignal(gallery_view.product_selected) as signal_spy:
        # Get the first product thumbnail and click it
        thumbnails = gallery_view.findChildren(ProductThumbnail)
        qtbot.mouseClick(thumbnails[0], Qt.MouseButton.LeftButton)
    
    # Check that the signal was emitted with the correct product ID
    assert signal_spy.args[0] == sample_products[0].id, "Signal emitted with incorrect product ID"


@pytest.mark.ui
def test_gallery_filtering(qtbot, mocker, sample_products):
    """Test filtering products in the gallery."""
    # Mock the product repository
    mock_repo = mocker.patch("imagen_desktop.data.repositories.product_repository.ProductRepository").return_value
    mock_repo.get_all.return_value = sample_products
    mock_repo.search.return_value = [sample_products[0]]  # Only return the first product for search
    
    # Mock the QPixmap loading
    mocker.patch.object(QPixmap, "load", return_value=True)
    
    # Create the gallery view
    gallery_view = GalleryView()
    qtbot.addWidget(gallery_view)
    
    # Find the search box
    search_box = gallery_view.findChild(QLineEdit)
    assert search_box is not None, "Search box not found"
    
    # Wait for the view to load products
    qtbot.wait(100)
    
    # Check that all products are initially shown
    thumbnails_before = gallery_view.findChildren(ProductThumbnail)
    assert len(thumbnails_before) == len(sample_products), "All products should be initially shown"
    
    # Enter a search term
    qtbot.keyClicks(search_box, "mountain")
    qtbot.keyPress(search_box, Qt.Key.Key_Return)
    
    # Wait for the search to complete
    qtbot.wait(100)
    
    # Check that only filtered products are shown
    mock_repo.search.assert_called_once_with("mountain")
    
    # Get the visible thumbnails after filtering
    thumbnails_after = [t for t in gallery_view.findChildren(ProductThumbnail) if t.isVisible()]
    assert len(thumbnails_after) == 1, "Only one product should be shown after filtering"