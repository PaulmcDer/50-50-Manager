import csv
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

st.title("🎟️ 50-50 Draw Manager")
st.write("Upload a ClubSpot CSV to generate the draw list.")

# --------------------------------------------------
# File Upload
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Select ClubSpot CSV",
    type=["csv"]
)

# --------------------------------------------------
# Auto Renew Option
# --------------------------------------------------

auto_renew = st.checkbox(
    "Auto Renew Draw Only",
    help="Only include names where Column H contains 'Enabled'."
)

# --------------------------------------------------
# Process CSV
# --------------------------------------------------

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

    # --------------------------------------------------
    # Offline Entries
    # --------------------------------------------------

    num_offline = 0

    if not auto_renew:

        num_offline = st.number_input(
            "Number of Offline Entries",
            min_value=0,
            value=0,
            step=1
        )

    # --------------------------------------------------
    # Generate Button
    # --------------------------------------------------

    if st.button("Generate Draw List"):

        for i in range(1, num_offline + 1):
            draw_entries.append(f"Offline Entry {i}")

        st.session_state["draw_list"] = "\n".join(draw_entries)
        st.session_state["entry_count"] = len(draw_entries)

# --------------------------------------------------
# Display Results
# --------------------------------------------------

if "draw_list" in st.session_state:

    st.success(
        f"Draw list generated successfully ({st.session_state['entry_count']} entries)"
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

    st.info(
        f"Total Entries: {st.session_state['entry_count']}"
    )
