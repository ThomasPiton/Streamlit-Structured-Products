import streamlit as st
import plotly.express as px
from src.displayer.display_base import DisplayBase

class DisplayIndexLevel(DisplayBase):
    
    def __init__(self, **kwargs):
        super().__init__()
        self.dtf = kwargs.get("index")

    def render(self):
        st.subheader("Index Level Results")

        if self.dtf is None:
            st.warning("No data provided.")
            return

        # Show raw data table
        st.dataframe(self.dtf)

        # Make sure 'Date' and 'index_value' are in your DataFrame
        if "Date" in self.dtf.columns and "index_value" in self.dtf.columns:
            fig = px.line(
                self.dtf,
                x="Date",
                y="index_value",
                title="Index Level Evolution",
                labels={"Date": "Date", "index_value": "Index Value"},
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("The columns 'Date' and 'index_value' are required to display the chart.")
            
class DisplayIndexLevelVsBenchmark(DisplayBase):
    
    def __init__(self, **kwargs):
        super().__init__()
        self.dtf = kwargs.get("index")

    def render(self):
        st.subheader("Index Level Results")

        if self.dtf is None:
            st.warning("No data provided.")
            return

        # Show raw data table
        st.dataframe(self.dtf)

        # Make sure 'Date' and 'index_value' are in your DataFrame
        if "Date" in self.dtf.columns and "index_value" in self.dtf.columns:
            fig = px.line(
                self.dtf,
                x="Date",
                y="index_value",
                title="Index Level Evolution",
                labels={"Date": "Date", "index_value": "Index Value"},
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("The columns 'Date' and 'index_value' are required to display the chart.")