"""
Tests for Page helper methods (add_shape, connect_shapes, etc.).
"""

import pytest
from lucidpy.models import Page, Shape, Line, Style, Stroke, Rectangle, Circle


class TestPageAddShape:
    """Test the Page.add_shape() method."""

    def test_add_shape_basic(self):
        """Test basic shape addition."""
        page = Page(id="test-page", title="Test")

        shape = page.add_shape(
            "rectangle", x=100, y=200, width=80, height=60, text="Test Shape"
        )

        assert shape.type == "rectangle"
        assert shape.boundingBox == {"x": 100, "y": 200, "w": 80, "h": 60}
        assert shape.text == "Test Shape"
        assert shape.id == "shape-1"
        assert len(page.shapes) == 1
        assert page.shapes[0] == shape

    def test_add_shape_with_defaults(self):
        """Test shape addition with default parameters."""
        page = Page(id="test-page", title="Test")

        shape = page.add_shape()  # All defaults

        assert shape.type == "rectangle"  # Default type
        assert shape.boundingBox == {"x": 0, "y": 0, "w": 50, "h": 50}
        assert shape.text == ""

    def test_add_shape_with_style(self):
        """Test adding shape with custom style."""
        page = Page(id="test-page", title="Test")

        custom_style = Style(
            fill={"type": "color", "color": "#FF0000"},
            stroke=Stroke(color="#000000", width=2),
        )

        shape = page.add_shape("circle", style=custom_style)

        assert shape.style.fill["color"] == "#FF0000"
        assert shape.style.stroke.width == 2

    def test_add_shape_all_types(self):
        """Test adding all supported shape types."""
        page = Page(id="test-page", title="Test")

        shape_types = [
            "rectangle",
            "circle",
            "diamond",
            "cloud",
            "hexagon",
            "octagon",
            "isocolesTriangle",
            "rightTriangle",
            "cross",
        ]

        for shape_type in shape_types:
            shape = page.add_shape(shape_type, text=f"Test {shape_type}")
            assert shape.type == shape_type
            assert shape.text == f"Test {shape_type}"

        assert len(page.shapes) == len(shape_types)

    def test_add_existing_shape_object(self):
        """Test adding an existing Shape object."""
        page = Page(id="test-page", title="Test")

        # Create shape separately
        existing_shape = Rectangle.create(x=50, y=50, text="Existing")

        # Add to page
        added_shape = page.add_shape(shape=existing_shape)

        assert added_shape == existing_shape
        assert added_shape.id == "shape-1"  # Gets auto-generated ID
        assert len(page.shapes) == 1

    def test_add_shape_with_manual_id(self):
        """Test adding shape with pre-existing ID."""
        page = Page(id="test-page", title="Test")

        shape = Shape(id="manual-id", type="rectangle", text="Manual ID")
        added_shape = page.add_shape(shape=shape)

        assert added_shape.id == "manual-id"

        # Next shape should get auto-generated ID
        next_shape = page.add_shape("circle")
        assert next_shape.id == "shape-1"


