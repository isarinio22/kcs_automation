"""
PDF export utilities for KCS report.
"""

from fpdf import FPDF
import os
from typing import List, Tuple

# ───────────────────────────── HELPERS ─────────────────────────────

def format_kcs_engagement_insight(percent: str) -> str:
    return (
        "Engineer KCS Engagement: % of closed cases involving any of the 4 Knowledge Actions "
        "(create, use, update, or provide feedback on Knowledge Articles / Docs).\n\n"
        f"MoM: This month, we had reached to our KPI by {percent}%."
    )

# ───────────────────────────── MAIN EXPORT FUNCTION ─────────────────────────────

def export_report_pdf(figures: List[Tuple[str, object, str]], output_path: str = "report.pdf"):
    """
    Export a PDF report with charts and insights.

    Parameters
    ----------
    figures : List of (title, figure, insight) tuples. Figures can be plotly or matplotlib objects.
    output_path : Path to save the PDF file.
    """
    import tempfile
    import matplotlib.pyplot as plt
    import plotly.graph_objs as go

    # Always use Arial font (built-in)
    font_name = "Arial"

    # Create a temporary directory to store images
    with tempfile.TemporaryDirectory() as tmpdir:
        image_paths = []
        for idx, (title, fig, insight) in enumerate(figures):
            img_path = os.path.join(tmpdir, f"chart_{idx}.png")
            # Save figure as image
            if hasattr(fig, "write_image"):  # Plotly
                fig.write_image(img_path, width=900, height=600, scale=2)
            elif hasattr(fig, "savefig"):    # Matplotlib
                fig.savefig(img_path, bbox_inches="tight", dpi=200)
            else:
                raise ValueError(f"Unsupported figure type: {type(fig)}")
            image_paths.append((title, img_path, insight))

        # Create PDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font(font_name, "", 18)
        pdf.cell(0, 10, "KCS Report", ln=True, align="C")
        pdf.ln(10)

        # Add charts and insights, each on a new page
        for idx, (title, img_path, insight) in enumerate(image_paths):
            pdf.add_page()
            pdf.set_font(font_name, "", 14)
            pdf.cell(0, 10, title, ln=True)
            pdf.ln(2)
            pdf.image(img_path, w=180)
            pdf.ln(8)
            if insight:
                # Special formatting for KCS Engagement insight (first chart)
                if idx == 0 and isinstance(insight, str) and insight.replace('.', '', 1).isdigit():
                    formatted = format_kcs_engagement_insight(insight)
                    pdf.set_font(font_name, "", 12)
                    pdf.multi_cell(0, 10, formatted)
                else:
                    pdf.set_font(font_name, "", 12)
                    # Convert dict insight to string if needed
                    if isinstance(insight, dict):
                        insight_str = "\n".join(f"{k}: {v}" for k, v in insight.items())
                        pdf.multi_cell(0, 10, insight_str)
                    else:
                        pdf.multi_cell(0, 10, str(insight))
                pdf.ln(2)

        pdf.output(output_path)
        print(f"PDF report saved to {output_path}")
