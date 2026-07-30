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
        albums_df = pd.read_excel(EXCEL_FILE, sheet_name='albums')
        tracks_df = pd.read_excel(EXCEL_FILE, sheet_name='tracks')
        
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
    
    show_victoria_only = st.sidebar.checkbox("⚡ Victoria 80s Anthems Only ([V])")
    search_query = st.sidebar.text_input("Αναζήτηση Καλλιτέχνη ή Άλμπουμ:", "")

    # ---------------------------------------------------------
    # VICTORIA ONLY MODE
    # ---------------------------------------------------------
    if show_victoria_only:
        st.title("⚡ Victoria Club ClassiX Selection ([V])")
        st.write("---")
        
        if 'Victoria_Track' in tracks_df.columns:
            victoria_tracks = tracks_df[
                tracks_df['Victoria_Track'].notna() & 
                (tracks_df['Victoria_Track'].astype(str).str.strip().str.upper() == 'V')
            ].copy()
            
            if not victoria_tracks.empty:
                merged_v = pd.merge(victoria_tracks, albums_df[['Album_ID', 'Artist', 'Album']], on='Album_ID', how='left')
                display_cols = ['Artist', 'Album', 'No', 'Track_Title', 'Genres_Subgenres', 'RYM_Rating', 'Compositional_Value', 'Audiophile_Interest']
                available_cols = [c for c in display_cols if c in merged_v.columns]
                
                st.dataframe(
                    merged_v[available_cols].rename(columns={
                        'Track_Title': 'Τίτλος Τραγουδιού',
                        'Genres_Subgenres': 'Είδος',
                        'RYM_Rating': 'RYM Track Rating',
                        'Compositional_Value': 'C.V.',
                        'Audiophile_Interest': 'A.I.'
                    }),
                    use_container_width=True
                )
            else:
                st.info("Δεν βρέθηκαν κομμάτια με τη σήμανση 'V' στη στήλη Victoria_Track.")
        else:
            st.warning("Η στήλη 'Victoria_Track' δεν βρέθηκε στο tab 'tracks'.")

    # ---------------------------------------------------------
    # STANDARD CATALOG VIEW (ORIGINAL LAYOUT WITH RYM TRACK RATINGS)
    # ---------------------------------------------------------
    else:
        filtered_albums = albums_df.copy()
        if search_query:
            filtered_albums = filtered_albums[
                filtered_albums['Artist'].str.contains(search_query, case=False, na=False) |
                filtered_albums['Album'].str.contains(search_query, case=False, na=False)
            ]

        album_list = filtered_albums['Artist'] + " - " + filtered_albums['Album'] + " (" + filtered_albums['Release_Year'].astype(str) + ")"
        
        if not album_list.empty:
            selected_album_str = st.selectbox("Επιλέξτε Άλμπουμ για προβολή:", album_list)
            
            selected_idx = album_list[album_list == selected_album_str].index[0]
            selected_album = filtered_albums.loc[selected_idx]
            album_id = str(selected_album['Album_ID']).strip()
            
            st.write("---")
            
            # Header Άλμπουμ & Hard Facts
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
            
            current_tracks = tracks_df[tracks_df['Album_ID'] == album_id].sort_values(by='No')
            
            if not current_tracks.empty:
                for idx, track in current_tracks.iterrows():
                    title = track['Track_Title']
                    
                    # Έλεγχος για το V
                    is_victoria = (
                        'Victoria_Track' in track and 
                        pd.notna(track['Victoria_Track']) and 
                        str(track['Victoria_Track']).strip().upper() == 'V'
                    )
                    
                    v_badge = " ⚡ **[V]**" if is_victoria else ""
                    
                    # Διάταξη σε 4 στήλες: Τίτλος | RYM Track Rating | C.V. | A.I.
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    
                    with c1:
                        st.markdown(f"**{track['No']}. {title}**{v_badge}")
                        st.caption(f"Είδος: {track['Genres_Subgenres']}")
                        if 'Notes_Hard_Facts' in track and pd.notna(track['Notes_Hard_Facts']):
                            st.write(f"*{track['Notes_Hard_Facts']}*")
                            
                    with c2:
                        rym_tr = track['RYM_Rating'] if 'RYM_Rating' in track and pd.notna(track['RYM_Rating']) else "-"
                        st.write(f"**RYM:** ⭐ {rym_tr}")
                        
                    with c3:
                        st.write(f"**C.V.:** {track['Compositional_Value']} / 5")
                        
                    with c4:
                        st.write(f"**A.I.:** {track['Audiophile_Interest']} / 5")
                        
                    st.write("---")
            else:
                st.warning("Δεν βρέθηκαν κομμάτια για το συγκεκριμένο άλμπουμ.")
        else:
            st.warning("Δεν βρέθηκαν άλμπουμ που να ταιριάζουν με την αναζήτησή σας.")