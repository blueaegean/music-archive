import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Music Archive Dashboard",
    page_icon="🎸",
    layout="wide"
)

# ---------------------------------------------------------
# Data Loading & Caching
# ---------------------------------------------------------
EXCEL_FILE = 'albums_analysis_fixed.xlsx'

@st.cache_data
def load_data():
    try:
        # Φόρτωση των δύο tabs από το Excel
        albums_df = pd.read_excel(EXCEL_FILE, sheet_name='albums')
        tracks_df = pd.read_excel(EXCEL_FILE, sheet_name='tracks')
        
        # Καθαρισμός κενών στα Album_ID για σωστό merge/filter
        albums_df['Album_ID'] = albums_df['Album_ID'].astype(str).str.strip()
        tracks_df['Album_ID'] = tracks_df['Album_ID'].astype(str).str.strip()
        
        return albums_df, tracks_df
    except Exception as e:
        st.error(f"Σφάλμα κατά τη φόρτωση του αρχείου Excel ({EXCEL_FILE}): {e}")
        return None, None

albums_df, tracks_df = load_data()

if albums_df is not None and tracks_df is not None:

    # ---------------------------------------------------------
    # Sidebar Filters
    # ---------------------------------------------------------
    st.sidebar.title("🔍 Φίλτρα & Αναζήτηση")
    
    # ⚡ ΕΙΔΙΚΟ ΦΙΛΤΡΟ: Victoria 80s Club Anthems
    show_victoria_only = st.sidebar.checkbox("⚡ Victoria 80s Anthems Only ([V])")
    
    # Φίλτρο Αναζήτησης Καλλιτέχνη / Άλμπουμ
    search_query = st.sidebar.text_input("Αναζήτηση Καλλιτέχνη ή Άλμπουμ:", "")

    # ---------------------------------------------------------
    # MAIN DISPLAY: VICTORIA ONLY MODE
    # ---------------------------------------------------------
    if show_victoria_only:
        st.title("⚡ Victoria Club ClassiX Selection ([V])")
        st.markdown("*Τα ιστορικά tracks που έσειαν το υπόγειο της Victoria στον Κορυδαλλό!*")
        st.write("---")
        
        # Φιλτράρισμα τραγουδιών που έχουν 'V' στη στήλη Victoria_Track
        if 'Victoria_Track' in tracks_df.columns:
            victoria_tracks = tracks_df[
                tracks_df['Victoria_Track'].notna() & 
                (tracks_df['Victoria_Track'].astype(str).str.strip().str.upper() == 'V')
            ].copy()
            
            if not victoria_tracks.empty:
                # Merge με τα στοιχεία του άλμπουμ για να φαίνεται ο καλλιτέχνης
                merged_v = pd.merge(victoria_tracks, albums_df[['Album_ID', 'Artist', 'Album']], on='Album_ID', how='left')
                
                # Προβολή αποτελεσμάτων
                display_cols = ['Artist', 'Album', 'No', 'Track_Title', 'Genres_Subgenres', 'Compositional_Value', 'Audiophile_Interest']
                available_cols = [c for c in display_cols if c in merged_v.columns]
                
                st.dataframe(
                    merged_v[available_cols].rename(columns={
                        'Track_Title': 'Τίτλος Τραγουδιού',
                        'Genres_Subgenres': 'Είδος',
                        'Compositional_Value': 'C.V.',
                        'Audiophile_Interest': 'A.I.'
                    }),
                    use_container_width=True
                )
            else:
                st.info("Δεν βρέθηκαν κομμάτια με τη σήμανση 'V' στη στήλη Victoria_Track.")
        else:
            st.warning("Η στήλη 'Victoria_Track' δεν βρέθηκε στο tab 'tracks' του Excel.")

    # ---------------------------------------------------------
    # MAIN DISPLAY: STANDARD CATALOG VIEW
    # ---------------------------------------------------------
    else:
        st.title("🎼 Music Archive & Vinyl Collection")
        
        # Εφαρμογή φίλτρου αναζήτησης στα άλμπουμ
        filtered_albums = albums_df.copy()
        if search_query:
            filtered_albums = filtered_albums[
                filtered_albums['Artist'].str.contains(search_query, case=False, na=False) |
                filtered_albums['Album'].str.contains(search_query, case=False, na=False)
            ]

        # Επιλογή Άλμπουμ από λίστα
        album_list = filtered_albums['Artist'] + " - " + filtered_albums['Album'] + " (" + filtered_albums['Release_Year'].astype(str) + ")"
        
        if not album_list.empty:
            selected_album_str = st.selectbox("Επιλέξτε Άλμπουμ για προβολή:", album_list)
            
            # Εντοπισμός του επιλεγμένου Album_ID
            selected_idx = album_list[album_list == selected_album_str].index[0]
            selected_album = filtered_albums.loc[selected_idx]
            album_id = str(selected_album['Album_ID']).strip()
            
            st.write("---")
            
            # ---------------------------------------------------------
            # Album Details & Hard Facts
            # ---------------------------------------------------------
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.header(f"{selected_album['Artist']}")
                st.subheader(f"{selected_album['Album']} ({selected_album['Release_Year']})")
                st.markdown(f"**Είδος:** {selected_album['Genres_Subgenres']}")
                st.markdown(f"**RYM Rating:** ⭐ {selected_album['RYM_Rating']}")
                st.markdown(f"**Έκδοση / Pressing:** {selected_album['Label_Pressing']}")

            with col2:
                st.subheader("📋 Hard Facts & Ηχητική Αξιολόγηση")
                st.info(selected_album['Notes_Hard_Facts'])

            st.write("---")
            st.subheader("🎵 Tracklist & Αξιολόγηση Κομματιών")
            
            # ---------------------------------------------------------
            # Tracklist Display
            # ---------------------------------------------------------
            current_tracks = tracks_df[tracks_df['Album_ID'] == album_id].sort_values(by='No')
            
            if not current_tracks.empty:
                for idx, track in current_tracks.iterrows():
                    title = track['Track_Title']
                    
                    # Έλεγχος για τη σήμανση Victoria [V]
                    is_victoria = (
                        'Victoria_Track' in track and 
                        pd.notna(track['Victoria_Track']) and 
                        str(track['Victoria_Track']).strip().upper() == 'V'
                    )
                    
                    # Διαμόρφωση τίτλου αν είναι Victoria Anthem
                    if is_victoria:
                        display_title = f"{title} ⚡ **[V - Victoria Anthem]**"
                    else:
                        display_title = title
                    
                    # Εμφάνιση στοιχείων τραγουδιού
                    with st.expander(f"**{track['No']}. {display_title}**"):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        with c1:
                            st.write(f"**Είδος:** {track['Genres_Subgenres']}")
                            if 'Notes_Hard_Facts' in track and pd.notna(track['Notes_Hard_Facts']):
                                st.write(f"*{track['Notes_Hard_Facts']}*")
                        with c2:
                            st.metric("Compositional Value", f"{track['Compositional_Value']} / 5")
                        with c3:
                            st.metric("Audiophile Interest", f"{track['Audiophile_Interest']} / 5")
            else:
                st.warning("Δεν βρέθηκαν κομμάτια για το συγκεκριμένο άλμπουμ στο tab 'tracks'.")
        else:
            st.warning("Δεν βρέθηκαν άλμπουμ που να ταιριάζουν με την αναζήτησή σας.")