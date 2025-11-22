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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ✨ CUSTOM CSS STYLING
def load_custom_css():
    st.markdown("""
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Haupt-Container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8f5e9 100%);
    }
    
    /* Titel-Styling */
    h1 {
        color: #2e7d32;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 3rem !important;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #388e3c;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        border-left: 5px solid #4caf50;
        padding-left: 15px;
        margin-top: 2rem;
    }
    
    h3 {
        color: #43a047;
        font-family: 'Poppins', sans-serif;
        font-weight: 500;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1b5e20 0%, #2e7d32 100%);
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Sidebar Divider */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2);
        margin: 1.5rem 0;
    }
    
    /* Sidebar Caption */
    [data-testid="stSidebar"] .stCaption {
        color: rgba(255,255,255,0.7) !important;
        font-size: 0.85rem;
    }
    
    /* Metriken */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #2e7d32;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #666;
        font-weight: 500;
    }
    
    /* Sidebar Metriken */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.9) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Info-Boxen */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid #4caf50;
    }
    
    /* Cards für Statistiken */
    div[data-testid="column"] {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    div[data-testid="column"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background: #4caf50;
    }
    
    /* Success/Warning/Error Messages */
    .stSuccess {
        background-color: #e8f5e9;
        color: #2e7d32;
        border-left: 5px solid #4caf50;
        border-radius: 8px;
    }
    
    .stWarning {
        background-color: #fff3e0;
        color: #e65100;
        border-left: 5px solid #ff9800;
        border-radius: 8px;
    }
    
    .stInfo {
        background-color: #e3f2fd;
        color: #1565c0;
        border-left: 5px solid #2196f3;
        border-radius: 8px;
    }
    
    /* Custom Header mit Gradient */
    .custom-header {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .custom-header h1 {
        color: white !important;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .custom-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Feature Cards */
    .feature-card {
        text-align: center;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .feature-title {
        color: #2e7d32;
        margin: 1rem 0 0.5rem 0;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .feature-desc {
        color: #666;
        font-size: 0.95rem;
    }
    
    /* Animationen */
    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(20px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4caf50;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #388e3c;
    }
    </style>
    """, unsafe_allow_html=True)

load_custom_css()

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

@st.cache_data
def get_exclusion_zones(_bäume, _constraints, abstand_bäume, buffer_linien):
    """Cached Berechnung der Ausschlusszonen"""
    return find_suitable_locations(_bäume, _constraints, abstand_bäume, buffer_linien)

@st.cache_data
def compute_planting_locations(_zones_dict, bounds, grid_spacing, unlock_zones_tuple, unlock_percentage):
    """Cached Berechnung der Pflanzstandorte"""
    from analysis import find_planting_locations, apply_zone_relaxation
    
    unlock_zones = list(unlock_zones_tuple)
    modified_zones = apply_zone_relaxation(_zones_dict, unlock_zones, unlock_percentage)
    
    return find_planting_locations(modified_zones, bounds, grid_spacing)

