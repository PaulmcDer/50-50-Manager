import csv
from html import escape
import pandas as pd
import streamlit as st
from st_copy_to_clipboard import st_copy_to_clipboard
from datetime import datetime
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
import gspread
from gspread.utils import ValueInputOption
from requests.exceptions import RequestException

# --------------------------------------------------
# Page Setup
# --------------------------------------------------

SHEET_ID = "1umG0zNs4Uz9IqfZXPXEeAgfSWoRTzDDsEwlSRC-3PnM"

st.set_page_config(
    page_title="50-50 Draw Manager",
    page_icon="🎟️",
    layout="wide"
)

# --------------------------------------------------
# 50-50 google sheet
# --------------------------------------------------

SHEETS_SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

@st.cache_resource
def get_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SHEETS_SCOPE
    )

    client = gspread.authorize(creds)
    client.set_timeout((5, 20))
    return client


@st.cache_resource
def get_fifty_sheet():
    return get_client().open_by_key(SHEET_ID).worksheet("50-50")

name_col = "Player's name"

# --------------------------------------------------
# CSS Styles
# --------------------------------------------------
st.markdown("""
<style>
:root {
    --draw-ink: #19332c;
    --draw-muted: #64746d;
    --draw-green: #2d8a63;
    --draw-green-dark: #236d4d;
    --draw-gold: #e7bd60;
    --draw-line: #dce5df;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 10% 0%, rgba(231, 189, 96, 0.12), transparent 32rem),
        #f5f8f5;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1080px;
    padding: 2rem 2rem 4rem;
}

.app-hero {
    position: relative;
    overflow: hidden;
    margin: 0 0 1.6rem;
    padding: clamp(1.5rem, 4vw, 2.5rem);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 22px;
    color: #fff;
    background: linear-gradient(120deg, #123f30 0%, #176b4b 65%, #25805a 100%);
    box-shadow: 0 16px 36px rgba(25, 51, 44, 0.14);
}

.app-hero::after {
    position: absolute;
    top: -5rem;
    right: -2rem;
    width: 18rem;
    height: 18rem;
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-radius: 50%;
    box-shadow: 0 0 0 2rem rgba(255, 255, 255, 0.035),
                0 0 0 4rem rgba(255, 255, 255, 0.025);
    content: "";
}

.hero-kicker {
    margin-bottom: 0.55rem;
    color: #f2d995;
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.13em;
    text-transform: uppercase;
}

.app-hero h1 {
    margin: 0;
    color: #fff;
    font-size: clamp(1.8rem, 4vw, 2.7rem);
    font-weight: 800;
    letter-spacing: -0.035em;
    line-height: 1.1;
}

.app-hero p {
    max-width: 42rem;
    margin: 0.8rem 0 0;
    color: rgba(255, 255, 255, 0.82);
    font-size: 1rem;
    line-height: 1.6;
}

button[data-baseweb="tab"] p {
    font-weight: 700 !important;
}

[data-testid="stTabs"] [role="tablist"] {
    gap: 0.45rem;
    border-bottom: 1px solid var(--draw-line);
}

[data-testid="stTabs"] button[role="tab"] {
    min-height: 3rem;
    padding: 0.65rem 1rem;
    border-radius: 10px 10px 0 0;
    color: var(--draw-muted);
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--draw-green);
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--draw-green);
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] p {
    color: var(--draw-ink);
}

[data-testid="stCaptionContainer"] p {
    color: var(--draw-muted);
}

.app-hero p {
    color: rgba(255, 255, 255, 0.82);
}

[data-testid="stFileUploader"] section {
    border: 1px dashed #b8c9be;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.72);
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border-color: #cbd8cf;
    border-radius: 10px;
    background-color: #fff;
}

[data-testid="stTextArea"] textarea {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
    line-height: 1.55;
}

div.stButton > button,
[data-testid="stDownloadButton"] button {
    min-height: 2.75rem;
    border-radius: 10px;
    font-weight: 700;
    transition: transform 120ms ease, box-shadow 120ms ease;
}

div.stButton > button:hover,
[data-testid="stDownloadButton"] button:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 14px rgba(25, 51, 44, 0.12);
}

div.stButton > button[kind="primary"] {
    border-color: var(--draw-green);
    background: var(--draw-green);
    color: #f5fbf7;
}

div.stButton > button[kind="primary"]:hover {
    border-color: var(--draw-green-dark);
    background: var(--draw-green-dark);
}

[data-testid="stDataFrame"] {
    overflow: hidden;
    border: 1px solid var(--draw-line);
    border-radius: 12px;
}

.status-card {
    margin: 0.8rem 0 1.1rem;
    padding: 0.9rem 1rem;
    border: 1px solid #ead9a9;
    border-left: 5px solid var(--draw-gold);
    border-radius: 12px;
    color: #53451f;
    background: #fffaf0;
    font-weight: 700;
}

/* Comfortable touch targets in both tablet orientations. */
[data-testid="stTabs"] [role="tablist"] {
    gap: 0.5rem;
    padding: 0.4rem;
    border: 1px solid var(--draw-line);
    border-radius: 16px;
    background: #eaf0eb;
}

[data-testid="stTabs"] button[role="tab"] {
    flex: 1;
    min-height: 56px;
    border-radius: 12px;
}

[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #174e38;
    background: #fff;
    box-shadow: 0 2px 6px rgba(25, 51, 44, 0.08);
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [data-baseweb="tab-border"] {
    display: none;
}

[data-testid="stTabs"] [role="tabpanel"] {
    padding-top: 1.5rem;
}

[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button,
[data-testid="stFileUploader"] button,
[data-testid="stNumberInput"] button {
    min-height: 52px;
    touch-action: manipulation;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    min-height: 52px;
    font-size: 1rem;
}

[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label {
    min-height: 48px;
    align-items: center;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-radius: 16px;
}

button:focus-visible, input:focus-visible, textarea:focus-visible {
    outline: 3px solid #a47720 !important;
    outline-offset: 3px;
}

.winner-card {
    padding: 1.25rem;
    margin: 0.5rem 0 1rem;
    background: #edf5ef;
    border: 1px solid #c8dece;
    border-radius: 16px;
}

.winner-card .winner-label {
    color: #41634e;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.winner-card h3 {
    padding: 0.35rem 0 0.65rem;
    margin: 0;
    color: #19332c;
    overflow-wrap: anywhere;
}

.winner-details {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem 2rem;
    color: #19332c;
    overflow-wrap: anywhere;
}

@media (pointer: coarse) {
    [data-testid="stNumberInput"] button {
        min-width: 48px;
    }
}

@media (prefers-reduced-motion: reduce) {
    div.stButton > button,
    [data-testid="stDownloadButton"] button {
        transition: none;
        transform: none !important;
    }
}

@media (max-width: 640px) {
    .block-container {
        padding: 1rem 1rem 2.5rem;
    }

    .app-hero {
        border-radius: 16px;
    }

    [data-testid="stTabs"] button[role="tab"] {
        padding: 0.55rem 0.65rem;
        font-size: 0.88rem;
    }
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <section class="app-hero">
        <div class="hero-kicker">Weekly draw · Committee tools</div>
        <h1>50-50 Draw Manager</h1>
        <p>Prepare your draw list, find a winning entry, and send the prize
        details for payment — all in one place.</p>
    </section>
    """,
    unsafe_allow_html=True
)


