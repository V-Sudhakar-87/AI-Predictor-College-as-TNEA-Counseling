from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
import os
import io
from datetime import datetime

try:
    from PIL import Image as PILImage
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


# =====================================================
# COLOR PALETTE
# =====================================================

COLOR_NAVY = HexColor("#1C1C1E")       # Header banner background - premium charcoal/graphite (no blue)
COLOR_HEADER_DARK = HexColor("#0F172A")  # Kept for page-2 table header row only
COLOR_GOLD = HexColor("#C9A227")       # Premium gold accent (replaces blue accent in header)
COLOR_GOLD_SOFT = HexColor("#E4C97A")  # Softer gold for secondary header text
COLOR_BLUE = HexColor("#0EA5E9")       # Accent blue (still used elsewhere: section titles, page-2 table)
COLOR_LIGHT_BLUE = HexColor("#38BDF8")  # Secondary accent
COLOR_SLATE_LIGHT = HexColor("#CBD5E1")  # Muted light text on dark bg
COLOR_SLATE_MUTED = HexColor("#94A3B8")  # Muted lighter text on dark bg
COLOR_TEXT_DARK = HexColor("#0F172A")   # Primary body text
COLOR_TEXT_GRAY = HexColor("#334155")   # Secondary body text
COLOR_TEXT_MUTED = HexColor("#64748B")  # Footer / captions
COLOR_ROW_ALT = HexColor("#F1F5F9")     # Alternate row background
COLOR_ROW_BASE = colors.white
COLOR_BORDER = HexColor("#CBD5E1")


# =====================================================
# BASE STYLES
# =====================================================

_base_styles = getSampleStyleSheet()

STYLE_COLLEGE_NAME = ParagraphStyle(
    "CollegeName",
    parent=_base_styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=17,
    leading=21,
    alignment=TA_CENTER,
    textColor=colors.white,
)

STYLE_SECTION_TITLE = ParagraphStyle(
    "SectionTitle",
    parent=_base_styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    alignment=TA_LEFT,
    textColor=COLOR_NAVY,
    spaceAfter=4,
)

STYLE_KV_ROW = ParagraphStyle(
    "KeyValueRow",
    parent=_base_styles["Normal"],
    fontName="Helvetica",
    fontSize=11,
    leading=18,
    alignment=TA_LEFT,
    textColor=COLOR_TEXT_GRAY,
)
STYLE_KV_ROW.tabs = [190]

STYLE_TABLE_HEADER = ParagraphStyle(
    "TableHeaderCell",
    parent=_base_styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=13,
    alignment=TA_LEFT,
    textColor=colors.white,
)

STYLE_TABLE_BODY = ParagraphStyle(
    "TableBodyCell",
    parent=_base_styles["BodyText"],
    fontName="Helvetica",
    fontSize=9.5,
    leading=13,
    alignment=TA_LEFT,
    textColor=COLOR_TEXT_GRAY,
)

STYLE_TABLE_BODY_BOLD = ParagraphStyle(
    "TableBodyCellBold",
    parent=STYLE_TABLE_BODY,
    fontName="Helvetica-Bold",
    textColor=COLOR_TEXT_DARK,
)

STYLE_FOOTER_LINE = ParagraphStyle(
    "FooterLine",
    parent=_base_styles["Normal"],
    fontName="Helvetica",
    fontSize=6.7,
    leading=9,
    alignment=TA_CENTER,
    textColor=COLOR_TEXT_MUTED,
)


# =====================================================
# HELPERS
# =====================================================

def _safe_image(path, width, height, dpi=150):
    """
    Returns a ReportLab Image flowable if the file exists, otherwise a
    transparent Spacer of the same footprint so the layout never breaks
    because an optional asset (e.g. founder logo) is missing.

    The source image is downscaled to just the pixel size actually needed
    on the page (at `dpi`) before being embedded, which is the main fix for
    bloated output PDFs when the original logo/photo files are very large.
    """
    if not (path and os.path.isfile(path)):
        return Spacer(width, height)

    try:
        if _PIL_AVAILABLE:
            target_w = max(int((width / inch) * dpi), 1)
            target_h = max(int((height / inch) * dpi), 1)

            pil_img = PILImage.open(path)
            has_alpha = pil_img.mode in ("RGBA", "LA") or (
                pil_img.mode == "P" and "transparency" in pil_img.info
            )
            pil_img = pil_img.convert("RGBA" if has_alpha else "RGB")
            pil_img = pil_img.resize((target_w, target_h), PILImage.LANCZOS)

            buffer = io.BytesIO()
            if has_alpha:
                pil_img.save(buffer, format="PNG", optimize=True)
            else:
                pil_img.save(buffer, format="JPEG", quality=82, optimize=True)
            buffer.seek(0)

            img = Image(buffer)
        else:
            img = Image(path)

        img.drawWidth = width
        img.drawHeight = height
        return img
    except Exception:
        pass
    return Spacer(width, height)


