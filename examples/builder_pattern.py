#!/usr/bin/env python3
"""
Demonstrates the PageBuilder pattern for fluent interface creation.
"""

from lucidpy import Document, PageBuilder

# Create document
doc = Document.create("Builder Pattern Demo")
page = doc.pages[0]

# Use builder pattern for chaining operations
builder = PageBuilder(page)

# Build a simple workflow
(
    builder.add_rectangle(50, 50, 100, 60, "Input Data")
    .add_diamond(200, 40, 80, 80, "Validate")
    .connect_last_two()
    .add_rectangle(350, 50, 100, 60, "Process")
    .connect_last_two(text="Valid")
    .add_rectangle(200, 150, 100, 60, "Log Error")
    .add_circle(500, 60, 30, "Complete")
    .build()
)

# Connect the validation to error logging
if len(page.shapes) >= 4:
    validate_shape = page.shapes[1]  # Diamond
    error_shape = page.shapes[3]  # Log Error
    page.connect_shapes(validate_shape, error_shape, text="Invalid")

# Connect process to complete
if len(page.shapes) >= 5:
    process_shape = page.shapes[2]  # Process
    complete_shape = page.shapes[4]  # Complete
    page.connect_shapes(process_shape, complete_shape)

print(f"Created workflow with {len(page.shapes)} shapes and {len(page.lines)} lines")
