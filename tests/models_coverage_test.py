"""
Tests to improve coverage for models.py module.
"""

import pytest
from pydantic import ValidationError
from lucidpy.models import (
    Color, ID, IDManager, Shape, Line, Page, Document,
    LayoutManager, PageBuilder, Cross, Rectangle, Circle,
    Diamond, Cloud, Hexagon, Octagon, IsocolesTriangle, RightTriangle,
    ShapeEndpoint, LineEndpoint, Style, Stroke, Text
)


class TestColorValidation:
    """Test Color custom validation."""

    def test_color_valid_formats(self):
        """Test valid color formats."""
        # These should not raise exceptions
        valid_colors = ["#FF0000", "#f00", "#123456", "#ABC"]

        for color in valid_colors:
            validated = Color.validate(color)
            assert validated == color

    def test_color_invalid_formats(self):
        """Test invalid color formats."""
        invalid_colors = [
            "FF0000",  # Missing #
            "#GG0000",  # Invalid hex character
            "#FF00",   # Wrong length
            "#FF00000", # Too long
            "",        # Empty
            "#",       # Just #
        ]

        for color in invalid_colors:
            with pytest.raises(ValueError, match="Invalid color format"):
                Color.validate(color)

    def test_color_non_string(self):
        """Test color validation with non-string input."""
        with pytest.raises(TypeError, match="string required"):
            Color.validate(123)

        with pytest.raises(TypeError, match="string required"):
            Color.validate(None)


class TestIDValidation:
    """Test ID custom validation."""

    def test_id_valid_formats(self):
        """Test valid ID formats."""
        valid_ids = [
            "a",
            "shape-1",
            "line_test",
            "item.123",
            "test~item",
            "a" * 36,  # Max length
        ]

        for id_val in valid_ids:
            validated = ID.validate(id_val)
            assert validated == id_val

    def test_id_invalid_formats(self):
        """Test invalid ID formats."""
        invalid_ids = [
            "a" * 37,  # Too long
            "",        # Empty
            "test@item",  # Invalid character
            "test#item",  # Invalid character
            "test item",  # Space not allowed
        ]

        for id_val in invalid_ids:
            with pytest.raises(ValueError, match="Invalid ID format"):
                ID.validate(id_val)

    def test_id_non_string(self):
        """Test ID validation with non-string input."""
        with pytest.raises(TypeError, match="string required"):
            ID.validate(123)


class TestIDManagerAdvanced:
    """Test advanced IDManager functionality."""

    def test_generate_custom_prefix_uuid_path(self):
        """Test UUID generation for custom prefixes."""
        manager = IDManager()

        # Generate ID with custom prefix (should use UUID)
        custom_id = manager.generate_id("custom-prefix")

        assert custom_id.startswith("custom-prefix-")
        # UUID part comes after the full prefix including hyphen
        parts = custom_id.split("-")
        assert len(parts) >= 3  # custom, prefix, uuid_part
        uuid_part = parts[-1]  # Last part is the UUID segment
        assert len(uuid_part) == 8  # UUID segment length

    def test_generate_id_collision_with_custom_prefix(self):
        """Test collision handling with custom prefixes."""
        manager = IDManager()

        # Pre-register a UUID-style ID
        manager.register_id("custom-abcd1234")

        # Generate new custom ID - should get different UUID
        new_id = manager.generate_id("custom")
        assert new_id.startswith("custom-")
        assert new_id != "custom-abcd1234"


class TestLucidBaseAutoID:
    """Test LucidBase automatic ID generation."""

    def test_lucid_base_with_id_manager(self):
        """Test LucidBase when ID manager is available."""
        # Create a shape that will have an ID manager attached
        page = Page(id="test-page", title="Test")
        shape = page.add_shape("rectangle")  # This sets _id_manager

        # Verify ID was auto-generated
        assert shape.id is not None
        assert shape.id.startswith("shape-")

    def test_lucid_base_without_id_manager(self):
        """Test LucidBase when no ID manager is available."""
        # Create shape directly without ID manager
        shape = Shape(type="rectangle")

        # Should have None ID since no ID manager
        assert shape.id is None


class TestShapeFactoryMethods:
    """Test shape factory method coverage."""

    def test_all_shape_factory_methods(self):
        """Test factory methods for all shape types."""
        shapes_to_test = [
            (Rectangle, {"x": 10, "y": 20, "width": 30, "height": 40}),
            (Circle, {"x": 50, "y": 60, "radius": 25}),
            (Cloud, {"x": 70, "y": 80, "width": 90, "height": 100}),
            (Diamond, {"x": 110, "y": 120, "width": 130, "height": 140}),
            (Hexagon, {"x": 150, "y": 160, "width": 170, "height": 180}),
            (Octagon, {"x": 190, "y": 200, "width": 210, "height": 220}),
            (IsocolesTriangle, {"x": 230, "y": 240, "width": 250, "height": 260}),
            (RightTriangle, {"x": 270, "y": 280, "width": 290, "height": 300}),
        ]

        for shape_class, params in shapes_to_test:
            shape = shape_class.create(text="Test Shape", **params)

            assert shape.text == "Test Shape"
            assert shape.id is None  # No ID manager in direct creation

            # Check bounding box was set correctly
            if "radius" in params:
                # Circle uses diameter
                expected_size = params["radius"] * 2
                assert shape.boundingBox["w"] == expected_size
                assert shape.boundingBox["h"] == expected_size
            else:
                assert shape.boundingBox["w"] == params["width"]
                assert shape.boundingBox["h"] == params["height"]


