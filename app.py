import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from analysis import load_data, load_all_constraints, find_suitable_locations, calculate_stats
import random

def gdf_to_clean_geojson(gdf):
    """Konvertiert GeoDataFrame zu sauberem GeoJSON ohne problematische Attribute"""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": geom.__geo_interface__,
                "properties": {}
            }
            for geom in gdf.geometry
        ]
    }

def get_random_color(seed):
    """Generiert eine zufällige aber konsistente Farbe"""
    random.seed(seed)
    colors = ['red', 'orange', 'crimson', 'darkred', 'orangered', 
              'coral', 'tomato', 'darkorange', 'indianred']
    return random.choice(colors)

st.set_page_config(
    page_title="City Forest Creator",
    page_icon="🌳",
    layout="wide"
)

@st.cache_data
def load_all_data():
    """Lädt und transformiert alle Daten einmal"""
    bäume = load_data()
    constraints = load_all_constraints()
    
    if bäume is not None:
        bäume_wgs84 = bäume.to_crs(epsg=4326)
        stats = calculate_stats(bäume)
        return bäume, bäume_wgs84, constraints, stats
    return None, None, None, None

st.title("🌳 City Forest Creator")
st.markdown("Finde geeignete Standorte für neue Bäume - **alle Dateien aus dem `constraints/` Ordner werden berücksichtigt!**")

# Sidebar - Basis-Einstellungen
st.sidebar.header("⚙️ Einstellungen")

abstand_bäume = st.sidebar.slider(
    "Mindestabstand zu Bäumen (m)", 
    min_value=2, 
    max_value=10, 
    value=5
)

buffer_linien = st.sidebar.slider(
    "Buffer für Linien-Geometrien (m)", 
    min_value=5, 
    max_value=20, 
    value=10
)

# ✅ DATEN ZUERST LADEN
with st.spinner("Lade Geodaten..."):
    bäume, bäume_wgs84, constraints, stats = load_all_data()