# ✨ CUSTOM HEADER
st.markdown("""
<div class="custom-header">
    <h1>🌳 City Forest Creator</h1>
    <p>Strategische Baumpflanzung für eine kühlere, grünere Stadt Heilbronn</p>
    <p style="font-size: 0.9rem; opacity: 0.8;">
        ⚡ Future City Hackathon 2025 | Challenge: "More trees in the city"
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Basis-Einstellungen
st.sidebar.markdown("### ⚙️ Einstellungen")
st.sidebar.markdown("---")

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

# Daten laden
with st.spinner("Lade Geodaten..."):
    bäume, bäume_wgs84, constraints, stats = load_all_data()

if bäume is not None:
    # Ausschlusszonen berechnen
    with st.spinner(f"Berechne Ausschlusszonen..."):
        ausschlusszonen_dict = get_exclusion_zones(bäume, constraints, abstand_bäume, buffer_linien)
        
        ausschlusszonen_wgs84 = {}
        for key, zone in ausschlusszonen_dict.items():
            if zone is not None:
                ausschlusszonen_wgs84[key] = zone.to_crs(epsg=4326)
    
    # What-If UI
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 What-If-Analyse")
    st.sidebar.caption("Entsperre Zonen teilweise für mehr Pflanzfläche")
    
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
    
    # Prioritäts-Heatmap Optionen
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔥 Prioritäts-Heatmap")
    show_heatmap = st.sidebar.checkbox("Zeige Hitze-Heatmap", value=False)

    if show_heatmap:
        heatmap_grid_size = st.sidebar.slider(
            "Heatmap Rasterweite (m)",
            min_value=50,
            max_value=300,
            value=150,
            step=50,
            help="Größere Zellen = schneller, aber gröber"
        )
    
    # Statistiken
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Statistiken")
    st.sidebar.metric("Anzahl Bäume", f"{stats['anzahl_bäume']:,}")
    
    # Zeige geladene Constraint-Layer
    st.sidebar.markdown("#### 🚫 Ausschlusszonen")
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
        st.sidebar.markdown("#### 🌲 Top 5 Baumarten")
        st.sidebar.write(stats['top_arten'])
    
    # Potenzielle Pflanzstandorte finden
    show_planting_locations = st.sidebar.checkbox("🌱 Zeige Pflanzstandorte", value=True)
    
    planting_locations_wgs84 = None
    if show_planting_locations:
        grid_spacing = st.sidebar.slider(
            "Rasterabstand (m)", 
            min_value=15,  
            max_value=50, 
            value=25,  
            help="Kleinerer Wert = mehr Punkte (langsamer). Empfohlen: 20-30m"
        )
        
        with st.spinner("Berechne Pflanzstandorte..."):
            planting_locations = compute_planting_locations(
                ausschlusszonen_dict,
                stats['bounds'],
                grid_spacing,
                tuple(unlock_zones),
                unlock_percentage
            )
            
            if planting_locations is not None:
                planting_locations_wgs84 = planting_locations.to_crs(epsg=4326)
                
                if unlock_zones and unlock_percentage > 0:
                    original_locations = compute_planting_locations(
                        ausschlusszonen_dict,
                        stats['bounds'],
                        grid_spacing,
                        tuple([]),
                        0
                    )
                    
                    if original_locations is not None:
                        delta = len(planting_locations) - len(original_locations)
                        if delta > 0:
                            st.sidebar.success(f"🎯 What-If: +{delta} zusätzliche Standorte!")
                            co2_gain = delta * 22
                            st.sidebar.metric("🌍 Zusätzl. CO2/Jahr", f"{co2_gain:,} kg")
                        elif delta < 0:
                            st.sidebar.warning(f"⚠️ {abs(delta)} Standorte weniger")
                        else:
                            st.sidebar.info("ℹ️ Keine Änderung")
                
                st.sidebar.success(f"✓ {len(planting_locations_wgs84):,} Standorte gefunden")
    
    # Hitze-Heatmap berechnen
    heatmap_wgs84 = None
    if show_heatmap:
        with st.spinner("Berechne Hitze-Heatmap..."):
            from analysis import calculate_tree_density_heatmap
            
            heatmap = calculate_tree_density_heatmap(
                bäume,
                stats['bounds'],
                heatmap_grid_size
            )
            
            if heatmap is not None:
                heatmap_wgs84 = heatmap.to_crs(epsg=4326)
                
                top_hotspots = heatmap.nlargest(5, 'heat_score')
                st.sidebar.markdown("#### 🔥 Top 5 Hitze-Hotspots")
                for idx, row in top_hotspots.iterrows():
                    st.sidebar.text(f"Score: {row['heat_score']:.2f} | {row['tree_count']} Bäume")
    
    # Karte
    st.markdown("## 🗺️ Interaktive Karte")
    
    center_lat = bäume_wgs84.geometry.y.mean()
    center_lon = bäume_wgs84.geometry.x.mean()
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    # Bäume
    baum_group = folium.FeatureGroup(
        name="🌳 Baumkataster",
        overlay=True,
        control=True,
        show=True
    ).add_to(m)
    
   # ⚡ Adaptives Sampling basierend auf Zoom-Level
    if len(bäume_wgs84) > 10000:
        sample_size = 200  # Große Stadt: weniger Marker
    elif len(bäume_wgs84) > 5000:
        sample_size = 300
    else:
        sample_size = min(500, len(bäume_wgs84))

    baum_sample = bäume_wgs84.sample(sample_size, random_state=42)
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
    
    # Pflanzstandorte
    if planting_locations_wgs84 is not None:
        from folium.plugins import MarkerCluster
        
        marker_cluster = MarkerCluster(
            name="🌱 Potenzielle Pflanzstandorte",
            overlay=True,
            control=True,
            show=False
        ).add_to(m)
        
        sample_size = min(1000, len(planting_locations_wgs84))
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
    
    # Hitze-Heatmap
    if heatmap_wgs84 is not None:
        import branca.colormap as cm
        
        colormap = cm.LinearColormap(
            colors=['blue', 'cyan', 'yellow', 'orange', 'red'],
            vmin=0,
            vmax=1,
            caption='Hitze-Score (0=kühl, 1=heiß)'
        )
        
        heatmap_group = folium.FeatureGroup(
            name="🔥 Hitze-Heatmap",
            overlay=True,
            control=True,
            show=True
        ).add_to(m)
        
        for idx, row in heatmap_wgs84.iterrows():
            color = colormap(row['heat_score'])
            
            folium.GeoJson(
                row['geometry'].__geo_interface__,
                style_function=lambda x, c=color: {
                    'fillColor': c,
                    'color': c,
                    'weight': 0.5,
                    'fillOpacity': 0.5
                },
                tooltip=f"Hitze: {row['heat_score']:.2f} | Bäume: {row['tree_count']}"
            ).add_to(heatmap_group)
        
        colormap.add_to(m)
    
    # Ausschlusszonen
    for idx, (key, zone_wgs84) in enumerate(ausschlusszonen_wgs84.items()):
        if zone_wgs84 is not None:
            if '🌳' in key or 'Baum' in key:
                color = 'green'
                fill_color = 'lightgreen'
            else:
                color = get_random_color(key)
                fill_color = color
            
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
    
    st_folium(m, width=1200, height=600, returned_objects=[])
    
    # Info
    st.info("""
    **Legende:**
    - 🔵 **Blaue Punkte** = Mögliche Pflanzstandorte (außerhalb aller Ausschlusszonen!)
    - 🟢 **Grüne Punkte** = Bestehende Bäume (Stichprobe)
    - 🟢 **Hellgrün** = Baum-Puffer (Mindestabstand)
    - 🔴 **Rote/Orange Bereiche** = Ausschlusszonen
    - 🔓 **Gestrichelte Bereiche** = Entsperrte Zonen (What-If)
    - 🔥 **Heatmap-Farben** = Blau (viele Bäume/kühl) → Rot (keine Bäume/heiß)
    
    💡 **Tipp:** 
    - Nutze die Layer-Steuerung oben rechts zum Ein-/Ausblenden
    - Klicke auf Punkt-Cluster zum Reinzoomen
    - What-If: Entsperre Zonen wie Parkplätze/Rasen für mehr Pflanzfläche!
    """)
    
    # Zusammenfassung
    st.markdown("## 📊 Zusammenfassung")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🌳 Bäume", f"{stats['anzahl_bäume']:,}")
    with col2:
        zones_count = len([z for z in ausschlusszonen_wgs84.values() if z is not None])
        st.metric("🚫 Ausschlusszonen", zones_count)
    with col3:
        st.metric("📏 Baum-Abstand", f"{abstand_bäume} m")
    with col4:
        if planting_locations_wgs84 is not None:
            st.metric("🌱 Pflanzstandorte", f"{len(planting_locations_wgs84):,}")
        else:
            st.metric("🌱 Pflanzstandorte", "—")