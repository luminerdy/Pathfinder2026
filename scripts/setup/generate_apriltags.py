#!/usr/bin/env python3
"""Generate print-ready Pathfinder2026 AprilTag assets."""

from pathlib import Path

from PIL import Image
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "apriltags" / "source"
PRINT_DIR = REPO_ROOT / "apriltags" / "print"
PDF_DIR = REPO_ROOT / "output" / "pdf"
TAG_IDS = (582, 583, 584, 585)
SOURCE_CELLS = 10
BLACK_TAG_CELLS = 8
BLACK_TAG_INCHES = 10.0
FULL_IMAGE_INCHES = BLACK_TAG_INCHES * SOURCE_CELLS / BLACK_TAG_CELLS
PNG_DPI = 300
PAGE_SIZE = (13 * inch, 19 * inch)


def make_print_png(tag_id):
    source_path = SOURCE_DIR / f"tag36h11_{tag_id}.png"
    output_path = PRINT_DIR / f"tag36h11_{tag_id}_10in.png"
    source = Image.open(source_path).convert("1")
    expected = (SOURCE_CELLS, SOURCE_CELLS)
    if source.size != expected:
        raise ValueError(f"{source_path} must be {expected[0]}x{expected[1]} pixels")

    pixels = round(FULL_IMAGE_INCHES * PNG_DPI)
    resized = source.resize((pixels, pixels), Image.Resampling.NEAREST)
    resized.save(output_path, dpi=(PNG_DPI, PNG_DPI), optimize=True)
    return output_path


def draw_tag_page(pdf, tag_id, png_path):
    page_width, page_height = PAGE_SIZE
    image_size = FULL_IMAGE_INCHES * inch
    image_x = (page_width - image_size) / 2
    image_y = 2.2 * inch

    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(page_width / 2, page_height - 0.65 * inch, f"Pathfinder2026 - Area {tag_id - 581}")
    pdf.setFont("Helvetica", 17)
    pdf.drawCentredString(page_width / 2, page_height - 1.0 * inch, f"tag36h11 ID {tag_id}")
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(page_width / 2, page_height - 1.3 * inch, "Print at Actual Size / 100% - do not Fit or Scale")
    pdf.drawCentredString(page_width / 2, page_height - 1.52 * inch, "The outside black square must measure exactly 10 inches")
    pdf.drawImage(str(png_path), image_x, image_y, image_size, image_size, preserveAspectRatio=True, mask="auto")
    pdf.setLineWidth(0.5)
    pdf.line(image_x, 1.7 * inch, image_x + 10 * inch, 1.7 * inch)
    pdf.line(image_x, 1.62 * inch, image_x, 1.78 * inch)
    pdf.line(image_x + 10 * inch, 1.62 * inch, image_x + 10 * inch, 1.78 * inch)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(image_x + 5 * inch, 1.43 * inch, "10-inch verification line")
    pdf.showPage()


def make_pdf(path, tag_ids, png_paths):
    pdf = canvas.Canvas(str(path), pagesize=PAGE_SIZE, pageCompression=1)
    pdf.setTitle("Pathfinder2026 AprilTags 582-585")
    pdf.setAuthor("Pathfinder2026")
    for tag_id in tag_ids:
        draw_tag_page(pdf, tag_id, png_paths[tag_id])
    pdf.save()


def main():
    PRINT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    png_paths = {tag_id: make_print_png(tag_id) for tag_id in TAG_IDS}
    for tag_id in TAG_IDS:
        make_pdf(PDF_DIR / f"Pathfinder2026_tag36h11_{tag_id}_10in.pdf", (tag_id,), png_paths)
    make_pdf(PDF_DIR / "Pathfinder2026_AprilTags_582-585_10in.pdf", TAG_IDS, png_paths)

    print(f"Generated {len(TAG_IDS)} print PNGs in {PRINT_DIR}")
    print(f"Generated individual and combined PDFs in {PDF_DIR}")


if __name__ == "__main__":
    main()
