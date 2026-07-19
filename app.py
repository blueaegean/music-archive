import streamlit as st
import pandas as pd
import os

# Ρύθμιση της σελίδας
st.set_page_config(page_title="Audiophile Album Archive", layout="wide")

# --- 1. ΦΟΡΤΩΣΗ ΔΕΔΟΜΕΝΩΝ ---
@st.cache_data
def load_data():
    df_albums = pd.read_excel("albums_analysis_fixed.xlsx", sheet_name="albums")
    df_tracks = pd.read_excel("albums_analysis_fixed.xlsx", sheet_name="tracks")
    return df_albums, df_tracks

try:
    df_pressings_all, df_tracks_all = load_data()
except Exception as e:
    st.error("Παρακαλώ βεβαιωθείτε ότι το αρχείο 'albums_analysis_fixed.xlsx' περιέχει τα tabs 'albums' και 'tracks' με τις σωστές αγγλικές κεφαλίδες.")
    st.stop()

# --- 2. ΠΛΑΪΝΗ ΜΠΑΡΑ (SIDEBAR) ---
st.sidebar.title("📁 Πλοήγηση & Αναζήτηση")

# Επιλογή Καλλιτέχνη
available_artists = sorted(df_pressings_all['Artist'].unique())
selected_artist = st.sidebar.selectbox("Επιλέξτε Καλλιτέχνη προς προβολή:", available_artists)

# Φιλτράρισμα των άλμπουμ του συγκεκριμένου καλλιτέχνη
filtered_albums = df_pressings_all[df_pressings_all['Artist'] == selected_artist]

# Dropdown άλμπουμ
album_options = []
for idx, r in filtered_albums.iterrows():
    year_val = r['Release_Year']
    if pd.notna(year_val):
        year_str = str(year_val).split()[-1]
        year_str = f" ({year_str.split('.')[0]})"
    else:
        year_str = ""
    album_options.append(f"{r['Album']}{year_str}")

selected_album_display = st.sidebar.selectbox("Επιλέξτε Άλμπουμ προς προβολή:", album_options)

# Ανάκτηση του σωστού άλμπουμ και του Album_ID του
selected_album_row = filtered_albums.iloc[album_options.index(selected_album_display)]
selected_album_id = selected_album_row['Album_ID']

# Φιλτράρισμα δεδομένων και tracks με βάση το Album_ID
album_facts = selected_album_row
album_tracks = df_tracks_all[df_tracks_all['Album_ID'] == selected_album_id].sort_values(by='No')

# --- ΑΥΤΟΜΑΤΟΙ ΥΠΟΛΟΓΙΣΜΟΙ ΣΤΑΤΙΣΤΙΚΩΝ ---
valid_cv = pd.to_numeric(album_tracks['Compositional_Value'], errors='coerce').dropna()
valid_ai = pd.to_numeric(album_tracks['Audiophile_Interest'], errors='coerce').dropna()

mean_cv = valid_cv.mean() if not valid_cv.empty else 0.0
mean_ai = valid_ai.mean() if not valid_ai.empty else 0.0

# Εύρεση Top Track(s) - Compositional Value
if not album_tracks.empty:
    temp_tracks = album_tracks.copy()
    temp_tracks['CV_num'] = pd.to_numeric(temp_tracks['Compositional_Value'], errors='coerce')
    max_cv = temp_tracks['CV_num'].max()
    top_tracks_df = temp_tracks[temp_tracks['CV_num'] == max_cv]
    top_track_list = [f"{r['Track_Title']}" for idx, r in top_tracks_df.iterrows()]
    top_track_name = f"{', '.join(top_track_list)} ({max_cv:.2f})"
else:
    top_track_name = "—"

# Εύρεση Sonic Highlight(s) - Audiophile Interest
if not album_tracks.empty:
    temp_tracks = album_tracks.copy()
    temp_tracks['AI_num'] = pd.to_numeric(temp_tracks['Audiophile_Interest'], errors='coerce')
    max_ai = temp_tracks['AI_num'].max()
    sonic_df = temp_tracks[temp_tracks['AI_num'] == max_ai]
    sonic_list = [f"{r['Track_Title']}" for idx, r in sonic_df.iterrows()]
    sonic_highlight_name = f"{', '.join(sonic_list)} ({max_ai:.2f})"
