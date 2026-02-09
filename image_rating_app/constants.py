from pathlib import Path

IMAGE_DIR = Path("new_images")
OUTPUT_DIR = Path("output")
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

DEFAULT_EMOTIONS = [
    "amusement",
    "anger",
    "attachment love",
    "awe",
    "craving",
    "disgust",
    "excitement",
    "fear",
    "joy",
    "neutral",
    "nurturant love",
    "sadness",
    "happiness",
    "suprise",
]

EMOTIONS_LEFT_COLUMN_COUNT = 12
OPTION_EMOTIONS_LABEL = "Emotion-based rating"
OPTION_QUALITY_LABEL = "Quality rating"
