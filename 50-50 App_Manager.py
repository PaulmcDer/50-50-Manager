import csv
import pandas as pd
import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

# --------------------------------------------------
# Page Setup
# --------------------------------------------------

SHEET_ID = "1umG0zNs4Uz9IqfZXPXEeAgfSWoRTzDDsEwlSRC-3PnM"

st.set_page_config(
    page_title="50-50 Draw Manager",
    page_icon="🎟️",
    layout="centered"
)

st.title("🎯 50-50 Draw Manager")

# --------------------------------------------------
# 50-50 google sheet
# --------------------------------------------------

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_client():

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    return gspread.authorize(creds)

client = get_client()

fifty_sheet = client.open_by_key(
    SHEET_ID
).worksheet("50-50")

name_col = "Player's name"

# --------------------------------------------------
# CSS Styles
# --------------------------------------------------
st.markdown("""
<style>

/* Bold tab text */
button[data-baseweb="tab"] p {
    font-weight: 700 !important;
}

/* Remove custom yellow backgrounds */
.stTextInput input,
.stSelectbox div,
.stTextArea textarea {
    background-color: inherit !important;
    color: inherit !important;
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
        # Winner Payment Submission
        # ------------------------------------------

        st.subheader("🏆 Submit Winner for Payment")

        search_type = st.radio(
            "Search By",
            ["Name", "Ticket Number"],
            horizontal=True
        )

        search_value = st.text_input(
            f"Search by {search_type}"
        )

        selected_row = None

        if search_value:

            if search_type == "Name":

                results = lookup_df[
                    lookup_df["Player's name"]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .str.contains(
                        search_value.strip().lower(),
                        regex=False,
                        na=False
                    )
                ]

            else:

                results = lookup_df[
                    lookup_df[ticket_col]
                    .astype(str)
                    .str.contains(
                        search_value.strip(),
                        regex=False,
                        na=False
                    )
                ]

            if len(results):

                st.dataframe(
                    results,
                    use_container_width=True
                )

                # Multiple matches
                if len(results) > 1:

                    winner_options = [
                        f"{row[name_col]} | {row[ticket_col]}"
                        for _, row in results.iterrows()
                    ]

                    selected_winner = st.selectbox(
                        "Select Winning Entry",
                        winner_options
                    )

                    selected_index = winner_options.index(
                        selected_winner
                    )

                    selected_row = results.iloc[selected_index]

                else:

                    selected_row = results.iloc[0]

            else:

                st.warning("No matching record found.")

        # -------------------------------------------------
        # Payment Submission Section
        # -------------------------------------------------

        if selected_row is not None:

            phone_number = str(
                selected_row["Player's phone number"]
            ).strip()

            phone_number = phone_number.replace("+", "")

            if phone_number.startswith("353"):
                phone_number = "0" + phone_number[3:]

            winner_name = selected_row["Player's name"]

            st.write(f"**Winner:** {winner_name}")
            st.write(f"**Phone:** {phone_number}")
            st.write(f"**Ticket:** {selected_row[ticket_col]}")

            jackpot_amount = st.number_input(
                "Jackpot Amount (€)",
                min_value=0.0,
                step=10.0
            )

            if st.button(
                "✅ Send Winner For Payment",
                type="primary"
            ):

                if jackpot_amount <= 0:

                    st.error(
                        "Please enter the jackpot amount before submitting."
                    )

                else:

                    fifty_sheet.append_row([
                        datetime.now().strftime("%d/%m/%Y"),
                        selected_row["Player's name"],
                        phone_number,
                        str(selected_row[ticket_col]),
                        jackpot_amount,
                        "Pending"
                    ])

                    st.success(
                        "Winner sent to Treasurer successfully."
                    )

        st.divider()
        