class TestCrossShapeValidation:
    """Test Cross shape specific validation."""

    def test_cross_valid_indents(self):
        """Test valid indent values for Cross shape."""
        valid_values = [0.0, 0.25, 0.5]

        for val in valid_values:
            cross = Cross(id="test", x=val, y=val)
            assert cross.x == val
            assert cross.y == val

    def test_cross_invalid_indents(self):
        """Test invalid indent values for Cross shape."""
        invalid_values = [-0.1, 0.6, 1.0, 2.0]

        for val in invalid_values:
            with pytest.raises(ValidationError):
                Cross(id="test", x=val)

            with pytest.raises(ValidationError):
                Cross(id="test", y=val)


class TestLineEndpointValidation:
    """Test LineEndpoint validation."""

    def test_line_endpoint_valid_position(self):
        """Test valid position values."""
        valid_positions = [0.0, 0.5, 1.0]

        for pos in valid_positions:
            endpoint = LineEndpoint(line_id="line-1", position=pos, line=None)
            assert endpoint.position == pos

    def test_line_endpoint_invalid_position(self):
        """Test invalid position values."""
        invalid_positions = [-0.1, 1.1, 2.0]

        for pos in invalid_positions:
            with pytest.raises(ValidationError):
                LineEndpoint(line_id="line-1", position=pos, line=None)


class TestShapeEndpointValidation:
    """Test ShapeEndpoint validation."""

    def test_shape_endpoint_with_shape_object(self):
        """Test ShapeEndpoint with Shape object."""
        shape = Rectangle.create(text="Test")
        shape.id = "shape-123"  # Set ID manually

        endpoint = ShapeEndpoint(shapeId=shape)
        assert endpoint.shapeId == "shape-123"

    def test_shape_endpoint_with_string_id(self):
        """Test ShapeEndpoint with string ID."""
        endpoint = ShapeEndpoint(shapeId="shape-456")
        assert endpoint.shapeId == "shape-456"

    def test_shape_endpoint_invalid_position(self):
        """Test ShapeEndpoint with invalid position."""
        with pytest.raises(ValidationError):
            ShapeEndpoint(shapeId="shape-1", position={"x": 1.5, "y": 0.5})

        with pytest.raises(ValidationError):
            ShapeEndpoint(shapeId="shape-1", position={"x": 0.5})  # Missing y

    def test_shape_endpoint_invalid_shapeId_type(self):
        """Test ShapeEndpoint with invalid shapeId type."""
        with pytest.raises(ValidationError):
            ShapeEndpoint(shapeId=123)  # Neither string, ID, nor Shape


class TestPageBuilderEdgeCases:
    """Test PageBuilder edge cases."""

    def test_page_builder_apply_grid_layout_empty_page(self):
        """Test applying grid layout to page with no shapes."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        # Should not raise error
        result = builder.apply_grid_layout()
        assert result == builder

    def test_page_builder_connect_last_two_edge_cases(self):
        """Test connect_last_two with edge cases."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        # No shapes - should not error
        result = builder.connect_last_two()
        assert result == builder
        assert len(page.lines) == 0

        # One shape - should not error
        builder.add_rectangle(text="Only shape")
        result = builder.connect_last_two()
        assert result == builder
        assert len(page.lines) == 0


class TestLayoutManagerEdgeCases:
    """Test LayoutManager edge cases."""

    def test_layout_manager_empty_shape_lists(self):
        """Test layout methods with empty shape lists."""
        # Should not raise errors
        LayoutManager.grid_layout([])
        LayoutManager.horizontal_layout([])
        LayoutManager.vertical_layout([])

    def test_layout_manager_single_shape(self):
        """Test layout methods with single shape."""
        page = Page(id="test-page", title="Test")
        shape = page.add_shape("rectangle")

        # All should work with single shape
        LayoutManager.grid_layout([shape], columns=1)
        LayoutManager.horizontal_layout([shape])
        LayoutManager.vertical_layout([shape])
        LayoutManager.center_shape(shape)


class TestDocumentEdgeCases:
    """Test Document edge cases."""

    def test_document_with_existing_pages(self):
        """Test Document with pre-existing pages."""
        existing_page = Page(id="existing-page", title="Existing")
        doc = Document(pages=[existing_page])

        # Add another page
        new_page = doc.add_page("New Page")

        assert len(doc.pages) == 2
        assert new_page.id == "page-1"  # Should not conflict with existing-page

    def test_document_page_id_collision_avoidance(self):
        """Test that document avoids page ID collisions."""
        doc = Document()

        # Pre-register a page ID
        doc._global_id_manager.register_id("page-1")

        # Add page - should get page-2
        page = doc.add_page("Test Page")
        assert page.id == "page-2"


class TestLineConnectionEdgeCases:
    """Test Line connection edge cases."""

    def test_line_connect_shapes_with_stroke_override(self):
        """Test Line.connect_shapes with stroke override."""
        page = Page(id="test-page", title="Test")
        shape1 = page.add_shape("rectangle")
        shape2 = page.add_shape("circle")

        line = Line(id="test-line")
        custom_stroke = Stroke(color="#FF0000", width=3)

        result = line.connect_shapes(shape1, shape2, stroke=custom_stroke, text="test")

        assert result == line
        assert line.stroke.color == "#FF0000"
        assert line.stroke.width == 3
        assert len(line.text) == 1
        assert line.text[0].text == "test"

    def test_line_create_between_factory(self):
        """Test Line.create_between factory method."""
        page = Page(id="test-page", title="Test")
        shape1 = page.add_shape("rectangle")
        shape2 = page.add_shape("circle")

        line = Line.create_between(shape1, shape2, line_type="elbow", text="connection")

        assert line.lineType == "elbow"
        assert line.endpoint1.shapeId == shape1.id
        assert line.endpoint2.shapeId == shape2.id
        assert len(line.text) == 1
        assert line.text[0].text == "connection"
