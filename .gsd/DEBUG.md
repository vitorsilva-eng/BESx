# Debug Session: PFC Dashboard Duplicate ID

## Resolution
root_cause: Two calls to `st.plotly_chart` with identical arguments (`plot_energy_balance(...)`) were used in different tabs. Streamlit's internal ID generation collided, causing the `StreamlitDuplicateElementId` error.
fix: Assigned unique `key` parameters to all `st.plotly_chart` calls within the `render_step_rules` function to ensure distinct element identities.
verification: Dashboard should now render all tabs without ID collision.
