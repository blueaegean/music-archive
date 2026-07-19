import streamlit as st
import pandas as pd

# Ρύθμιση της σελίδας σε Wide Mode για να απλώνουν όμορφα οι πίνακες
st.set_page_config(page_title="Audiophile Album Archive", layout="wide")

# Φόρτωση των δεδομένων από το Excel
@st.cache_data
def load_data():
    df = pd.read_excel("albums_analysis_fixed.xlsx", sheet_name="albums analysis")
    return df

try:
    df_raw = load_data()
except Exception as e:
    st.error("Παρακαλώ βεβαιωθείτε ότι το αρχείο 'albums_analysis_fixed.xlsx' βρίσκεται στον ίδιο φάκελο με το 'app.py'.")
    st.stop()

# Διαχωρισμός Tracks και Pressing Facts
df_tracks_all = df_raw[df_raw['No'] != '#'].copy()
df_pressings_all = df_raw[df_raw['No'] == '#'].copy()

# Τίτλος Εφαρμογής
st.title("🎵 Audiophile Album Archive & Music Library")
st.markdown("---")

# Sidebar - Πλοήγηση & Φίλτρα
st.sidebar.header("🗂️ Πλοήγηση & Αναζήτηση")

# Επιλογή Καλλιτέχνη & Άλμπουμ
available_artists = sorted(df_pressings_all['Καλλιτέχνης'].unique())
selected_artist = st.sidebar.selectbox("Επιλέξτε Καλλιτέχνη προς προβολή:", available_artists)

# Φιλτράρισμα για τα άλμπουμ του συγκεκριμένου καλλιτέχνη
filtered_df_by_artist = df_pressings_all[df_pressings_all['Καλλιτέχνης'] == selected_artist]

# Dropdown άλμπουμ που δείχνει και το έτος σε παρένθεση (με ασφαλή έλεγχο)
album_options = []
for idx, r in filtered_df_by_artist.iterrows():
    year_val = r['Έτος Κυκλοφορίας']
    # Έλεγχος αν το έτος είναι έγκυρος αριθμός
    if pd.notna(year_val) and str(year_val).replace('.','',1).isdigit():
        year_str = f" ({int(float(year_val))})"
    else:
        year_str = ""
    album_options.append(f"{r['Άλμπουμ']}{year_str}")

selected_album_display = st.sidebar.selectbox("Επιλέξτε Άλμπουμ προς προβολή:", album_options)

# Ανάκτηση του καθαρού τίτλου για το φιλτράρισμα
selected_album = filtered_df_by_artist.iloc[album_options.index(selected_album_display)]['Άλμπουμ']

# Φιλτράρισμα δεδομένων και tracks για το επιλεγμένο άλμπουμ
album_facts = df_pressings_all[df_pressings_all['Άλμπουμ'] == selected_album].iloc[0]
album_tracks = df_tracks_all[df_tracks_all['Άλμπουμ'] == selected_album].sort_values(by='No')

# --- ΚΥΡΙΩΣ ΠΑΡΑΘΥΡΟ ΕΦΑΡΜΟΓΗΣ ---
st.header(f"💿 {album_facts['Καλλιτέχνης']} — *{album_facts['Άλμπουμ']}*")

notes_text = str(album_facts['Σημειώσεις / Hard Facts'])
if "|" in notes_text:
    history_part, hard_facts_part = notes_text.split("|", 1)
else:
    history_part = notes_text
    hard_facts_part = ""

st.info(f"**Ιστορικό Πλαίσιο & Παραγωγή:**\n\n{history_part.replace('Α) Ιστορικό Πλαίσιο & Παραγωγή:', '').strip()}")

if hard_facts_part:
    st.warning(f"**📋 Hard Facts Έκδοσης Βινυλίου:**\n\n{hard_facts_part.replace('Hard Facts:', '').strip()}")

# Εμφάνιση των tracks σε καθαρή, αναγνώσιμη μορφή λίστας με κάρτες
for index, row in album_tracks.iterrows():
    with st.container():
        # Χρησιμοποιούμε st.columns με σταθερές αναλογίες για απόλυτη ευθυγράμμιση
        col1, col2, col3 = st.columns([3, 2, 5])
        
        with col1:
            st.markdown(f"**{row['No']}. {row['Track / Έκδοση']}**")
            st.caption(f"*{row['Genres / Subgenres']}*")
            
        with col2:
            # Μετατροπή του Σ.Α. σε C.V. και ευθυγράμμιση
            st.markdown(f"🎵 **C.V.:** {row['Compositional Value']:.2f} <br> 🎧 **A.I.:** {row['Audiophile Interest']:.2f}", unsafe_allow_html=True)
            
        with col3:
            st.write(row['Σημειώσεις / Hard Facts'])
            
        # Προσθήκη extra κενού (padding) πριν τη γραμμή για να αναπνέει το κείμενο
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("---")

st.caption("💡 *Σημείωση: Για να προσθέσετε νέα άλμπουμ, απλώς συμπληρώστε τις γραμμές στο αρχείο Excel και κάντε Refresh (R) στην εφαρμογή.*")