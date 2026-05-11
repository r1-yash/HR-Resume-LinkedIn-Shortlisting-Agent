from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import List, Dict, Any

def generate_pdf_report(candidates: List[Dict[str, Any]], output_path: str):
    """Generates a PDF report from a list of candidate results."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []
    
    title_style = styles['Heading1']
    Story.append(Paragraph("HR Shortlisting Report", title_style))
    Story.append(Spacer(1, 12))
    
    for i, candidate in enumerate(candidates, 1):
        Story.append(Paragraph(f"{i}. {candidate['candidate_name']} (ID: {candidate['candidate_id']})", styles['Heading2']))
        Story.append(Paragraph(f"<b>Final Score:</b> <font color='red'>{candidate['final_score']} / 100</font>", styles['Normal']))
        Story.append(Paragraph(f"<b>Recommendation:</b> {candidate['recommendation']}", styles['Normal']))
        Story.append(Spacer(1, 6))
        
        # Dimensions Table
        data = [["Dimension", "Score", "Weight", "Justification"]]
        dims = candidate['dimensions']
        
        for d_key, d_val in dims.items():
            data.append([
                d_key.capitalize(),
                str(d_val['score']),
                f"{int(d_val['weight']*100)}%",
                Paragraph(d_val['justification'], styles['Normal'])
            ])
            
        t = Table(data, colWidths=[100, 50, 50, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        Story.append(t)
        Story.append(Spacer(1, 24))
        
    doc.build(Story)
    return output_path
