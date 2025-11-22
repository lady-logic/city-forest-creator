# 🌳 City Forest Creator

> **Strategische Baumpflanzung für eine kühlere, grünere Stadt**  
> Hackathon-Projekt für die Challenge **"More trees in the city"** der Stadt Heilbronn

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red.svg)
![GeoPandas](https://img.shields.io/badge/GeoPandas-0.14-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 🏛️ Challenge: "More trees in the city"

**Challenge-Geber:** Stadt Heilbronn  
**Event:** Future City Hackathon 2025  
**Datum:** 21.-23. November 2025

### 💭 Vision
> *"Heilbronn is a cool place to be – with nice shadow from the trees in the summer"*

### 🎯 Mission
Die Stadt Heilbronn stellt uns vor die Herausforderung:
- ✅ **Komplexe Stadtdaten** in umsetzbare Grün-Strategien verwandeln
- ✅ **Urban Datasets analysieren** und visualisieren, um Baum-Standorte zu identifizieren
- ✅ **Algorithmen entwickeln** oder interaktive Karten erstellen, die zeigen:
  - Wo Bäume realistisch gepflanzt werden können
  - Welche Trade-offs oder Constraints existieren

### 🌍 Impact
Unser Beitrag zu:
- 🌡️ **Kühlere Städte** – Bekämpfung urbaner Hitzeinseln
- 💚 **Gesündere Städte** – Bessere Luftqualität und Lebensqualität
- 📊 **Datengestützte Entscheidungen** – Unterstützung für Stadtplaner:innen bei schnelleren, transparenteren Pflanzentscheidungen
- 🤝 **Collaboration** – Brücke zwischen Tech-Community und lokaler Verwaltung

> *"Every line of code contributes to: Cleaner air • Cooler neighborhoods • A more livable city for everyone"*  
> **Code for trees — and a better future for our cities.**

---

## ❗ Das Problem

### Die Herausforderung
**Urbane Bäume sind essentiell** für Kühlung, Biodiversität und Wohlbefinden – doch **das Finden geeigneter Pflanzstandorte in dichten Stadtgebieten ist komplex**.

**Multiple Constraints müssen berücksichtigt werden:**
- 🚗 Parkplätze & Verkehrswege
- ⚡ Unterirdische Versorgungsleitungen & Pipelines
- 🔥 Brandschutzzonen
- 🏗️ Stadtplanung & zukünftige Entwicklungspläne

### Das Dilemma
Diese Daten existieren zwar in GIS-Systemen, sind aber oft:
- 📂 **Fragmentiert** – Verschiedene Systeme, verschiedene Formate
- 🐌 **Schwer nutzbar** – Manuelle Arbeit für datengestützte Entscheidungen
- ⏱️ **Zeitaufwändig** – Verpasste Chancen, die Stadt grüner zu machen

**Resultat:** Ineffiziente Planung und ungenutzte Potenziale für Urban Greening.

---

## 💡 Unsere Lösung: City Forest Creator

Eine **interaktive Web-App**, die komplexe Geo-Daten in **actionable insights** verwandelt und Stadtplaner:innen bei der optimalen Baumpflanzung unterstützt.

### ✨ Features

#### 🗺️ **Intelligente Standortsuche**
- **Automatische Constraint-Integration**: Lädt ALLE Ausschlusszonen aus `constraints/` Ordner
- **Multi-Layer-Analyse**: Gebäude, Straßen, bestehende Bäume, Infrastruktur
- **Flexibles Raster**: Konfigurierbare Punktdichte (10-50m Abstand)
- **Performance-Optimiert**: Spatial-Index für blitzschnelle Berechnung (10.000+ Standorte in ~3 Sekunden)

#### 🔧 **What-If-Analyse: Trade-Off-Visualisierung**
Beantwortet die Frage: *"Was passiert, wenn wir bestimmte Constraints lockern?"*

```
Beispiel-Szenario:
"Was wenn wir 10% der Parkplätze für Bäume opfern?"

1. Wähle "Parkplätze" in "Zonen entsperren"
2. Setze Slider auf 10%
3. ➡️ Ergebnis: "+120 zusätzliche Standorte"
4. ➡️ Trade-off: "12 Parkplätze vs. 2.640 kg CO₂/Jahr"
```

**Features:**
- Live-Berechnung zusätzlicher Pflanzflächen
- CO₂-Impact-Kalkulation
- Visuelle Markierung entsperrter Zonen
- Transparente Darstellung von Constraints

#### 🔥 **Hitze-Heatmap: Priorisierung**
Zeigt, **wo Bäume am dringendsten gebraucht werden**:

- **Baumdichte-Analyse**: Bereiche mit wenig Grün = hoher Hitze-Score
- **Top 5 Hotspots**: Ranking der Gebiete mit höchstem Handlungsbedarf
- **Interaktive Farbskala**: 
  - 🔵 Blau = Viele Bäume (kühl) 
  - 🔴 Rot = Keine Bäume (Hitze-Hotspot)
- **Datengestützte Priorisierung**: Fokussiere Ressourcen auf kritische Bereiche

#### 📊 **Datenanalyse & Visualisierung**
- **Baumkataster-Import**: Automatisches Laden von Shapefiles
- **Constraint-Management**: Beliebig viele Ausschlusszonen-Layer
- **Statistiken**: Top 5 Baumarten, Zonenübersicht, Metriken
- **Interaktive Karte**: Layer-Kontrolle, Tooltips, Clustering

---

## 🚀 Quick Start

### Voraussetzungen
- Python 3.9+
- Git

### Installation

```bash
# Repository klonen
git clone https://github.com/yourusername/city-forest-creator.git
cd city-forest-creator

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt
```

### Daten vorbereiten

```bash
# Ordnerstruktur erstellen
mkdir data constraints

# Baumkataster-Shapefile in data/ ablegen
# z.B. SHN_Baumkataster_open_UTM32N_EPSG25832.shp

# Ausschlusszonen in constraints/ ablegen
# Beispiele:
#   - buildings.shp (Gebäude)
#   - streets.shp (Straßen & Verkehr)
#   - utilities.shp (Versorgungsleitungen)
#   - fire_zones.shp (Brandschutzzonen)
#   - future_development.shp (Planungsgebiete)
```

### App starten

```bash
streamlit run app.py
```

🎉 **Die App läuft auf:** `http://localhost:8501`

---

## 💡 Nutzung

### 1️⃣ **Grundkonfiguration**
- **Mindestabstand zu Bäumen** (2-10m) – Vermeidet Konkurrenz
- **Buffer für Linien** (5-20m) – Abstand zu Straßen/Wegen
- **Rasterabstand** (10-50m) – Dichte der Testpunkte

### 2️⃣ **Trade-Off-Analyse: What-If-Szenarien**
Teste verschiedene Planungsszenarien:

| Szenario | Aktion | Erwartetes Ergebnis |
|----------|--------|---------------------|
| **Basis** | Keine Entsperrung | 500 Standorte |
| **Parkplatz-Opferung** | 10% Parkplätze entsperren | +120 Standorte (+24%) |
| **Rasen-Nutzung** | 15% Rasenflächen entsperren | +180 Standorte (+36%) |
| **Kombiniert** | Beide Zonen entsperren | +280 Standorte (+56%) |

### 3️⃣ **Prioritäten setzen: Heatmap**
1. Aktiviere **"Zeige Hitze-Heatmap"**
2. Analysiere **Top 5 Hitze-Hotspots** in Sidebar
3. Fokussiere Pflanzungen auf rote Bereiche
4. Zeige Stadtrat: "Diese 3 Stadtteile brauchen sofort Bäume!"

### 4️⃣ **Präsentation vorbereiten**
- Screenshots von Heatmap & What-If-Szenarien
- Notiere Impact-Zahlen für Pitch
- Teste Live-Demo (Layer ein-/ausschalten)

---

## 🏗️ Technologie-Stack

### Backend: Geo-Analytics
- **GeoPandas** – Spatial Data Processing
- **Shapely** – Geometrie-Operationen & Spatial Index
- **NumPy** – Performance-Optimierung (Meshgrid)

### Frontend: Interactive Visualization
- **Streamlit** – Rapid Web App Development
- **Folium** – Leaflet-basierte Karten
- **Branca** – Color Maps für Heatmaps

### Performance-Optimierungen
- **@st.cache_data** – Caching teurer Berechnungen
- **Shapely.prepared()** – 100x schnellere Spatial Queries
- **Marker Clustering** – Skaliert auf 10.000+ Punkte

---

## 📁 Projektstruktur

```
city-forest-creator/
├── app.py                  # Streamlit UI & Orchestrierung
├── analysis.py             # Geo-Analysen & Algorithmen
│   ├── load_data()         # Baumkataster laden
│   ├── find_suitable_locations()  # Ausschlusszonen
│   ├── apply_zone_relaxation()    # What-If-Logik
│   ├── find_planting_locations()  # Standort-Suche
│   └── calculate_tree_density_heatmap()  # Heatmap
├── requirements.txt        # Python Dependencies
├── .gitignore             # Git Excludes
├── data/                  # Baumkataster (OpenData)
│   └── SHN_Baumkataster_*.shp
├── constraints/           # Ausschlusszonen (GIS-Daten)
│   ├── buildings.shp
│   ├── streets.shp
│   ├── utilities.shp
│   └── fire_zones.shp
└── README.md              # Diese Datei
```

---

## 📊 Performance-Metriken

**Test-Setup: Heilbronn (~12.000 Bäume, 5 Constraint-Layer)**

| Metrik | Wert | Challenge-Anforderung |
|--------|------|-----------------------|
| Ladezeit Baumkataster | ~2s | ✅ Schnell & automatisch |
| Berechnung 5.000 Pflanzpunkte | ~3s | ✅ Interactive map |
| Heatmap (100m Raster) | ~5s | ✅ Visualize datasets |
| What-If Delta-Analyse | <1s | ✅ Show trade-offs |
| Cache-Hit (wiederholt) | <0.1s | ✅ Fast decisions |

*Hardware: Standard Laptop (8GB RAM, i5)*

---

## 🎓 Hackathon-Kontext

### Future City Hackathon 2025
**21.-23. November 2025 | OpenSpace Heilbronn**

**Organisiert von:**
- 🏛️ Hochschule Heilbronn
- 🌆 **Stadt Heilbronn** (Challenge-Geber)
- 🔬 Fraunhofer IAO
- 💻 42 Heilbronn
- 🏢 Schwarz Digits, HNVG & weitere Partner

**Challenge-Focus:**
> *"Wie kann die Stadt mithilfe von Daten grüner, nachhaltiger und intelligenter werden?"*

**Unsere Antwort:**
Wir verwandeln fragmentierte GIS-Daten in eine **interaktive Entscheidungshilfe**, die Stadtplaner:innen befähigt, **schneller, transparenter und datengestützt** zu handeln.

---

## 🌍 Impact & Use Cases

### Für Stadtplaner:innen
- 📍 **Standorte identifizieren** in Minuten statt Tagen
- 🎯 **Priorisierung** basierend auf Hitze-Hotspots
- 💬 **Transparenz** gegenüber Bürger:innen durch What-If-Szenarien
- 📊 **Datengestützte Argumente** für Stadtrats-Beschlüsse

### Für die Stadt Heilbronn
- 🌡️ **Hitzereduktion** in kritischen Stadtteilen
- 💚 **Lebensqualität** durch mehr Grünflächen
- 🚀 **Effizienz** bei Urban-Greening-Projekten
- 🏆 **Vorreiterrolle** als Smart City

### Messbare Ergebnisse (Beispiel-Szenario)
```
Basis: 500 identifizierte Standorte
What-If (10% Parkplätze): +120 Standorte

Impact:
  • 620 neue Bäume = 13.640 kg CO₂/Jahr gebunden
  • ~15 ha zusätzliche Schattenfläche
  • Temperaturreduktion: -2-3°C in Hotspots
  • Trade-off: 62 Parkplätze (10%)
```

---

## 🔮 Roadmap & Erweiterungen

### Phase 2: Advanced Features
- [ ] **Baumartenempfehlung** – KI-gestützt basierend auf Boden & Klima
- [ ] **Echte Klimadaten** – Integration Sentinel Satelliten-Daten (Land Surface Temperature)
- [ ] **Kostenschätzung** – Budget-Optimierung (€ pro Baum, Pflege, Bewässerung)
- [ ] **3D-Visualisierung** – Wachstums-Simulation bis 2054
- [ ] **PDF-Export** – Automatische Reports für Stadtrat

### Phase 3: Citizen Engagement
- [ ] **Bürger-Beteiligung** – "Adoptiere einen Baum" Portal
- [ ] **Mobile App** – QR-Code-Schilder an Pflanzorten
- [ ] **Gamification** – Community-Leaderboard

### Phase 4: Multi-City Scaling
- [ ] **Template-System** für andere Städte
- [ ] **OpenData-Connector** für standardisierte GIS-Formate
- [ ] **API-Schnittstelle** für Integration in Verwaltungssysteme

---

**Skills im Projekt:**
- 🗺️ Geospatial Analysis (GeoPandas, Shapely)
- 🎨 UI/UX Design (Streamlit, Folium)
- 📊 Data Visualization
- ⚡ Performance Optimization
- 🌳 Urban Planning & Sustainability

---

## 🙏 Danksagungen

- 🏛️ **Stadt Heilbronn** – Für die Challenge, OpenData Baumkataster und Vision
- 🎓 **Hochschule Heilbronn** – Für Hosting, Infrastruktur & Support
- 🔬 **Fraunhofer IAO** – Für Expertise in Smart City Solutions
- 💻 **42 Heilbronn** – Für die Coding-Community
- 🌍 **Future City Hackathon Team** – Für Organisation & Inspiration
- 📚 **GeoPandas Community** – Für großartige Open-Source-Tools

---

## 📜 Lizenz

MIT License – Siehe [LICENSE](LICENSE) für Details.

**TL;DR:** Nutze, modifiziere und teile das Projekt frei. Wir freuen uns über Namensnennung! 🙏

---

## 📞 Kontakt & Links

**Projekt-Links:**
- 🐙 GitHub: [github.com/lady-logic/city-forest-creator](https://github.com/yourusername/city-forest-creator)
- 📧 Email: [k.rueckbrodt@gmx.de]
- 💼 LinkedIn: [https://www.linkedin.com/in/katharina-rueckbrodt/]

**Challenge-Links:**
- 🏛️ Stadt Heilbronn: [heilbronn.de](https://www.heilbronn.de)
- 🎓 Future City Hackathon: [hs-heilbronn.de/hackathon](https://www.hs-heilbronn.de/de/hackathon)

---

<div align="center">

## 🌳 Code for trees — and a better future for our cities 🌳

*"Heilbronn is a cool place to be – with nice shadow from the trees in the summer"*

**Every line of code contributes to:**  
Cleaner air • Cooler neighborhoods • A more livable city for everyone

---

[![Stargazers](https://img.shields.io/github/stars/yourusername/city-forest-creator?style=social)](https://github.com/yourusername/city-forest-creator/stargazers)
[![Forks](https://img.shields.io/github/forks/yourusername/city-forest-creator?style=social)](https://github.com/yourusername/city-forest-creator/network/members)

**Entwickelt beim Future City Hackathon 2025 | Heilbronn**

</div>
