import json
import re
import uuid
from typing import List, Literal, Optional, Any, Union, Set
from pydantic import BaseModel, Field, field_validator, model_validator


class Color(str):
    """A string type that matches the Lucidchart color pattern.

    A hexadecimal color code, e.g., '#RRGGBB' or '#RGB'.
    """

    @classmethod
    def __get_validators__(cls):  # noqa
        yield cls.validate

    @classmethod
    def validate(cls, v, values=None, config=None, field=None):
        """Validate that the color is a valid hexadecimal color code."""
        if not isinstance(v, str):
            raise TypeError("string required")
        if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", v):
            raise ValueError("Invalid color format")
        return v


class ID(str):
    """A string type that matches the Lucidchart ID pattern.

    36 characters long, alphanumeric, and containing only -, _, ., and ~.
    """

    @classmethod
    def __get_validators__(cls):  # noqa
        yield cls.validate

    @classmethod
    def validate(cls, v, values=None, config=None, field=None):
        """Validate that the ID is 36 characters long and contains only valid characters."""
        if not isinstance(v, str):
            raise TypeError("string required")
        if not re.match(r"^[a-zA-Z0-9\-\_\.\~]{1,36}$", v):
            raise ValueError("Invalid ID format")
        return v


class _LucidBase(BaseModel):
    def model_dump_json(self, *, indent=True, ignore_null=True) -> str:
        def recursive_model_dump(obj: Any) -> Any:
            if isinstance(obj, BaseModel):
                return {
                    k: recursive_model_dump(v)
                    for k, v in obj.__dict__.items()
                    if (v is not None or not ignore_null or v == 0)
                    and not k.startswith("_")  # Exclude private attributes
                    and not isinstance(v, IDManager)  # Exclude IDManager instances
                }
            elif isinstance(obj, list):
                return [
                    recursive_model_dump(item)
                    for item in obj
                    if item is not None or not ignore_null or item == 0
                ]
            elif isinstance(obj, dict):
                return {
                    key: recursive_model_dump(value)
                    for key, value in obj.items()
                    if value is not None or not ignore_null or value == 0
                }
            else:
                return obj

        data = recursive_model_dump(self)
        return json.dumps(data, indent=indent)


class IDManager:
    """Manages unique ID generation for shapes and lines."""

    def __init__(self):
        self._used_ids: Set[str] = set()
        self._counters = {"shape": 0, "line": 0, "page": 0, "group": 0}

    def generate_id(self, prefix: str = "item") -> str:
        """Generate a unique ID with the given prefix."""
        if prefix in self._counters:
            self._counters[prefix] += 1
            candidate = f"{prefix}-{self._counters[prefix]}"
        else:
            # Use UUID for custom prefixes to ensure uniqueness
            candidate = f"{prefix}-{str(uuid.uuid4())[:8]}"

        # Ensure uniqueness
        while candidate in self._used_ids:
            if prefix in self._counters:
                self._counters[prefix] += 1
                candidate = f"{prefix}-{self._counters[prefix]}"
            else:
                candidate = f"{prefix}-{str(uuid.uuid4())[:8]}"

        self._used_ids.add(candidate)
        return candidate

    def register_id(self, id_str: str) -> None:
        """Register an existing ID to prevent duplicates."""
        self._used_ids.add(id_str)

    def is_available(self, id_str: str) -> bool:
        """Check if an ID is available."""
        return id_str not in self._used_ids


class LucidBase(_LucidBase):
    """Base model for Lucid entities."""

    id: Optional[ID] = None

    def __init__(self, **data):
        # Auto-generate ID if not provided
        if "id" not in data or data["id"] is None:
            if hasattr(self, "_id_manager"):
                prefix = getattr(self, "_id_prefix", "item")
                data["id"] = self._id_manager.generate_id(prefix)
        super().__init__(**data)


