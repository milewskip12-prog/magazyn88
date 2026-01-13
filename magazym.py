import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia - dane pobierane z Streamlit Secrets
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("Skonfiguruj klucze SUPABASE_URL i SUPABASE_KEY w Secrets!")
    st.stop()

st.title("Zarządzanie Kategoriami Produktów")

# --- SEKCJA: DODAWANIE KATEGORII ---
st.header("Dodaj nową kategorię")
with st.form("dodaj_kategorie", clear_on_submit=True):
    nazwa = st.text_input("Nazwa kategorii (wymagane) *")
    opis = st.text_area("Opis kategorii")
    submit = st.form_submit_button("Dodaj do bazy")

    if submit:
        if nazwa:
            try:
                # Zgodnie ze schematem: kolumny 'nazwa' i 'opis'
                data = supabase.table("kategorie").insert({
                    "nazwa": nazwa,
                    "opis": opis if opis else None
                }).execute()
                st.success(f"Dodano kategorię: {nazwa}")
                st.rerun()
            except Exception as e:
                st.error(f"Błąd podczas dodawania: {e}")
        else:
            st.warning("Pole 'Nazwa' nie może być puste!")

st.divider()

# --- SEKCJA: LISTA I USUWANIE ---
st.header("Istniejące kategorie")

def pobierz_kategorie():
    return supabase.table("kategorie").select("*").order("id").execute()

try:
    kategorie = pobierz_kategorie().data
    
    if kategorie:
        for kat in kategorie:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{kat['nazwa']}** (ID: {kat['id']})")
                if kat['opis']:
                    st.caption(kat['opis'])
            
            with col2:
                # Przycisk usuwania
                if st.button("Usuń", key=f"btn_{kat['id']}"):
                    try:
                        supabase.table("kategorie").delete().eq("id", kat['id']).execute()
                        st.success("Usunięto!")
                        st.rerun()
                    except Exception as e:
                        st.error("Błąd: Prawdopodobnie kategoria jest używana w tabeli produkty.")
    else:
        st.info("Brak kategorii w bazie.")
except Exception as e:
    st.error(f"Nie udało się pobrać danych: {e}")
