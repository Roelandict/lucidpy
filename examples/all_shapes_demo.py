#!/usr/bin/env python3
"""
Demonstrate all available shape types with automatic ID generation.
"""

from lucidpy import Document, LayoutManager

# Create document
doc = Document.create("All Shapes Demo")
page = doc.pages[0]

# Create one of each shape type
shapes = [
    page.add_shape("rectangle", text="Rectangle"),
    page.add_shape("circle", text="Circle"),
    page.add_shape("diamond", text="Diamond"),
    page.add_shape("cloud", text="Cloud"),
    page.add_shape("hexagon", text="Hexagon"),
    page.add_shape("octagon", text="Octagon"),
    page.add_shape("isocolesTriangle", text="Isoceles"),
    page.add_shape("rightTriangle", text="Right Triangle"),
    page.add_shape("cross", text="Cross"),
]

# Apply grid layout (3x3)
LayoutManager.grid_layout(shapes, columns=3, spacing_x=150, spacing_y=150)

# Add some connections to show different line types
page.connect_shapes(shapes[0], shapes[1], line_type="straight", text="straight")
page.connect_shapes(shapes[1], shapes[2], line_type="elbow", text="elbow")
page.connect_shapes(shapes[3], shapes[4], line_type="curved", text="curved")

# Show automatic ID generation
print("Shape IDs generated automatically:")
for shape in shapes:
    print(f"  {shape.text}: {shape.id}")

print("\nLine IDs generated automatically:")
for line in page.lines:
    print(f"  {line.id}: {line.lineType} line")