class Stroke(_LucidBase):
    """Stroke model to define the look of a line or border.

    Attributes:
        color (str): The color of the stroke in hexadecimal format (e.g., '#RRGGBB' or '#RGB').
        width (int): The width of the stroke.
        style (Literal['solid', 'dashed', 'dotted']): The style of the stroke, which can be 'solid',
        'dashed', or 'dotted'.
    """

    width: int = None
    color: str = Field(default=None, pattern=r"^#(?:[0-9a-fA-F]{3}){1,2}$")
    style: Literal["solid", "dashed", "dotted"] = None


class Style(_LucidBase):
    """Style model to define the look of a shape or line."""

    fill: Union[str, dict] = Field(
        default_factory=lambda: {"type": "color", "color": "#ffffff"}
    )
    stroke: Optional[Stroke] = Stroke(color="#000000", width=1, style="solid")
    rounding: Optional[int] = None

    @field_validator("fill", mode="before")
    def validate_fill(cls, v):
        if isinstance(v, str):
            return {"type": "color", "color": v}
        return v


class Shape(LucidBase):
    # actions: Optional[List[dict]] = []
    # customData: Optional[List[dict]] = []
    # linkedData: Optional[List[dict]] = []
    type: Literal[
        "rectangle",
        "circle",
        "cloud",
        "diamond",
        "cross",
        "hexagon",
        "octagon",
        "isocolesTriangle",
        "rightTriangle",
    ]
    text: Optional[str] = ""
    style: Style = Style()
    opacity: Optional[int] = None
    note: Optional[str] = None
    boundingBox: dict = {"x": 0, "y": 0, "w": 50, "h": 50}

    _id_prefix = "shape"

    def __init__(self, **data):
        # Set default position if not provided
        if "boundingBox" not in data:
            data["boundingBox"] = {"x": 0, "y": 0, "w": 50, "h": 50}
        super().__init__(**data)

    @classmethod
    def create(
        cls,
        shape_type: str,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ):
        """Convenient factory method for creating shapes."""
        return cls(
            type=shape_type,
            boundingBox={"x": x, "y": y, "w": width, "h": height},
            text=text,
            **kwargs,
        )


class Rectangle(Shape):
    type: str = "rectangle"

    @classmethod
    def create(
        cls,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ):
        return cls(
            boundingBox={"x": x, "y": y, "w": width, "h": height}, text=text, **kwargs
        )


class Circle(Shape):
    type: str = "circle"

    @classmethod
    def create(
        cls, x: float = 0, y: float = 0, radius: float = 25, text: str = "", **kwargs
    ):
        # For circles, width and height should be equal (diameter)
        diameter = radius * 2
        return cls(
            boundingBox={"x": x, "y": y, "w": diameter, "h": diameter},
            text=text,
            **kwargs,
        )


class Cloud(Shape):
    type: str = "cloud"

    @classmethod
    def create(
        cls,
        x: float = 0,
        y: float = 0,
        width: float = 60,
        height: float = 40,
        text: str = "",
        **kwargs,
    ):
        return cls(
            boundingBox={"x": x, "y": y, "w": width, "h": height}, text=text, **kwargs
        )


class Diamond(Shape):
    type: str = "diamond"

    @classmethod
    def create(
        cls,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ):
        return cls(
            boundingBox={"x": x, "y": y, "w": width, "h": height}, text=text, **kwargs
        )


class Hexagon(Shape):
    type: str = "hexagon"

    @classmethod
    def create(
        cls,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ):
        return cls(
            boundingBox={"x": x, "y": y, "w": width, "h": height}, text=text, **kwargs
        )


class Octagon(Shape):
    type: str = "octagon"

    @classmethod
    def create(
        cls,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ):
        return cls(
            boundingBox={"x": x, "y": y, "w": width, "h": height}, text=text, **kwargs
        )


class IsocolesTriangle(Shape):
    type: str = "isocolesTriangle"

    @classmethod
    def create(
        cls,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ):
        return cls(
            boundingBox={"x": x, "y": y, "w": width, "h": height}, text=text, **kwargs
        )


class RightTriangle(Shape):
    type: str = "rightTriangle"

    @classmethod
    def create(
        cls,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ):
        return cls(
            boundingBox={"x": x, "y": y, "w": width, "h": height}, text=text, **kwargs
        )


