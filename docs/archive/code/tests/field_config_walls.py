"""
Wall-Centered Field Configuration
4 AprilTags, one per wall, centered
tag36h11 family, IDs 582-585
"""

from field_config import FieldConfig, WallConfig

# 4-tag wall-centered field (easier to mount than corners)
# Using actual tag IDs on field: 582-585
WALL_CENTERED_6X6 = FieldConfig(
    name="wall_centered_6x6",
    description="6x6 ft field with one tag per wall (centered) - tag36h11",
    size_ft=(6, 6),
    tag_height_in=10,
    tag_size_in=10,  # Upgraded from 6" to 10" for better detection
    walls=[
        WallConfig(
            name="north",
            length_ft=6,
            tags=[582],  # Area 1: start square and blue blocks
            position="top"
        ),
        WallConfig(
            name="east",
            length_ft=6,
            tags=[583],  # Area 2: red blocks
            position="right"
        ),
        WallConfig(
            name="south",
            length_ft=6,
            tags=[584],  # Area 3: yellow blocks
            position="bottom"
        ),
        WallConfig(
            name="west",
            length_ft=6,
            tags=[585],  # Area 4: delivery zone
            position="left"
        )
    ]
)

# Make this the default
DEFAULT_FIELD = WALL_CENTERED_6X6
