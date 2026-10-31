import csv
import pandas as pd
import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard

# --------------------------------------------------
# Page Setup
# --------------------------------------------------

st.set_page_config(
    page_title="50-50 Draw Manager",
    page_icon="🎟️",
    layout="centered"
)

st.title("🎯 50-50 Draw Manager")

# --------------------------------------------------
# CSS Styles
# --------------------------------------------------
st.markdown("""
<style>

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #374151 !important;
    font-weight: 600;
}

/* Selected tab */
.stTabs [aria-selected="true"] {
    color: #1f2937 !important;
    font-weight: 700;
}

/* Optional gold underline */
.stTabs [aria-selected="true"]::after {
    background-color: #d4af37;
}

/* Main page background */
.stApp {
    background-color: #fff9e6;
}

/* Make tabs slightly darker */
.stTabs [data-baseweb="tab"] {
    color: #2c3e50 !important;
    font-weight: 600;
}
/* All alert boxes */
div[data-testid="stAlert"] {
    background-color: #f8f8f8 !important;
    border-radius: 10px;
    border: 1px solid #dddddd !important;
}
</style>
""", unsafe_allow_html=True)

def show_message(text, icon="✅"):
    st.markdown(
        f"""
        <div style="
            background-color:#fff9e6;
            border-left:5px solid #d4af37;
            padding:15px;
            border-radius:10px;
            color:#5a4a00;
            font-weight:600;
            margin:10px 0;
        ">
            {icon} {text}
        </div>
        """,
        unsafe_allow_html=True
    )
# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab1, tab2 = st.tabs(
    ["🎟 Generate Draw List", "🏆 Winner Lookup"]
)

# ==================================================
# TAB 1 - DRAW LIST GENERATOR
# ==================================================

with tab1:

    st.write("Upload a ClubSpot CSV to generate the draw list.")

    uploaded_file = st.file_uploader(
        "Select ClubSpot CSV",
        type=["csv"],
        key="draw_generator"
    )

    auto_renew = st.checkbox(
        "Auto Renew Draw Only",
        help="Only include names where Column H contains 'Enabled'."
    )

    if uploaded_file is not None:

        draw_entries = []

        reader = csv.reader(
            uploaded_file.getvalue().decode("utf-8-sig").splitlines()
        )

        # Skip header row
        next(reader, None)

        for row in reader:

            # Column C = Ticket Number
            ticket_number = row[2].strip() if len(row) >= 3 else ""

            # Column D = Player Name
            player_name = row[3].strip() if len(row) >= 4 else ""

            # Create entry
            if ticket_number:
                entry = f"{player_name} T{ticket_number}"
            else:
                entry = player_name

            if auto_renew:

                # Column H = Auto Renew Status
                col_h = row[7].strip() if len(row) >= 8 else ""

                if col_h.lower() == "enabled":
                    draw_entries.append(entry)

            else:
                draw_entries.append(entry)

        num_offline = 0

        if not auto_renew:

            num_offline = st.number_input(
                "Number of Offline Entries",
                min_value=0,
                value=0,
                step=1
            )

        if st.button("Generate Draw List"):

            for i in range(1, num_offline + 1):
                draw_entries.append(f"Offline Entry {i}")

            st.session_state["draw_list"] = "\n".join(draw_entries)
            st.session_state["entry_count"] = len(draw_entries)

    if "draw_list" in st.session_state:

        show_message(
            f"Total Entries: {st.session_state['entry_count']}",
            "📊"
        )


        st.text_area(
            "Draw List",
            st.session_state["draw_list"],
            height=350
        )

        st_copy_to_clipboard(
            st.session_state["draw_list"],
            "📋 Copy Names to Clipboard"
        )

        st.download_button(
            label="📥 Download Draw List",
            data=st.session_state["draw_list"],
            file_name="draw_list.txt",
            mime="text/plain"
        )

# ==================================================
# TAB 2 - WINNER LOOKUP
# ==================================================

with tab2:

    st.write(
        "Upload any historical ClubSpot draw file and search for player details."
    )

    winner_file = st.file_uploader(
        "Upload Draw CSV",
        type=["csv"],
        key="winner_lookup"
    )

    if winner_file is not None:

        df = pd.read_csv(winner_file)

        # ------------------------------------------
        # Detect ticket column automatically
        # ------------------------------------------

        if "Ticket number(s)" in df.columns:
            ticket_col = "Ticket number(s)"

        elif "Played number(s)" in df.columns:
            ticket_col = "Played number(s)"

        else:
            st.error("Could not find ticket number column.")
            st.stop()

        # ------------------------------------------
        # Verify required columns
        # ------------------------------------------

        required_columns = [
            "Player's name",
            "Player's email",
            "Player's phone number"
        ]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            st.error(
                f"Missing required columns: {', '.join(missing)}"
            )
            st.stop()

        lookup_df = df[
            [
                ticket_col,
                "Player's name",
                "Player's email",
                "Player's phone number"
            ]
        ].copy()

        show_message(
            f"{len(lookup_df)} Entries Loaded",
            "📂"
        )

        st.divider()

        # ------------------------------------------
        # Search by Player Name
        # ------------------------------------------

        search_name = st.text_input(
            "Search by Player Name"
        )

        if search_name:

            results = lookup_df[
                lookup_df["Player's name"]
                .astype(str)
                .str.contains(
                    search_name,
                    case=False,
                    na=False
                )
            ]

            st.subheader("Name Search Results")

            if len(results):
                st.dataframe(
                    results,
                    use_container_width=True
                )
            else:
                st.warning("No matching player found.")

        st.divider()

        # ------------------------------------------
        # Search by Ticket Number
        # ------------------------------------------

        search_ticket = st.text_input(
            "Search by Ticket Number"
        )

        if search_ticket:

            results = lookup_df[
                lookup_df[ticket_col]
                .astype(str)
                .str.contains(
                    search_ticket,
                    na=False
                )
            ]

            st.subheader("Ticket Search Results")

            if len(results):
                st.dataframe(
                    results,
                    use_container_width=True
                )
            else:
                st.warning("No matching ticket found.")

        st.divider()

        # ------------------------------------------
        # Full List
        # ------------------------------------------

        with st.expander("View Full Player List"):

            st.dataframe(
                lookup_df,
                use_container_width=True,
                height=400
            )