class Cross(Shape):
    """Represents a cross shape in Lucidchart.

    Attributes:
        x (float): Horizontal indent, must be between 0.0 and 0.5.
        y (float): Vertical indent, must be between 0.0 and 0.5.
    """

    type: str = "cross"
    x: Optional[float] = 0
    y: Optional[float] = 0

    @field_validator("x", "y")
    def indent_must_be_between_0_and_0_5(cls, v, field):
        """Validate that the indent is between 0.0 and 0.5."""
        if v is not None and not (0.0 <= v <= 0.5):
            field_name = field.field_name if hasattr(field, 'field_name') else 'value'
            raise ValueError(f"{field_name} must be between 0.0 and 0.5")
        return v


class Endpoint(BaseModel):
    """Generic Endpoint model.

    This shouldn't be used directly, but rather as a base class for more specific endpoint types.

    Ref: https://developer.lucid.co/docs/lines-si#endpoint-type

    Args:
        _type_ (str): The type of the endpoint.
        _style_ (str): The style of the endpoint.
    """

    type: str
    style: Literal[
        "none",
        "aggregation",
        "arrow",
        "hollowArrow",
        "openArrow",
        "async1",
        "async2",
        "closedSquare",
        "openSquare",
        "bpmnConditional",
        "bpmnDefault",
        "closedCircle",
        "openCircle",
        "composition",
        "exactlyOne",
        "generalization",
        "many",
        "nesting",
        "one",
        "oneOrMore",
        "zeroOrMore",
        "zeroOrOne",
    ] = "arrow"


class Text(BaseModel):
    """Text used in the Line model.

    Attributes:
        text (str): The text to display.
        position (float): The position of the text on the line (0.0-1.0).
        side (Literal['top', 'middle', 'bottom']): The side of the line where the text should appear.
    """

    text: str
    position: float = Field(0.5, ge=0.0, le=1.0)
    side: Literal["top", "middle", "bottom"] = "middle"


class Line(LucidBase):
    """Represents a Line model in the Lucid system.

    Attributes:
        type (Literal['straight', 'curved', 'elbow']): The type of the line.
        endpoint1 (Endpoint): The first endpoint of the line.
        endpoint2 (Endpoint): The second endpoint of the line.
        stroke (dict): Dictionary containing stroke properties of the line.
        text (List[Text]): List of Text objects associated with the line.
        endpoints (List[Endpoint]): List of Endpoint objects associated with the line.
    """

    lineType: Literal["straight", "curved", "elbow"] = "straight"
    endpoint1: Optional[Endpoint] = None
    endpoint2: Optional[Endpoint] = None
    stroke: Stroke = Stroke()
    text: List[Text] = []

    _id_prefix = "line"

    def connect_shapes(
        self, shape1: Shape, shape2: Shape, stroke: Stroke = None, text: str = None
    ):
        """Connect two shapes with the line.

        Args:
            shape1 (Shape): The first shape to connect.
            shape2 (Shape): The second shape to connect.
            stroke (Stroke): The stroke style to use for the line.
            text (Optional[str]): The text to display on the line.
        """
        self.endpoint1 = ShapeEndpoint(shapeId=shape1.id)
        self.endpoint2 = ShapeEndpoint(shapeId=shape2.id)
        if stroke:
            self.stroke = stroke
        if text:
            self.text = [Text(text=text)]
        return self

    @classmethod
    def create_between(
        cls,
        shape1: Shape,
        shape2: Shape,
        line_type: str = "straight",
        text: str = None,
        **kwargs,
    ):
        """Convenient factory method for creating lines between shapes."""
        line = cls(lineType=line_type, **kwargs)
        line.connect_shapes(shape1, shape2, text=text)
        return line