def show_message(text, icon="✅"):
    st.markdown(
        f"""
        <div class="status-card">
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

    st.subheader("1. Prepare your draw")
    st.caption(
        "Upload the latest ClubSpot export to generate the draw list"
    )

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

        if st.button("Generate Draw List", type="primary", width="stretch"):

            for i in range(1, num_offline + 1):
                draw_entries.append(f"Offline Entry {i}")

            st.session_state["draw_list"] = "\n".join(draw_entries)
            st.session_state["entry_count"] = len(draw_entries)

    if "draw_list" in st.session_state:

        st.subheader("2. Copy or download")
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
            mime="text/plain",
            width="stretch"
        )

# ==================================================
# TAB 2 - WINNER LOOKUP
# ==================================================

with tab2:

    st.subheader("1. Load your draw entries")
    st.caption(
        "Upload the ClubSpot draw export, then search by player name "
        "or ticket number to confirm the winner's details."
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

        st.subheader("2. Find the winning entry")

        search_type = st.radio(
            "Search By",
            ["Name", "Ticket Number"],
            horizontal=True
        )

        search_value = st.text_input(
            f"Search by {search_type}",
            placeholder="Enter a player name" if search_type == "Name" else "Enter a ticket number"
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
                    width="stretch",
                    row_height=48
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

            st.subheader("3. Send for payment")
            st.markdown(
                f"""<section class="winner-card">
                    <div class="winner-label">Selected winner</div>
                    <h3>{escape(str(winner_name))}</h3>
                    <div class="winner-details">
                        <span><strong>Phone</strong><br>{escape(phone_number)}</span>
                        <span><strong>Ticket</strong><br>{escape(str(selected_row[ticket_col]))}</span>
                    </div>
                </section>""",
                unsafe_allow_html=True
            )

            jackpot_amount = st.number_input(
                "Jackpot Amount (€)",
                min_value=0.0,
                step=10.0
            )

            if st.button(
                "✅ Send Winner For Payment",
                type="primary",
                width="stretch"
            ):

                if jackpot_amount <= 0:

                    st.error(
                        "Please enter the jackpot amount before submitting."
                    )

                else:

                    try:
                        with st.spinner("Sending winner to Treasurer..."):
                            get_fifty_sheet().append_row(
                                [
                                    datetime.now().strftime("%d/%m/%Y"),
                                    selected_row["Player's name"],
                                    phone_number,
                                    str(selected_row[ticket_col]),
                                    jackpot_amount,
                                    "Pending"
                                ],
                                value_input_option=ValueInputOption.raw,
                                include_values_in_response=False
                            )
                    except KeyError:
                        st.error(
                            "Google Sheets credentials are not configured. "
                            "Add `gcp_service_account` to Streamlit secrets."
                        )
                    except (GoogleAuthError, gspread.exceptions.GSpreadException,
                            RequestException, ValueError) as error:
                        st.error(f"Could not send winner to Google Sheets: {error}")
                    else:
                        st.success(
                            "Winner sent to Treasurer successfully."
                        )

        st.divider()
