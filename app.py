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
available_albums = df_pressings_all['Άλμπουμ'].unique()
selected_album = st.sidebar.selectbox("Επιλέξτε Άλμπουμ προς προβολή:", available_albums)

# Φιλτράρισμα δεδομένων για το επιλεγμένο άλμπουμ
album_facts = df_pressings_all[df_pressings_all['Άλμπουμ'] == selected_album].iloc[0]
album_tracks = df_tracks_all[df_tracks_all['Άλμπουμ'] == selected_album].sort_values(by='No')

# Στατιστικά στη Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Γρήγορα Στατιστικά Άλμπουμ")
st.sidebar.metric(label="RYM Score", value=f"{album_facts['RYM Rating']} / 5.0")
st.sidebar.write(f"**Έτος Κυκλοφορίας:** {str(album_facts['Έτος Κυκλοφορίας']).strip()}")
st.sidebar.write(f"**Genres:** {album_facts['Genres / Subgenres']}")

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
        # Δημιουργούμε 3 στήλες: μία για τον τίτλο/νούμερο, μία για τα ratings και μία για τις σημειώσεις
        col1, col2, col3 = st.columns([2, 2, 5])
        
        with col1:
            st.markdown(f"**{row['No']}. {row['Track / Έκδοση']}**")
            st.caption(f"*{row['Genres / Subgenres']}*")
            
        with col2:
            st.markdown(f"🎵 **Σ.Α.:** {row['Compositional Value']:.2f} | 🎧 **A.I.:** {row['Audiophile Interest']:.2f}")
            
        with col3:
            st.write(row['Σημειώσεις / Hard Facts'])
            
        st.markdown("---")

st.caption("💡 *Σημείωση: Για να προσθέσετε νέα άλμπουμ, απλώς συμπληρώστε τις γραμμές στο αρχείο Excel και κάντε Refresh (R) στην εφαρμογή.*")