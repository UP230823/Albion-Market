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
st.sidebar.image("https://assets.albiononline.com/assets/images/logo.png", width=150)
st.sidebar.header("🎯 Herramientas")
menu = st.sidebar.radio("Selecciona un Módulo:", [
    "🏹 Flipper (Mercado & Royal Cities)", 
    "🔨 Crafting Scanner Masivo", 
    "✨ Arbitraje Fragmentos"
])
st.sidebar.markdown("---")

# ==========================================
# MÓDULO 1: EL FLIPPER MULTICIUDAD
# ==========================================
if menu == "🏹 Flipper (Mercado & Royal Cities)":
    st.title("🏹 Albion Master Hunter (Flipper)")
    
    # --- PANEL DE CONTROL ESTILO PRO ---
    st.markdown("### 🌍 Locaciones de Compra (Buy Locations)")
    cc1, cc2, cc3, cc4, cc5, cc6 = st.columns(6)
    c_caerleon = cc1.checkbox("Caerleon", value=True)
    c_fort = cc2.checkbox("Fort Sterling")
    c_lym = cc3.checkbox("Lymhurst")
    c_bridge = cc4.checkbox("Bridgewatch")
    c_mart = cc5.checkbox("Martlock")
    c_thet = cc6.checkbox("Thetford")
    
    ciudades_activas = []
    if c_caerleon: ciudades_activas.append("Caerleon")
    if c_fort: ciudades_activas.append("Fort Sterling")
    if c_lym: ciudades_activas.append("Lymhurst")
    if c_bridge: ciudades_activas.append("Bridgewatch")
    if c_mart: ciudades_activas.append("Martlock")
    if c_thet: ciudades_activas.append("Thetford")
    
    if not ciudades_activas:
        st.warning("Debes seleccionar al menos una ciudad de compra.")
        st.stop()

    st.markdown("### ⚙️ Filtros del Mercado")
    colA, colB, colC = st.columns(3)
    categoria_sel = colA.selectbox("Categoría:", list(items_db.CATEGORIAS.keys()))
    tiers_visibles = colB.multiselect("Tiers:", [4, 5, 6, 7, 8], default=[4, 5, 6, 7, 8])
    calidades_sel = colC.multiselect(
        "Calidades Base:", options=[1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5],
        format_func=lambda x: {1:"Normal", 2:"Good", 3:"Outstanding", 4:"Excellent", 5:"Masterpiece"}[x]
    )

    st.markdown("---")
    tabs = st.tabs(["T4", "T5", "T6", "T7", "T8"])
    precios_mat = {}

    for i, t in enumerate([4, 5, 6, 7, 8]):
        with tabs[i]:
            c1, c2, c3 = st.columns(3)
            val_r = m_prices.get(f"T{t}_RUNE", def_p[t][0])
            val_s = m_prices.get(f"T{t}_SOUL", def_p[t][1])
            val_re = m_prices.get(f"T{t}_RELIC", def_p[t][2])
            
            precios_mat[t] = [
                c1.number_input(f"Rune T{t}", min_value=0, value=int(val_r), step=1, key=f"runa_t{t}_fix"),
                c2.number_input(f"Soul T{t}", min_value=0, value=int(val_s), step=1, key=f"alma_t{t}_fix"),
                c3.number_input(f"Relic T{t}", min_value=0, value=int(val_re), step=1, key=f"reli_t{t}_fix")
            ]

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1: btn_normal = st.button("🚀 BÚSQUEDA NORMAL")
    with col2: btn_masivo_200 = st.button("🔥 MASIVO (> 200k)")
    with col3: btn_masivo_300 = st.button("💎 MASIVO (> 300k)")

    def procesar_busqueda(ids_api, info_diccionarios, umbral_profit=1000):
        datos = []
        chunk_size = 100 
        
        ciudades_query = ",".join(ciudades_activas) + ",BlackMarket"
        
        with st.spinner(f'Analizando lotes del mercado (0 / {len(ids_api)} items)...'):
            progress_bar = st.progress(0)
            for i in range(0, len(ids_api), chunk_size):
                chunk = ids_api[i:i + chunk_size]
                url = f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(chunk)}?locations={ciudades_query}"
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
            db[item][q][city] = {'venta_min': e['sell_price_min'], 'compra_max': e['buy_price_max'], 'fecha': e['sell_price_min_date'] if city != 'Black Market' else e['buy_price_max_date']}

        resultados = []
        ahora = datetime.utcnow()
        q_nombres = {1:"Normal", 2:"Good", 3:"Outstanding", 4:"Excellent", 5:"Masterpiece"}

        with st.spinner('Calculando cascada de ineficiencias inter-ciudad...'):
            for t in tiers_visibles:
                p_r, p_s, p_re = precios_mat[t]
                for key, nombre_en in info_diccionarios.items():
                    base_id = f"T{t}_{key}"
                    if "MAIN" in key: cant = 288
                    elif "2H" in key: cant = 384
                    elif any(x in key for x in ["ARMOR", "BAG"]): cant = 192
                    else: cant = 96 

                    for q_compra in calidades_sel:
                        # Encontrar la base más barata entre todas las ciudades seleccionadas
                        mejor_ciudad = ""
                        p_base_q = float('inf')
                        
                        for city in ciudades_activas:
                            precio_aqui = db.get(base_id, {}).get(q_compra, {}).get(city, {}).get('venta_min', 0)
                            if 0 < precio_aqui < p_base_q:
                                p_base_q = precio_aqui
                                mejor_ciudad = city
                                
                        if p_base_q == float('inf'): continue

                        for e in [0, 1, 2, 3]:
                            target_id = base_id if e == 0 else f"{base_id}@{e}"
                            p_venta_final, f_str, q_vendida_como = 0, "", q_compra
                            for q_venta in range(1, q_compra + 1):
                                info_bm = db.get(target_id, {}).get(q_venta, {}).get('Black Market', {})
                                p_bm = info_bm.get('compra_max', 0)
                                if p_bm > p_venta_final:
                                    p_venta_final, f_str, q_vendida_como = p_bm, info_bm.get('fecha'), q_venta

                            if p_venta_final == 0: continue
                            costo_mat, receta_texto = 0, "Direct (No enchant)"
                            if e == 1: 
                                costo_mat += (p_r * cant); receta_texto = f"+ {cant} Runes"
                            elif e == 2: 
                                costo_mat += (p_r * cant) + (p_s * cant); receta_texto = f"+ {cant} Runes + {cant} Souls"
                            elif e == 3: 
                                costo_mat += (p_r * cant) + (p_s * cant) + (p_re * cant); receta_texto = f"+ {cant} Runes + {cant} Souls + {cant} Relics"
                            
                            costo_total = p_base_q + costo_mat
                            profit = (p_venta_final * 0.92) - costo_total 
                            
                            if profit >= umbral_profit:
                                try:
                                    dt = datetime.strptime(f_str, '%Y-%m-%dT%H:%M:%S')
                                    min_diff = int((ahora - dt).total_seconds() / 60)
                                    if min_diff <= 60:
                                        si_hubo_truco = q_nombres[q_compra] if q_compra == q_vendida_como else f"{q_nombres[q_compra]} ➔ {q_nombres[q_vendida_como]}"
                                        resultados.append({
                                            "Item": f"{nombre_en}", "Tier": f"{t}.{e}", "Quality": si_hubo_truco, "Buy At": mejor_ciudad, "Action": receta_texto,
                                            "Net Profit": int(profit), "ROI %": round((profit / costo_total) * 100, 1),
                                            "Total Cost": int(costo_total), "BM Pays": int(p_venta_final), "Ago": f"{min_diff}m"
                                        })
                                except: continue

        if resultados:
            df = pd.DataFrame(resultados).sort_values(by="Net Profit", ascending=False)
            df = df.drop_duplicates(subset=['Item', 'Tier', 'BM Pays'])
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
# MÓDULO 2: CRAFTING SCANNER MASIVO
# ==========================================
elif menu == "🔨 Crafting Scanner Masivo":
    st.title("🏭 Analizador de Cadenas de Producción")
    st.write("Escanea todo el mercado de un encantamiento específico. Calcula la ruta más barata: comprar refinado vs refinarlo tú mismo.")
    
    col1, col2, col3 = st.columns(3)
    encantamiento_c = col1.selectbox("Filtro de Encantamiento a Escanear:", [4, 3, 2, 1, 0], format_func=lambda x: f".{x}")
    dev_craft = col2.slider("% Devolución Crafteo (Caerleon)", 0.0, 50.0, 15.2)
    dev_refine = col3.slider("% Devolución Refinado (Otras ciudades)", 0.0, 50.0, 36.7)
    
    st.info("⚠️ Este escaneo es profundo. Analizará miles de precios de materiales y equipo simultáneamente.")
    
    MAT_MAP = {"Madera": {"raw": "WOOD", "ref": "PLANKS"}, "Cuero": {"raw": "HIDE", "ref": "LEATHER"}, "Tela": {"raw": "FIBER", "ref": "CLOTH"}, "Metal": {"raw": "ORE", "ref": "METALBAR"}}
    RAW_RATIO = {4: 2, 5: 3, 6: 4, 7: 5, 8: 5}
    
    def get_mat_type(item_str, cat_name):
        s, c = item_str.upper(), cat_name.upper()
        if any(x in s for x in ["PLATE", "SWORD", "AXE", "MACE", "HAMMER", "CROSSBOW", "DAGGER"]): return "Metal"
        if any(x in s for x in ["LEATHER", "BOW", "SPEAR"]): return "Cuero"
        if any(x in s for x in ["CLOTH", "STAFF", "MAGIC", "BOOK"]): return "Tela"
        if "BOW" in c or "SPEAR" in c or "NATURE" in c or "STAFF" in c: return "Madera"
        return "Metal" 

    if st.button(f"🔥 INICIAR ESCANEO GLOBAL .{encantamiento_c}"):
        mats_ids = []
        suffix = f"@{encantamiento_c}" if encantamiento_c > 0 else ""
        for t in [4, 5, 6, 7, 8]:
            base_ref_t = f"T{t-1}" if t > 4 else "T3"
            for mat in MAT_MAP.values():
                mats_ids.extend([f"T{t}_{mat['ref']}{suffix}", f"T{t}_{mat['raw']}{suffix}", f"{base_ref_t}_{mat['ref']}"])
        
        dic_maestro = {}
        for cat in items_db.CATEGORIAS.values(): dic_maestro.update(cat)
        
        equip_ids = [f"T{t}_{key}{suffix}" for t in [4,5,6,7,8] for key in dic_maestro.keys()]
        
        datos_mats = []
        datos_equip = []
        
        with st.spinner("Descargando precios de TODA la cadena de suministros..."):
            for i in range(0, len(mats_ids), 100):
                chunk = mats_ids[i:i + 100]
                try:
                    res = requests.get(f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(chunk)}?locations=Caerleon", timeout=10)
                    if res.status_code == 200: datos_mats.extend(res.json())
                except: pass
            
            bar = st.progress(0)
            for i in range(0, len(equip_ids), 100):
                chunk = equip_ids[i:i + 100]
                try:
                    res = requests.get(f"https://www.albion-online-data.com/api/v2/stats/prices/{','.join(chunk)}?locations=BlackMarket", timeout=10)
                    if res.status_code == 200: datos_equip.extend(res.json())
                except: pass
                bar.progress(min(1.0, (i + 100) / len(equip_ids)))

        db_mats = {e['item_id']: e['sell_price_min'] for e in datos_mats if e['sell_price_min'] > 0}
        
        resultados_craft = []
        ahora = datetime.utcnow()
        
        with st.spinner("Calculando rutas de producción óptimas..."):
            for e in datos_equip:
                p_bm = e['buy_price_max']
                if p_bm == 0: continue
                
                item_full = e['item_id']
                parts = item_full.split('_', 1)
                t_str = parts[0] 
                tier_num = int(t_str[1])
                key_base = parts[1].split('@')[0]
                
                nombre_en = dic_maestro.get(key_base, key_base)
                tipo_mat = get_mat_type(key_base, "")
                
                if "MAIN" in key_base: cant_mats = 16
                elif "2H" in key_base: cant_mats = 24 
                elif any(x in key_base for x in ["ARMOR", "BAG"]): cant_mats = 16
                elif any(x in key_base for x in ["SHOES", "HEAD"]): cant_mats = 8
                else: cant_mats = 8

                id_ref = f"T{tier_num}_{MAT_MAP[tipo_mat]['ref']}{suffix}"
                id_raw = f"T{tier_num}_{MAT_MAP[tipo_mat]['raw']}{suffix}"
                base_ref_t = f"T{tier_num-1}" if tier_num > 4 else "T3"
                id_base_ref = f"{base_ref_t}_{MAT_MAP[tipo_mat]['ref']}"
                
                precio_refinado = db_mats.get(id_ref, float('inf'))
                precio_raw = db_mats.get(id_raw, float('inf'))
                precio_base_ref = db_mats.get(id_base_ref, float('inf'))
                
                costo_ruta_refinado = (precio_refinado * cant_mats) * (1 - (dev_craft / 100))
                
                costo_refinar_1_ud = (precio_raw * RAW_RATIO[tier_num]) + precio_base_ref
                costo_refinar_1_ud = costo_refinar_1_ud * (1 - (dev_refine / 100))
                costo_ruta_raw = (costo_refinar_1_ud * cant_mats) * (1 - (dev_craft / 100))
                
                mejor_ruta = "Ninguna"
                costo_optimo = float('inf')
                
                if costo_ruta_refinado < costo_ruta_raw and precio_refinado != float('inf'):
                    mejor_ruta = f"Buy Refined ({precio_refinado} c/u)"
                    costo_optimo = costo_ruta_refinado
                elif costo_ruta_raw <= costo_ruta_refinado and precio_raw != float('inf') and precio_base_ref != float('inf'):
                    mejor_ruta = f"Buy Raw ({precio_raw} c/u) & Refine"
                    costo_optimo = costo_ruta_raw
                
                if costo_optimo == float('inf'): continue 
                
                profit = (p_bm * 0.92) - costo_optimo
                
                if profit > 100000:
                    try:
                        dt = datetime.strptime(e['buy_price_max_date'], '%Y-%m-%dT%H:%M:%S')
                        min_diff = int((ahora - dt).total_seconds() / 60)
                        
                        # --- FILTRO INTELIGENTE DE TIEMPO (Mantenido) ---
                        limite_tiempo = 10080 if encantamiento_c == 4 else 60 
                        
                        if min_diff <= limite_tiempo:
                            resultados_craft.append({
                                "Item": f"{nombre_en} .{encantamiento_c}",
                                "Tier": f"T{tier_num}",
                                "Optimal Route": mejor_ruta,
                                "Craft Profit": int(profit),
                                "ROI %": round((profit / costo_optimo) * 100, 1),
                                "Final Cost": int(costo_optimo),
                                "BM Pays": int(p_bm),
                                "Ago": f"{min_diff}m"
                            })
                    except: pass
        
        if resultados_craft:
            df_c = pd.DataFrame(resultados_craft).sort_values(by="Craft Profit", ascending=False)
            st.success(f"¡Se encontraron {len(df_c)} oportunidades masivas de producción!")
            st.dataframe(df_c, use_container_width=True)
        else:
            st.warning("No hay márgenes de crafteo rentables actualmente para ese encantamiento.")

# ==========================================
# MÓDULO 3: ARBITRAJE DE FRAGMENTOS
# ==========================================
elif menu == "✨ Arbitraje Fragmentos":
    st.title("✨ Monitoreo de Artefactos (Caerleon)")
    if m_prices:
        datos_art = []
        for t in [4, 5, 6, 7, 8]:
            datos_art.append({"Level": f"Tier {t}", "1 Rune": int(m_prices.get(f"T{t}_RUNE", 0)), "1 Soul": int(m_prices.get(f"T{t}_SOUL", 0)), "1 Relic": int(m_prices.get(f"T{t}_RELIC", 0))})
        st.dataframe(pd.DataFrame(datos_art), use_container_width=True)