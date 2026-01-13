import streamlit as st
from supabase import create_client, Client

# Konfiguracja połączenia z Supabase Secrets
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("Błąd: Skonfiguruj SUPABASE_URL i SUPABASE_KEY w Secrets.")
    st.stop()

st.title("Zarządzanie Sklepem")

menu = st.sidebar.selectbox("Menu", ["Kategorie", "Produkty"])

# --- ZAKŁADKA KATEGORIE ---
if menu == "Kategorie":
    st.header("Zarządzaj Kategoriami")
    
    with st.form("form_kat", clear_on_submit=True):
        nazwa = st.text_input("Nazwa kategorii")
        opis = st.text_area("Opis")
        if st.form_submit_button("Dodaj kategorię"):
            # POPRAWIONA LINIA (użycie jawnego słownika)
            dane_kategorii = {"nazwa": nazwa, "opis": opis}
            supabase.table("kategorie").insert(dane_kategorii).execute()
            st.success(f"Dodano kategorię: {nazwa}")
            st.rerun()

    st.subheader("Lista kategorii")
    kats = supabase.table("kategorie").select("*").execute().data
    for k in kats:
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{k['nazwa']}** (ID: {k['id']})")
        if col2.button("Usuń", key=f"del_k_{k['id']}"):
            supabase.table("kategorie").delete().eq("id", k['id']).execute()
            st.rerun()

# --- ZAKŁADKA PRODUKTY ---
elif menu == "Produkty":
    st.header("Zarządzaj Produktami")
    
    # Pobranie kategorii do selectboxa
    kats = supabase.table("kategorie").select("id, nazwa").execute().data
    opcje_kat = {k['nazwa']: k['id'] for k in kats}

    if not opcje_kat:
        st.warning("Najpierw dodaj przynajmniej jedną kategorię!")
    else:
        with st.form("form_prod", clear_on_submit=True):
            nazwa_p = st.text_input("Nazwa produktu")
            liczba = st.number_input("Liczba (int8)", step=1, value=0)
            cena = st.number_input("Cena (numeryczny)", step=0.01, value=0.0)
            wybrana_kat = st.selectbox("Kategoria", options=list(opcje_kat.keys()))
            
            if st.form_submit_button("Dodaj produkt"):
                nowy_prod = {
                    "nazwa": nazwa_p,
                    "liczba": int(liczba),
                    "cena": float(cena),
                    "kategoria_id": opcje_kat[wybrana_kat] # Klucz obcy
                }
                supabase.table("produkty").insert(nowy_prod).execute()
                st.success(f"Dodano produkt: {nazwa_p}")
                st.rerun()

    st.subheader("Lista produktów")
    prods = supabase.table("produkty").select("*").execute().data
    for p in prods:
        c1, c2 = st.columns([4, 1])
        c1.write(f"**{p['nazwa']}** — Cena: {p['cena']} | Ilość: {p['liczba']}")
        if c2.button("Usuń", key=f"del_p_{p['id']}"):
            supabase.table("produkty").delete().eq("id", p['id']).execute()
            st.rerun()
