#!/usr/bin/env python3
"""
Basic usage example for lucidpy - creating a simple flowchart.
"""

from lucidpy import Document, LucidchartClient

# Create a document with automatic ID generation
doc = Document.create("My Flowchart")
page = doc.pages[0]

# Add shapes - IDs are automatically generated!
start = page.add_shape("circle", x=50, y=50, width=60, height=60, text="Start")
process = page.add_shape(
    "rectangle", x=200, y=40, width=120, height=80, text="Process Data"
)
decision = page.add_shape("diamond", x=400, y=30, width=100, height=100, text="Valid?")
success = page.add_shape("rectangle", x=600, y=40, width=120, height=80, text="Success")
error = page.add_shape(
    "rectangle", x=400, y=200, width=120, height=80, text="Handle Error"
)

# Connect shapes with lines
page.connect_shapes(start, process)
page.connect_shapes(process, decision)
page.connect_shapes(decision, success, text="Yes")
page.connect_shapes(decision, error, text="No")

# Upload to Lucidchart (requires API key in config.toml)
# client = LucidchartClient()
# result = client.create_document("My Flowchart", document=doc)
# print(f"Document created: {result}")

# Or export the JSON
print(doc.model_dump_json())
