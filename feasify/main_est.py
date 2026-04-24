"""Detailed project estimate command."""
from datetime import datetime


def run_estimate(
    cts_number: str = "N/A",
    plot_area: float = 500,
    zone: str = "suburbs",
    use_type: str = "residential",
    floors: int = 15,
    road_width: float = 12,
    unit_mix: str = "",
    land_cost: float = 0,
    finish: str = "premium",
    json_output: bool = False,
):
    """Run detailed project cost estimate."""
    from feasify.agents.cost_engine import build_cost_stack
    from feasify.agents.dcpr import calculate_feasibility
    from feasify.agents.clearance_engine import resolve_clearances
    import json
    
    # Parse unit mix
    units = {}
    if unit_mix:
        for part in unit_mix.split(","):
            if ":" in part:
                typ, cnt = part.split(":")
                units[typ.upper()] = int(cnt)
    
    # Calculate feasibility
    fea = calculate_feasibility(
        plot_area_sqm=plot_area,
        zone=zone,
        use_type=use_type,
        road_width_m=road_width,
        num_floors=floors
    )
    
    bua_sqm = fea.get("permissible_bua_sqm", 0)
    bua_sqft = bua_sqm * 10.764
    
    # Calculate clearances
    clearances = resolve_clearances(
        height_m=fea.get("approx_height_m", 45),
        bua_sqm=bua_sqm,
        plot_area_sqm=plot_area,
        use=use_type
    )
    
    # Calculate costs
    land = land_cost * 1e7 if land_cost > 0 else 0
    cost = build_cost_stack(
        bua_sqft=bua_sqft,
        zone_type=zone,
        num_floors=floors,
        base_construction_cost=0,
        clearance_fees=sum(c.get("fee", 0) for c in clearances),
        land_cost=land,
        finish_grade=finish,
        use=use_type,
        use_live_rates=True
    )
    
    # Build unit details
    unit_details = []
    if units:
        sqft_per_unit = {"1BHK": 450, "2BHK": 650, "3BHK": 900, "4BHK": 1200, "SHOP": 200}
        for utyp, cnt in units.items():
            sf = sqft_per_unit.get(utyp, 600)
            unit_details.append({
                "type": utyp,
                "count": cnt,
                "area_sqft": sf,
                "total_area": sf * cnt
            })
    
    result = {
        "project": {
            "cts_number": cts_number,
            "generated_at": datetime.now().isoformat(),
            "location": {"zone": zone, "plot_sqm": plot_area},
            "development": {"floors": floors, "bua_sqft": round(bua_sqft), "height_m": round(fea.get("approx_height_m", 0), 1)}
        },
        "feasibility": fea,
        "units": unit_details,
        "cost_detail": {
            "land_cost": cost["land_cost"],
            "construction": {"base": cost["construction"]["base_construction"], "material_prices": cost["construction"].get("material_prices", {}), "rate_source": cost["construction"].get("rate_source", "PWD")},
            "government_premiums": cost["government_premiums"],
            "professional_fees": cost["professional_fees"],
            "statutory": cost["statutory"],
            "financing": cost["financing"]
        },
        "clearances": clearances,
        "summary": {"grand_total": cost["grand_total"], "cost_per_sqft": cost["cost_per_sqft"], "cost_per_sqm": cost["cost_per_sqm"]}
    }
    
    if json_output:
        return json.dumps(result, default=str, indent=2)
    
    # Rich output
    print("\n" + "="*60)
    print(f"FEASIFY PROJECT ESTIMATE - {cts_number}")
    print("="*60)
    print(f"Plot: {plot_area} sq.m | Zone: {zone} | Floors: {floors}")
    print(f"BUA: {bua_sqft:,.0f} sqft | Height: {fea.get('approx_height_m', 0)}m")
    print("-"*60)
    
    # Unit mix
    if unit_details:
        print("\nUNIT MIX:")
        for u in unit_details:
            print(f"  {u['type']}: {u['count']} x {u['area_sqft']} = {u['total_area']:,} sqft")
        total_units = sum(u['count'] for u in unit_details)
        total_area = sum(u['total_area'] for u in unit_details)
        print(f"  TOTAL: {total_units} units | {total_area:,} sqft")
    
    print("\nCOST BREAKDOWN:")
    print(f"  Land:              ₹{land:>15,.0f}")
    print(f"  Construction:     ₹{cost['construction']['total_construction']:>15,.0f}")
    print(f"  Gov Premiums:      ₹{cost['government_premiums']['total_government_premiums']:>15,.0f}")
    print(f"  Professional:      ₹{cost['professional_fees']['total_professional_fees']:>15,.0f}")
    print(f"  Statutory:         ₹{cost['statutory']['total_statutory']:>15,.0f}")
    print(f"  Financing:        ₹{cost['financing']['financing_cost']:>15,.0f}")
    print("-"*60)
    print(f"  GRAND TOTAL:      ₹{cost['grand_total']:>15,.0f}")
    print(f"\n  Cost/sqft: ₹{cost['cost_per_sqft']:,.0f} | Cost/sqm: ₹{cost['cost_per_sqm']:,.0f}")
    
    return result