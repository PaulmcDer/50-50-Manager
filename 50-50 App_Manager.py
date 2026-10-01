import csv
import streamlit as st

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

    column_d_values = []

    reader = csv.reader(
        uploaded_file.getvalue().decode("utf-8-sig").splitlines()
    )

    # Skip header row
    next(reader, None)

    for row in reader:

        col_d = row[3] if len(row) >= 4 else ""

        if auto_renew:

            col_h = row[7] if len(row) >= 8 else ""

            if col_h.strip().lower() == "enabled":
                column_d_values.append(col_d)

        else:
            column_d_values.append(col_d)

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
            column_d_values.append(f"offline entry {i}")

        draw_list = "\n".join(column_d_values)

        st.success(
            f"Draw list generated successfully ({len(column_d_values)} entries)"
        )

        st.text_area(
            "Draw List",
            draw_list,
            height=350
        )

        st.download_button(
            label="📥 Download Draw List",
            data=draw_list,
            file_name="draw_list.txt",
            mime="text/plain"
        )