def _preferred_branches_text(student):
    branches = student.get("preferredBranches") or []
    if not branches:
        return "All Branches"
    return ", ".join(branches)


STYLE_KV_LABEL = ParagraphStyle(
    "KeyValueLabel",
    parent=_base_styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=16,
    alignment=TA_LEFT,
    textColor=COLOR_TEXT_DARK,
)

STYLE_KV_COLON = ParagraphStyle(
    "KeyValueColon",
    parent=_base_styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    leading=16,
    alignment=TA_CENTER,
    textColor=COLOR_BLUE,
)

STYLE_KV_VALUE = ParagraphStyle(
    "KeyValueValue",
    parent=_base_styles["Normal"],
    fontName="Helvetica",
    fontSize=11,
    leading=16,
    alignment=TA_LEFT,
    textColor=COLOR_TEXT_GRAY,
)


def _kv_row(label, value):
    safe_value = "" if value is None else str(value)
    return [
        Paragraph(label, STYLE_KV_LABEL),
        Paragraph(":", STYLE_KV_COLON),
        Paragraph(safe_value, STYLE_KV_VALUE),
    ]


# =====================================================
# FOOTER (drawn on every page)
# =====================================================

_FOOTER_LINES = [
    "Developed by AI Counseling Predictor Team",
    "This report is generated using Artificial Intelligence based on previous TNEA counselling trends.",
    "Admission is subject to Anna University counselling rules.",
    "This report DOES NOT guarantee admission.",
    "Generated using AI Counseling Predictor.",
]


def _draw_footer(canvas, doc):
    canvas.saveState()

    page_width, _ = A4
    left_margin = doc.leftMargin
    right_margin = doc.rightMargin
    footer_top = 58

    # Separator line above footer
    canvas.setStrokeColor(COLOR_BORDER)
    canvas.setLineWidth(0.7)
    canvas.line(
        left_margin,
        footer_top,
        page_width - right_margin,
        footer_top,
    )

    # Footer text lines
    canvas.setFont("Helvetica", 6.7)
    canvas.setFillColor(COLOR_TEXT_MUTED)

    text_y = footer_top - 11
    for line in _FOOTER_LINES:
        canvas.drawCentredString(page_width / 2.0, text_y, line)
        text_y -= 8.5

    # Page number
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(COLOR_NAVY)
    canvas.drawRightString(
        page_width - right_margin,
        footer_top - 11,
        "Page {}".format(canvas.getPageNumber()),
    )

    canvas.restoreState()


# =====================================================
# PAGE 1 - COVER / HEADER + STUDENT PROFILE
# =====================================================

def _build_header(logo_path, founder_path):
    logo_flowable = _safe_image(logo_path, 0.8 * inch, 0.8 * inch)
    founder_flowable = _safe_image(founder_path, 0.8 * inch, 0.8 * inch)

    header_text = Paragraph(
        "EINSTEIN COLLEGE OF ENGINEERING<br/>"
        "<font size=9 color='#CBD5E1'>Affiliated to Anna University</font><br/>"
        "<font size=11.5 color='#E4C97A'><b>TNEA AI COUNSELING PREDICTOR</b></font><br/>"
        "<font size=8.5 color='#94A3B8'>Recommendation Report 2026</font>",
        STYLE_COLLEGE_NAME,
    )

    header_table = Table(
        [[logo_flowable, header_text, founder_flowable]],
        colWidths=[90, 355, 90],
    )

    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("ALIGN", (2, 0), (2, 0), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 16),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
                ("LEFTPADDING", (0, 0), (0, 0), 14),
                ("RIGHTPADDING", (2, 0), (2, 0), 14),
                ("LINEBELOW", (0, 0), (-1, -1), 2.2, COLOR_GOLD),
                ("ROUNDEDCORNERS", [10, 10, 10, 10]),
            ]
        )
    )

    return header_table


