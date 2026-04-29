import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import items_db 

st.set_page_config(page_title="Albion Master Hunter Suite", layout="wide")

# --- FUNCIÓN AUTO-PRECIOS DE MATERIALES EN CAERLEON ---
@st.cache_data(ttl=600)
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
def_p = {4: [11, 89, 411], 5: [48, 278, 744], 6: [223, 1057, 2721], 7: [856, 2585, 8990], 8: [3050, 9988, 29985]}

# ==========================================
# MENÚ DE NAVEGACIÓN LATERAL
# ==========================================
st.sidebar.image("https://assets.albiononline.com/assets/images/logo.png", width=150) # Un toque visual
st.sidebar.header("🎯 Herramientas")
menu = st.sidebar.radio("Selecciona un Módulo:", [
    "🏹 Flipper (Mercado)", 
    "🔨 Crafting Scanner", 
    "✨ Arbitraje Fragmentos"
])
st.sidebar.markdown("---")

# ==========================================
# MÓDULO 1: EL FLIPPER ORIGINAL (INTACTO)
# ==========================================
if menu == "🏹 Flipper (Mercado)":
    
    st.title("🏹 Albion Master Hunter (Riesgo Cero)")
    
    categoria_sel = st.sidebar.selectbox("Seleccionar Árbol/Equipo", list(items_db.CATEGORIAS.keys()))
    tiers_visibles = st.sidebar.multiselect("Tiers:", [4, 5, 6, 7, 8], default=[4, 5, 6, 7, 8])

    calidades_sel = st.sidebar.multiselect(
        "Calidades de Compra Base:",
        options=[1, 2, 3, 4, 5],
        default=[1, 2, 3, 4, 5],
        format_func=lambda x: {1:"Normal", 2:"Buena", 3:"Notable", 4:"Sobresaliente", 5:"Obra Maestra"}[x]
    )

    tabs = st.tabs(["T4", "T5", "T6", "T7", "T8"])
    precios_mat = {}

    for i, t in enumerate([4, 5, 6, 7, 8]):
        with tabs[i]:
            c1, c2, c3 = st.columns(3)
            val_r = m_prices.get(f"T{t}_RUNE", def_p[t][0])
            val_s = m_prices.get(f"T{t}_SOUL", def_p[t][1])
            val_re = m_prices.get(f"T{t}_RELIC", def_p[t][2])
            
            precios_mat[t] = [
                c1.number_input(f"Runa T{t}", min_value=0, value=int(val_r), step=1, key=f"runa_t{t}_fix"),
                c2.number_input(f"Alma T{t}", min_value=0, value=int(val_s), step=1, key=f"alma_t{t}_fix"),
                c3.number_input(f"Reliquia T{t}", min_value=0, value=int(val_re), step=1, key=f"reli_t{t}_fix")
            ]

    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1: btn_normal = st.button("🚀 BÚSQUEDA NORMAL")
    with col2: btn_masivo_200 = st.button("🔥 MASIVO (> 200k)")
    with col3: btn_masivo_300 = st.button("💎 MASIVO (> 300k)")

    def procesar_busqueda(ids_api, info_diccionarios, umbral_profit=1000):
        datos = []
        chunk_size = 100 
        
        with st.spinner(f'Analizando lotes del mercado (0 / {len(ids_api)} items)...'):
            progress_bar = st.progress(0)
            for i in range(0, len(ids_api), chunk_size):
                chunk = ids_api[i:i + chunk_size]
                url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(chunk)}?locations=Caerleon,BlackMarket"
                try:
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200: datos.extend(res.json())
                except: pass
                progreso = min(1.0, (i + chunk_size) / len(ids_api))
                progress_bar.progress(progreso)

        db = {}
        for e in datos:
            item, q, city = e['item_id'], e['quality'], e['city']
            if item not in db: db[item] = {}
            if q not in db[item]: db[item][q] = {}
            db[item][q][city] = {
                'venta_min': e['sell_price_min'], 'compra_max': e['buy_price_max'], 
                'fecha': e['sell_price_min_date'] if city == 'Caerleon' else e['buy_price_max_date']
            }

        resultados = []
        ahora = datetime.utcnow()
        q_nombres = {1:"Normal", 2:"Buena", 3:"Notable", 4:"Sobresaliente", 5:"Obra Maestra"}

        with st.spinner('Calculando cascada de ineficiencias...'):
            for t in tiers_visibles:
                p_r, p_s, p_re = precios_mat[t]
                for key, nombre_es in info_diccionarios.items():
                    base_id = f"T{t}_{key}"
                    if "MAIN" in key: cant = 288
                    elif "2H" in key: cant = 384
                    elif any(x in key for x in ["ARMOR", "BAG"]): cant = 192
                    else: cant = 96 

                    for q_compra in calidades_sel:
                        p_base_q = db.get(base_id, {}).get(q_compra, {}).get('Caerleon', {}).get('venta_min', 0)
                        if p_base_q == 0: continue

                        for e in [0, 1, 2, 3]:
                            target_id = base_id if e == 0 else f"{base_id}@{e}"
                            p_venta_final, f_str, q_vendida_como = 0, "", q_compra

                            for q_venta in range(1, q_compra + 1):
                                info_bm = db.get(target_id, {}).get(q_venta, {}).get('Black Market', {})
                                p_bm = info_bm.get('compra_max', 0)
                                if p_bm > p_venta_final:
                                    p_venta_final, f_str, q_vendida_como = p_bm, info_bm.get('fecha'), q_venta

                            if p_venta_final == 0: continue

                            costo_mat = 0
                            receta_texto = "Directo (Sin encantar)"
                            if e == 1: 
                                costo_mat += (p_r * cant)
                                receta_texto = f"+ {cant} Runas"
                            elif e == 2: 
                                costo_mat += (p_r * cant) + (p_s * cant)
                                receta_texto = f"+ {cant} Runas + {cant} Almas"
                            elif e == 3: 
                                costo_mat += (p_r * cant) + (p_s * cant) + (p_re * cant)
                                receta_texto = f"+ {cant} Runas + {cant} Almas + {cant} Reliquias"
                            
                            costo_total = p_base_q + costo_mat
                            profit = (p_venta_final * 0.92) - costo_total 
                            
                            if profit >= umbral_profit:
                                try:
                                    dt = datetime.strptime(f_str, '%Y-%m-%dT%H:%M:%S')
                                    min_diff = int((ahora - dt).total_seconds() / 60)
                                    if min_diff <= 60:
                                        si_hubo_truco = q_nombres[q_compra] if q_compra == q_vendida_como else f"{q_nombres[q_compra]} ➔ {q_nombres[q_vendida_como]}"
                                        resultados.append({
                                            "Objeto": f"{nombre_es}", "Tier": f"{t}.{e}", "Calidad": si_hubo_truco, "Receta": receta_texto,
                                            "Profit Neto": int(profit), "ROI %": round((profit / costo_total) * 100, 1),
                                            "Costo Total": int(costo_total), "BM Paga": int(p_venta_final), "Hace": f"{min_diff}m"
                                        })
                                except: continue

        if resultados:
            df = pd.DataFrame(resultados).sort_values(by="Profit Neto", ascending=False)
            df = df.drop_duplicates(subset=['Objeto', 'Tier', 'BM Paga'])
            st.success(f"¡Se encontraron {len(df)} oportunidades rentables!")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning(f"No hay profit fresco (<60m) superior a {umbral_profit} silver. ¡Actualiza el mercado!")

    if btn_normal:
        items_info = items_db.CATEGORIAS[categoria_sel]
        ids_api = [f"T{t}_{key}{e}" for t in tiers_visibles for key in items_info.keys() for e in ["", "@1", "@2", "@3"]]
        procesar_busqueda(ids_api, items_info, umbral_profit=1000)

    if btn_masivo_200 or btn_masivo_300:
        umbral = 200000 if btn_masivo_200 else 300000
        dic_maestro = {}
        for cat in items_db.CATEGORIAS.values(): dic_maestro.update(cat)
        ids_api_masivo = [f"T{t}_{key}{e}" for t in tiers_visibles for key in dic_maestro.keys() for e in ["", "@1", "@2", "@3"]]
        procesar_busqueda(ids_api_masivo, dic_maestro, umbral_profit=umbral)

