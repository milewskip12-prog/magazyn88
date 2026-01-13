import streamlit as st
from supabase import create_client, Client

# --- KONFIGURACJA POŁĄCZENIA ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception:
    st.error("Błąd: Skonfiguruj SUPABASE_URL i SUPABASE_KEY w Secrets.")
    st.stop()

st.set_page_config(page_title="System Magazynowy", layout="wide")

# --- NAWIGACJA ---
menu = st.sidebar.radio("Nawigacja", ["📊 Przegląd", "📂 Kategorie", "📦 Produkty"])

# --- FUNKCJE ---
def pobierz_dane(tabela):
    try:
        return supabase.table(tabela).select("*").execute().data
    except Exception as e:
        st.error(f"Błąd pobierania z {tabela}: {e}")
        return []

# --- 1. PRZEGLĄD (DASHBOARD) ---
if menu == "📊 Przegląd":
    st.title("📊 Stan Magazynu")
    produkty = pobierz_dane("produkty")
    
    if produkty:
        # Obliczenia bez pandas
        calkowita_wartosc = sum(p['cena'] * p['liczba'] for p in produkty)
        suma_sztuk = sum(p['liczba'] for p in produkty)
        liczba_pozycji = len(produkty)
        
        # Metryki na górze strony
        m1, m2, m3 = st.columns(3)
        m1.metric("Wartość towaru", f"{calkowita_wartosc:,.2f} zł")
        m2.metric("Suma jednostek", suma_sztuk)
        m3.metric("Liczba produktów", liczba_pozycji)
        
        st.divider()
        
        # Sekcja alertów
        niskie_stany = [p for p in produkty if p['liczba'] < 5]
        if niskie_stany:
            st.warning(f"⚠️ Uwaga: {len(niskie_stany)} produkty są bliskie wyczerpania!")
            for np in niskie_stany:
                st.write(f"- {np['nazwa']} (zostało tylko: **{np['liczba']} szt.**)")
    else:
        st.info("Magazyn jest pusty. Dodaj produkty, aby zobaczyć statystyki.")

# --- 2. KATEGORIE ---
elif menu == "📂 Kategorie":
    st.header("Zarządzanie Kategoriami")
    
    # Formularz w expanderze (ładniejszy UI)
    with st.expander("➕ Dodaj nową kategorię"):
        with st.form("form_kat", clear_on_submit=True):
            nazwa_k = st.text_input("Nazwa kategorii")
            opis_k = st.text_input("Krótki opis")
            if st.form_submit_button("Zapisz kategorię"):
                if nazwa_k:
                    supabase.table("kategorie").insert({"nazwa": nazwa_k, "opis": opis_k}).execute()
                    st.rerun()
                else:
                    st.error("Nazwa jest wymagana!")

    st.subheader("Lista kategorii")
    kats = pobierz_dane("kategorie")
    for k in kats:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"### {k['nazwa']}")
            if k['opis']: c1.caption(k['opis'])
            if c2.button("Usuń", key=f"kat_{k['id']}"):
                supabase.table("kategorie").delete().eq("id", k['id']).execute()
                st.rerun()

# --- 3. PRODUKTY ---
elif menu == "📦 Produkty":
    st.header("Baza Produktów")
    
    kats_data = pobierz_dane("kategorie")
    mapa_kat = {k['nazwa']: k['id'] for k in kats_data}

    with st.expander("➕ Dodaj nowy produkt do magazynu"):
        if not mapa_kat:
            st.warning("Najpierw stwórz przynajmniej jedną kategorię!")
        else:
            with st.form("form_prod", clear_on_submit=True):
                col1, col2 = st.columns(2)
                nazwa_p = col1.text_input("Nazwa produktu")
                kat_p = col1.selectbox("Wybierz kategorię", options=list(mapa_kat.keys()))
                cena_p = col2.number_input("Cena (zł)", min_value=0.0, step=0.01)
                liczba_p = col2.number_input("Ilość", min_value=0, step=1)
                
                if st.form_submit_button("Dodaj do stanu"):
                    payload = {
                        "nazwa": nazwa_p, 
                        "liczba": liczba_p, 
                        "cena": cena_p, 
                        "kategoria_id": mapa_kat[kat_p]
                    }
                    supabase.table("produkty").insert(payload).execute()
                    st.rerun()

    st.subheader("Aktualny inwentarz")
    produkty = pobierz_dane("produkty")
    
    # Wyświetlanie jako estetyczna lista/karty
    for p in produkty:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
            c1.write(f"**{p['nazwa']}**")
            
            # Kolorowy wskaźnik stanu
            if p['liczba'] == 0:
                c2.error("Brak na stanie")
            elif p['liczba'] < 5:
                c2.warning(f"Niski stan: {p['liczba']}")
            else:
                c2.success(f"Dostępne: {p['liczba']}")
                
            c3.write(f"{p['cena']:.2f} zł / szt.")
            
            if c4.button("Usuń", key=f"prod_{p['id']}"):
                supabase.table("produkty").delete().eq("id", p['id']).execute()
                st.rerun()
