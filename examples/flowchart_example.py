#!/usr/bin/env python3
"""
Create a complete flowchart demonstrating various shapes and connections.
"""

from lucidpy import Document, Style, Stroke

# Create document
doc = Document.create("Complete Flowchart Example")
page = doc.pages[0]

# Define custom styles
decision_style = Style(
    fill={"type": "color", "color": "#FFE6CC"}, stroke=Stroke(color="#D79B00", width=2)
)

process_style = Style(
    fill={"type": "color", "color": "#D5E8D4"}, stroke=Stroke(color="#82B366", width=2)
)

error_style = Style(
    fill={"type": "color", "color": "#F8CECC"}, stroke=Stroke(color="#B85450", width=2)
)

# Create flowchart
start = page.add_shape("circle", x=400, y=50, width=80, height=80, text="Start")

# Input phase
input_data = page.add_shape(
    "rectangle",
    x=350,
    y=180,
    width=180,
    height=60,
    text="Receive Input",
    style=process_style,
)

# Validation
validate = page.add_shape(
    "diamond",
    x=350,
    y=300,
    width=180,
    height=120,
    text="Valid Input?",
    style=decision_style,
)

# Success path
process_data = page.add_shape(
    "rectangle",
    x=150,
    y=450,
    width=160,
    height=60,
    text="Process Data",
    style=process_style,
)

store_result = page.add_shape(
    "rectangle",
    x=150,
    y=580,
    width=160,
    height=60,
    text="Store Result",
    style=process_style,
)

# Error path
log_error = page.add_shape(
    "rectangle", x=550, y=450, width=160, height=60, text="Log Error", style=error_style
)

notify_user = page.add_shape(
    "rectangle",
    x=550,
    y=580,
    width=160,
    height=60,
    text="Notify User",
    style=error_style,
)

# End states
success_end = page.add_shape(
    "circle", x=190, y=720, width=80, height=80, text="Success", style=process_style
)

error_end = page.add_shape(
    "circle", x=590, y=720, width=80, height=80, text="Failed", style=error_style
)

# Connect everything
page.connect_shapes(start, input_data)
page.connect_shapes(input_data, validate)

# Success path connections
page.connect_shapes(
    validate, process_data, text="Yes", stroke=Stroke(color="#82B366", width=2)
)
page.connect_shapes(process_data, store_result)
page.connect_shapes(store_result, success_end)

# Error path connections
page.connect_shapes(
    validate, log_error, text="No", stroke=Stroke(color="#B85450", width=2)
)
page.connect_shapes(log_error, notify_user)
page.connect_shapes(notify_user, error_end)

# Add a retry loop
retry_line = page.add_line(line_type="elbow")
retry_line.connect_shapes(notify_user, input_data, text="Retry")

print(f"Created flowchart with {len(page.shapes)} shapes and {len(page.lines)} lines")
print(f"All shape IDs: {[s.id for s in page.shapes]}")
print(f"All line IDs: {[l.id for l in page.lines]}")

# Export JSON (uncomment to see output)
# print(doc.model_dump_json())
