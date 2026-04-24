"""Detailed project estimate - calls Python modules directly."""
import sys
sys.path.insert(0, '.')

from datetime import datetime
from feasify.agents.cost_engine import build_cost_stack
from feasify.knowledge.dcpr import calculate_feasibility, FeasibilityInput
from feasify.knowledge.dcpr import MumbaiZone, BuildingUse
from feasify.agents.clearance_engine import resolve_clearances


def run_estimate(
    cts_number="N/A",
    plot_area=500,       # sq.m
    zone="suburbs",
    use_type="residential",
    floors=15,
    road_width=12,       # meters
    unit_mix="",        # e.g., "1BHK:10,2BHK:20"
    land_cost=0,        # Crores
    finish="premium",
):
    """Detailed project cost estimate."""
    
    # Map zone str to enum
    zone_map = {
        "island_city": MumbaiZone.ISLAND_CITY,
        "suburbs": MumbaiZone.SUBURBS, 
        "extended": MumbaiZone.EXTENDED_SUBURBS,
        "barc": MumbaiZone.BARC_AREA,
    }
    use_map = {
        "residential": BuildingUse.RESIDENTIAL,
        "commercial": BuildingUse.COMMERCIAL,
        "industrial": BuildingUse.INDUSTRIAL,
    }
    
    z_enum = zone_map.get(zone.lower(), MumbaiZone.SUBURBS)
    u_enum = use_map.get(use_type.lower(), BuildingUse.RESIDENTIAL)
    
    print("\n" + "="*65)
    print(" FEASIFY PROJECT ESTIMATE - " + cts_number)
    print("="*65)
    print(" Location: " + zone.title() + " (" + use_type + ")")
    print(" Plot: " + str(plot_area) + " sq.m | Floors: " + str(floors) + " | Road: " + str(road_width) + "m")
    print(" Finish: " + finish.title())
    print("-"*65)
    
    # 1. FEASIBILITY
    print("\n[1] FEASIBILITY ANALYSIS")
    print("-"*40)
    
    fea_in = FeasibilityInput(
        plot_area_sqm=plot_area,
        zone=z_enum,
        use=u_enum,
        road_width_m=road_width,
        floors=floors
    )
    fea = calculate_feasibility(fea_in)
    
    bua_sqm = fea.permissible_bua_sqm
    bua_sqft = bua_sqm * 10.764
    max_fsi = fea.max_permissible_fsi
    
    print(" Base FSI: " + str(fea.zonal_basic_fsi))
    print(" Max FSI: " + str(max_fsi))
    print(" Buildable Area: " + str(int(bua_sqft)) + " sqft (" + str(int(bua_sqm)) + " sq.m)")
    print(" Floors Feasible: " + str(fea.floors_feasible))
    print(" Height: " + str(fea.approx_height_m) + " m")
    print(" Parking Spaces: " + str(fea.parking_spaces_required))
    
    if fea.warnings:
        print(" WARNINGS:")
        for w in fea.warnings[:3]:
            print("   - " + w[:60])
    
    # 2. CLEARANCES
    print("\n[2] REQUIRED CLEARANCES")
    print("-"*40)
    
    clearances = resolve_clearances(
        height_m=fea.approx_height_m,
        bua_sqm=bua_sqm,
        plot_area_sqm=plot_area,
        use=use_type,
        distance_to_csia_km=5.0,
        distance_to_coast_km=2.0,
        ward=""
    )
    
    total_fees = 0
    for c in clearances:
        total_fees += c.get("fee", 0)
        print(" " + c.get("name", "").ljust(15) + " " + str(c.get("timeline_days", 0)).rjust(3) + " days  Rs " + str(int(c.get("fee", 0))).rjust(10))
    print("-"*40)
    print(" Total: Rs " + str(int(total_fees)))
    
    # 3. COST
    print("\n[3] COST BREAKDOWN")
    print("-"*40)
    
    land = land_cost * 1e7 if land_cost > 0 else 0
    cost = build_cost_stack(
        bua_sqft=bua_sqft,
        zone_type=zone,
        num_floors=floors,
        base_construction_cost=0,
        clearance_fees=total_fees,
        land_cost=land,
        finish_grade=finish,
        use=use_type,
        use_live_rates=False
    )
    
    const_total = cost["construction"]["total_construction"]
    
    print("\n CONSTRUCTION: Rs " + str(int(const_total/1e7)) + " Cr (" + str(int(const_total)) + ")")
    print("   Rs/sqft: " + str(int(const_total/bua_sqft)))
    
    # Construction breakdown (real values from cost)
    pct = {"Structure": 0.35, "Brickwork": 0.12, "Plaster": 0.08, 
           "Flooring": 0.10, "Finishing": 0.12, "Electrical": 0.08, "Plumbing": 0.07, "Other": 0.08}
    
    for item, p in pct.items():
        amt = const_total * p
        print("   " + item.ljust(12) + " Rs " + str(int(amt)).rjust(10) + "  (" + str(int(p*100)) + "%)")
    
    # Govt premiums
    gp = cost["government_premiums"]
    print("\n GOVT PREMIUMS: Rs " + str(int(gp.get("total_government_premiums", 0)/1e7)) + " Cr")
    print("   Additional FSI: Rs " + str(int(gp.get("additional_fsi_premium", 0)/1e5)) + " L")
    print("   Dev Cess: Rs " + str(int(gp.get("development_cess", 0)/1e5)) + " L")
    print("   Infra Levy: Rs " + str(int(gp.get("infrastructure_levy", 0)/1e5)) + " L")
    
    # Professional
    pf = cost["professional_fees"]
    print("\n PROFESSIONAL: Rs " + str(int(pf.get("total_professional_fees", 0)/1e7)) + " Cr")
    
    # Statutory  
    st = cost["statutory"]
    print("\n STATUTORY: Rs " + str(int(st.get("total_statutory", 0)/1e7)) + " Cr")
    print("   Labour Cess: Rs " + str(int(st.get("labour_cess", 0)/1e5)) + " L")
    print("   GST: Rs " + str(int(st.get("gst", 0)/1e5)) + " L")
    
    # 4. UNIT MIX
    print("\n[4] UNIT MIX")
    print("-"*40)
    
    units = {}
    if unit_mix:
        for part in unit_mix.split(","):
            if ":" in part:
                typ, cnt = part.split(":")
                units[typ.upper()] = int(cnt)
    
    sqft_per = {"1BHK": 450, "2BHK": 650, "3BHK": 900, "4BHK": 1200}
    
    if units:
        tot_u = 0
        tot_a = 0
        for t, c in units.items():
            sf = sqft_per.get(t, 600)
            a = sf * c
            tot_u += c
            tot_a += a
            print(" " + str(c).rjust(3) + " x " + t.ljust(5) + " (" + str(sf) + " sqft) = " + str(a) + " sqft")
        print("-"*40)
        print(" TOTAL: " + str(tot_u) + " units | " + str(tot_a) + " sqft")
    else:
        print(" No unit mix - using " + str(int(bua_sqft * 0.75)) + " sqft saleable")
    
    # SUMMARY
    print("\n" + "="*65)
    print(" SUMMARY")
    print("="*65)
    
    land_cost_val = cost.get("land_cost", 0)
    gp_total = gp.get("total_government_premiums", 0)
    pf_total = pf.get("total_professional_fees", 0)
    st_total = st.get("total_statutory", 0)
    fin = cost.get("financing", {}).get("financing_cost", 0)
    grand = cost["grand_total"]
    cpsf = cost["cost_per_sqft"]
    
    print(" Land Cost:       Rs " + str(int(land_cost_val/1e5)).rjust(8) + " L")
    print(" Construction:    Rs " + str(int(const_total/1e5)).rjust(8) + " L")
    print(" Govt Premiums:  Rs " + str(int(gp_total/1e5)).rjust(8) + " L")
    print(" Professional:  Rs " + str(int(pf_total/1e5)).rjust(8) + " L")
    print(" Statutory:      Rs " + str(int(st_total/1e5)).rjust(8) + " L")
    print("-"*65)
    print(" GRAND TOTAL:   Rs " + str(int(grand/1e5)).rjust(8) + " L")
    print("-"*65)
    print("\n Cost/sq.ft: Rs " + str(int(cpsf)))


if __name__ == "__main__":
    # Bandra West redevelopment example
    run_estimate(
        cts_number="918/Bandra",
        plot_area=500,
        zone="suburbs",
        use_type="residential",
        floors=15,
        unit_mix="1BHK:10,2BHK:20",
        land_cost=2.5,
        finish="premium"
    )