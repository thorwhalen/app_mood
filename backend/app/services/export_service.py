"""Export service for generating downloadable files."""
import csv
import io
from typing import List
from ..models import Analysis


def export_analyses_to_csv(analyses: List[Analysis]) -> str:
    """
    Export analysis results to CSV format.

    Args:
        analyses: List of Analysis objects to export

    Returns:
        CSV content as string
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "ID",
        "Mood ID",
        "Model ID",
        "User ID",
        "Input Text",
        "Sentiment Score",
        "Analyzed At"
    ])

    # Write data rows
    for analysis in analyses:
        writer.writerow([
            analysis.id,
            analysis.mood_id,
            analysis.model_id or "",
            analysis.user_id or "",
            analysis.input_text,
            analysis.score,
            analysis.analyzed_at.isoformat()
        ])

    return output.getvalue()
