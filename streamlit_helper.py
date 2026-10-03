"""
Helper functions for Streamlit app
"""

import streamlit as st

def select_by_search_streamlit(available_crimes, max_select):
    """Search and select crimes with enhanced filtering"""
    st.markdown("#### Search & Filter Crimes")
    
    # Search input
    search_term = st.text_input(
        "Enter search term:",
        placeholder="e.g., murder, theft, cyber, women...",
        key="crime_search_input"
    )
    
    if search_term:
        # Filter crimes based on search
        search_lower = search_term.lower()
        matching_crimes = [c for c in available_crimes if search_lower in c.lower()]
        
        if matching_crimes:
            st.success(f"Found {len(matching_crimes)} matching crimes")
            
            # Show matches with selection
            selected_crimes = st.multiselect(
                f"Select from search results (max {max_select}):",
                matching_crimes,
                key="search_results_multi",
                max_selections=max_select
            )
            
            return selected_crimes
        else:
            st.warning(f"No crimes found matching '{search_term}'")
            st.info("Try different keywords like: murder, theft, cyber, women, drug, fraud")
    
    return []

def select_by_category_streamlit(available_crimes, max_select):
    """Select crimes by category with enhanced UI"""
    from Data import categorize_crimes
    
    categories = categorize_crimes(available_crimes)
    
    st.markdown("#### Browse by Crime Categories")
    
    selected_crimes = []
    
    # Show categories in expandable sections
    for category, crimes in categories.items():
        with st.expander(f"{category} ({len(crimes)} crimes)", expanded=False):
            
            # Quick select all in category
            if st.checkbox(f"Select all {category}", key=f"select_all_{category}"):
                remaining_slots = max_select - len(selected_crimes)
                crimes_to_add = crimes[:remaining_slots]
                selected_crimes.extend(crimes_to_add)
                st.info(f"Added {len(crimes_to_add)} crimes from {category}")
            else:
                # Individual selection within category
                for crime in crimes[:10]:  # Limit display to prevent UI overflow
                    if len(selected_crimes) < max_select:
                        if st.checkbox(crime, key=f"crime_check_{crime}"):
                            if crime not in selected_crimes:
                                selected_crimes.append(crime)
    
    if selected_crimes:
        st.success(f"Selected {len(selected_crimes)} crimes across categories")
    
    return selected_crimes[:max_select]