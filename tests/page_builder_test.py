"""
Tests for PageBuilder fluent interface pattern.
"""

import pytest
from lucidpy.models import Page, PageBuilder, LayoutManager


class TestPageBuilderBasics:
    """Test basic PageBuilder functionality."""

    def test_page_builder_creation(self):
        """Test creating a PageBuilder instance."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        assert builder.page == page

    def test_page_builder_build(self):
        """Test that build() returns the page."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        result = builder.build()
        assert result == page


class TestPageBuilderShapeAddition:
    """Test adding shapes through PageBuilder."""

    def test_add_shape_basic(self):
        """Test basic shape addition with chaining."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        result = builder.add_shape("rectangle", x=100, y=200, text="Test")

        # Should return builder for chaining
        assert isinstance(result, PageBuilder)
        assert result == builder

        # Shape should be added to page
        assert len(page.shapes) == 1
        shape = page.shapes[0]
        assert shape.type == "rectangle"
        assert shape.boundingBox["x"] == 100
        assert shape.boundingBox["y"] == 200
        assert shape.text == "Test"

    def test_add_rectangle(self):
        """Test add_rectangle() convenience method."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        result = builder.add_rectangle(x=50, y=75, width=120, height=80, text="Rectangle")

        assert isinstance(result, PageBuilder)
        assert len(page.shapes) == 1

        shape = page.shapes[0]
        assert shape.type == "rectangle"
        assert shape.boundingBox == {"x": 50, "y": 75, "w": 120, "h": 80}
        assert shape.text == "Rectangle"

    def test_add_circle(self):
        """Test add_circle() convenience method."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        result = builder.add_circle(x=100, y=150, radius=30, text="Circle")

        assert isinstance(result, PageBuilder)
        assert len(page.shapes) == 1

        shape = page.shapes[0]
        assert shape.type == "circle"
        assert shape.boundingBox == {"x": 100, "y": 150, "w": 60, "h": 60}  # diameter = 2*radius
        assert shape.text == "Circle"

    def test_add_diamond(self):
        """Test add_diamond() convenience method."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        result = builder.add_diamond(x=200, y=250, width=100, height=100, text="Diamond")

        assert isinstance(result, PageBuilder)
        assert len(page.shapes) == 1

        shape = page.shapes[0]
        assert shape.type == "diamond"
        assert shape.boundingBox == {"x": 200, "y": 250, "w": 100, "h": 100}
        assert shape.text == "Diamond"


class TestPageBuilderChaining:
    """Test method chaining in PageBuilder."""

    def test_chain_multiple_shapes(self):
        """Test chaining multiple shape additions."""
        page = Page(id="test-page", title="Test")

        result = (PageBuilder(page)
                 .add_rectangle(x=0, y=0, text="Start")
                 .add_circle(x=150, y=0, radius=25, text="Middle")
                 .add_diamond(x=300, y=0, text="End")
                 .build())

        assert result == page
        assert len(page.shapes) == 3

        # Check shape types and positions
        assert page.shapes[0].type == "rectangle"
        assert page.shapes[0].text == "Start"
        assert page.shapes[1].type == "circle"
        assert page.shapes[1].text == "Middle"
        assert page.shapes[2].type == "diamond"
        assert page.shapes[2].text == "End"

    def test_chain_with_connections(self):
        """Test chaining shapes with connections."""
        page = Page(id="test-page", title="Test")

        (PageBuilder(page)
         .add_rectangle(text="Step 1")
         .add_rectangle(text="Step 2")
         .connect_last_two()
         .add_rectangle(text="Step 3")
         .connect_last_two(text="Next")
         .build())

        assert len(page.shapes) == 3
        assert len(page.lines) == 2

        # Check connections
        line1 = page.lines[0]
        assert line1.endpoint1.shapeId == page.shapes[0].id
        assert line1.endpoint2.shapeId == page.shapes[1].id

        line2 = page.lines[1]
        assert line2.endpoint1.shapeId == page.shapes[1].id
        assert line2.endpoint2.shapeId == page.shapes[2].id
        assert line2.text[0].text == "Next"


class TestPageBuilderConnections:
    """Test connection methods in PageBuilder."""

    def test_connect_last_two_basic(self):
        """Test connecting last two shapes."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        builder.add_rectangle(text="First")
        builder.add_circle(text="Second")
        result = builder.connect_last_two()

        assert isinstance(result, PageBuilder)
        assert len(page.lines) == 1

        line = page.lines[0]
        assert line.endpoint1.shapeId == page.shapes[0].id
        assert line.endpoint2.shapeId == page.shapes[1].id

    def test_connect_last_two_with_text(self):
        """Test connecting last two shapes with text."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        (builder
         .add_diamond(text="Decision")
         .add_rectangle(text="Action")
         .connect_last_two(text="Yes"))

        line = page.lines[0]
        assert len(line.text) == 1
        assert line.text[0].text == "Yes"

    def test_connect_last_two_different_line_types(self):
        """Test connecting with different line types."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        (builder
         .add_rectangle(text="A")
         .add_rectangle(text="B")
         .connect_last_two(line_type="elbow")
         .add_rectangle(text="C")
         .connect_last_two(line_type="curved"))

        assert page.lines[0].lineType == "elbow"
        assert page.lines[1].lineType == "curved"

    def test_connect_last_two_insufficient_shapes(self):
        """Test connect_last_two when there are fewer than 2 shapes."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        # No shapes
        result = builder.connect_last_two()
        assert isinstance(result, PageBuilder)
        assert len(page.lines) == 0

        # Only one shape
        builder.add_rectangle(text="Only")
        result = builder.connect_last_two()
        assert isinstance(result, PageBuilder)
        assert len(page.lines) == 0


