import streamlit as st
import pandas as pd
import os

# Ρύθμιση της σελίδας
st.set_page_config(page_title="Audiophile Album Archive", layout="wide")

# --- 1. ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ (Από τα 2 Tabs) ---
@st.cache_data
def load_data():
    # Διαβάζουμε και τα δύο tabs από το ίδιο αρχείο Excel
    df_albums = pd.read_excel("albums_analysis_fixed.xlsx", sheet_name="albums")
    df_tracks = pd.read_excel("albums_analysis_fixed.xlsx", sheet_name="tracks")
    return df_albums, df_tracks

try:
    df_pressings_all, df_tracks_all = load_data()
except Exception as e:
    st.error("Παρακαλώ βεβαιωθείτε ότι το αρχείο 'albums_analysis_fixed.xlsx' περιέχει τα tabs 'albums' και 'tracks'.")
    st.stop()

# --- 2. ΠΛΑΪΝΗ ΜΠΑΡΑ (SIDEBAR) ---
st.sidebar.title("📁 Πλοήγηση & Αναζήτηση")

# Επιλογή Καλλιτέχνη
available_artists = sorted(df_pressings_all['Καλλιτέχνης'].unique())
selected_artist = st.sidebar.selectbox("Επιλέξτε Καλλιτέχνη προς προβολή:", available_artists)

# Φιλτράρισμα των άλμπουμ του συγκεκριμένου καλλιτέχνη
filtered_albums = df_pressings_all[df_pressings_all['Καλλιτέχνης'] == selected_artist]

# Dropdown άλμπουμ που δείχνει και το έτος σε παρένθεση
album_options = []
for idx, r in filtered_albums.iterrows():
    year_val = r['Έτος Κυκλοφορίας']
    if pd.notna(year_val):
        year_str = str(year_val).split()[-1]  # Παίρνει το έτος (π.χ. από "29 May 2026" ή "2009")
        year_str = f" ({year_str.split('.')[0]})"
    else:
        year_str = ""
    album_options.append(f"{r['Άλμπουμ']}{year_str}")

selected_album_display = st.sidebar.selectbox("Επιλέξτε Άλμπουμ προς προβολή:", album_options)

# Ανάκτηση του σωστού άλμπουμ και του Album_ID του
selected_album_row = filtered_albums.iloc[album_options.index(selected_album_display)]
selected_album_id = selected_album_row['Album_ID']

# Φιλτράρισμα δεδομένων και tracks με βάση το Album_ID
album_facts = selected_album_row
album_tracks = df_tracks_all[df_tracks_all['Album_ID'] == selected_album_id].sort_values(by='No')

# Προσθήκη συνολικής βαθμολογίας άλμπουμ στα αριστερά
st.sidebar.write("---")
st.sidebar.markdown(f"🌟 **Συνολικό RYM Rating:** {album_facts['RYM Rating']}")

# --- 3. ΚΥΡΙΩΣ ΠΑΡΑΘΥΡΟ ΕΦΑΡΜΟΓΗΣ ---
st.title("🎵 Audiophile Album Archive & Music Library")
st.subheader(f"🎚️ {album_facts['Καλλιτέχνης']} — *{album_facts['Άλμπουμ']}*")

# Εμφάνιση Ιστορικού Πλαισίου & Hard Facts του Άλμπουμ
st.info(f"{album_facts['Σημειώσεις / Hard Facts']}")

st.write("---")
st.markdown("### 💿 Ανάλυση Κομματιών (Tracks Analysis)")

# Εμφάνιση των τραγουδιών σε καθαρή audiophile γεωμετρία
for index, row in album_tracks.iterrows():
    with st.container():
        # Δημιουργούμε 3 στήλες: 1 για τον τίτλο, 1 για τα Ratings, 1 για τις Σημειώσεις
        col1, col2, col3 = st.columns([2, 1, 3])
        
        with col1:
            st.markdown(f"**{row['No']}. {row['Track / Έκδοση']}**")
            st.caption(f"*{row['Genres / Subgenres']}*")
            
        with col2:
            st.markdown(f"⭐ **RYM:** {row['RYM Rating']}")
            st.markdown(f"🎵 **C.V.:** {row['Compositional Value']:.2f}")
            st.markdown(f"🎧 **A.I.:** {row['Audiophile Interest']:.2f}")
            
        with col3:
            st.write(row['Σημειώσεις / Hard Facts'])
            
        st.write("---")