class LineEndpoint(Endpoint):
    """Represents an endpoint on a line.

    Attributes:
        line_id (ID): The id for which line to attach the endpoint to.
        position (float): A relative position specifying where on the target line this endpoint
        should attach (must be between 0.0-1.0 inclusive).
    """

    type: str = "lineEndpoint"
    line: Optional[Line]
    line_id: ID = Field(...)
    position: float

    @field_validator("position")
    def position_must_be_between_0_and_1(cls, v):
        """Validate that the position is between 0.0 and 1.0."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("position must be between 0.0 and 1.0")
        return v


class ShapeEndpoint(Endpoint):
    """Represents an endpoint on a shape.

    Attributes:
        shapeId (ID): The ID of the shape to attach the endpoint to. Can also accept a Shape instance.
        position (dict): The position on the shape where the endpoint is attached.
    """

    type: str = "shapeEndpoint"
    shapeId: Optional[Union[ID, Shape, str]]
    position: dict = Field(default_factory=lambda: {"x": 0.5, "y": 0.5})

    @model_validator(mode="before")
    def check_shape_or_shapeId(cls, values):
        shapeId = values.get("shapeId")
        if isinstance(shapeId, Shape):
            values["shapeId"] = shapeId.id
        elif isinstance(shapeId, str):
            # Accept string IDs as well
            values["shapeId"] = shapeId
        elif shapeId is not None and not isinstance(shapeId, ID):
            raise ValueError("shape_id must be an instance of ID, Shape, or string")
        return values

    @field_validator("position")
    def position_must_be_valid(cls, v):
        """Validate that the position is a dict with x and y between 0.0 and 1.0."""
        if not isinstance(v, dict):
            raise ValueError("position must be a dictionary")
        if "x" not in v or "y" not in v:
            raise ValueError("position must contain x and y coordinates")
        if not (0.0 <= v["x"] <= 1.0 and 0.0 <= v["y"] <= 1.0):
            raise ValueError("x and y must be between 0.0 and 1.0")
        return v


class Page(LucidBase):
    title: str
    # settings: Optional[dict] = {}
    # dataBackedShapes: Optional[List[dict]] = []
    # groups: Optional[List[dict]] = []
    # layers: Optional[List[dict]] = []
    # customData: Optional[List[dict]] = []
    shapes: List[Shape] = []
    lines: List[Line] = []

    _id_prefix = "page"

    def __init__(self, **data):
        super().__init__(**data)
        self._id_manager = IDManager()

        # Register existing IDs
        for shape in self.shapes:
            if shape.id:
                self._id_manager.register_id(shape.id)
        for line in self.lines:
            if line.id:
                self._id_manager.register_id(line.id)

    def add_shape(
        self,
        shape_type: str = None,
        shape: Shape = None,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ) -> Shape:
        """Add a shape to the page."""
        if shape is None:
            if shape_type is None:
                shape_type = "rectangle"
            shape = Shape.create(shape_type, x, y, width, height, text, **kwargs)

        # Ensure shape has an ID
        if shape.id is None:
            shape.id = self._id_manager.generate_id("shape")
        else:
            self._id_manager.register_id(shape.id)

        # Set the ID manager on the shape for future operations
        shape._id_manager = self._id_manager

        self.shapes.append(shape)
        return shape

    def add_line(
        self,
        shape1: Shape = None,
        shape2: Shape = None,
        line_type: str = "straight",
        text: str = None,
        **kwargs,
    ) -> Line:
        """Add a line between two shapes."""
        line = Line(lineType=line_type, **kwargs)

        # Ensure line has an ID
        if line.id is None:
            line.id = self._id_manager.generate_id("line")
        else:
            self._id_manager.register_id(line.id)

        # Set the ID manager on the line
        line._id_manager = self._id_manager

        if shape1 and shape2:
            line.connect_shapes(shape1, shape2, text=text)

        self.lines.append(line)
        return line

    def connect_shapes(
        self,
        shape1: Shape,
        shape2: Shape,
        line_type: str = "straight",
        text: str = None,
        **kwargs,
    ) -> Line:
        """Create a line connection between two existing shapes."""
        return self.add_line(shape1, shape2, line_type, text, **kwargs)


class Document(_LucidBase):
    version: int = 1
    pages: List[Page] = []

    def __init__(self, **data):
        super().__init__(**data)
        self._global_id_manager = IDManager()

    def add_page(self, title: str, **kwargs) -> Page:
        """Add a new page to the document."""
        page = Page(title=title, **kwargs)

        # Ensure page has an ID
        if page.id is None:
            page.id = self._global_id_manager.generate_id("page")
        else:
            self._global_id_manager.register_id(page.id)

        self.pages.append(page)
        return page

    @classmethod
    def create(cls, title: str = "New Document") -> "Document":
        """Create a new document with a default page."""
        doc = cls()
        doc.add_page(title)
        return doc


class LayoutManager:
    """Utility class for positioning and layout operations."""

    @staticmethod
    def grid_layout(
        shapes: List[Shape],
        columns: int = 3,
        spacing_x: float = 100,
        spacing_y: float = 100,
        start_x: float = 50,
        start_y: float = 50,
    ):
        """Arrange shapes in a grid layout."""
        for i, shape in enumerate(shapes):
            row = i // columns
            col = i % columns
            shape.boundingBox["x"] = start_x + col * spacing_x
            shape.boundingBox["y"] = start_y + row * spacing_y

    @staticmethod
    def horizontal_layout(
        shapes: List[Shape], spacing: float = 100, start_x: float = 50, y: float = 50
    ):
        """Arrange shapes horizontally."""
        for i, shape in enumerate(shapes):
            shape.boundingBox["x"] = start_x + i * spacing
            shape.boundingBox["y"] = y

    @staticmethod
    def vertical_layout(
        shapes: List[Shape], spacing: float = 100, x: float = 50, start_y: float = 50
    ):
        """Arrange shapes vertically."""
        for i, shape in enumerate(shapes):
            shape.boundingBox["x"] = x
            shape.boundingBox["y"] = start_y + i * spacing

    @staticmethod
    def center_shape(
        shape: Shape, container_width: float = 800, container_height: float = 600
    ):
        """Center a shape within a container."""
        shape_width = shape.boundingBox["w"]
        shape_height = shape.boundingBox["h"]
        shape.boundingBox["x"] = (container_width - shape_width) / 2
        shape.boundingBox["y"] = (container_height - shape_height) / 2


class PageBuilder:
    """Builder pattern for creating complex page layouts."""

    def __init__(self, page: Page):
        self.page = page

    def add_shape(
        self,
        shape_type: str,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ) -> "PageBuilder":
        """Add a shape and return the builder for chaining."""
        self.page.add_shape(shape_type, None, x, y, width, height, text, **kwargs)
        return self

    def add_rectangle(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ) -> "PageBuilder":
        """Add a rectangle and return the builder for chaining."""
        return self.add_shape("rectangle", x, y, width, height, text, **kwargs)

    def add_circle(
        self, x: float = 0, y: float = 0, radius: float = 25, text: str = "", **kwargs
    ) -> "PageBuilder":
        """Add a circle and return the builder for chaining."""
        diameter = radius * 2
        return self.add_shape("circle", x, y, diameter, diameter, text, **kwargs)

    def add_diamond(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 50,
        height: float = 50,
        text: str = "",
        **kwargs,
    ) -> "PageBuilder":
        """Add a diamond and return the builder for chaining."""
        return self.add_shape("diamond", x, y, width, height, text, **kwargs)

    def connect_last_two(
        self, line_type: str = "straight", text: str = None, **kwargs
    ) -> "PageBuilder":
        """Connect the last two shapes added."""
        if len(self.page.shapes) >= 2:
            shape1 = self.page.shapes[-2]
            shape2 = self.page.shapes[-1]
            self.page.connect_shapes(shape1, shape2, line_type, text, **kwargs)
        return self

    def apply_grid_layout(
        self,
        columns: int = 3,
        spacing_x: float = 100,
        spacing_y: float = 100,
        start_x: float = 50,
        start_y: float = 50,
    ) -> "PageBuilder":
        """Apply grid layout to all shapes on the page."""
        LayoutManager.grid_layout(
            self.page.shapes, columns, spacing_x, spacing_y, start_x, start_y
        )
        return self

    def build(self) -> Page:
        """Return the completed page."""
        return self.page