class TestPageBuilderLayouts:
    """Test layout application in PageBuilder."""

    def test_apply_grid_layout(self):
        """Test applying grid layout through builder."""
        page = Page(id="test-page", title="Test")

        (PageBuilder(page)
         .add_rectangle(text="1")
         .add_rectangle(text="2")
         .add_rectangle(text="3")
         .add_rectangle(text="4")
         .apply_grid_layout(columns=2, spacing_x=120, spacing_y=100)
         .build())

        # Check grid positions
        expected_positions = [
            (50, 50),    # Default start position
            (170, 50),   # 50 + 120
            (50, 150),   # 50 + 100
            (170, 150)   # 50 + 120, 50 + 100
        ]

        for i, (exp_x, exp_y) in enumerate(expected_positions):
            assert page.shapes[i].boundingBox["x"] == exp_x
            assert page.shapes[i].boundingBox["y"] == exp_y

    def test_apply_grid_layout_custom_params(self):
        """Test grid layout with custom parameters."""
        page = Page(id="test-page", title="Test")

        (PageBuilder(page)
         .add_circle(text="A")
         .add_circle(text="B")
         .add_circle(text="C")
         .apply_grid_layout(
             columns=3,
             spacing_x=100,
             spacing_y=80,
             start_x=200,
             start_y=150
         )
         .build())

        # All should be in same row (3 columns, 3 shapes)
        for i, shape in enumerate(page.shapes):
            assert shape.boundingBox["x"] == 200 + i * 100
            assert shape.boundingBox["y"] == 150

    def test_apply_grid_layout_returns_builder(self):
        """Test that apply_grid_layout returns builder for chaining."""
        page = Page(id="test-page", title="Test")
        builder = PageBuilder(page)

        result = builder.apply_grid_layout()
        assert isinstance(result, PageBuilder)
        assert result == builder


class TestPageBuilderComplexWorkflows:
    """Test complex workflows using PageBuilder."""

    def test_create_flowchart(self):
        """Test creating a complete flowchart."""
        page = Page(id="test-page", title="Test")

        (PageBuilder(page)
         .add_circle(text="Start")
         .add_rectangle(text="Input")
         .connect_last_two()
         .add_diamond(text="Valid?")
         .connect_last_two()
         .add_rectangle(text="Process")
         .connect_last_two(text="Yes")
         .add_circle(text="End")
         .connect_last_two()
         .build())

        assert len(page.shapes) == 5
        assert len(page.lines) == 4

        # Check shape types in order
        expected_types = ["circle", "rectangle", "diamond", "rectangle", "circle"]
        for i, expected_type in enumerate(expected_types):
            assert page.shapes[i].type == expected_type

        # Check that lines connect sequential shapes
        for i in range(len(page.lines)):
            line = page.lines[i]
            assert line.endpoint1.shapeId == page.shapes[i].id
            assert line.endpoint2.shapeId == page.shapes[i + 1].id

    def test_create_org_chart_structure(self):
        """Test creating an organizational chart structure."""
        page = Page(id="test-page", title="Test")

        (PageBuilder(page)
         .add_rectangle(text="CEO")
         .add_rectangle(text="CTO")
         .add_rectangle(text="CFO")
         .add_rectangle(text="Dev Team")
         .add_rectangle(text="QA Team")
         .apply_grid_layout(columns=3, spacing_x=150, spacing_y=120)
         .build())

        # Add manual connections for hierarchy
        ceo = page.shapes[0]
        cto = page.shapes[1]
        cfo = page.shapes[2]
        dev_team = page.shapes[3]
        qa_team = page.shapes[4]

        # Connect CEO to department heads
        page.connect_shapes(ceo, cto)
        page.connect_shapes(ceo, cfo)

        # Connect CTO to teams
        page.connect_shapes(cto, dev_team)
        page.connect_shapes(cto, qa_team)

        assert len(page.shapes) == 5
        assert len(page.lines) == 4

    def test_builder_with_mixed_operations(self):
        """Test builder with mixed operations and manual additions."""
        page = Page(id="test-page", title="Test")

        # Use builder for initial setup
        (PageBuilder(page)
         .add_rectangle(text="A")
         .add_rectangle(text="B")
         .connect_last_two()
         .build())

        # Add more shapes manually
        shape_c = page.add_shape("diamond", text="C")
        page.connect_shapes(page.shapes[1], shape_c)

        # Continue with builder
        (PageBuilder(page)
         .add_circle(text="D")
         .build())

        page.connect_shapes(shape_c, page.shapes[-1])

        assert len(page.shapes) == 4
        assert len(page.lines) == 3

        # Verify IDs are still unique
        all_ids = [s.id for s in page.shapes] + [l.id for l in page.lines]
        assert len(set(all_ids)) == len(all_ids)
