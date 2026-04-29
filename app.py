import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import items_db 

st.set_page_config(page_title="Albion Master Hunter - AutoMarket", layout="wide")

# --- FUNCIÓN AUTO-PRECIOS DE MATERIALES EN CAERLEON ---
@st.cache_data(ttl=600) # Se actualiza cada 10 min
def get_material_prices():
    ids = []
    for t in [4,5,6,7,8]:
        ids.extend([f"T{t}_RUNE", f"T{t}_SOUL", f"T{t}_RELIC"])
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids)}?locations=Caerleon"
    try:
        res = requests.get(url, timeout=5).json()
        precios = {e['item_id']: e['sell_price_min'] for e in res if e['sell_price_min'] > 0}
        return precios
    except:
        return {}

m_prices = get_material_prices()

st.sidebar.header("🎯 Panel de Control")
categoria_sel = st.sidebar.selectbox("Seleccionar Árbol/Equipo", list(items_db.CATEGORIAS.keys()))
tiers_visibles = st.sidebar.multiselect("Tiers:", [4, 5, 6, 7, 8], default=[4, 5, 6])

# --- CALIDADES ---
calidades_sel = st.sidebar.multiselect(
    "Calidades:",
    options=[1, 2, 3, 4, 5],
    default=[1, 2, 3, 4, 5],
    format_func=lambda x: {1:"Normal", 2:"Buena", 3:"Notable", 4:"Sobresaliente", 5:"Obra Maestra"}[x]
)

st.title(f"🏹 Escaneo BM + Caerleon: {categoria_sel}")

# --- INPUTS CORREGIDOS ---
tabs = st.tabs(["T4", "T5", "T6", "T7", "T8"])
precios_mat = {}

# Precios base si la API falla
def_p = {
    4: [11, 89, 411],
    5: [48, 278, 744],
    6: [223, 1057, 2721],
    7: [856, 2585, 8990],
    8: [3050, 9988, 29985]
}

for i, t in enumerate([4, 5, 6, 7, 8]):
    with tabs[i]:
        c1, c2, c3 = st.columns(3)
        val_r = m_prices.get(f"T{t}_RUNE", def_p[t][0])
        val_s = m_prices.get(f"T{t}_SOUL", def_p[t][1])
        val_re = m_prices.get(f"T{t}_RELIC", def_p[t][2])
        
        # FIX DEFINITIVO: Especificar explícitamente value=... y min_value=...
        precios_mat[t] = [
            c1.number_input(f"Runa T{t}", min_value=0, value=int(val_r), step=1, key=f"runa_t{t}_fix"),
            c2.number_input(f"Alma T{t}", min_value=0, value=int(val_s), step=1, key=f"alma_t{t}_fix"),
            c3.number_input(f"Reliquia T{t}", min_value=0, value=int(val_re), step=1, key=f"reli_t{t}_fix")
        ]

if st.button("🚀 INICIAR BÚSQUEDA INTEGRAL"):
    items_info = items_db.CATEGORIAS[categoria_sel]
    ids_api = []
    for t in tiers_visibles:
        for key in items_info.keys():
            base = f"T{t}_{key}"
            ids_api.extend([base, f"{base}@1", f"{base}@2", f"{base}@3"])
    
    url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids_api)}?locations=Caerleon,BlackMarket&qualities={','.join(map(str, calidades_sel))}"
    
    with st.spinner('Consultando mercado...'):
        datos = requests.get(url).json()

    # Mapeo: [item_id][calidad][ciudad]
    db = {}
    for e in datos:
        item, q, city = e['item_id'], e['quality'], e['city']
        if item not in db: db[item] = {}
        if q not in db[item]: db[item][q] = {}
        
        db[item][q][city] = {
            'venta_min': e['sell_price_min'], # Comprar base
            'compra_max': e['buy_price_max'], # Vender a orden
            'fecha': e['sell_price_min_date'] if city == 'Caerleon' else e['buy_price_max_date']
        }

    resultados = []
    ahora = datetime.utcnow()

    for t in tiers_visibles:
        p_r, p_s, p_re = precios_mat[t]
        for key, nombre_es in items_info.items():
            base_id = f"T{t}_{key}"
            
            # --- LÓGICA DE MATERIALES ---
            if "MAIN" in key: cant = 288
            elif "2H" in key: cant = 384
            elif any(x in key for x in ["ARMOR", "BAG"]): cant = 192
            else: cant = 96 

            for q in calidades_sel:
                # 1. Compramos la BASE plana en Caerleon
                p_base_q = db.get(base_id, {}).get(q, {}).get('Caerleon', {}).get('venta_min', 0)
                if p_base_q == 0: continue

                for e in [0, 1, 2, 3]:
                    target_id = base_id if e == 0 else f"{base_id}@{e}"
                    
                    # 2. Buscamos la mejor orden de compra
                    info_bm = db.get(target_id, {}).get(q, {}).get('Black Market', {})
                    info_caerleon = db.get(target_id, {}).get(q, {}).get('Caerleon', {})
                    
                    p_bm = info_bm.get('compra_max', 0)
                    p_cae = info_caerleon.get('compra_max', 0)
                    
                    if p_bm >= p_cae:
                        p_venta_final = p_bm
                        lugar_venta = "Black Market"
                        f_str = info_bm.get('fecha')
                    else:
                        p_venta_final = p_cae
                        lugar_venta = "Caerleon"
                        f_str = info_caerleon.get('fecha')
                    
                    if p_venta_final == 0: continue

                    # 3. Costo de encantamiento
                    costo_mat = 0
                    if e >= 1: costo_mat += (p_r * cant)
                    if e >= 2: costo_mat += (p_s * cant)
                    if e == 3: costo_mat += (p_re * cant)
                    
                    costo_total = p_base_q + costo_mat
                    profit = (p_venta_final * 0.92) - costo_total # Tax 8%
                    
                    if profit > 1000:
                        try:
                            dt = datetime.strptime(f_str, '%Y-%m-%dT%H:%M:%S')
                            min_diff = int((ahora - dt).total_seconds() / 60)
                            if min_diff < 1440:
                                resultados.append({
                                    "Objeto": f"{nombre_es}",
                                    "Tier": f"{t}.{e}",
                                    "Calidad": {1:"Normal", 2:"Buena", 3:"Notable", 4:"Sobresaliente", 5:"Obra Maestra"}[q],
                                    "Vender en": lugar_venta,
                                    "Profit": int(profit),
                                    "ROI %": round((profit / costo_total) * 100, 1),
                                    "Costo Total": int(costo_total),
                                    "BM Paga": int(p_venta_final),
                                    "Dato": f"{min_diff}m"
                                })
                        except: continue

    if resultados:
        st.dataframe(pd.DataFrame(resultados).sort_values(by="Profit", ascending=False), use_container_width=True)
    else:
        st.warning("No hay profit tras el análisis. ¡Haz un barrido de mercado en el juego!")