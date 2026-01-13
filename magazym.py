import streamlit as st
from supabase import create_client, Client

# 1. Bezpieczne połączenie z Supabase
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Błąd konfiguracji: Sprawdź zakładkę Secrets w Streamlit. {e}")
    st.stop()

st.title("Zarządzanie Sklepem (Supabase)")

menu = st.sidebar.selectbox("Menu", ["Kategorie", "Produkty"])

# --- ZAKŁADKA KATEGORIE ---
if menu == "Kategorie":
    st.header("Kategorie Produktów")
    
    with st.form("form_kat", clear_on_submit=True):
        nazwa = st.text_input("Nazwa kategorii *")
        opis = st.text_input("Opis")
        submit = st.form_submit_button("Dodaj kategorię")
        
        if submit:
            if nazwa:
                # POPRAWKA: Jawne tworzenie słownika danych
                payload = {"nazwa": nazwa, "opis": opis if opis else None}
                try:
                    supabase.table("kategorie").insert(payload).execute()
                    st.success(f"Dodano: {nazwa}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd bazy: {e}")
            else:
                st.warning("Nazwa jest wymagana.")

    # Wyświetlanie i usuwanie
    res_k = supabase.table("kategorie").select("*").execute()
    for k in res_k.data:
        c1, c2 = st.columns([4, 1])
        c1.write(f"ID: {k['id']} | **{k['nazwa']}**")
        if c2.button("Usuń", key=f"k_{k['id']}"):
            supabase.table("kategorie").delete().eq("id", k['id']).execute()
            st.rerun()

# --- ZAKŁADKA PRODUKTY ---
elif menu == "Produkty":
    st.header("Produkty")
    
    # Pobranie kategorii do listy rozwijanej
    kats = supabase.table("kategorie").select("id, nazwa").execute().data
    opcje_kat = {k['nazwa']: k['id'] for k in kats}

    if not opcje_kat:
        st.info("Najpierw dodaj kategorię w menu po lewej.")
    else:
        with st.form("form_prod", clear_on_submit=True):
            n_p = st.text_input("Nazwa produktu")
            liczba = st.number_input("Ilość", min_value=0, step=1)
            cena = st.number_input("Cena", min_value=0.0, step=0.01)
            kat_nazwa = st.selectbox("Kategoria", options=list(opcje_kat.keys()))
            
            if st.form_submit_button("Dodaj produkt"):
                # POPRAWKA: Dopasowanie do kolumny 'kategoria.id' ze schematu
                dane_p = {
                    "nazwa": n_p,
                    "liczba": liczba,
                    "cena": cena,
                    "kategoria.id": opcje_kat[kat_nazwa] # Tutaj upewnij się, czy w bazie nie masz kategoria_id
                }
                try:
                    supabase.table("produkty").insert(dane_p).execute()
                    st.success("Dodano produkt.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Błąd: {e}")

    # Lista produktów
    res_p = supabase.table("produkty").select("*").execute()
    for p in res_p.data:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{p['nazwa']}** ({p['cena']} zł) - Ilość: {p['liczba']}")
        if col2.button("Usuń", key=f"p_{p['id']}"):
            supabase.table("produkty").delete().eq("id", p['id']).execute()
            st.rerun()
