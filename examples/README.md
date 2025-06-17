# Lucidpy Examples

This directory contains examples demonstrating the new usability features in lucidpy.

## Examples Overview

### Basic Usage (`basic_usage.py`)
Shows the fundamental features:
- Automatic ID generation for shapes and lines
- Simple shape creation with `page.add_shape()`
- Easy shape connections with `page.connect_shapes()`
- Document creation and JSON export

### All Shapes Demo (`all_shapes_demo.py`)
Demonstrates:
- All available shape types in lucidpy
- Grid layout with `LayoutManager.grid_layout()`
- Different line types (straight, elbow, curved)
- Automatic ID generation across multiple shapes

### Layout Utilities (`layout_demo.py`)
Shows layout management features:
- Grid layouts for organized positioning
- Horizontal layouts for linear arrangements
- Mixing different layout types
- Shape positioning without manual coordinate calculation

### Builder Pattern (`builder_pattern.py`)
Demonstrates the fluent interface:
- Method chaining with `PageBuilder`
- Sequential shape addition
- Automatic connections between shapes
- Workflow creation

### Complete Flowchart (`flowchart_example.py`)
Advanced example showing:
- Custom styling with colors and strokes
- Complex flowchart with multiple paths
- Error handling workflow
- Advanced shape positioning and connections

### Automatic IDs Demo (`automatic_ids_demo.py`)
Compares old vs new approaches:
- Manual ID management (old way)
- Automatic ID generation (new way)
- Builder pattern usage
- Layout utilities demonstration

## Running Examples

Run any example with:
```bash
uv run python examples/<example_name>.py
```

For example:
```bash
uv run python examples/basic_usage.py
uv run python examples/all_shapes_demo.py
```

## Key Features Demonstrated

1. **Automatic ID Generation**: No more manual `"shape-1"`, `"line-1"` naming
2. **Helper Methods**: `page.add_shape()`, `page.connect_shapes()`
3. **Layout Utilities**: Grid, horizontal, vertical, and center layouts
4. **Builder Pattern**: Fluent interface for complex diagrams
5. **Factory Methods**: Convenient shape creation
6. **Pydantic Models**: Full type safety and validation preserved
