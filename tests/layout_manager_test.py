"""
Tests for LayoutManager utility functions.
"""

import pytest
from lucidpy.models import Page, LayoutManager


class TestLayoutManagerGridLayout:
    """Test LayoutManager.grid_layout() method."""

    def test_grid_layout_basic(self):
        """Test basic grid layout with default spacing."""
        page = Page(id="test-page", title="Test")

        # Create 6 shapes
        shapes = [page.add_shape("rectangle", text=f"Shape {i}") for i in range(6)]

        # Apply 2x3 grid layout
        LayoutManager.grid_layout(shapes, columns=2)

        # Check positions (default spacing: 100x100, start: 50,50)
        expected_positions = [
            (50, 50),  # Row 0, Col 0
            (150, 50),  # Row 0, Col 1
            (50, 150),  # Row 1, Col 0
            (150, 150),  # Row 1, Col 1
            (50, 250),  # Row 2, Col 0
            (150, 250),  # Row 2, Col 1
        ]

        for i, (expected_x, expected_y) in enumerate(expected_positions):
            assert shapes[i].boundingBox["x"] == expected_x
            assert shapes[i].boundingBox["y"] == expected_y

    def test_grid_layout_custom_spacing(self):
        """Test grid layout with custom spacing."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("rectangle") for _ in range(4)]

        # Apply with custom spacing
        LayoutManager.grid_layout(
            shapes, columns=2, spacing_x=200, spacing_y=150, start_x=100, start_y=75
        )

        expected_positions = [
            (100, 75),  # Row 0, Col 0
            (300, 75),  # Row 0, Col 1 (100 + 200)
            (100, 225),  # Row 1, Col 0 (75 + 150)
            (300, 225),  # Row 1, Col 1
        ]

        for i, (expected_x, expected_y) in enumerate(expected_positions):
            assert shapes[i].boundingBox["x"] == expected_x
            assert shapes[i].boundingBox["y"] == expected_y

    def test_grid_layout_single_column(self):
        """Test grid layout with single column (vertical arrangement)."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("rectangle") for _ in range(3)]

        LayoutManager.grid_layout(shapes, columns=1, spacing_y=80)

        # All should be in same column (x=50), different rows
        for i, shape in enumerate(shapes):
            assert shape.boundingBox["x"] == 50
            assert shape.boundingBox["y"] == 50 + i * 80

    def test_grid_layout_single_row(self):
        """Test grid layout with more columns than shapes."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("rectangle") for _ in range(3)]

        LayoutManager.grid_layout(shapes, columns=5, spacing_x=120)

        # All should be in same row (y=50), different columns
        for i, shape in enumerate(shapes):
            assert shape.boundingBox["x"] == 50 + i * 120
            assert shape.boundingBox["y"] == 50

    def test_grid_layout_empty_list(self):
        """Test grid layout with empty shape list."""
        # Should not raise any exceptions
        LayoutManager.grid_layout([], columns=3)


class TestLayoutManagerHorizontalLayout:
    """Test LayoutManager.horizontal_layout() method."""

    def test_horizontal_layout_basic(self):
        """Test basic horizontal layout."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("rectangle", text=f"Shape {i}") for i in range(4)]

        LayoutManager.horizontal_layout(shapes)

        # Check positions (default spacing: 100, start_x: 50, y: 50)
        for i, shape in enumerate(shapes):
            assert shape.boundingBox["x"] == 50 + i * 100
            assert shape.boundingBox["y"] == 50

    def test_horizontal_layout_custom_params(self):
        """Test horizontal layout with custom parameters."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("circle") for _ in range(3)]

        LayoutManager.horizontal_layout(shapes, spacing=150, start_x=200, y=300)

        expected_x_positions = [200, 350, 500]  # 200, 200+150, 200+150*2

        for i, shape in enumerate(shapes):
            assert shape.boundingBox["x"] == expected_x_positions[i]
            assert shape.boundingBox["y"] == 300

    def test_horizontal_layout_single_shape(self):
        """Test horizontal layout with single shape."""
        page = Page(id="test-page", title="Test")

        shape = page.add_shape("rectangle")

        LayoutManager.horizontal_layout([shape], start_x=100, y=200)

        assert shape.boundingBox["x"] == 100
        assert shape.boundingBox["y"] == 200


class TestLayoutManagerVerticalLayout:
    """Test LayoutManager.vertical_layout() method."""

    def test_vertical_layout_basic(self):
        """Test basic vertical layout."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("rectangle", text=f"Shape {i}") for i in range(4)]

        LayoutManager.vertical_layout(shapes)

        # Check positions (default spacing: 100, x: 50, start_y: 50)
        for i, shape in enumerate(shapes):
            assert shape.boundingBox["x"] == 50
            assert shape.boundingBox["y"] == 50 + i * 100

    def test_vertical_layout_custom_params(self):
        """Test vertical layout with custom parameters."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("diamond") for _ in range(3)]

        LayoutManager.vertical_layout(shapes, spacing=120, x=250, start_y=100)

        expected_y_positions = [100, 220, 340]  # 100, 100+120, 100+120*2

        for i, shape in enumerate(shapes):
            assert shape.boundingBox["x"] == 250
            assert shape.boundingBox["y"] == expected_y_positions[i]

    def test_vertical_layout_single_shape(self):
        """Test vertical layout with single shape."""
        page = Page(id="test-page", title="Test")

        shape = page.add_shape("circle")

        LayoutManager.vertical_layout([shape], x=150, start_y=75)

        assert shape.boundingBox["x"] == 150
        assert shape.boundingBox["y"] == 75


class TestLayoutManagerCenterShape:
    """Test LayoutManager.center_shape() method."""

    def test_center_shape_default_container(self):
        """Test centering shape in default container."""
        page = Page(id="test-page", title="Test")

        # Create shape with known dimensions
        shape = page.add_shape("rectangle", width=100, height=80)

        LayoutManager.center_shape(shape)

        # Default container: 800x600
        # Expected position: ((800-100)/2, (600-80)/2) = (350, 260)
        assert shape.boundingBox["x"] == 350
        assert shape.boundingBox["y"] == 260

    def test_center_shape_custom_container(self):
        """Test centering shape in custom container."""
        page = Page(id="test-page", title="Test")

        shape = page.add_shape("circle", width=60, height=60)

        LayoutManager.center_shape(shape, container_width=400, container_height=300)

        # Expected position: ((400-60)/2, (300-60)/2) = (170, 120)
        assert shape.boundingBox["x"] == 170
        assert shape.boundingBox["y"] == 120

    def test_center_shape_larger_than_container(self):
        """Test centering shape larger than container."""
        page = Page(id="test-page", title="Test")

        shape = page.add_shape("rectangle", width=200, height=150)

        LayoutManager.center_shape(shape, container_width=100, container_height=100)

        # Should result in negative positions
        # Expected: ((100-200)/2, (100-150)/2) = (-50, -25)
        assert shape.boundingBox["x"] == -50
        assert shape.boundingBox["y"] == -25

    def test_center_shape_preserves_size(self):
        """Test that centering preserves shape size."""
        page = Page(id="test-page", title="Test")

        original_width = 120
        original_height = 90
        shape = page.add_shape(
            "rectangle", width=original_width, height=original_height
        )

        LayoutManager.center_shape(shape)

        # Size should be unchanged
        assert shape.boundingBox["w"] == original_width
        assert shape.boundingBox["h"] == original_height


class TestLayoutManagerCombinations:
    """Test combinations of layout operations."""

    def test_grid_then_center_adjustment(self):
        """Test applying grid layout then adjusting positions."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("rectangle") for _ in range(4)]

        # Apply grid layout
        LayoutManager.grid_layout(shapes, columns=2, spacing_x=100, spacing_y=100)

        # Verify grid layout applied
        assert shapes[0].boundingBox["x"] == 50  # Top-left
        assert shapes[1].boundingBox["x"] == 150  # Top-right

        # Center one specific shape
        LayoutManager.center_shape(shapes[0], container_width=200, container_height=200)

        # First shape should be centered, others unchanged
        assert shapes[0].boundingBox["x"] == 75  # (200-50)/2
        assert shapes[0].boundingBox["y"] == 75  # (200-50)/2
        assert shapes[1].boundingBox["x"] == 150  # Unchanged

    def test_mixed_layouts(self):
        """Test applying different layouts to different shape groups."""
        page = Page(id="test-page", title="Test")

        # Create two groups of shapes
        group1 = [page.add_shape("rectangle", text=f"Group1-{i}") for i in range(3)]
        group2 = [page.add_shape("circle", text=f"Group2-{i}") for i in range(3)]

        # Apply horizontal layout to group1
        LayoutManager.horizontal_layout(group1, start_x=50, y=100)

        # Apply vertical layout to group2
        LayoutManager.vertical_layout(group2, x=400, start_y=50)

        # Verify group1 is horizontal
        for i, shape in enumerate(group1):
            assert shape.boundingBox["x"] == 50 + i * 100
            assert shape.boundingBox["y"] == 100

        # Verify group2 is vertical
        for i, shape in enumerate(group2):
            assert shape.boundingBox["x"] == 400
            assert shape.boundingBox["y"] == 50 + i * 100