# ==========================================
# MÓDULO 2: CRAFTING SCANNER
# ==========================================
elif menu == "🔨 Crafting Scanner":
    st.title("🔨 Crafting Scanner (Caerleon -> BM)")
    st.write("Verifica si fabricar el objeto desde cero deja más ganancia que comprarlo hecho.")
    
    col1, col2 = st.columns(2)
    tier_c = col1.selectbox("Tier Base a fabricar (Plano):", [4, 5, 6, 7, 8])
    categoria_craft = col2.selectbox("Familia de Objetos:", list(items_db.CATEGORIAS.keys()))
    
    st.info("💡 Ingresa el precio del material refinado principal (Cuero, Tela, Metal o Madera) que usa esta familia.")
    col3, col4 = st.columns(2)
    costo_mat = col3.number_input(f"Costo de 1 Material Refinado T{tier_c}:", value=150, step=10)
    devolucion = col4.slider("% Devolución de Recursos (Caerleon Base = 15.2%)", 0.0, 50.0, 15.2)
    
    if st.button("🛠️ Analizar Rentabilidad de Crafteo"):
        items_info = items_db.CATEGORIAS[categoria_craft]
        ids_api = [f"T{tier_c}_{key}" for key in items_info.keys()]
        
        with st.spinner('Revisando el Black Market...'):
            url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(ids_api)}?locations=BlackMarket"
            try:
                datos = requests.get(url, timeout=10).json()
                resultados_craft = []
                ahora = datetime.utcnow()
                
                for e in datos:
                    p_bm = e['buy_price_max']
                    if p_bm == 0: continue
                    
                    item_id = e['item_id']
                    key_base = item_id.split('_', 1)[1] if '_' in item_id else item_id
                    nombre = items_info.get(key_base, item_id)
                    
                    # Identificar cuántos materiales usa según la familia
                    if "MAIN" in key_base: mats = 16
                    elif "2H" in key_base: mats = 24 # Varía un poco (20 a 32), usamos promedio 24
                    elif any(x in key_base for x in ["ARMOR", "BAG"]): mats = 16
                    elif any(x in key_base for x in ["SHOES", "HEAD"]): mats = 8
                    else: mats = 8
                    
                    costo_fabricacion = (costo_mat * mats) * (1 - (devolucion / 100))
                    profit_craft = (p_bm * 0.92) - costo_fabricacion
                    
                    if profit_craft > 0:
                        try:
                            dt = datetime.strptime(e['buy_price_max_date'], '%Y-%m-%dT%H:%M:%S')
                            min_diff = int((ahora - dt).total_seconds() / 60)
                            if min_diff <= 60:
                                resultados_craft.append({
                                    "Objeto a Fabricar": nombre,
                                    "Materiales Necesarios": mats,
                                    "Receta Costo": int(costo_fabricacion),
                                    "BM Paga": int(p_bm),
                                    "Profit de Crafteo": int(profit_craft),
                                    "Hace": f"{min_diff}m"
                                })
                        except: pass
                        
                if resultados_craft:
                    df_c = pd.DataFrame(resultados_craft).sort_values(by="Profit de Crafteo", ascending=False)
                    st.dataframe(df_c, use_container_width=True)
                else:
                    st.warning("No hay profit al craftear con ese costo de material. ¡Intenta con órdenes de compra para los recursos!")
            except Exception as e:
                st.error("Error al conectar con la API.")

