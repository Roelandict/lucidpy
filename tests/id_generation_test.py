"""
Tests for automatic ID generation functionality.
"""

import pytest
from lucidpy.models import IDManager, Document, Page, Shape, Line


class TestIDManager:
    """Test the IDManager class."""

    def test_generate_id_with_prefix(self):
        """Test ID generation with specific prefix."""
        manager = IDManager()

        # Test known prefixes
        shape_id = manager.generate_id("shape")
        assert shape_id == "shape-1"

        line_id = manager.generate_id("line")
        assert line_id == "line-1"

        # Test sequential generation
        shape_id2 = manager.generate_id("shape")
        assert shape_id2 == "shape-2"

    def test_generate_id_with_custom_prefix(self):
        """Test ID generation with custom prefix."""
        manager = IDManager()

        custom_id = manager.generate_id("custom")
        assert custom_id.startswith("custom-")
        assert len(custom_id.split("-")[1]) == 8  # UUID segment

    def test_register_existing_id(self):
        """Test registering existing IDs."""
        manager = IDManager()

        # Register an existing ID
        manager.register_id("shape-5")

        # Generate new ID should not conflict
        new_id = manager.generate_id("shape")
        assert new_id == "shape-1"

        # Check availability
        assert not manager.is_available("shape-5")
        assert manager.is_available("shape-10")

    def test_unique_id_generation(self):
        """Test that generated IDs are unique."""
        manager = IDManager()

        # Generate many IDs
        ids = []
        for _ in range(100):
            ids.append(manager.generate_id("test"))

        # Check uniqueness
        assert len(set(ids)) == len(ids)

    def test_collision_avoidance(self):
        """Test that ID generation avoids registered IDs."""
        manager = IDManager()

        # Register shape-1 and shape-2
        manager.register_id("shape-1")
        manager.register_id("shape-2")

        # Next generated ID should be shape-3
        new_id = manager.generate_id("shape")
        assert new_id == "shape-3"


class TestDocumentIDGeneration:
    """Test ID generation at the Document level."""

    def test_document_create_with_auto_id(self):
        """Test document creation with automatic page ID."""
        doc = Document.create("Test Document")

        assert len(doc.pages) == 1
        page = doc.pages[0]
        assert page.id == "page-1"
        assert page.title == "Test Document"

    def test_add_multiple_pages(self):
        """Test adding multiple pages generates unique IDs."""
        doc = Document()

        page1 = doc.add_page("Page 1")
        page2 = doc.add_page("Page 2")
        page3 = doc.add_page("Page 3")

        assert page1.id == "page-1"
        assert page2.id == "page-2"
        assert page3.id == "page-3"

    def test_document_with_existing_page_id(self):
        """Test adding page with existing ID."""
        doc = Document()

        # Create page with specific ID
        page = Page(id="custom-page", title="Custom Page")
        doc.pages.append(page)

        # Add another page - should get auto-generated ID
        new_page = doc.add_page("Auto Page")
        assert new_page.id == "page-1"


class TestPageIDGeneration:
    """Test ID generation at the Page level."""

    def test_page_add_shape_auto_id(self):
        """Test adding shapes with automatic ID generation."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle", text="Shape 1")
        shape2 = page.add_shape("circle", text="Shape 2")

        assert shape1.id == "shape-1"
        assert shape2.id == "shape-2"

    def test_page_add_line_auto_id(self):
        """Test adding lines with automatic ID generation."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle")
        shape2 = page.add_shape("circle")

        line1 = page.connect_shapes(shape1, shape2)
        line2 = page.add_line()  # Line without connections

        assert line1.id == "line-1"
        assert line2.id == "line-2"

    def test_existing_shapes_id_registration(self):
        """Test that existing shapes are registered with ID manager."""
        # Create shapes with manual IDs
        shape1 = Shape(id="existing-1", type="rectangle")
        shape2 = Shape(id="existing-2", type="circle")

        page = Page(id="test-page", title="Test", shapes=[shape1, shape2])

        # Add new shape - should not conflict
        new_shape = page.add_shape("diamond")
        assert new_shape.id == "shape-1"  # Doesn't conflict with existing-1


class TestShapeIDGeneration:
    """Test shape creation with ID generation."""

    def test_shape_factory_methods(self):
        """Test that shape factory methods respect ID generation."""
        from lucidpy.models import Rectangle, Circle, Diamond

        # Direct creation should allow None ID
        rect = Rectangle.create(text="Test Rectangle")
        assert rect.id is None  # No ID manager attached

        circle = Circle.create(radius=30, text="Test Circle")
        assert circle.id is None

    def test_shape_with_manual_id(self):
        """Test creating shapes with manual IDs."""
        page = Page(id="test-page", title="Test")

        # Add shape with manual ID
        manual_shape = Shape(id="manual-shape", type="rectangle")
        added_shape = page.add_shape(shape=manual_shape)

        assert added_shape.id == "manual-shape"

        # Next auto-generated shape should not conflict
        auto_shape = page.add_shape("circle")
        assert auto_shape.id == "shape-1"


class TestLineIDGeneration:
    """Test line creation with ID generation."""

    def test_line_creation_auto_id(self):
        """Test line creation with automatic ID."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle")
        shape2 = page.add_shape("circle")

        # Create line with automatic ID
        line = page.connect_shapes(shape1, shape2, text="connection")

        assert line.id == "line-1"
        assert len(line.text) == 1
        assert line.text[0].text == "connection"

    def test_line_factory_method(self):
        """Test Line.create_between factory method."""
        page = Page(id="test-page", title="Test")

        shape1 = page.add_shape("rectangle")
        shape2 = page.add_shape("circle")

        # Use factory method
        from lucidpy.models import Line

        line = Line.create_between(shape1, shape2, text="test")

        # Add to page to get ID
        line.id = page._id_manager.generate_id("line")
        page.lines.append(line)

        assert line.id == "line-1"
        assert line.endpoint1.shapeId == shape1.id
        assert line.endpoint2.shapeId == shape2.id
