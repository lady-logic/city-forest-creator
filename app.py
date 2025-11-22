import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from analysis import load_data, load_all_constraints, find_suitable_locations, calculate_stats
import random
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from io import BytesIO

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
        padding: 1rem 2rem;  
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;  
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .custom-header h1 {
    color: white !important;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    font-size: 2.5rem !important; 
}

    .custom-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;  
        margin-top: 0.3rem;  
        margin-bottom: 0;
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

@st.cache_data
def compute_heatmap(_bäume, bounds, grid_size):
    """Cached Heatmap-Berechnung"""
    from analysis import calculate_tree_density_heatmap
    return calculate_tree_density_heatmap(_bäume, bounds, grid_size)

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

with st.sidebar.expander("📥 Constraints hochladen", expanded=False):
    st.caption("Lade neue Ausschlusszonen hoch")
    
    uploaded_file = st.file_uploader(
        "Shapefile als ZIP",
        type=['zip'],
        help="ZIP mit .shp, .dbf, .shx, .prj",
        key="shapefile_upload"
    )
    
    if uploaded_file is not None:
        import zipfile
        import tempfile
        import shutil
        from pathlib import Path
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # ZIP entpacken
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Finde .shp Dateien
            shp_files = list(Path(temp_dir).glob("**/*.shp"))
            
            if shp_files:
                st.info(f"📂 Gefunden: {len(shp_files)} Shapefile(s)")
                
                # Zeige Dateinamen
                for shp in shp_files:
                    st.text(f"• {shp.name}")
                
                # Button zum Import
                if st.button("✅ Importieren", key="import_btn"):
                    # Kopiere alle Dateien
                    os.makedirs("constraints", exist_ok=True)
                    
                    for shp_file in shp_files:
                        base_name = shp_file.stem
                        source_dir = shp_file.parent
                        
                        for ext in ['.shp', '.dbf', '.shx', '.prj', '.cpg', '.sbn', '.sbx']:
                            source_file = source_dir / f"{base_name}{ext}"
                            if source_file.exists():
                                dest_file = Path("constraints") / source_file.name
                                shutil.copy2(source_file, dest_file)
                    
                    st.success("✅ Import erfolgreich!")
                    st.info("🔄 Lade Seite neu (F5) um Daten zu aktualisieren")
                    
                    # Automatisch neu laden nach 2 Sekunden
                    import time
                    time.sleep(2)
                    st.cache_data.clear()
                    st.rerun()
            else:
                st.error("❌ Keine .shp Dateien gefunden!")
                st.caption("ZIP sollte enthalten: name.shp, name.dbf, name.shx, etc.")

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
    
    # ✅ DASHBOARD OBEN in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Live-Dashboard")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("🌳 Bäume", f"{stats['anzahl_bäume']:,}")
    with col2:
        zones_count = len([z for z in ausschlusszonen_dict.values() if z is not None])
        st.metric("🚫 Zonen", zones_count)
    
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
    
    
    
    # Potenzielle Pflanzstandorte finden
    st.sidebar.markdown("---")
    show_planting_locations = st.sidebar.checkbox("🌱 Zeige Pflanzstandorte", value=True)
    
    planting_locations_wgs84 = None
    original_locations_wgs84 = None
    
    if show_planting_locations:
        grid_spacing = st.sidebar.slider(
            "Rasterabstand (m)", 
            min_value=15,  
            max_value=50, 
            value=25,  
            help="Kleinerer Wert = mehr Punkte (langsamer). Empfohlen: 20-30m"
        )
        
        with st.spinner("Berechne Pflanzstandorte..."):
            # Berechne aktuelle Standorte (mit What-If)
            planting_locations = compute_planting_locations(
                ausschlusszonen_dict,
                stats['bounds'],
                grid_spacing,
                tuple(unlock_zones),
                unlock_percentage
            )
            
            if planting_locations is not None:
                planting_locations_wgs84 = planting_locations.to_crs(epsg=4326)
                
                # ✅ WHAT-IF IMPACT - PROMINENT
                if unlock_zones and unlock_percentage > 0:
                    original_locations = compute_planting_locations(
                        ausschlusszonen_dict,
                        stats['bounds'],
                        grid_spacing,
                        tuple([]),
                        0
                    )
                    
                    if original_locations is not None:
                        original_locations_wgs84 = original_locations.to_crs(epsg=4326)
                        delta = len(planting_locations) - len(original_locations)
                        
                        # ✅ PROMINENT Impact Box
                        st.sidebar.markdown("---")
                        st.sidebar.markdown("### 🎯 What-If Impact")
                        
                        if delta > 0:
                            col1, col2 = st.sidebar.columns(2)
                            with col1:
                                st.metric(
                                    "Neue Standorte", 
                                    f"{len(planting_locations):,}",
                                    delta=f"+{delta}",
                                    delta_color="normal"
                                )
                            with col2:
                                co2_gain = delta * 22
                                st.metric(
                                    "CO₂/Jahr", 
                                    f"{co2_gain/1000:.1f} t",
                                    delta=f"+{co2_gain:,} kg",
                                    delta_color="normal"
                                )
                            
                            # Trade-off Visualisierung
                            st.sidebar.progress(unlock_percentage / 100)
                            st.sidebar.caption(f"💡 {unlock_percentage}% der Zone(n) genutzt = **+{delta} Bäume**")
                            
                        elif delta < 0:
                            st.sidebar.error(f"⚠️ {abs(delta)} Standorte weniger")
                        else:
                            st.sidebar.info("ℹ️ Keine Änderung")
                else:
                    st.sidebar.success(f"✓ {len(planting_locations_wgs84):,} Standorte gefunden")
    
    # Prioritäts-Heatmap Optionen
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔥 Prioritäts-Heatmap")
    show_heatmap = st.sidebar.checkbox("Zeige Hitze-Heatmap", value=False)

    heatmap_grid_size = 150
    if show_heatmap:
        heatmap_grid_size = st.sidebar.slider(
            "Heatmap Rasterweite (m)",
            min_value=50,
            max_value=300,
            value=150,
            step=50,
            help="Größere Zellen = schneller, aber gröber"
        )
    
    # Hitze-Heatmap berechnen
    heatmap_wgs84 = None
    if show_heatmap:
        with st.spinner("Berechne Hitze-Heatmap..."):
            heatmap = compute_heatmap(bäume, stats['bounds'], heatmap_grid_size)
            
            if heatmap is not None:
                heatmap_wgs84 = heatmap.to_crs(epsg=4326)
                
                top_hotspots = heatmap.nlargest(5, 'heat_score')
                st.sidebar.markdown("---")
                st.sidebar.markdown("#### 🔥 Top 5 Hitze-Hotspots")
                for idx, row in top_hotspots.iterrows():
                    st.sidebar.text(f"Score: {row['heat_score']:.2f} | {row['tree_count']} Bäume")

    # Export & Berichte
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export & Berichte")
    
    # ===== GeoJSON/CSV Export =====
    if planting_locations_wgs84 is not None and len(planting_locations_wgs84) > 0:
        with st.sidebar.expander("💾 Standorte exportieren", expanded=False):
            st.caption(f"Exportiere {len(planting_locations_wgs84):,} Pflanzstandorte")
            
            # GeoJSON Export
            geojson_str = planting_locations_wgs84.to_json()
            
            st.download_button(
                label="📍 Download GeoJSON",
                data=geojson_str,
                file_name=f"heilbronn_pflanzstandorte_{len(planting_locations_wgs84)}.geojson",
                mime="application/json",
                help="Für QGIS, ArcGIS, Google Maps",
                key="download_geojson"
            )
            
            # CSV Export
            import pandas as pd
            csv_data = pd.DataFrame({
                'id': range(1, len(planting_locations_wgs84) + 1),
                'latitude': planting_locations_wgs84.geometry.y,
                'longitude': planting_locations_wgs84.geometry.x,
                'whatif_aktiv': 'Ja' if (unlock_zones and unlock_percentage > 0) else 'Nein',
                'entsperrte_zonen': ', '.join(unlock_zones) if unlock_zones else 'Keine'
            })
            
            st.download_button(
                label="📊 Download CSV",
                data=csv_data.to_csv(index=False),
                file_name=f"heilbronn_standorte_{len(planting_locations_wgs84)}.csv",
                mime="text/csv",
                help="Für Excel, Google Sheets",
                key="download_csv"
            )
            
            st.success(f"✅ {len(planting_locations_wgs84):,} Standorte bereit zum Export")
    
    # ===== Email-Template =====
    with st.sidebar.expander("✉️ Email-Vorlage", expanded=False):
        st.caption("Erstelle Email für Stadtplanung")
        
        # Email-Text generieren
        standorte_count = len(planting_locations_wgs84) if planting_locations_wgs84 is not None else 0
        co2_gesamt = standorte_count * 22
        
        # Delta für What-If
        delta_text = ""
        if unlock_zones and unlock_percentage > 0 and original_locations_wgs84 is not None:
            delta = len(planting_locations_wgs84) - len(original_locations_wgs84)
            delta_co2 = delta * 22
            delta_text = f"""
WHAT-IF SZENARIO:
- Durch Nutzung von {unlock_percentage}% der Zone(n): {', '.join(unlock_zones)}
- Zusätzliche Bäume: +{delta}
- Zusätzliche CO₂-Bindung: +{delta_co2:,} kg/Jahr
- Trade-off: {int(delta * 0.5)} Parkplätze für {delta} Bäume
"""
        
        email_betreff = "Baumpflanzung Heilbronn - Analyseergebnisse"
        
        email_text = f"""Betreff: {email_betreff}

Sehr geehrte Damen und Herren,

anbei die Ergebnisse unserer Standortanalyse für strategische Baumpflanzungen in Heilbronn.

═══════════════════════════════════════
KERNZAHLEN
═══════════════════════════════════════
- Analysierte Bäume: {stats['anzahl_bäume']:,}
- Neue Pflanzstandorte identifiziert: {standorte_count:,}
- CO₂-Bindung/Jahr: {co2_gesamt:,} kg (~{co2_gesamt/1000:.1f} Tonnen)
- Ausschlusszonen berücksichtigt: {len([z for z in ausschlusszonen_dict.values() if z is not None])}
{delta_text}
═══════════════════════════════════════
PRIORITÄTS-HOTSPOTS
═══════════════════════════════════════
Die Heatmap-Analyse zeigt die dringendsten Bereiche für Baumpflanzungen auf.
Fokus auf Stadtteile mit höchstem Hitze-Score empfohlen.

═══════════════════════════════════════
NÄCHSTE SCHRITTE
═══════════════════════════════════════
1. Review der identifizierten Standorte
2. Priorisierung nach Hitze-Hotspots
3. Bürgerdialog bei Trade-off-Szenarien
4. Pilot-Projekt starten (50-100 Bäume)

═══════════════════════════════════════
DATENEXPORT
═══════════════════════════════════════
Interaktive Karte: http://localhost:8501
Export: GeoJSON/CSV verfügbar über die App

Mit freundlichen Grüßen
City Forest Creator Team
Future City Hackathon 2025
"""
        
        
        # Mailto-Link
        import urllib.parse
        mailto_link = f"mailto:stadtplanung@heilbronn.de?subject={urllib.parse.quote(email_betreff)}&body={urllib.parse.quote(email_text)}"
        
        st.markdown(f"[📧 Email in Standard-Programm öffnen]({mailto_link})")
        
        # Copy-Button Alternative
        st.caption("💡 Tipp: Text markieren und Strg+C zum Kopieren")
    
    # Parkplatz vs. Baum Trade-off Visualisierung
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌡️ Parkplatz vs. Baum")

    if unlock_zones:
        st.sidebar.markdown("""
        **Ein Parkplatz (12m²) vs. Ein Baum:**
        
        🚗 **Parkplatz:**
        - Speichert Hitze: +60°C Oberfläche
        - Versiegelt Boden: 12m² Regenwasser-Verlust
        - Luftqualität: 0 kg CO₂ gebunden
        
        🌳 **Baum:**
        - Kühlt Umgebung: -2-3°C in 50m Radius
        - Schattenfläche: ~60m² (5x Parkplatz!)
        - Filtert Luft: 22 kg CO₂/Jahr + Feinstaub
        - Immobilienwert: +3-8% in Baumalleen
        - Lebensqualität: ❤️
        """)
        
        # Rechner
        parkplaetze = int(unlock_percentage / 100 * 500)  # Annahme: 500 Parkplätze in Zone
        baeume = delta
        
        st.sidebar.metric("Trade-off", f"{parkplaetze} Parkplätze = {baeume} Bäume")
        st.sidebar.caption(f"Das sind {int(baeume/parkplaetze*100)}% mehr Schattenfläche!")
   
   
    # Karte
    
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
    
    # Adaptives Sampling
    if len(bäume_wgs84) > 10000:
        sample_size = 200
    elif len(bäume_wgs84) > 5000:
        sample_size = 300
    else:
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
    
    # ✅ ORIGINAL-Standorte (wenn What-If aktiv) - in GRAU
    if original_locations_wgs84 is not None:
        from folium.plugins import MarkerCluster
        
        original_cluster = MarkerCluster(
            name="🔵 Basis-Standorte (ohne What-If)",
            overlay=True,
            control=True,
            show=False
        ).add_to(m)
        
        sample_size = min(500, len(original_locations_wgs84))
        original_sample = original_locations_wgs84.sample(sample_size, random_state=42) if len(original_locations_wgs84) > sample_size else original_locations_wgs84
        
        for idx, row in original_sample.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=3,
                color='gray',
                fill=True,
                fillColor='lightgray',
                fillOpacity=0.5,
                weight=1,
                popup="Basis-Standort (ohne What-If)"
            ).add_to(original_cluster)
    
    # ✅ NEUE Pflanzstandorte (mit What-If) - FARBIG
    if planting_locations_wgs84 is not None:
        from folium.plugins import MarkerCluster
        
        # Farbe abhängig von What-If
        is_whatif = unlock_zones and unlock_percentage > 0
        marker_color = 'green' if is_whatif else 'blue'
        fill_color = 'lightgreen' if is_whatif else 'lightblue'
        layer_name = "🌱 Pflanzstandorte (mit What-If!)" if is_whatif else "🌱 Potenzielle Pflanzstandorte"
        
        marker_cluster = MarkerCluster(
            name=layer_name,
            overlay=True,
            control=True,
            show=True
        ).add_to(m)
        
        sample_size = min(1000, len(planting_locations_wgs84))
        location_sample = planting_locations_wgs84.sample(sample_size, random_state=42) if len(planting_locations_wgs84) > sample_size else planting_locations_wgs84
        
        for idx, row in location_sample.iterrows():
            folium.CircleMarker(
                location=[row.geometry.y, row.geometry.x],
                radius=4,
                color=marker_color,
                fill=True,
                fillColor=fill_color,
                fillOpacity=0.8,
                weight=1,
                popup="Pflanzstandort" + (" (mit What-If entsperrt!)" if is_whatif else "")
            ).add_to(marker_cluster)
    
    # ✅ Hitze-Heatmap (nur Hotspots > 0.3)
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
        
        # Nur Hotspots rendern
        hot_cells = heatmap_wgs84[heatmap_wgs84['heat_score'] > 0.3]
        
        if len(hot_cells) > 200:
            hot_cells = hot_cells.nlargest(200, 'heat_score')
        
        for idx, row in hot_cells.iterrows():
            color = colormap(row['heat_score'])
            
            folium.GeoJson(
                row['geometry'].__geo_interface__,
                style_function=lambda x, c=color: {
                    'fillColor': c,
                    'color': c,
                    'weight': 0.5,
                    'fillOpacity': 0.6
                },
                tooltip=f"Hitze: {row['heat_score']:.2f} | Bäume: {row['tree_count']}"
            ).add_to(heatmap_group)
        
        colormap.add_to(m)
        
        st.caption(f"🔥 Zeige {len(hot_cells)} von {len(heatmap_wgs84)} Heatmap-Zellen (nur Hotspots > 0.3)")
    
    # ✅ Ausschlusszonen mit STÄRKEREM Highlight
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
                        'weight': 4 if u else 2,
                        'fillOpacity': 0.2 if u else 0.4,
                        'dashArray': '10, 5' if u else None
                    }
                ).add_to(zone_group)
            except Exception as e:
                st.warning(f"⚠ Konnte {key} nicht zur Karte hinzufügen: {e}")
    
    folium.LayerControl().add_to(m)
    
    # Berechne Bounds aller Bäume
    bounds = [
        [bäume_wgs84.geometry.y.min(), bäume_wgs84.geometry.x.min()],
        [bäume_wgs84.geometry.y.max(), bäume_wgs84.geometry.x.max()]
    ]
    m.fit_bounds(bounds, padding=[50, 50])  # 50px Padding
    
    st_folium(m, width=1400, height=800, returned_objects=[])
    
    # Info
    st.info("""
    **Legende:**
    - 🟢 **Grüne Punkte (Pflanzstandorte)** = Mit What-If entsperrt! (Neue Flächen)
    - 🔵 **Blaue Punkte** = Basis-Pflanzstandorte (ohne What-If)
    - ⚪ **Graue Punkte** = Original-Standorte zum Vergleich (ausblendbar)
    - 🌳 **Dunkelgrüne Punkte** = Bestehende Bäume (Stichprobe)
    - 🟢 **Hellgrün** = Baum-Puffer (Mindestabstand)
    - 🔴 **Rote/Orange Bereiche** = Ausschlusszonen
    - 🔓 **Dick gestrichelt** = Entsperrte Zonen (What-If aktiv!)
    - 🔥 **Heatmap-Farben** = Blau (viele Bäume/kühl) → Rot (keine Bäume/heiß)
    
    💡 **Tipp:** 
    - Nutze die Layer-Steuerung oben rechts zum Ein-/Ausblenden
    - Aktiviere "Basis-Standorte" für direkten Vergleich
    - What-If-Impact siehst du SOFORT in der Sidebar oben!
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
            # Zeige Delta wenn What-If aktiv
            if original_locations_wgs84 is not None:
                delta = len(planting_locations_wgs84) - len(original_locations_wgs84)
                st.metric(
                    "🌱 Pflanzstandorte", 
                    f"{len(planting_locations_wgs84):,}",
                    delta=f"+{delta}" if delta > 0 else None
                )
            else:
                st.metric("🌱 Pflanzstandorte", f"{len(planting_locations_wgs84):,}")
        else:
            st.metric("🌱 Pflanzstandorte", "—")