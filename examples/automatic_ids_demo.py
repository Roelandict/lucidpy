#!/usr/bin/env python3
"""
Example demonstrating the new usability improvements in lucidpy.
This shows how automatic ID generation and builder patterns make
creating Lucidchart documents much easier.
"""

from lucidpy import Document, PageBuilder, LayoutManager


def old_way_example():
    """Example of the old way - manual ID management."""
    doc = Document()
    page = doc.add_page("Manual ID Example")

    # Old way - had to manually manage IDs
    rect1 = Rectangle(
        id="rect-1", boundingBox={"x": 50, "y": 50, "w": 100, "h": 50}, text="Process 1"
    )
    rect2 = Rectangle(
        id="rect-2",
        boundingBox={"x": 200, "y": 50, "w": 100, "h": 50},
        text="Process 2",
    )

    page.shapes.extend([rect1, rect2])
    return doc


def new_way_example():
    """Example of the new way - automatic ID generation and helpers."""
    # Create document with automatic page creation
    doc = Document.create("Workflow Diagram")
    page = doc.pages[0]

    # Add shapes with automatic ID generation and convenient positioning
    start = page.add_shape("circle", x=50, y=100, width=60, height=60, text="Start")
    process1 = page.add_shape(
        "rectangle", x=150, y=90, width=100, height=80, text="Process 1"
    )
    decision = page.add_shape(
        "diamond", x=300, y=80, width=100, height=100, text="Decision?"
    )
    process2 = page.add_shape(
        "rectangle", x=450, y=90, width=100, height=80, text="Process 2"
    )
    end = page.add_shape("circle", x=600, y=100, width=60, height=60, text="End")

    # Connect shapes easily
    page.connect_shapes(start, process1)
    page.connect_shapes(process1, decision)
    page.connect_shapes(decision, process2, text="Yes")
    page.connect_shapes(process2, end)

    return doc


def builder_pattern_example():
    """Example using the builder pattern for complex layouts."""
    doc = Document.create("Builder Pattern Demo")
    page = doc.pages[0]

    # Use the builder pattern for fluent interface
    builder = PageBuilder(page)

    result = (
        builder.add_rectangle(0, 0, 80, 50, "Step 1")
        .add_rectangle(0, 0, 80, 50, "Step 2")
        .add_rectangle(0, 0, 80, 50, "Step 3")
        .add_circle(0, 0, 30, "Decision")
        .add_rectangle(0, 0, 80, 50, "Final")
        .apply_grid_layout(columns=2, spacing_x=120, spacing_y=80)
        .connect_last_two()
        .build()
    )

    return doc


def layout_utilities_example():
    """Example showing layout utilities."""
    doc = Document.create("Layout Demo")
    page = doc.pages[0]

    # Create multiple shapes
    shapes = []
    for i in range(6):
        shape = page.add_shape("rectangle", text=f"Item {i + 1}")
        shapes.append(shape)

    # Apply different layouts
    LayoutManager.grid_layout(shapes[:4], columns=2, spacing_x=120, spacing_y=80)
    LayoutManager.horizontal_layout(shapes[4:], start_x=50, y=250)

    return doc


if __name__ == "__main__":
    # Demonstrate the improvements
    print("Creating examples with improved lucidpy...")

    # Create examples
    old_doc = old_way_example()
    new_doc = new_way_example()
    builder_doc = builder_pattern_example()
    layout_doc = layout_utilities_example()

    print(f"Old way document: {len(old_doc.pages[0].shapes)} shapes")
    print(
        f"New way document: {len(new_doc.pages[0].shapes)} shapes, {len(new_doc.pages[0].lines)} lines"
    )
    print(f"Builder pattern document: {len(builder_doc.pages[0].shapes)} shapes")
    print(f"Layout utilities document: {len(layout_doc.pages[0].shapes)} shapes")

    # Show that IDs are automatically generated
    print("\nAutomatic ID generation:")
    for i, shape in enumerate(new_doc.pages[0].shapes):
        print(f"  Shape {i + 1}: {shape.id}")
