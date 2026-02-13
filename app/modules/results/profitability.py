from pathlib import Path

from empire.input_client.client import EmpireInputClient
from empire.output_client.client import EmpireOutputClient

if __name__ == "__main__":
    active_results = Path(
        "/Users/martihj/mnt/Solstorm/OpenEMPIRE/Results/norway_anaalysis/ncc6000.0_na0.75_w0.0_wog0.0_pTrue"
    )
    active_results = Path(
        "/Users/martihj/gitsource/OpenEMPIRE/Results/norway_analysis/ncc6000.0_na0.75_w0.0_wog0.0_pTrue"
    )
    output_client = EmpireOutputClient(output_path=active_results / "Output")
    input_client = EmpireInputClient(dataset_path=active_results / "Input/Xlsx")

    df = output_client.get_node_operational_values()

    df[df["Period"] == "2055-2060"]

    period = "2055-2060"
    df_t = df.query(f"Period == '{period}'")

    generator_columns = [
        "Liginiteexisting_MW",
        "Lignite_MW",
        "LigniteCCSadv_MW",
        "Coalexisting_MW",
        "Coal_MW",
        "CoalCCSadv_MW",
        "Gasexisting_MW",
        "GasOCGT_MW",
        "GasCCGT_MW",
        "GasCCSadv_MW",
        "Oilexisting_MW",
        "Bioexisting_MW",
        "Bio10cofiring_MW",
        "Nuclear_MW",
        "Wave_MW",
        "Geo_MW",
        "Hydroregulated_MW",
        "Hydrorun-of-the-river_MW",
        "Bio_MW",
        "Windonshore_MW",
        "Windoffshoregrounded_MW",
        "Windoffshorefloating_MW",
        "Solar_MW",
        "Bio10cofiringCCS_MW",
        "LigniteCCSsup_MW",
        "CoalCCS_MW",
        "GasCCS_MW",
        "Waste_MW",
        "storCharge_MW",
        "storDischarge_MW",
        "storEnergyLevel_MWh",
        "LossesChargeDischargeBleed_MW",
    ]

    df_rev = df_t[["Node", "Scenario", "Hour"]].copy(deep=True)
    for col in generator_columns:
        df_rev["Rev_" + col] = df_t[col] * df_t["Price_EURperMWh"] * 1.0

    df_rev