if bäume is not None:
    # Ausschlusszonen berechnen
    with st.spinner(f"Berechne Ausschlusszonen..."):
        ausschlusszonen_dict = find_suitable_locations(
            bäume, 
            constraints, 
            abstand_bäume,
            buffer_linien
        )
        
        # Zu WGS84 konvertieren für Karte
        ausschlusszonen_wgs84 = {}
        for key, zone in ausschlusszonen_dict.items():
            if zone is not None:
                ausschlusszonen_wgs84[key] = zone.to_crs(epsg=4326)
    
    # ✅ JETZT ERST What-If UI (constraints ist jetzt verfügbar!)
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 What-If-Analyse")
    st.sidebar.caption("Entsperre Zonen teilweise für mehr Pflanzfläche")
    
    # Nur Zonen anbieten, die nicht der Baum-Puffer sind
    available_zones = [k for k in constraints.keys() if k != '🌳_Baum_Puffer']
    
    unlock_zones = st.sidebar.multiselect(
        "Zonen entsperren:",
        options=available_zones,
        default=[],
        help="Diese Zonen dürfen teilweise für Baumpflanzungen genutzt werden"
    )
    
    unlock_percentage = st.sidebar.slider(
        "Nutzbare Fläche der Zone (%)", 
        min_value=0, 
        max_value=100, 
        value=10,
        step=5,
        help="Wieviel Prozent der entsperrten Zonen dürfen genutzt werden?",
        disabled=len(unlock_zones) == 0
    ) if unlock_zones else 0
    
    if unlock_zones:
        st.sidebar.info(f"💡 {unlock_percentage}% von {len(unlock_zones)} Zone(n) entsperrt")
    
    # Statistiken
    st.sidebar.markdown("---")
    st.sidebar.header("📊 Statistiken")
    st.sidebar.metric("Anzahl Bäume", stats['anzahl_bäume'])
    
    # Zeige geladene Constraint-Layer
    st.sidebar.subheader("🚫 Ausschlusszonen")
    loaded_count = sum(1 for v in constraints.values() if v is not None)
    st.sidebar.metric("Geladene Dateien", loaded_count)
    
    if constraints:
        for key, layer in constraints.items():
            status = "✓" if layer is not None else "✗"
            count = f"({len(layer)} Features)" if layer is not None else ""
            is_unlocked = "🔓" if key in unlock_zones else ""
            st.sidebar.text(f"{status} {key} {count} {is_unlocked}")
    else:
        st.sidebar.warning("Keine Constraints im 'constraints/' Ordner gefunden")
    
    if 'top_arten' in stats:
        st.sidebar.subheader("🌲 Top 5 Baumarten")
        st.sidebar.write(stats['top_arten'])
    
    # Potenzielle Pflanzstandorte finden
    show_planting_locations = st.sidebar.checkbox("🌱 Zeige Pflanzstandorte", value=True)
    
    planting_locations_wgs84 = None
    if show_planting_locations:
        grid_spacing = st.sidebar.slider(
            "Rasterabstand (m)", 
            min_value=10, 
            max_value=50, 
            value=20,
            help="Kleinerer Wert = mehr Punkte (langsamer)"
        )
        
        with st.spinner("Berechne Pflanzstandorte..."):
            from analysis import find_planting_locations, apply_zone_relaxation
            
            # ✅ What-If: Zonen entsperren
            modified_zones = apply_zone_relaxation(
                ausschlusszonen_dict,
                unlock_zones,
                unlock_percentage
            )
            
            planting_locations = find_planting_locations(
                modified_zones,
                stats['bounds'],
                grid_spacing
            )
            
            if planting_locations is not None:
                planting_locations_wgs84 = planting_locations.to_crs(epsg=4326)
                
                # ✅ Zeige Impact der What-If-Analyse
                if unlock_zones and unlock_percentage > 0:
                    original_locations = find_planting_locations(
                        ausschlusszonen_dict,
                        stats['bounds'],
                        grid_spacing
                    )
                    if original_locations is not None:
                        delta = len(planting_locations) - len(original_locations)
                        if delta > 0:
                            st.sidebar.success(f"🎯 What-If: +{delta} zusätzliche Standorte!")
                            co2_gain = delta * 22  # kg CO2 pro Baum/Jahr
                            st.sidebar.metric("🌍 Zusätzl. CO2/Jahr", f"{co2_gain:,} kg")
                        else:
                            st.sidebar.warning("⚠️ Keine zusätzlichen Standorte gefunden")
                
                st.sidebar.success(f"✓ {len(planting_locations_wgs84)} Standorte gefunden")
    
    # Karte
    st.subheader("🗺️ Interaktive Karte")
    
    # Zentrum berechnen
    center_lat = bäume_wgs84.geometry.y.mean()
    center_lon = bäume_wgs84.geometry.x.mean()
    
    # Folium Map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    # Bäume in FeatureGroup (standardmäßig SICHTBAR)
    baum_group = folium.FeatureGroup(
        name="🌳 Baumkataster",
        overlay=True,
        control=True,
        show=True
    ).add_to(m)
    
    sample_size = min(500, len(bäume_wgs84))
    baum_sample = bäume_wgs84.sample(sample_size, random_state=42)
    
    for idx, row in baum_sample.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=2,
            color='green',
            fill=True,
            fillOpacity=0.6,
            weight=0
        ).add_to(baum_group)
    
    # Pflanzstandorte (standardmäßig VERSTECKT)
    if planting_locations_wgs84 is not None:
        from folium.plugins import MarkerCluster
        
        marker_cluster = MarkerCluster(
            name="🌱 Potenzielle Pflanzstandorte",
            overlay=True,
            control=True,
            show=False
        ).add_to(m)
        
        # Sample für Performance (max 2000 Punkte)
        sample_size = min(2000, len(planting_locations_wgs84))
        location_sample = planting_locations_wgs84.sample(sample_size, random_state=42) if len(planting_locations_wgs84) > sample_size else planting_locations_wgs84
        
        for idx, row in location_sample.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=4,
                color='blue',
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.7,
                weight=1,
                popup="Möglicher Pflanzstandort"
            ).add_to(marker_cluster)
    
    # Ausschlusszonen (standardmäßig VERSTECKT)
    for idx, (key, zone_wgs84) in enumerate(ausschlusszonen_wgs84.items()):
        if zone_wgs84 is not None:
            # Farben
            if '🌳' in key or 'Baum' in key:
                color = 'green'
                fill_color = 'lightgreen'
            else:
                color = get_random_color(key)
                fill_color = color
            
            # Highlight entsperrte Zonen
            is_unlocked = key in unlock_zones
            zone_name = f"🔓 {key}" if is_unlocked else key
            
            try:
                clean_geojson = gdf_to_clean_geojson(zone_wgs84)
                
                zone_group = folium.FeatureGroup(
                    name=zone_name,
                    overlay=True,
                    control=True,
                    show=False
                ).add_to(m)
                
                folium.GeoJson(
                    clean_geojson,
                    style_function=lambda x, c=color, fc=fill_color, u=is_unlocked: {
                        'fillColor': fc,
                        'color': c,
                        'weight': 3 if u else 2,
                        'fillOpacity': 0.3 if u else 0.4,
                        'dashArray': '5, 5' if u else None
                    }
                ).add_to(zone_group)
            except Exception as e:
                st.warning(f"⚠ Konnte {key} nicht zur Karte hinzufügen: {e}")
    
    folium.LayerControl().add_to(m)
    
    # Map rendern
    st_folium(m, width=1200, height=600, returned_objects=[])
    
    # Info
    st.info("""
    **Legende:**
    - 🔵 **Blaue Punkte** = Mögliche Pflanzstandorte (außerhalb aller Ausschlusszonen!)
    - 🟢 **Grüne Punkte** = Bestehende Bäume (Stichprobe)
    - 🟢 **Hellgrün** = Baum-Puffer (Mindestabstand)
    - 🔴 **Rote/Orange Bereiche** = Ausschlusszonen
    - 🔓 **Gestrichelte Bereiche** = Entsperrte Zonen (What-If)
    
    💡 **Tipp:** 
    - Nutze die Layer-Steuerung oben rechts zum Ein-/Ausblenden
    - Klicke auf Punkt-Cluster zum Reinzoomen
    - What-If: Entsperre Zonen wie Parkplätze/Rasen für mehr Pflanzfläche!
    """)
    
    # Zusammenfassung
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌳 Bäume", stats['anzahl_bäume'])
    with col2:
        zones_count = len([z for z in ausschlusszonen_wgs84.values() if z is not None])
        st.metric("🚫 Ausschlusszonen", zones_count)
    with col3:
        st.metric("📏 Baum-Abstand", f"{abstand_bäume} m")
    with col4:
        if planting_locations_wgs84 is not None:
            st.metric("🌱 Pflanzstandorte", len(planting_locations_wgs84))
        else:
            st.metric("🌱 Pflanzstandorte", "—")