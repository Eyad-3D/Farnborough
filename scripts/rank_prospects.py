#!/usr/bin/env python3
"""Rank FIA2026 UK-presence exhibitors by likely interest in AVL simulation
tools (and CAE/simulation generally). Reads data/uk_exhibitors.csv, applies
an explicit score map for named prospects plus keyword heuristics for the
rest, writes data/simulation_prospects.csv sorted by score.

Tiers:
 5 = Hot: electrified/hydrogen/eVTOL/UAV propulsion, engines, missiles - core AVL fit
 4 = Strong: design authorities with system/thermal/actuation/transmission sim needs
 3 = Moderate: general CAE users, flight dynamics, space thermal, eng-services, R&D orgs
 2 = Niche: manufacturing/process simulation only (casting, forging, composites, materials)
 1 = Unlikely: build-to-print, electronics CEM, distribution, services, associations
"""
import csv

EXPLICIT = {
 # ---- Tier 5: hot prospects ----
 "Vertical Aerospace": (5, "eVTOL OEM in certification: in-house battery packs, e-powertrain, thermal mgmt, loads - full AVL AAM stack (battery, e-drive, thermal, systems, XiL)"),
 "ZeroAvia": (5, "Hydrogen-electric powertrains: PEM fuel-cell stack/BoP simulation, H2 storage, e-motor, thermal - exactly AVL's H2 aviation offering; UK R&D at Kemble"),
 "Rolls-Royce Plc": (5, "Gas turbines + UltraFan power gearbox (EXCITE-class dynamics), combustion, thermals, hybrid-electric heritage (ACCEL); largest UK CAE budget, entrenched in-house/vendor mix"),
 "GKN Aerospace": (5, "H2GEAR liquid-hydrogen propulsion programme + electrical wing at Global Technology Centre Bristol: fuel-cell, cryogenic thermal and e-systems simulation"),
 "Evolito": (5, "Aerospace axial-flux e-motors + DAL-A power systems: electromagnetic/thermal/NVH e-machine simulation (EXCITE M class) and certification-grade MBD"),
 "Intelligent Energy Ltd": (5, "Aviation hydrogen fuel cells (IE-FLIGHT): stack electrochemistry, thermal and system simulation - direct FIRE M / CRUISE M fit"),
 "MBDA (UK) / MBDA Corporate": (5, "Missile propulsion (solid/turbojet), aerothermal, guidance HWIL, model-based engineering at Stevenage/Bristol; deep simulation budget"),
 "BAE Systems": (5, "GCAP/Tempest model-based digital enterprise, PHASA-35 HAPS (solar-electric, batteries), hybrid demonstrators; enterprise-scale co-simulation/XiL buyer"),
 "GCAP Agency and Edgewing": (5, "Next-gen fighter JV standing up a digital/model-based engineering ecosystem in Reading now - co-simulation, digital twin and toolchain decisions being made"),
 "Airbus": (5, "Filton wing aero/loads + ZEROe hydrogen workstreams; large multiphysics estate; UK R&D buys tools locally"),
 "Hewland Engineering": (5, "Designs+tests aerospace/eVTOL transmissions: gear dynamics and NVH simulation (EXCITE core use-case)"),
 "Helix": (5, "Aerospace electric powertrains (ex-Integral Powertrain, automotive pedigree - likely already knows AVL): e-machine + inverter design simulation"),
 "Drive System Design": (5, "Electrified-propulsion engineering consultancy: heavy simulation user (also a services competitor); buys e-drive/system tools"),
 "Greenjets Ltd": (5, "Electric ducted-fan propulsion development: fan aero CFD, e-motor, battery-system simulation"),
 "PMW Dynamics": (5, "Bespoke aerospace e-motors (jet starters, UAV/HAPS propulsion): EM-thermal motor design simulation"),
 "Nema Ltd": (5, "High-speed high-temp aerospace motors + active magnetic bearing R&D: rotordynamics + EM co-simulation"),
 "Avvron Ltd": (5, "UK-designed heavy-fuel UAV engines: classic AVL fit (cycle sim, combustion CFD, cranktrain/friction dynamics)"),
 "Leonardo SpA": (5, "Yeovil helicopters: main-gearbox dynamics/NVH (EXCITE Power Unit territory), rotor loads, electrification studies; Edinburgh radar thermal"),
 "RTX (Pratt & Whitney | Collins | Raytheon)": (5, "Collins Wolverhampton elecTRAS electro-mechanical actuation centre: EMA, power-electronics and thermal simulation; local UK engineering procurement"),
 "ITP Aero": (5, "Whetstone engine design centre (~850 eng): rotatives design, engine-airframe integration, control systems, test-rig modelling"),
 # ---- Tier 4: strong ----
 "AALTO": (4, "Zephyr stratospheric UAS: battery (Si-anode), solar-electric propulsion, extreme thermal - battery aging + thermal simulation"),
 "Lockheed Martin (+ Corporation)": (4, "LM UK Ampthill military land vehicles/turrets: AVL's defence powertrain + vehicle-systems simulation strength applies"),
 "QinetiQ Ltd": (4, "National T&E and research house: broad modelling & simulation user across air/land/sea; tool-evaluation culture"),
 "Eaton (+ Ultra PCS)": (4, "Fuel systems + air-to-air refuelling (Wimborne) and stores/controls (Cheltenham): fluid-system and controls simulation"),
 "Parker Aerospace (incl. Parker Meggitt)": (4, "Braking thermal, fire/sensing, fluid conveyance engineering at Ansty: thermal + fluid system simulation"),
 "Honeywell (Aerospace + Control Systems Ltd)": (4, "Yeovil environmental control/life support: thermodynamic + fluid system simulation (toolchain often US-steered)"),
 "GE Aerospace": (4, "Cheltenham avionics/power + Dowty adjacency; strong in-house tools, selective external buys"),
 "Dowty, a GE Aerospace company": (4, "Propeller design Gloucester: aeroelastics, composites, hub dynamics simulation"),
 "Moog Inc.": (4, "Tewkesbury actuation design: servo-hydraulic/EMA system simulation"),
 "Olsen Actuators & Drives": (4, "EMA/roller-screw design for space/eVTOL/defence: drivetrain + motor simulation"),
 "AMETEK": (4, "Airtechnology Weybridge fans/motors/thermal systems: fan aero + e-motor simulation"),
 "Cambridge Aerospace": (4, "Interceptor developer (Skyhammer): propulsion, aero, GNC simulation - fast-moving, tool-hungry startup"),
 "Callen-Lenz": (4, "UAS design house: flight dynamics, propulsion integration, autonomy simulation"),
 "Windracers": (4, "ULTRA heavy-lift UAV OEM: piston propulsion integration, flight loads, reliability modelling"),
 "Zero Emissions Aerospace (ZeAero)": (4, "Zero-emission propulsion engineering: hydrogen/electric system simulation (small team)"),
 "Argive": (4, "Alloyed venture: engines via digital twin + AM - builds own digital platform, may license combustion/system CAE"),
 "B2Space": (4, "Near-space launch (rockoon): propulsion, aerothermal, trajectory simulation (early stage)"),
 "Missiles and Space Batteries Ltd": (4, "Thermal battery design: electrochemical + thermal transient simulation (niche chemistry)"),
 "Stirling Dynamics": (4, "Flight controls/actuation + simulation services (Expleo): buys modelling tools; also partner/competitor for services"),
 "Elbit Systems": (3, "UK electro-optics/avionics engineering: moderate multiphysics needs"),
 "Saab AB": (4, "Saab UK: Blue Bear (Bedford) autonomy R&D + Seaeye (Fareham) electric underwater vehicles - batteries, e-motors, autonomy sim"),
 "Héroux-Devtek": (4, "APPH Runcorn landing-gear design: drop dynamics, hydraulics, structures simulation"),
 "CAV Systems Ltd": (4, "Ice protection design: icing CFD (FENSAP-class) + thermal simulation - strong general-CAE buyer, low AVL overlap"),
 "Martin-Baker Aircraft Co.": (4, "Ejection systems: crash/multibody/aero/pyro simulation - heavy general-CAE user, low AVL overlap"),
 # ---- Tier 3 ----
 "AtkinsRéalis": (3, "Engineering consultancy: bulk CAE license buyer + potential channel/partner"),
 "Tata Technologies Europe Ltd": (3, "Engineering services (Warwick): heavy sim user, also a competitor/reseller ecosystem"),
 "Amentum": (3, "Engineering services: project-driven simulation use"),
 "L3Harris Technologies": (3, "Crawley builds training simulators - simulation company itself; buys flight models/IGs rather than CAE"),
 "Babcock International Group": (3, "Support engineering: selective simulation use"),
 "Marshall Aerospace": (3, "Mods/integration engineering: structures/fuel system analysis"),
 "General Dynamics Mission Systems": (3, "Hastings avionics: HIL/embedded rather than multiphysics"),
 "Northrop Grumman": (3, "UK nav/mission systems: moderate"),
 "Surrey Satellite Technology Ltd": (3, "Spacecraft thermal/power simulation (space-specific toolchain)"),
 "Space Forge": (3, "Re-entry aerothermal + in-space process simulation (space-specific)"),
 "Open Cosmos": (3, "Smallsat design: mission/thermal sim, space-specific"),
 "AALTO dup": (0, ""),
 "Goonhilly / COMSAT": (2, "Ground segment: RF/link budget, little multiphysics"),
 "Viasat": (2, "UK ops/engineering is comms-centric"),
 "Eutelsat Group": (2, "OneWeb ops: constellation/link simulation, space-specific"),
 "MDA Space": (3, "Harwell robotics: multibody/controls simulation"),
 "QinetiQ - Pioneers of Tomorrow": (1, "Careers stand (company ranked separately)"),
 "Transense Technologies plc": (3, "SAW torque/temperature sensing R&D: partner potential for test/validation more than CAE buyer"),
 "D-RisQ Ltd": (2, "Sells formal-verification software: partner in certification MBD toolchains, not a CAE buyer"),
 "TWI Limited": (3, "Joining/structural integrity RTO: process + FEA simulation services buyer"),
 "Lucideon": (2, "Materials consultancy: limited CAE"),
 "Element Materials Technology": (2, "Physical test house: complementary to simulation, small tool spend"),
 "TISICS Ltd": (3, "Metal-matrix composite development: micromechanics/process modelling"),
 "iCOMAT": (3, "Fibre-steered composites: process + structural simulation user"),
 "Hexcel": (3, "Duxford composites R&D: process/materials modelling"),
 "Syensqo": (3, "Composite materials R&D: process/materials modelling"),
 "SHD Composite Materials": (2, "Prepreg manufacture: modest process modelling"),
 "Duvelco Limited": (2, "Polyimide materials: tribology/materials characterisation, small CAE need"),
 "Castings Technology (Cti)": (3, "Casting R&D house: solidification/process simulation (MAGMA/ProCAST class)"),
 "Proxima Powder Metallurgy": (3, "PM-HIP aerostructures: process + structures simulation for design freedom claims"),
 "Doncasters": (2, "Precision casting: process simulation only"),
 "Expromet Technologies Group": (2, "Castings group: process simulation only"),
 "Forged Solutions Group": (2, "Forging: process simulation (FORGE/DEFORM class)"),
 "Independent Forgings & Alloys": (2, "Forging: process simulation only"),
 "Special Quality Alloys": (2, "Forging/processing: process simulation only"),
 "Loop Technology": (2, "Composites automation: robot/offline-programming simulation"),
 "Cygnet Texkimp": (2, "Machinery design: machine FEA, niche"),
 "TEK4 Limited": (2, "EDM machine design: machine-level FEA/controls"),
 "Scintam Engineering": (2, "Portable EDM tools: EDM process modelling, niche"),
 "Cranfield University (+ CraneAero PoT)": (3, "Academic: propulsion/electrification research - university partnership programme target"),
 "University of Nottingham": (3, "Institute for Aerospace Technology: UK aerospace electrification research hub - strong academic target"),
 "Institute for Aerospace Technology (Univ. of Nottingham)": (3, "As above (exhibits on MAA stand)"),
 "AVRRC, Loughborough University": (3, "VR/simulation research centre; Loughborough links to Intelligent Energy"),
 "Altitude, University of Lancashire": (3, "Air/space innovation facility with indoor flight-test zone"),
 "Advanced Manufacturing Innovation Centre (AMIC)": (3, "QUB Belfast manufacturing R&D: process simulation"),
 "NCC and West of England Mayoral Combined Authority": (3, "National Composites Centre: composites process simulation at scale"),
 "High Value Manufacturing Catapult": (3, "Manufacturing R&D network: process simulation"),
 "Aerospace Technology Institute": (3, "Programme funder/influencer for UK propulsion R&D (not a buyer itself)"),
 "Alfor Aviation": (3, "P2F conversion development: structures/loads simulation"),
 "UAVE Ltd": (3, "Long-endurance UAV manufacture/ops: flight-performance + engine integration modelling"),
 "Novomorphic Ltd": (2, "Semiconductor design house: EDA simulation (Cadence ecosystem), not multiphysics CAE"),
 "Phixos": (2, "Safety-critical software/hardware engineering: V&V tooling rather than CAE"),
 "Antrica": (2, "Video encoder boards: SI/thermal at board level"),
 "Smith Myers Communications": (2, "Airborne comms: RF simulation niche"),
 "HR Smith Group": (2, "Antennas/ELT: RF simulation niche"),
 "Oxley Group": (2, "Electronics/lighting design: modest thermal/optical simulation"),
 "Matt Black Systems": (2, "MMI/avionics units: modest structural/thermal analysis"),
 "Barnbrook Systems Ltd": (2, "Electro-mechanical units: modest"),
 "Cross Manufacturing": (3, "Brush/ring seals for engines: secondary-air + sealing simulation, credible niche"),
 "Porvair Filtration Group": (2, "Filtration: CFD niche"),
 "Pall Corporation": (3, "Portsmouth filtration R&D: CFD user"),
 "SKF": (3, "AMPEP Clevedon aero bearings: tribology simulation (largely in-house SKF tools)"),
 "HQW Aerospace": (2, "Precision bearings: bearing analysis niche"),
 "CDI-Hallite Aerospace": (2, "Seals: elastomer FEA niche"),
 "Specialised Polymer Engineering": (2, "Seals: elastomer FEA niche"),
 "Southbourne Rubber": (1, "Seals build-to-print"),
 "Trelleborg Aerospace": (2, "Seal design: elastomer FEA"),
 "Magnet Schultz Ltd": (3, "Solenoid/electromagnet design: EM simulation buyer (JMAG/Maxwell class)"),
 "Teledyne": (2, "e2v sensors/semis: device-level TCAD/EDA, not AVL domain"),
 "Amphenol Ltd": (2, "Interconnect design: SI + mechanical FEA niche"),
 "Intelligent? dup": (0, ""),
}