def _build_student_profile(student, generated_time):
    elements = []

    elements.append(Paragraph("STUDENT PROFILE", STYLE_SECTION_TITLE))
    elements.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=COLOR_BLUE,
            spaceAfter=12,
        )
    )

    field_rows = [
        ("Student Name", student.get("name", "")),
        ("Community", student.get("community", "")),
        ("Rank", student.get("rank", "")),
        ("Preferred District", student.get("district", "")),
        ("Maths", student.get("maths", "")),
        ("Physics", student.get("physics", "")),
        ("Chemistry", student.get("chemistry", "")),
        ("Cutoff", student.get("cutoff", "")),
        ("Preferred Branches", _preferred_branches_text(student)),
        ("Generated Time", generated_time),
    ]

    data = [_kv_row(label, value) for label, value in field_rows]

    # Fixed column widths (label / colon / value) guarantee every row lines
    # up exactly, no matter how long the label or value text is.
    kv_table = Table(data, colWidths=[150, 18, 300])
    kv_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                # No GRID / no BACKGROUND -> stays an invisible layout grid,
                # not a visible "table" look.
            ]
        )
    )

    elements.append(kv_table)
    return elements


# =====================================================
# PAGE 2 - RECOMMENDED COLLEGES TABLE
# =====================================================

def _build_recommendations_table(recommendations):
    header_row = [
        Paragraph("College Code", STYLE_TABLE_HEADER),
        Paragraph("College Name", STYLE_TABLE_HEADER),
        Paragraph("District", STYLE_TABLE_HEADER),
        Paragraph("Available Branches", STYLE_TABLE_HEADER),
    ]

    data = [header_row]

    for rec in reversed(recommendations):
        branches = rec.get("branches", []) or []
        #branches = list(reversed(branches))  # <-- branches printed in reverse order
        branches_text = "<br/>"+",".join(branches) if branches else "-"

        data.append(
            [
                Paragraph(str(rec.get("code", "")), STYLE_TABLE_BODY_BOLD),
                Paragraph(str(rec.get("college", "")), STYLE_TABLE_BODY),
                Paragraph(str(rec.get("district", "")), STYLE_TABLE_BODY),
                Paragraph(branches_text , STYLE_TABLE_BODY),
            ]
        )

    table = Table(
        data,
        colWidths=[62, 210, 95, 155],
        repeatRows=1,
    )

    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]

    # Zebra striping for data rows (row 0 is the header)
    for row_index in range(1, len(data)):
        bg = COLOR_ROW_ALT if row_index % 2 == 0 else COLOR_ROW_BASE
        style_commands.append(
            ("BACKGROUND", (0, row_index), (-1, row_index), bg)
        )

    table.setStyle(TableStyle(style_commands))

    return table


# =====================================================
# MAIN ENTRY POINT
# =====================================================

def generate_pdf(student, recommendations, output_file="report.pdf"):
    generated_time = datetime.now().strftime("%d-%b-%Y %I:%M %p")

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    logo_path = os.path.join(
        BASE_DIR,
        "..",
        "assets",
        "Founder Logo (1).png",
        
    )

    founder_path = os.path.join(
        BASE_DIR,
        "..",
        "assets",
        "COLLEGE LOGO (1).png",
    )

    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=28,
        leftMargin=28,
        topMargin=28,
        bottomMargin=78,
    )

    story = []

    # ---------------------------------------------------
    # PAGE 1 - Header + Student Profile
    # ---------------------------------------------------

    story.append(_build_header(logo_path, founder_path))
    story.append(Spacer(1, 22))
    story.extend(_build_student_profile(student, generated_time))

    story.append(PageBreak())

    # ---------------------------------------------------
    # PAGE 2 - AI Recommended Colleges
    # ---------------------------------------------------

    story.append(Paragraph("AI RECOMMENDED COLLEGES", STYLE_SECTION_TITLE))
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.2,
            color=COLOR_BLUE,
            spaceAfter=14,
        )
    )
    story.append(_build_recommendations_table(recommendations))

    doc.build(
        story,
        onFirstPage=_draw_footer,
        onLaterPages=_draw_footer,
    )


# ---------------------------------------------------
# TEST
# ---------------------------------------------------

   
     #(0, 0), (-1, 0), COLOR_NAVY