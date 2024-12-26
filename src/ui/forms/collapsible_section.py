"""Collapsible section widget for organizing form elements."""
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class CollapsibleSection(QFrame):
    """A collapsible section with header and content."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.title = title
        self.is_expanded = True
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        # Title label
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(title_label)
        
        # Toggle button
        self.toggle_btn = QPushButton("▼")
        self.toggle_btn.setFixedSize(20, 20)
        self.toggle_btn.clicked.connect(self.toggle)
        header_layout.addWidget(self.toggle_btn)
        
        layout.addWidget(header)
        
        # Content
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self.content)
    
    def add_widget(self, widget: QWidget):
        """Add a widget to the content area."""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add a layout to the content area."""
        self.content_layout.addLayout(layout)
    
    def toggle(self):
        """Toggle the expanded state."""
        self.is_expanded = not self.is_expanded
        self.content.setVisible(self.is_expanded)
        self.toggle_btn.setText("▼" if self.is_expanded else "▶")
    
    def set_expanded(self, expanded: bool):
        """Set the expanded state."""
        if expanded != self.is_expanded:
            self.toggle()