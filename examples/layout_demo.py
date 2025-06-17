#!/usr/bin/env python3
"""
Demonstrates layout utilities for automatic shape positioning.
"""

from lucidpy import Document, LayoutManager

# Create document
doc = Document.create("Layout Examples")
page = doc.pages[0]

# Create shapes for grid layout
grid_shapes = []
for i in range(6):
    shape = page.add_shape("rectangle", text=f"Step {i + 1}")
    grid_shapes.append(shape)

# Apply grid layout (2 columns x 3 rows)
LayoutManager.grid_layout(
    grid_shapes, columns=2, spacing_x=150, spacing_y=100, start_x=50, start_y=50
)

# Create shapes for horizontal layout
horizontal_shapes = []
for i in range(3):
    shape = page.add_shape("circle", text=f"Node {i + 1}")
    horizontal_shapes.append(shape)

# Apply horizontal layout
LayoutManager.horizontal_layout(horizontal_shapes, spacing=120, start_x=50, y=400)

# Connect some shapes
page.connect_shapes(grid_shapes[0], grid_shapes[1], text="Next")
page.connect_shapes(grid_shapes[1], grid_shapes[2])
page.connect_shapes(grid_shapes[2], grid_shapes[3])

print(f"Created document with {len(page.shapes)} shapes and {len(page.lines)} lines")
print(f"Shape IDs: {[shape.id for shape in page.shapes]}")