KEYWORD_TIERS = [
 (["stockholder","distributor","distribution","supply","stockist","logistics","recruitment","talent","consultancy","HR services","certification services","education","careers","animation","fumigation","packaging","flight case","furniture","investment","inward","trade association","government","university","council","charity","regulator","funding","catapult","agency","livery","non-profit"], 1),
 (["machining","CNC","precision engineering","build-to-print","make-to-print","fabrication","fasteners","springs","pressings","castings","forging","plating","heat treatment","coatings","surface","tooling","gears","gearboxes","sheet-metal","wire","tube","rolled","extrusion","mouldings","plastics","composites manufacture","electronics manufacture","PCB","CEM","cables"], 1),
]

def heuristic(basis):
    b = basis.lower()
    for words, tier in KEYWORD_TIERS:
        if any(w.lower() in b for w in words):
            return tier
    return 1

rows = []
with open("data/uk_exhibitors.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        name = r["Company Name"]; cat = r["Category"]
        if cat.startswith("UK organisation") and name not in EXPLICIT:
            tier, why = 1, "Organisation - not a tool buyer (see notes for research bodies)"
        elif cat.startswith("UK-based distribution") and name not in EXPLICIT:
            tier, why = 1, "Distribution/services - no simulation need"
        elif name in EXPLICIT:
            tier, why = EXPLICIT[name]
            if tier == 0:
                continue
        else:
            tier = heuristic(r["UK Presence (basis)"])
            why = "Heuristic: " + ("manufacturing/services profile - little design simulation" if tier == 1 else "")
        rows.append({"Company": name, "Stand": r["Stand Number"], "Tier (5=hot)": tier,
                     "Rationale": why, "Category": cat, "UK basis": r["UK Presence (basis)"],
                     "Source Page": r["Source Page"]})

rows.sort(key=lambda x: (-x["Tier (5=hot)"], x["Company"].lower()))
with open("data/simulation_prospects.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["Tier (5=hot)", "Company", "Stand", "Rationale", "Category", "UK basis", "Source Page"])
    w.writeheader()
    for r in rows:
        w.writerow(r)

from collections import Counter
print("total:", len(rows), Counter(r["Tier (5=hot)"] for r in rows))
for r in rows[:25]:
    print(r["Tier (5=hot)"], "|", r["Company"], "|", r["Stand"])
