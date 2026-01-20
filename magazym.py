import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA POŁĄCZENIA ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_connection()

if not supabase:
    st.error("Błąd połączenia. Sprawdź Secrets w Streamlit Cloud.")
    st.stop()

st.set_page_config(page_title="System Magazynowy", layout="wide")

# --- FUNKCJE ---
def pobierz_dane(tabela):
    try:
        return supabase.table(tabela).select("*").order("id").execute().data
    except Exception as e:
        st.error(f"Błąd pobierania ({tabela}): {e}")
        return []

# --- NAWIGACJA ---
menu = st.sidebar.radio("Nawigacja", ["📊 Przegląd", "📂 Kategorie", "📦 Produkty"])

# --- 1. PRZEGLĄD ---
if menu == "📊 Przegląd":
    st.title("📊 Stan Magazynu")
    produkty = pobierz_dane("produkty")
    
    if produkty:
        calkowita_wartosc = sum(float(p.get('cena', 0)) * int(p.get('liczba', 0)) for p in produkty)
        suma_sztuk = sum(int(p.get('liczba', 0)) for p in produkty)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Wartość towaru", f"{calkowita_wartosc:,.2f} zł")
        m2.metric("Suma jednostek", suma_sztuk)
        m3.metric("Liczba pozycji", len(produkty))
        
        st.divider()
        niskie_stany = [p for p in produkty if int(p.get('liczba', 0)) < 5]
        if niskie_stany:
            st.warning(f"⚠️ Uwaga: {len(niskie_stany)} produkty na wyczerpaniu!")
            for np in niskie_stany:
                st.write(f"- {np['nazwa']} (zostało: **{np['liczba']}**)")
    else:
        st.info("Magazyn jest pusty.")

# --- 2. KATEGORIE ---
elif menu == "📂 Kategorie":
    st.header("Zarządzanie Kategoriami")
    
    with st.expander("➕ Dodaj nową kategorię"):
        with st.form("form_kat", clear_on_submit=True):
            nazwa_k = st.text_input("Nazwa kategorii")
            opis_k = st.text_input("Opis")
            if st.form_submit_button("Zapisz"):
                if nazwa_k:
                    supabase.table("kategorie").insert({"nazwa": nazwa_k, "opis": opis_k}).execute()
                    st.rerun()

    kats = pobierz_dane("kategorie")
    for k in kats:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"### {k['nazwa']}")
            if c2.button("Usuń", key=f"k_{k['id']}"):
                supabase.table("kategorie").delete().eq("id", k['id']).execute()
                st.rerun()

# --- 3. PRODUKTY ---
elif menu == "📦 Produkty":
    st.header("Baza Produktów")
    
    kats_data = pobierz_dane("kategorie")
    mapa_kat = {k['nazwa']: k['id'] for k in kats_data}

    with st.expander("➕ Dodaj produkt"):
        if not mapa_kat:
            st.warning("Najpierw stwórz kategorię!")
        else:
            with st.form("form_prod", clear_on_submit=True):
                col1, col2 = st.columns(2)
                nazwa_p = col1.text_input("Nazwa produktu")
                kat_p = col1.selectbox("Kategoria", options=list(mapa_kat.keys()))
                cena_p = col2.number_input("Cena (zł)", min_value=0.0)
                liczba_p = col2.number_input("Ilość", min_value=0, step=1)
                
                if st.form_submit_button("Dodaj do bazy"):
                    if nazwa_p:
                        # KLUCZOWA ZMIANA: używamy "kategoria.id" zgodnie z Twoim schematem
                        payload = {
                            "nazwa": nazwa_p, 
                            "liczba": liczba_p, 
                            "cena": cena_p, 
                            "kategoria.id": mapa_kat[kat_p]
                        }
                        try:
                            supabase.table("produkty").insert(payload).execute()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Błąd zapisu: {e}")
                    else:
                        st.error("Podaj nazwę!")

    st.subheader("Aktualny stan")
    produkty = pobierz_dane("produkty")
    for p in produkty:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"**{p['nazwa']}**")
            c2.write(f"Stan: {p['liczba']}")
            c3.write(f"{p['cena']} zł")
            if c4.button("Usuń", key=f"p_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p['id']).execute()
                st.rerun()