class TestPageAddLine:
    """Test the Page.add_line() method."""

    def test_add_line_between_shapes(self):
        """Test adding line between two shapes."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle", text="Start")
        shape2 = page.add_shape("circle", text="End")

        line = page.add_line(shape1, shape2, text="connection")

        assert line.id == "line-1"
        assert line.endpoint1.shapeId == shape1.id
        assert line.endpoint2.shapeId == shape2.id
        assert len(line.text) == 1
        assert line.text[0].text == "connection"
        assert len(page.lines) == 1

    def test_add_line_different_types(self):
        """Test adding lines with different types."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle")
        shape2 = page.add_shape("circle")
        shape3 = page.add_shape("diamond")

        straight_line = page.add_line(shape1, shape2, line_type="straight")
        elbow_line = page.add_line(shape2, shape3, line_type="elbow")
        curved_line = page.add_line(shape1, shape3, line_type="curved")

        assert straight_line.lineType == "straight"
        assert elbow_line.lineType == "elbow"
        assert curved_line.lineType == "curved"
        assert len(page.lines) == 3

    def test_add_line_with_custom_stroke(self):
        """Test adding line with custom stroke."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle")
        shape2 = page.add_shape("circle")

        custom_stroke = Stroke(color="#FF0000", width=3, style="dashed")
        line = page.add_line(shape1, shape2, stroke=custom_stroke)

        assert line.stroke.color == "#FF0000"
        assert line.stroke.width == 3
        assert line.stroke.style == "dashed"

    def test_add_line_without_shapes(self):
        """Test adding line without connecting to shapes."""
        page = Page(id="test-page", title="Test")

        line = page.add_line(line_type="curved")

        assert line.id == "line-1"
        assert line.lineType == "curved"
        assert line.endpoint1 is None
        assert line.endpoint2 is None
        assert len(page.lines) == 1


class TestPageConnectShapes:
    """Test the Page.connect_shapes() method."""

    def test_connect_shapes_basic(self):
        """Test basic shape connection."""
        page = Page(id="test-page", title="Test")

        start = page.add_shape("circle", text="Start")
        end = page.add_shape("rectangle", text="End")

        connection = page.connect_shapes(start, end)

        assert connection.id == "line-1"
        assert connection.endpoint1.shapeId == start.id
        assert connection.endpoint2.shapeId == end.id
        assert len(page.lines) == 1

    def test_connect_shapes_with_text(self):
        """Test connecting shapes with text label."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("diamond", text="Decision")
        shape2 = page.add_shape("rectangle", text="Process")

        connection = page.connect_shapes(shape1, shape2, text="Yes")

        assert len(connection.text) == 1
        assert connection.text[0].text == "Yes"

    def test_connect_shapes_different_line_types(self):
        """Test connecting shapes with different line types."""
        page = Page(id="test-page", title="Test")

        shapes = [page.add_shape("rectangle") for _ in range(4)]

        line1 = page.connect_shapes(shapes[0], shapes[1], line_type="straight")
        line2 = page.connect_shapes(shapes[1], shapes[2], line_type="elbow")
        line3 = page.connect_shapes(shapes[2], shapes[3], line_type="curved")

        assert line1.lineType == "straight"
        assert line2.lineType == "elbow"
        assert line3.lineType == "curved"

    def test_connect_shapes_with_stroke_style(self):
        """Test connecting shapes with custom stroke."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle")
        shape2 = page.add_shape("circle")

        stroke = Stroke(color="#00FF00", width=2, style="dotted")
        connection = page.connect_shapes(shape1, shape2, stroke=stroke)

        assert connection.stroke.color == "#00FF00"
        assert connection.stroke.width == 2
        assert connection.stroke.style == "dotted"

    def test_multiple_connections(self):
        """Test creating multiple connections between different shapes."""
        page = Page(id="test-page", title="Test")

        # Create a small network
        center = page.add_shape("circle", text="Center")
        nodes = [page.add_shape("rectangle", text=f"Node {i}") for i in range(3)]

        # Connect center to all nodes
        connections = []
        for i, node in enumerate(nodes):
            conn = page.connect_shapes(center, node, text=f"Link {i}")
            connections.append(conn)

        assert len(page.lines) == 3
        assert all(conn.endpoint1.shapeId == center.id for conn in connections)
        assert [conn.endpoint2.shapeId for conn in connections] == [
            node.id for node in nodes
        ]


class TestPageIDManagement:
    """Test ID management within pages."""

    def test_id_uniqueness_across_shapes_and_lines(self):
        """Test that shapes and lines get unique IDs."""
        page = Page(id="test-page", title="Test")

        # Add multiple shapes and lines
        shapes = [page.add_shape("rectangle") for _ in range(5)]
        lines = []

        # Connect shapes in a chain
        for i in range(len(shapes) - 1):
            line = page.connect_shapes(shapes[i], shapes[i + 1])
            lines.append(line)

        # Check all IDs are unique
        shape_ids = [shape.id for shape in shapes]
        line_ids = [line.id for line in lines]
        all_ids = shape_ids + line_ids

        assert len(set(all_ids)) == len(all_ids)  # All unique
        assert shape_ids == ["shape-1", "shape-2", "shape-3", "shape-4", "shape-5"]
        assert line_ids == ["line-1", "line-2", "line-3", "line-4"]

    def test_id_manager_shared_between_operations(self):
        """Test that the same ID manager is used for all operations."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle")
        line1 = page.add_line()
        shape2 = page.add_shape("circle")

        shape3 = page.add_shape("diamond")
        line2 = page.connect_shapes(shape1, shape2)

        # IDs should be sequential across different operations
        assert shape1.id == "shape-1"
        assert line1.id == "line-1"
        assert shape2.id == "shape-2"
        assert shape3.id == "shape-3"
        assert line2.id == "line-2"
