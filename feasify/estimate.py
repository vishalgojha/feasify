"""Detailed project estimate command - reverse engineer costs."""
import subprocess
from datetime import datetime


def run_estimate(
    cts_number="N/A",
    plot_area=500,
    zone="suburbs",
    use_type="residential",
    floors=15,
    road_width=12,
    unit_mix="",
    land_cost=0,
    finish="premium",
):
    """Run detailed project cost estimate - reverse from params to cost."""
    
    print("\n" + "="*60)
    print("FEASIFY PROJECT ESTIMATE - " + cts_number)
    print("="*60)
    print("Location: " + zone.title() + " | Plot: " + str(plot_area) + " sq.m")
    print("Floors: " + str(floors) + " | Use: " + use_type + " | Finish: " + finish)
    
    # Step 1: Feasibility
    print("\n[1] Calculating feasibility...")
    fea = subprocess.run(
        ["python", "-m", "feasify", "feasibility", str(plot_area), zone, 
         use_type, str(road_width), str(floors), "--json"],
        capture_output=True, text=True, cwd=".", errors="replace"
    )
    
    # Parse JSON manually
    fea_data = {}
    for line in fea.stdout.split('\n'):
        line = line.strip()
        if line.startswith('{') and '"zonal_basic_fsi"' in line:
            start = line.find('{')
            end = line.rfind('}') + 1
            if start >= 0 and end > 0:
                import json
                try:
                    fea_data = json.loads(line[start:end])
                except:
                    pass
            break
    
    bua_sqft = fea_data.get("permissible_bua_sqft", 11840)
    max_fsi = fea_data.get("max_permissible_fsi", 2.2)
    height = fea_data.get("approx_height_m", 45)
    
    print("   Base FSI: " + str(fea_data.get("zonal_basic_fsi", 1.0)) + " | Max FSI: " + str(max_fsi))
    print("   Buildable: " + str(int(bua_sqft)) + " sqft | Height: " + str(height) + "m")
    
    # Step 2: Cost (main calculation)
    print("\n[2] Calculating cost...")
    land = land_cost * 1e7 if land_cost > 0 else 0
    cost_cmd = subprocess.run(
        ["python", "-m", "feasify", "cost", str(int(bua_sqft)), zone, str(floors),
         use_type, "--finish", finish, "--land-cost", str(int(land)), "--json"],
        capture_output=True, text=True, cwd=".", errors="replace"
    )
    
    cost_data = {}
    for line in cost_cmd.stdout.split('\n'):
        line = line.strip()
        if line.startswith('{') and '"grand_total"' in line:
            import json
            start = line.find('{')
            end = line.rfind('}') + 1
            if start >= 0 and end > 0:
                try:
                    cost_data = json.loads(line[start:end])
                except:
                    pass
            break
    
    total_const = cost_data.get("construction", {}).get("total_construction", 0)
    grand_total = cost_data.get("grand_total", 0)
    cost_per_sqft = cost_data.get("cost_per_sqft", 0)
    
    print("   Construction: Rs " + str(int(total_const/1e7)) + " Cr")
    print("   Grand Total: Rs " + str(int(grand_total/1e7)) + " Cr")
    
    # Step 3: Unit mix
    print("\n[3] Unit mix analysis...")
    units = {}
    if unit_mix:
        for part in unit_mix.split(","):
            if ":" in part:
                typ, cnt = part.split(":")
                units[typ.upper()] = int(cnt)
    
    sqft_per_unit = {"1BHK": 450, "2BHK": 650, "3BHK": 900, "4BHK": 1200}
    total_units = 0
    total_unit_area = 0
    
    if units:
        for utyp, cnt in units.items():
            sf = sqft_per_unit.get(utyp, 600)
            area = sf * cnt
            total_units += cnt
            total_unit_area += area
            print("   " + str(cnt) + " x " + utyp + " (" + str(sf) + " sqft) = " + str(area) + " sqft")
        print("   TOTAL: " + str(total_units) + " units | " + str(total_unit_area) + " sqft")
    else:
        saleable = int(bua_sqft * 0.75)
        print("   Saleable area available: ~" + str(saleable) + " sqft (75% of BUA)")
    
    # =========================================================================
    # COST BREAKDOWN
    # =========================================================================
    print("\n" + "="*60)
    print("COST BREAKDOWN")
    print("="*60)
    
    # Construction detail
    pct_breakdown = {
        "Structure (RCC)": 0.35,
        "Brickwork": 0.12,
        "Plaster": 0.08,
        "Flooring": 0.10,
        "Finishing": 0.12,
        "Electrical": 0.08,
        "Plumbing": 0.07,
        "Other": 0.08
    }
    
    print("\nCONSTRUCTION (Rs " + str(int(total_const/1e7)) + " Cr):")
    for item, pct in pct_breakdown.items():
        amt = total_const * pct
        print("   " + item.ljust(15) + " Rs " + str(int(amt)).rjust(12) + "  (" + str(int(pct*100)) + "%)")
    print("   " + "-"*15 + " Rs " + str(int(total_const)).rjust(12))
    
    # Govt premiums
    gp = cost_data.get("government_premiums", {})
    print("\nGOVERNMENT PREMIUMS:")
    for k in ["additional_fsi_premium", "development_cess", "infrastructure_levy"]:
        if k in gp:
            print("   " + k.replace("_", " ").title().ljust(20) + " Rs " + str(int(gp.get(k, 0))).rjust(12))
    print("   " + "TOTAL".ljust(20) + " Rs " + str(int(gp.get("total_government_premiums", 0))).rjust(12))
    
    # Professional fees
    pf = cost_data.get("professional_fees", {})
    print("\nPROFESSIONAL FEES:")
    for k, v in pf.items():
        if isinstance(v, (int, float)) and v > 0:
            print("   " + k.replace("_", " ").title().ljust(20) + " Rs " + str(int(v)).rjust(12))
    
    # Statutory
    st = cost_data.get("statutory", {})
    print("\nSTATUTORY:")
    for k, v in st.items():
        if isinstance(v, (int, float)) and v > 0:
            print("   " + k.replace("_", " ").title().ljust(20) + " Rs " + str(int(v)).rjust(12))
    
    # SUMMARY
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("Land Cost:          Rs " + str(int(cost_data.get("land_cost", 0))).rjust(12))
    print("Construction:      Rs " + str(int(total_const)).rjust(12))
    print("Govt Premiums:     Rs " + str(int(gp.get("total_government_premiums", 0))).rjust(12))
    print("Professional:      Rs " + str(int(pf.get("total_professional_fees", 0))).rjust(12))
    print("Statutory:         Rs " + str(int(st.get("total_statutory", 0))).rjust(12))
    fin = cost_data.get("financing", {}).get("financing_cost", 0)
    print("Financing:         Rs " + str(int(fin)).rjust(12))
    print("-"*60)
    print("GRAND TOTAL:       Rs " + str(int(grand_total)).rjust(12))
    print("\nCost per sq.ft: Rs " + str(int(cost_per_sqft)) + " | Cost per sq.m: Rs " + str(int(cost_data.get("cost_per_sqm", 0))))


if __name__ == "__main__":
    import sys
    
    # Simple argparse
    kwargs = {}
    for arg in sys.argv[1:]:
        if "=" in arg:
            k, v = arg.split("=")
            if k.startswith("--"):
                kwargs[k[2:]] = v
    
    run_estimate(**kwargs)


# CLI shortcut - just run with parameters
if __name__ == "__main__":
    # If run directly
    pass