# ==========================================
# MÓDULO 3: ARBITRAJE DE FRAGMENTOS
# ==========================================
elif menu == "✨ Arbitraje Fragmentos":
    st.title("✨ Monitoreo de Artefactos (Caerleon)")
    st.write("Verifica el costo de Runas, Almas y Reliquias en tiempo real para saber si te conviene transmutar o comprar directo.")
    
    if m_prices:
        datos_art = []
        for t in [4, 5, 6, 7, 8]:
            r = m_prices.get(f"T{t}_RUNE", def_p[t][0])
            s = m_prices.get(f"T{t}_SOUL", def_p[t][1])
            re = m_prices.get(f"T{t}_RELIC", def_p[t][2])
            
            datos_art.append({
                "Nivel": f"Tier {t}",
                "Precio 1 Runa": int(r),
                "Precio 1 Alma": int(s),
                "Precio 1 Reliquia": int(re),
            })
        
        st.dataframe(pd.DataFrame(datos_art), use_container_width=True)
        st.info("💡 **Tip de Trader:** Si el precio de un Alma está absurdamente más barato que 10 Runas, compra las Almas directo. Si las Runas están regaladas, transmútalas en el Manipulador de Energía.")
    else:
        st.error("No se pudieron cargar los precios de los artefactos. ¿Está abierto el Albion Data Client?")