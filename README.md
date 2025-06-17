# Lucidpy
The unofficial Lucid Chart Simple API python wrapper library

This project is a Python library for interacting with the Lucidchart API. It utilizes `httpx` for making HTTP requests and `Pydantic` for data validation and serialization. The library is designed to be flexible and easy to use, allowing developers to integrate Lucidchart functionalities into their applications seamlessly.

## Features

- **API Client**: A robust client for interacting with the Lucidchart API, handling authentication and requests.
- **Data Models**: Pydantic models for validating and serializing API data structures such as documents, pages, and shapes.
- **Utilities**: Helper functions for common tasks related to API interactions.

## Installation

You can install the library using pip:

```
pip install lucidpy
```

## Usage

### Basic Example

Create diagrams with automatic ID generation:

```python
from lucidpy import Document, LucidchartClient

# Create a document - IDs are automatically generated!
doc = Document.create("My Flowchart")
page = doc.pages[0]

# Add shapes without worrying about IDs
start = page.add_shape("circle", x=50, y=50, width=60, height=60, text="Start")
process = page.add_shape("rectangle", x=200, y=40, width=120, height=80, text="Process")
end = page.add_shape("circle", x=400, y=50, width=60, height=60, text="End")

# Connect shapes
page.connect_shapes(start, process)
page.connect_shapes(process, end)

# Upload to Lucidchart
client = LucidchartClient(api_key='your_api_key')
client.create_document("My Flowchart", document=doc)
```

### Layout Utilities

Automatically position shapes in common patterns:

```python
from lucidpy import Document, LayoutManager

doc = Document.create("Grid Layout")
page = doc.pages[0]

# Create shapes
shapes = [page.add_shape("rectangle", text=f"Step {i+1}") for i in range(6)]

# Apply grid layout
LayoutManager.grid_layout(shapes, columns=3, spacing_x=120, spacing_y=100)
```

### Builder Pattern

Use the fluent interface for complex diagrams:

```python
from lucidpy import Document, PageBuilder

doc = Document.create("Workflow")
page = doc.pages[0]

(PageBuilder(page)
    .add_rectangle(0, 0, 100, 60, "Start")
    .add_diamond(150, 0, 80, 80, "Check")
    .connect_last_two()
    .add_rectangle(300, 0, 100, 60, "Process")
    .connect_last_two(text="OK")
    .build())
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