else:
    sonic_highlight_name = "—"

# --- ΕΜΦΑΝΙΣΗ ΣΤΟΙΧΕΙΩΝ ΣΤΗ SIDEBAR ---
st.sidebar.write("---")

# Εμφάνιση εξωφύλλου αν υπάρχει URL
if 'Image_URL' in album_facts and pd.notna(album_facts['Image_URL']):
    st.sidebar.image(album_facts['Image_URL'], use_container_width=True)
    st.sidebar.write("---")

st.sidebar.markdown(f"🌟 **Συνολικό RYM Rating:** {album_facts['RYM_Rating']}")
st.sidebar.markdown(f"🏷️ **Genres:** {album_facts['Genres_Subgenres']}")

if 'Label_Pressing' in album_facts and pd.notna(album_facts['Label_Pressing']):
    st.sidebar.markdown(f"📀 **Έκδοση:** {album_facts['Label_Pressing']}")

st.sidebar.write("---")
st.sidebar.markdown("### 📊 Στατιστικά Άλμπουμ (Μ.Ο.)")
st.sidebar.markdown(f"🎵 **Μέσο C.V.:** {mean_cv:.2f} / 5.00")
st.sidebar.markdown(f"🎧 **Μέσο A.I.:** {mean_ai:.2f} / 5.00")
st.sidebar.write("---")
st.sidebar.markdown(f"🔥 **Top Track:** {top_track_name}")
st.sidebar.markdown(f"✨ **Sonic Highlight:** {sonic_highlight_name}")

# Προσθήκη κουμπιού Discogs αν υπάρχει URL
if 'Discogs_URL' in album_facts and pd.notna(album_facts['Discogs_URL']):
    st.sidebar.write("---")
    st.sidebar.link_button("🛒 Δείτε το στο Discogs", album_facts['Discogs_URL'], use_container_width=True)


# --- 3. ΚΥΡΙΩΣ ΠΑΡΑΘΥΡΟ ΕΦΑΡΜΟΓΗΣ ---
st.title("🎵 Audiophile Album Archive & Music Library")
st.subheader(f"🎚️ {album_facts['Artist']} — *{album_facts['Album']}*")
st.write("---")

# Δημιουργία Tabs
tab1, tab2 = st.tabs(["💿 Ανάλυση Κομματιών (Tracks)", "📖 Πληροφορίες Έκδοσης & Ιστορικό"])

with tab1:
    st.markdown("### Tracks Analysis")
    st.write("")
    
    for index, row in album_tracks.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1.5, 3])
            
            with col1:
                st.markdown(f"**{row['No']}. {row['Track_Title']}**")
                st.caption(f"*{row['Genres_Subgenres']}*")
                
            with col2:
                st.markdown(f"⭐ **RYM:** {row['RYM_Rating']}")
                
                try:
                    cv_val = float(row['Compositional_Value'])
                    st.write(f"🎵 **C.V.:** {cv_val:.2f}")
                    st.progress(min(cv_val / 5.0, 1.0))
                except:
                    st.write(f"🎵 **C.V.:** {row['Compositional_Value']}")
                
                st.write("") 
                
                try:
                    ai_val = float(row['Audiophile_Interest'])
                    st.write(f"🎧 **A.I.:** {ai_val:.2f}")
                    st.progress(min(ai_val / 5.0, 1.0))
                except:
                    st.write(f"🎧 **A.I.:** {row['Audiophile_Interest']}")
                
            with col3:
                st.write(row['Notes_Hard_Facts'])
                
            st.write("---")

with tab2:
    st.markdown("### 📝 Ιστορικό Πλαίσιο & Hard Facts")
    st.info(f"{album_facts['Notes_Hard_Facts']}")