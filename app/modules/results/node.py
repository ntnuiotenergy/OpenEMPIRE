import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class NodeResults:
    def __init__(self, output_client):
        self.output_client = output_client

    def plot_accumulated_system_investments_in_transmission(self) -> go.Figure:
        df_trans = self.output_client.get_transmission_values()
        df_trans = df_trans.groupby(["Period"])["transmissionInstalledCap_MW"].sum().to_frame().reset_index()
        return px.line(
            df_trans,
            x="Period",
            y="transmissionInstalledCap_MW",
            title="Accumulated system investments in Transmission",
        )

    def plot_accumulated_system_investments_in_generation(self) -> go.Figure:
        df_gen = self.output_client.get_generators_values()
        df_gen = df_gen.groupby(["Period", "GeneratorType"])["genInstalledCap_MW"].sum().to_frame().reset_index()
        return px.line(
            df_gen,
            x="Period",
            y="genInstalledCap_MW",
            color="GeneratorType",
            title="Accumulated system investments in Generation",
        )

    def _transmission_values(self, col, offset):
        df = self.output_client.get_transmission_values()

        default_nodes = ["NO1", "NO2", "NO3", "NO4", "NO5"]
        nodes = np.unique(df[["BetweenNode", "AndNode"]].values.flatten())
        selected_nodes = col.multiselect(
            "Select nodes:"+offset, nodes, default=[item for item in default_nodes if item in nodes]
        )

        df = df.query(f"BetweenNode in {selected_nodes} or AndNode in {selected_nodes}").copy(deep=True)

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values:" + offset, column_values)

        df["From-To"] = df["BetweenNode"] + "-" + df["AndNode"]

        return df, selected_column

    def plot_transmission_values(self, col):
        df, selected_column = self._transmission_values(col, "   ")
        fig = px.bar(
            df,
            x="From-To",
            y=selected_column,
            facet_col="Period",
            title="Transmission Values",
        )

        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig

    def plot_transmission_values_line(self, col):
        df, selected_column = self._transmission_values(col, "    ")
        fig = px.line(
            df,
            x="Period",
            y=selected_column,
            color="From-To",
            title="Transmission Values",
        )

        return fig

    def plot_generator_values(self, col):
        df = self.output_client.get_generators_values()

        default_nodes = ["NO1", "NO2", "NO3", "NO4", "NO5"]
        nodes = df["Node"].unique()
        selected_nodes = col.multiselect(
            "Select nodes: ", nodes, default=[item for item in default_nodes if item in nodes]
        )

        df = df.query(f"Node in {selected_nodes}")

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values: ", column_values)

        fig = px.bar(
            df,
            x="Node",
            y=selected_column,
            color="GeneratorType",
            facet_col="Period",
            title="Generator Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig

    def plot_generator_values_line(self, col):
        df = self.output_client.get_generators_values()
        selected_generator_technology = col.selectbox("Select Generator Technology:  ", df["GeneratorType"].unique())
        df = df.query(f"GeneratorType in '{selected_generator_technology}'")

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values:  ", column_values)

        fig = px.line(
            df,
            x="Period",
            y=selected_column,
            color="Node",
            title="Generator Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

        return fig

    def plot_storage_values(self, col):
        df = self.output_client.get_storage_values()

        default_nodes = ["NO1", "NO2", "NO3", "NO4", "NO5"]
        nodes = df["Node"].unique()
        selected_nodes = col.multiselect(
            "Select nodes:  ", nodes, default=[item for item in default_nodes if item in nodes]
        )
        df = df.query(f"Node in {selected_nodes}")

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values: ", column_values)

        fig = px.bar(
            df,
            x="Node",
            y=selected_column,
            color="StorageType",
            facet_col="Period",
            title="Storage Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig

    def plot_storage_values_line(self, col):
        df = self.output_client.get_storage_values()
        selected_storage_technology = col.radio("Select Storage Technology:  ", df["StorageType"].unique())
        df = df.query(f"StorageType in '{selected_storage_technology}'")

        column_values = df.columns[3:]
        selected_column = col.selectbox("Select column values:  ", column_values)

        fig = px.line(
            df,
            x="Period",
            y=selected_column,
            color="Node",
            title="Storage Values",
            # labels={"storPWInstalledCap_MW": "Technology", "Value": "Installed Capacity [GW]"},
        )

        # Update outer x-axis titles
        periods = df["Period"].unique()
        for i, period in enumerate(periods, start=1):
            fig.update_xaxes(title=period[:5], col=i)

        # Remove "Period='value'" labels
        fig.for_each_annotation(lambda a: a.update(text=""))
        return fig


    def plot_node_operation_values(self, df, max_hour_season, node, scenario, period):
        filtered_df = df.query(f"Scenario == '{scenario}' and Period == '{period}'")

        columns = [i for i in df.columns if "_MW" in i and i not in ["AllGen_MW", "Net_load_MW", "storEnergyLevel_MWh"]]

        current_columns = list(set(columns).intersection(set(filtered_df.columns)))

        column_sums = filtered_df[current_columns].sum().abs()

        # Find columns where the sum is less than 1 MW
        sum_hours = filtered_df["Hour"].max()
        columns_to_drop = column_sums[column_sums < 1 * sum_hours].index
        filtered_columns = list(set(current_columns).difference(set(columns_to_drop.to_list() + ["Load_MW"])))

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
        fig.add_trace(go.Scatter(x=filtered_df["Hour"], y=filtered_df["Price_EURperMWh"], name="Energy Price", yaxis="y2"))

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

    def plot_transmission_flow(self, df, max_hour_season, node, scenario, period):
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
    
    
    def get_build_technology_by_node(self,df_gen, node):
        df_gen = df_gen[["Node", "GeneratorType", "Period", "genInvCap_MW"]]
        df_gen = df_gen.pivot(index=["Node", "Period"], values="genInvCap_MW", columns="GeneratorType").fillna(0.0)
        df_gen[df_gen < 0.1] = 0.0

        df_t = df_gen[df_gen.index.get_level_values("Node")==node]
        return df_t.T[df_t.sum()>1]

    def visualize_built_capacity_in_nodes(self):
        import streamlit as st
        
        df_gen = self.output_client.get_generators_values()
        default_nodes = ["NO1", "NO2", "NO3", "NO4", "NO5"]
        nodes = df_gen["Node"].unique()
        
        selected_nodes = st.multiselect(
            "Select nodes:   ", nodes, default=[item for item in default_nodes if item in nodes]
        )
        
        for node in selected_nodes:
            df_built = self.get_build_technology_by_node(df_gen=df_gen, node=node)
            st.write(f"Built capacity [GW] in {node}")
            df_built.columns = df_built.columns.get_level_values(1)
            st.dataframe((df_built.round(0)/1e3).style.format("{:.2f}").background_gradient(cmap="Blues"))