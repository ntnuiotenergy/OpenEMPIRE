import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class OperationalResults:
    def __init__(self, output_client, input_client):
        self.output_client = output_client
        self.input_client = input_client

    def get_nodes(self):
        nodes = self.input_client.sets.get_nodes()["Node"].to_list()
        return [i.replace(" ", "") for i in nodes]

    def add_vertical_season_lines(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        max_hour_season = {}
        for season in df["Season"].unique():
            max_hour_season[season] = df.loc[df["Season"] == season, "Hour"].max()

        for season in max_hour_season:
            fig.add_vline(
                x=max_hour_season[season],
                line_width=2,
                line_color="grey",
                annotation_text=season,
                annotation_position="top left",
                annotation_font_size=8,
            )
        return fig

    def plot_node_operation_values(self, df, node, scenario, period):
        filtered_df = df.query(f"Scenario == '{scenario}' and Period == '{period}'")

        columns = [i for i in df.columns if "_MW" in i and i not in ["AllGen_MW", "Net_load_MW", "storEnergyLevel_MWh"]]

        current_columns = list(set(columns).intersection(set(filtered_df.columns)))

        column_sums = filtered_df[current_columns].sum().abs()

        # Find columns where the absolute sum is less than 0.01 MW
        sum_hours = filtered_df["Hour"].max()
        columns_to_drop = column_sums[column_sums < 0.01 * sum_hours].index
        filtered_columns = set(current_columns).difference(set(columns_to_drop.to_list() + ["Load_MW"]))
        filtered_columns = list(filtered_columns.union(set(["LoadShed_MW"]))) # Include if it was removed

        # Melting the DataFrame to have a long-form DataFrame which is suitable for line plots in plotly
        melted_df = pd.melt(filtered_df, id_vars=["Hour"], value_vars=filtered_columns)

        # Calculate the sum of values for each variable
        sums = melted_df.groupby("variable")["value"].sum()

        # Sort variables based on their sums for a more readable area plot
        sorted_variables = sums.sort_values(ascending=False).index.tolist()

        # Sort the DataFrame based on the sorted order of variables
        melted_df["variable"] = pd.Categorical(melted_df["variable"], categories=sorted_variables, ordered=True)
        melted_df = melted_df.sort_values("variable")

        # Creating the line plot
        fig = px.area(
            melted_df,
            x="Hour",
            y="value",
            color="variable",
            title=f"Operational values for {node}, {scenario}, {period}",
        )
        fig.add_trace(go.Scatter(x=filtered_df["Hour"], y=-filtered_df["Load_MW"], name="Load_MW"))

        fig.update_layout(
            xaxis=dict(title="Hour", domain=[0.3, 1]),
            yaxis=dict(title="Value (MW)"),
            yaxis2=dict(
                title="Energy Price [EUR/MWh]",
                side="left",
                overlaying="y",
                showgrid=False,  # Hides the secondary y-axis gridlines if desired
                # tickmode="auto",  # Ensures ticks are automatically generated
                anchor="free",
                position=0.15,
            ),
        )
        fig.add_trace(
            go.Scatter(x=filtered_df["Hour"], y=filtered_df["Price_EURperMWh"], name="Energy Price", yaxis="y2")
        )

        fig = self.add_vertical_season_lines(fig, filtered_df)

        return fig

    def plot_storage_operation_values(self, df, node, scenario, period):
        
        filtered_df = df.query(f"Scenario == '{scenario}' and Period == '{period}'")

        storage_columns = ["storCharge_MW", "storDischarge_MW", "storEnergyLevel_MWh", "LossesChargeDischargeBleed_MW"]
        current_columns = list(set(storage_columns).intersection(set(filtered_df.columns)))

        # column_sums = filtered_df[current_columns].sum().abs()

        # Find columns where the absolute sum is less than 1 MW
        # sum_hours = filtered_df["Hour"].max()
        # columns_to_drop = column_sums[column_sums < 1 * sum_hours].index.to_list()
        columns_to_drop = []
        filtered_columns = list(set(current_columns).difference(set(columns_to_drop + ["Load_MW"])))

        # Melting the DataFrame to have a long-form DataFrame which is suitable for line plots in plotly
        melted_df = pd.melt(filtered_df, id_vars=["Hour"], value_vars=filtered_columns)

        # Calculate the sum of values for each variable
        sums = melted_df.groupby("variable")["value"].sum()

        # Sort variables based on their sums for a more readable area plot
        sorted_variables = sums.sort_values(ascending=False).index.tolist()

        # Sort the DataFrame based on the sorted order of variables
        melted_df["variable"] = pd.Categorical(melted_df["variable"], categories=sorted_variables, ordered=True)
        melted_df = melted_df.sort_values("variable")

        # Creating the line plot
        fig = px.area(
            melted_df,
            x="Hour",
            y="value",
            color="variable",
            title=f"Operational storage values for {node}, {scenario}, {period}",
        )
        fig.add_trace(go.Scatter(x=filtered_df["Hour"], y=-filtered_df["Load_MW"], name="Load_MW"))

        fig.update_layout(
            xaxis=dict(title="Hour", domain=[0.3, 1]),
            yaxis=dict(title="Value (MW)"),
            yaxis2=dict(
                title="Energy Price [EUR/MWh]",
                side="left",
                overlaying="y",
                showgrid=False,  # Hides the secondary y-axis gridlines if desired
                # tickmode="auto",  # Ensures ticks are automatically generated
                anchor="free",
                position=0.15,
            ),
        )
        fig.add_trace(
            go.Scatter(x=filtered_df["Hour"], y=filtered_df["Price_EURperMWh"], name="Energy Price", yaxis="y2")
        )

        fig = self.add_vertical_season_lines(fig, filtered_df)

        return fig

    def plot_curtailment_operational(self, df, node, scenario, period):

        filtered_df = df.query(f"Scenario == '{scenario}' and Period == '{period}'")

        fig = px.line(
            filtered_df,
            x="Hour",
            y="Curtailment_MWh",
            color="RESGeneratorType",
            title=f"Operational curtailment values for {node}, {scenario}, {period}",
        )

        return fig

    def plot_transmission_flow(self, df, node, scenario, period):
        filtered_df = df.query(f"Scenario == '{scenario}' and Period == '{period}'").copy(deep=True)

        filtered_df["From-To"] = filtered_df["FromNode"] + "-" + filtered_df["ToNode"]

        melted_df = pd.melt(filtered_df, id_vars=["Hour", "FromNode", "ToNode"], value_vars=["TransmissionRecieved_MW"])
        melted_df.loc[melted_df["FromNode"] == node, "value"] *= -1.0  # Negative if flow out of node

        melted_df["From-To"] = melted_df["FromNode"] + "-" + melted_df["ToNode"]

        filtered_lines = melted_df.groupby(["From-To"]).sum()["value"].abs() > 0.1
        melted_df = melted_df.loc[melted_df["From-To"].map(filtered_lines)]

        sums = melted_df.groupby("From-To")["value"].sum()

        # Sort variables based on their sums for a more readable area plot
        sorted_variables = sums.sort_values(ascending=False).index.tolist()

        # Sort the DataFrame based on the sorted order of variables
        melted_df["From-To"] = pd.Categorical(melted_df["From-To"], categories=sorted_variables, ordered=True)
        melted_df = melted_df.sort_values("From-To")

        fig = px.area(
            melted_df,
            x="Hour",
            y="value",
            color="From-To",
            title=f"Exchange for {node}, {scenario}, {period}",
        )

        fig = self.add_vertical_season_lines(fig, filtered_df)

        return fig

    def plot_duration_curve(self, df, node, period):
        filtered_df = df.query(f"Node == '{node}' and Period == '{period}'").copy(deep=True)

        max_hours = filtered_df["Hour"].max()

        trace = []
        x = np.arange(start=0, stop=1.0, step=1 / len(filtered_df))
        for col in filtered_df.columns[5:]:
            if col == "Price_EURperMWh":
                trace.append(go.Scatter(x=x, y=filtered_df[col].sort_values(ascending=False), name=col, yaxis="y2"))
            elif filtered_df[col].sum() > 0.01 * max_hours:
                trace.append(go.Scatter(x=x, y=filtered_df[col].sort_values(ascending=False), name=col))

        fig = go.Figure(data=trace)
        fig.update_layout(
            title=f"Duration curves over all scenarios and seasons for {node}, {period}",
            yaxis=dict(title="Capacity [MW]"),
            xaxis=dict(title="[-]", domain=[0.3, 1]),
            yaxis2=dict(
                title="Energy Price [EUR/MWh]",
                side="left",
                overlaying="y",
                showgrid=False,  # Hides the secondary y-axis gridlines if desired
                # tickmode="auto",  # Ensures ticks are automatically generated
                anchor="free",
                position=0.15,
            ),
        )

        return fig

    def get_capture_rate(self, df, node, period) -> pd.DataFrame:
        """
        Computes capture rates for a node in a given period.

        :param df: Operational data
        :param node: Node
        :param period: Period
        :return: Data frame with capture rates
        """

        filtered_df = df.query(f"Node == '{node}' and Period == '{period}'").copy(deep=True)

        columns = [
            i
            for i in df.columns
            if "_MW" in i
            and i not in ["AllGen_MW", "Net_load_MW", "storEnergyLevel_MWh", "LossesChargeDischargeBleed_MW"]
        ]
        current_columns = list(set(columns).intersection(set(filtered_df.columns)))
        column_sums = filtered_df[current_columns].sum().abs()

        sum_hours = filtered_df["Hour"].max()
        # Find columns where the sum is less than 1 MW
        columns_to_drop = column_sums[column_sums < 1 * sum_hours].index
        filtered_columns = list(set(current_columns).difference(set(columns_to_drop.to_list() + ["Load_MW"])))

        avg_price = filtered_df["Price_EURperMWh"].mean()
        capture_rate = {}
        for col in filtered_columns:
            col_sum = filtered_df.loc[:, col].sum()
            if np.abs(col_sum) > 0.1:
                achieved_price = (filtered_df.loc[:, col] * filtered_df["Price_EURperMWh"]).sum() / col_sum
                capture_rate[col] = [achieved_price / avg_price * 100, achieved_price]

        return pd.DataFrame(capture_rate, index=["Capture rate", "Achieved price [EUR/MWh]"]).T.sort_values(
            by="Capture rate", ascending=False
        )

    def plot_node_flow(self, df, node):
        df_t = df.groupby(["Period"])[["FlowOut_MW", "FlowIn_MW"]].sum().reset_index()
        df_t["FlowTotal_MW"] = df_t["FlowOut_MW"] + df_t["FlowIn_MW"]
        melted_df = pd.melt(
            df_t,
            id_vars=["Period"],
            value_vars=["FlowOut_MW", "FlowIn_MW", "FlowTotal_MW"],
            value_name="Flow_MW",
            var_name="FlowType",
        )

        return px.line(melted_df, x="Period", y="Flow_MW", color="FlowType", title="Flow in/out of node {node}")
