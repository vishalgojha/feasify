"""Report generation - JSON, CLI (Rich tables), and PDF output."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, field
import logging

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("reportlab not installed. PDF generation will be unavailable.")

logger = logging.getLogger(__name__)

@dataclass
class ProjectReport:
    """Complete project feasibility report."""
    cts_number: str
    generated_at: str = ""
    plot_details: Dict[str, Any] = field(default_factory=dict)
    spatial_context: Dict[str, Any] = field(default_factory=dict)
    design: Dict[str, Any] = field(default_factory=dict)
    clearances: List[Dict[str, Any]] = field(default_factory=list)
    cost_stack: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""
    risks: List[str] = field(default_factory=list)
    critical_path: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()


def generate_report(
    cts_number: str,
    spatial_context: Dict[str, Any],
    design: Dict[str, Any],
    clearances: List[Dict[str, Any]],
    cost_stack: Dict[str, Any],
    recommendation: str,
    risks: List[str] = None,
    output_dir: str = "data/reports"
) -> Dict[str, Any]:
    """
    Compile all analysis into a structured ProjectReport and save JSON.
    
    Args:
        cts_number: CTS number
        spatial_context: Output from get_spatial_context()
        design: Output from calculate_feasibility()
        clearances: Output from resolve_clearances()
        cost_stack: Output from build_cost_stack()
        recommendation: Agent's recommendation text
        risks: List of identified risks
        output_dir: Directory to save reports
    
    Returns:
        Dictionary with report summary and file paths
    """
    report = ProjectReport(
        cts_number=cts_number,
        spatial_context=spatial_context,
        design=design,
        clearances=clearances,
        cost_stack=cost_stack,
        recommendation=recommendation,
        risks=risks or [],
    )
    
    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = output_path / f"{cts_number}_{timestamp}.json"
    try:
        with open(json_file, 'w') as f:
            json.dump(report.__dict__, f, indent=2, default=str)
        logger.info(f"JSON report saved: {json_file}")
    except Exception as e:
        logger.error(f"Failed to save JSON report: {e}")
        json_file = None
    
    return {
        "cts_number": cts_number,
        "generated_at": report.generated_at,
        "json_file": str(json_file) if json_file else None,
        "summary": {
            "total_cost": cost_stack.get("grand_total", 0),
            "cost_per_sqft": cost_stack.get("cost_per_sqft", 0),
            "max_fsi": design.get("max_permissible_fsi", 0),
            "height_m": design.get("approx_height_m", 0),
            "num_clearances": len(clearances),
            "max_timeline_days": max((c.get("timeline_days", 0) for c in clearances), default=0),
        },
        "recommendation": recommendation,
        "risks": risks or [],
    }


def print_cli_report(report: ProjectReport):
    """Print formatted report to CLI using Rich tables."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
        
        console = Console()
        
        # Title
        console.print(Panel.fit(
            f"[bold cyan]Feasify Project Report[/bold cyan]\n"
            f"CTS: {report.cts_number} | Generated: {report.generated_at[:10]}",
            title="Mumbai Real Estate Feasibility"
        ))
        
        # Plot & Design Table
        design_table = Table(title="Plot & Design")
        design_table.add_column("Parameter", style="cyan")
        design_table.add_column("Value", style="green")
        
        if report.plot_details:
            for key in ["plot_id", "area_sqft", "zone_type", "owner", "address"]:
                if key in report.plot_details:
                    design_table.add_row(key.replace("_", " ").title(), str(report.plot_details[key]))
        
        if report.design:
            design_table.add_row("Max FSI", str(report.design.get("max_permissible_fsi", "N/A")))
            design_table.add_row("BUA (sqft)", f"{report.design.get('permissible_bua_sqft', 0):,.0f}")
            design_table.add_row("Height (m)", f"{report.design.get('approx_height_m', 0):.1f}")
            design_table.add_row("Floors", str(report.design.get("floors_feasible", "N/A")))
        
        console.print(design_table)
        
        # Clearances Table
        if report.clearances:
            clearance_table = Table(title="Required Clearances")
            clearance_table.add_column("Clearance", style="cyan")
            clearance_table.add_column("Days", style="yellow")
            clearance_table.add_column("Fee (₹)", style="red")
            clearance_table.add_column("Risk", style="magenta")
            
            for c in report.clearances:
                clearance_table.add_row(
                    c.get("name", ""),
                    str(c.get("timeline_days", 0)),
                    f"{c.get('fee', 0):,.0f}",
                    c.get("risk_level", "low")
                )
            
            console.print(clearance_table)
        
        # Cost Stack Table
        if report.cost_stack:
            cost_table = Table(title="Cost Stack")
            cost_table.add_column("Component", style="cyan")
            cost_table.add_column("Amount (₹)", style="green")
            
            cs = report.cost_stack
            cost_table.add_row("Land Cost", f"{cs.get('land_cost', 0):,.0f}")
            cost_table.add_row("Construction", f"{cs.get('construction', {}).get('total_construction', 0):,.0f}")
            cost_table.add_row("Govt. Premiums", f"{cs.get('government_premiums', {}).get('total_government_premiums', 0):,.0f}")
            cost_table.add_row("Professional Fees", f"{cs.get('professional_fees', {}).get('total_professional_fees', 0):,.0f}")
            cost_table.add_row("Clearances", f"{cs.get('clearances', {}).get('total_clearance_fees', 0):,.0f}")
            cost_table.add_row("Financing", f"{cs.get('financing', {}).get('financing_cost', 0):,.0f}")
            cost_table.add_row("[bold]Grand Total[/bold]", f"[bold]₹{cs.get('grand_total', 0):,.0f}[/bold]")
            cost_table.add_row("Cost/sqft", f"₹{cs.get('cost_per_sqft', 0):.0f}")
            
            console.print(cost_table)
        
        # Recommendation
        if report.recommendation:
            console.print(Panel(
                report.recommendation,
                title="Recommendation",
                border_style="green"
            ))
        
        # Risks
        if report.risks:
            console.print("[bold red]Identified Risks:[/bold red]")
            for i, risk in enumerate(report.risks, 1):
                console.print(f"  {i}. {risk}")
        
        # Critical Path
        if report.critical_path:
            cp = report.critical_path
            console.print(Panel(
                f"Critical Path: {' → '.join(cp.get('critical_sequence', []))}\n"
                f"Total Days: {cp.get('total_days', 0)}\n"
                f"Bottleneck: {cp.get('bottleneck', 'N/A')} ({cp.get('bottleneck_risk', 'unknown')} risk)",
                title="Timeline Analysis"
            ))
        
    except ImportError:
        logger.warning("rich not installed. Using plain text output.")
        print_report_plain(report)


