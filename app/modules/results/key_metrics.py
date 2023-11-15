import streamlit as st


class KeyMetricsResults:
    def __init__(self, output_client, input_client):
        self.output_client = output_client
        self.input_client = input_client

    def generators(self, period):
        df = self.output_client.get_generators_values()
        df.loc[df["genExpectedAnnualProduction_GWh"] < 1, "genExpectedCapacityFactor"] = 0.0
        df_temp = df[["Node", "GeneratorType", "Period", "genExpectedAnnualProduction_GWh"]]
        df["TotalGeneration_GWh"] = df_temp.groupby(["Node", "Period"])["genExpectedAnnualProduction_GWh"].transform(
            "sum"
        )
        df["GenerationShare_Percent"] = (df["genExpectedAnnualProduction_GWh"] / df["TotalGeneration_GWh"]) * 100

        df_temp = df[["Node", "GeneratorType", "Period", "genInstalledCap_MW"]]
        df["TotalCapacity_MW"] = df_temp.groupby(["Node", "Period"])["genInstalledCap_MW"].transform("sum")
        df["CapacityShare_Percent"] = (df["genInstalledCap_MW"] / df["TotalGeneration_GWh"]) * 100

        # Select measure
        measures = [
            "genInvCap_MW",
            "genInstalledCap_MW",
            "genExpectedCapacityFactor",
            "DiscountedInvestmentCost_Euro",
            "genExpectedAnnualProduction_GWh",
            "GenerationShare_Percent",
            "CapacityShare_Percent",
        ]
        measure = st.selectbox(
            "Select measure: ",
            measures,
            index=measures.index("GenerationShare_Percent") if "GenerationShare_Percent" in measures else 0,
        )

        df_sum = df.query(f"Period == '{period}'").pivot(index="Node", columns="GeneratorType", values=measure)

        # Select nodes and generators with defaults
        default_nodes = [
            "NO1",
            "NO2",
            "NO3",
            "NO4",
            "NO5",
            "Sweden",
            "Finland",
            "GreatBrit.",
            "France",
            "Italy",
            "Germany",
            "Poland",
            "SorligeNordsjoI",
            "SorligeNordsoII",
            "UtsiraNord",
        ]
        nodes = df_sum.index.to_list()
        selected_nodes = st.multiselect(
            "Select nodes: ", options=df_sum.index, default=[item for item in default_nodes if item in nodes]
        )
        selected_generators = st.multiselect(
            "Select generators: ", options=df_sum.columns, default=df_sum.columns.tolist()
        )

        # Process the dataframe and display it
        df_sum = (
            df_sum.loc[selected_nodes, selected_generators]
            .fillna(0.0)
            .loc[:, df_sum.sum(axis=0) > 1.0]
            .assign(Active_sum=lambda x: x.sum(axis=1))
            .T
        )

        return df_sum, measure, selected_nodes

    def average_power_prices(self, df, load_weighted: bool = True):
        if not load_weighted:
            avg_prices = df.groupby(["Node", "Period"])["Price_EURperMWh"].mean().to_frame().reset_index()
            avg_prices = avg_prices.pivot(columns="Node", index="Period")
            avg_prices.columns = avg_prices.columns.droplevel()

            return avg_prices

        else:
            df["PriceLoadWeighted"] = (df["Load_MW"] * df["Price_EURperMWh"]) / df.groupby(["Node", "Period"])[
                "Load_MW"
            ].transform("mean")

            # If NaN values (with zero load in node) fill the non-weighted price
            df.loc[:, "PriceLoadWeighted"] = df["PriceLoadWeighted"].fillna(df["Price_EURperMWh"])

            avg_weighted_price = df.groupby(["Node", "Period"])["PriceLoadWeighted"].mean().to_frame().reset_index()
            avg_weighted_price = avg_weighted_price.pivot(columns="Node", index="Period")

            df.drop(columns="PriceLoadWeighted")

            avg_weighted_price.columns = avg_weighted_price.columns.droplevel()

            return avg_weighted_price

    def total_flow(self, df):
        df_t = df.groupby(["Node", "Period"])[["FlowOut_MW", "FlowIn_MW"]].sum().reset_index()
        df_t["FlowTotal_MW"] = df_t["FlowOut_MW"] + df_t["FlowIn_MW"]
        return df_t.pivot(index="Period", columns="Node", values="FlowTotal_MW")