def print_report_plain(report: ProjectReport):
    """Fallback plain text report."""
    print("=" * 60)
    print(f"FEASIFY PROJECT REPORT - CTS: {report.cts_number}")
    print("=" * 60)
    print(f"\nDesign:")
    if report.design:
        for key, value in report.design.items():
            print(f"  {key}: {value}")
    
    print(f"\nClearances ({len(report.clearances)}):")
    for c in report.clearances:
        print(f"  {c.get('name')}: {c.get('timeline_days')} days, ₹{c.get('fee', 0):,.0f}")
    
    print(f"\nRecommendation:")
    print(report.recommendation)
    
    if report.risks:
        print(f"\nRisks:")
        for risk in report.risks:
            print(f"  • {risk}")


def generate_pdf_report(
    report: ProjectReport,
    output_dir: str = "data/reports"
) -> str:
    """
    Generate PDF report using reportlab.
    
    Returns:
        Path to generated PDF file
    """
    if not REPORTLAB_AVAILABLE:
        logger.error("reportlab not installed. Cannot generate PDF.")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    pdf_file = output_path / f"{report.cts_number}_{timestamp}.pdf"
    
    try:
        doc = SimpleDocTemplate(str(pdf_file), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title Page
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E88E5'),
            spaceAfter=30,
        )
        story.append(Paragraph("Feasify Project Report", title_style))
        story.append(Paragraph(f"CTS Number: {report.cts_number}", styles['Normal']))
        story.append(Paragraph(f"Generated: {report.generated_at[:10]}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
        
        # Plot Details
        if report.plot_details:
            story.append(Paragraph("Plot Details", styles['Heading2']))
            plot_data = [[key, str(value)] for key, value in report.plot_details.items() if key not in ['source', 'error']]
            plot_table = Table(plot_data, colWidths=[5*cm, 10*cm])
            plot_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212121')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(plot_table)
            story.append(Spacer(1, 0.3*cm))
        
        # Design Parameters
        if report.design:
            story.append(Paragraph("Design Parameters", styles['Heading2']))
            design_data = [["Parameter", "Value"]]
            for key in ["zonal_basic_fsi", "max_permissible_fsi", "permissible_bua_sqm", 
                         "approx_height_m", "floors_feasible", "parking_spaces_required"]:
                if key in report.design:
                    design_data.append([key.replace("_", " ").title(), f"{report.design[key]:.2f}"])
            
            design_table = Table(design_data, colWidths=[7*cm, 8*cm])
            design_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E88E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(design_table)
            story.append(Spacer(1, 0.3*cm))
        
        # Clearances
        if report.clearances:
            story.append(Paragraph("Required Clearances", styles['Heading2']))
            clear_data = [["Clearance", "Days", "Fee (₹)", "Risk"]]
            for c in report.clearances:
                clear_data.append([
                    c.get("name", ""),
                    str(c.get("timeline_days", 0)),
                    f"{c.get('fee', 0):,.0f}",
                    c.get("risk_level", "low")
                ])
            
            clear_table = Table(clear_data, colWidths=[4*cm, 3*cm, 4*cm, 4*cm])
            clear_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(clear_table)
            story.append(Spacer(1, 0.3*cm))
        
        # Cost Stack
        if report.cost_stack:
            story.append(Paragraph("Cost Stack", styles['Heading2']))
            cs = report.cost_stack
            cost_data = [["Component", "Amount (₹)"]]
            
            components = [
                ("Land Cost", cs.get("land_cost", 0)),
                ("Construction", cs.get("construction", {}).get("total_construction", 0)),
                ("Government Premiums", cs.get("government_premiums", {}).get("total_government_premiums", 0)),
                ("Professional Fees", cs.get("professional_fees", {}).get("total_professional_fees", 0)),
                ("Clearances", sum(c.get("fee", 0) for c in report.clearances)),
                ("Financing", cs.get("financing", {}).get("financing_cost", 0)),
            ]
            
            for name, amount in components:
                cost_data.append([name, f"₹{amount:,.0f}"])
            
            cost_data.append(["Grand Total", f"₹{cs.get('grand_total', 0):,.0f}"])
            cost_data.append(["Cost per sq.ft.", f"₹{cs.get('cost_per_sqft', 0):.0f}"])
            
            cost_table = Table(cost_data, colWidths=[8*cm, 7*cm])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (-1, -2), (-1, -1), colors.HexColor('#E8F5E9')),
                ('FONTNAME', (-1, -2), (-1, -1), 'Helvetica-Bold'),
            ]))
            story.append(cost_table)
            story.append(Spacer(1, 0.3*cm))
        
        # Recommendation
        if report.recommendation:
            story.append(Paragraph("Recommendation", styles['Heading2']))
            story.append(Paragraph(report.recommendation, styles['Normal']))
            story.append(Spacer(1, 0.3*cm))
        
        # Risks
        if report.risks:
            story.append(Paragraph("Identified Risks", styles['Heading2']))
            for risk in report.risks:
                story.append(Paragraph(f"• {risk}", styles['Normal']))
        
        doc.build(story)
        logger.info(f"PDF report generated: {pdf_file}")
        return str(pdf_file)
    
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {e}")
        return None
