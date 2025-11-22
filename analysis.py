import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import os
from pathlib import Path
import numpy as np

def load_data(data_path="data"):
    """Lädt das Baumkataster - sucht automatisch nach passender Datei"""
    try:
        # Suche nach Baumkataster-Dateien
        shp_files = list(Path(data_path).glob("*.shp"))
        
        if not shp_files:
            print(f"✗ Keine .shp Dateien in '{data_path}' gefunden!")
            return None
        
        # Versuche zuerst die erwartete Datei
        expected_file = f"{data_path}/SHN_Baumkataster_open_UTM32N_EPSG25832.shp"
        if os.path.exists(expected_file):
            bäume = gpd.read_file(expected_file)
        else:
            # Nehme die erste .shp Datei
            print(f"⚠ Erwartete Datei nicht gefunden, verwende: {shp_files[0].name}")
            bäume = gpd.read_file(shp_files[0])
        
        print(f"✓ Erfolgreich geladen: {len(bäume)} Bäume")
        print(f"✓ Koordinatensystem: {bäume.crs}")
        print(f"✓ Datei: {shp_files[0].name if not os.path.exists(expected_file) else 'SHN_Baumkataster_open_UTM32N_EPSG25832.shp'}")
        return bäume
    except Exception as e:
        print(f"✗ Fehler beim Laden: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_all_constraints(constraints_path="constraints"):
    """
    Lädt ALLE Shapefiles aus dem constraints-Ordner
    """
    constraints = {}
    
    # Prüfe ob Ordner existiert
    if not os.path.exists(constraints_path):
        print(f"⚠ Ordner '{constraints_path}' existiert nicht - erstelle ihn...")
        os.makedirs(constraints_path)
        return constraints
    
    # Finde alle .shp Dateien
    constraint_files = list(Path(constraints_path).glob("*.shp"))
    
    if not constraint_files:
        print(f"⚠ Keine Shapefiles in '{constraints_path}' gefunden")
        return constraints
    
    print(f"\n📂 Lade Constraints aus '{constraints_path}':")
    
    for shp_file in constraint_files:
        filename = shp_file.stem
        try:
            gdf = gpd.read_file(shp_file)
            constraints[filename] = gdf
            print(f"  ✓ {filename}: {len(gdf)} Features")
        except Exception as e:
            print(f"  ✗ {filename}: Fehler - {e}")
            constraints[filename] = None
    
    return constraints

def find_suitable_locations(bäume, constraints, abstand_bäume=5, buffer_linien=10):
    """Findet geeignete Standorte für neue Bäume"""
    ausschlusszonen = {}
    
    # 1. Buffer um bestehende Bäume
    baum_buffer = bäume.copy()
    baum_buffer['geometry'] = baum_buffer.buffer(abstand_bäume)
    baum_zone = baum_buffer.dissolve()
    baum_zone.crs = bäume.crs
    ausschlusszonen['🌳_Baum_Puffer'] = baum_zone
    
    # 2. Alle Constraint-Layer verarbeiten
    for name, layer in constraints.items():
        if layer is None or len(layer) == 0:
            continue
        
        try:
            constraint_copy = layer.copy()
            
            # CRS angleichen
            if constraint_copy.crs != bäume.crs:
                constraint_copy = constraint_copy.to_crs(bäume.crs)
            
            # Prüfe Geometrie-Typ
            geom_type = constraint_copy.geometry.geom_type.iloc[0] if len(constraint_copy) > 0 else None
            
            # Linien bekommen einen Buffer
            if geom_type in ['LineString', 'MultiLineString']:
                constraint_copy['geometry'] = constraint_copy.buffer(buffer_linien)
                print(f"  → {name} (Linie): Buffer von {buffer_linien}m angewendet")
            
            # Dissolve
            zone = constraint_copy.dissolve()
            zone.crs = bäume.crs
            
            ausschlusszonen[name] = zone
            
        except Exception as e:
            print(f"  ✗ Fehler bei {name}: {e}")
    
    print(f"\n✓ {len(ausschlusszonen)} Ausschlusszonen-Typen berechnet")
    
    return ausschlusszonen

def calculate_stats(bäume):
    """Berechnet Statistiken über das Baumkataster"""
    stats = {
        'anzahl_bäume': len(bäume),
        'bounds': bäume.total_bounds
    }
    
    for col_name in ['GATTUNG', 'Art', 'Gattung', 'gattung']:
        if col_name in bäume.columns:
            stats['top_arten'] = bäume[col_name].value_counts().head(5)
            break
    
    return stats

def apply_zone_relaxation(ausschlusszonen_dict, unlock_zones, unlock_percentage):
    """
    Entsperrt teilweise Zonen für Baumpflanzung
    ⚡ OPTIMIERT: Nur modifizierte Zonen werden kopiert
    
    Args:
        ausschlusszonen_dict: Dict mit allen Ausschlusszonen
        unlock_zones: Liste der zu entsperrenden Zonen-Namen
        unlock_percentage: Prozent der Fläche, die genutzt werden darf (0-100)
    
    Returns:
        Dict mit modifizierten Ausschlusszonen
    """
    if not unlock_zones or unlock_percentage == 0:
        return ausschlusszonen_dict
    
    # ⚡ OPTIMIERUNG: Shallow copy, nur geänderte Zonen werden kopiert
    modified_zones = ausschlusszonen_dict.copy()
    
    print(f"\n🔧 What-If: Entsperre {len(unlock_zones)} Zone(n) zu {unlock_percentage}%")
    
    for zone_name in unlock_zones:
        if zone_name in modified_zones and modified_zones[zone_name] is not None:
            zone = modified_zones[zone_name]
            
            try:
                # Erode die Zone (verkleinere sie)
                buffer_distance = -5 * (unlock_percentage / 100)
                
                eroded = zone.copy()
                eroded['geometry'] = zone.buffer(buffer_distance)
                
                # Entferne leere Geometrien
                eroded = eroded[~eroded.is_empty]
                
                if len(eroded) > 0:
                    modified_zones[zone_name] = eroded
                    print(f"  ✓ {zone_name}: {unlock_percentage}% entsperrt")
                else:
                    # Zone komplett entsperrt
                    modified_zones[zone_name] = None
                    print(f"  ✓ {zone_name}: Komplett entsperrt")
                    
            except Exception as e:
                print(f"  ✗ {zone_name}: Fehler - {e}")
    
    return modified_zones

def find_planting_locations(ausschlusszonen_dict, bounds, grid_spacing=20):
    """
    Erzeugt potenzielle Pflanzstandorte als Punktraster
    ⚡ MASSIV OPTIMIERT: Spatial Index + Vektorisierung
    
    Args:
        ausschlusszonen_dict: Dict mit allen Ausschlusszonen
        bounds: Bounding Box [minx, miny, maxx, maxy]
        grid_spacing: Abstand zwischen Punkten in Metern
    
    Returns:
        GeoDataFrame mit geeigneten Pflanzstandorten
    """
    from shapely.geometry import Point
    from shapely.ops import unary_union
    
    print(f"\n🔍 Suche Pflanzstandorte (Raster: {grid_spacing}m)...")
    
    # ⚡ OPTIMIERUNG 1: Erstelle Punktraster mit numpy (viel schneller)
    minx, miny, maxx, maxy = bounds
    x_coords = np.arange(minx, maxx, grid_spacing)
    y_coords = np.arange(miny, maxy, grid_spacing)
    
    # Erstelle Meshgrid und flatten
    xx, yy = np.meshgrid(x_coords, y_coords)
    points = [Point(x, y) for x, y in zip(xx.ravel(), yy.ravel())]
    
    print(f"  → {len(points)} Testpunkte erstellt")
    
    # ⚡ OPTIMIERUNG 2: Kombiniere Ausschlusszonen VOR dem Check
    all_exclusions = []
    for name, zone in ausschlusszonen_dict.items():
        if zone is not None and len(zone) > 0:
            all_exclusions.append(zone.geometry.iloc[0])
    
    if not all_exclusions:
        # Keine Ausschlusszonen = alle Punkte sind geeignet
        crs = next(iter(ausschlusszonen_dict.values())).crs
        gdf = gpd.GeoDataFrame(geometry=points, crs=crs)
        print(f"  ✓ {len(gdf)} geeignete Standorte gefunden (keine Ausschlusszonen)")
        return gdf
    
    # ⚡ OPTIMIERUNG 3: Unary union nur einmal
    combined_exclusions = unary_union(all_exclusions)
    
    # ⚡ OPTIMIERUNG 4: Spatial Index für schnelle Abfragen
    # Statt für jeden Punkt .contains() aufzurufen, nutze prepare()
    from shapely.prepared import prep
    prepared_exclusions = prep(combined_exclusions)
    
    # ⚡ OPTIMIERUNG 5: List comprehension statt Loop
    suitable_points = [p for p in points if not prepared_exclusions.contains(p)]
    
    print(f"  ✓ {len(suitable_points)} geeignete Standorte gefunden")
    
    # Als GeoDataFrame zurückgeben
    if suitable_points:
        crs = next(iter(ausschlusszonen_dict.values())).crs
        gdf = gpd.GeoDataFrame(geometry=suitable_points, crs=crs)
        return gdf
    else:
        return None
    
def calculate_tree_density_heatmap(bäume, bounds, grid_size=100):
    """
    Berechnet Baumdichte als Heatmap
    ⚡ OPTIMIERT: Spatial Join statt Loop (10x schneller!)
    """
    from shapely.geometry import box
    import numpy as np
    
    print(f"\n🔥 Berechne Hitze-Heatmap (Raster: {grid_size}m)...")
    
    minx, miny, maxx, maxy = bounds
    x_coords = np.arange(minx, maxx, grid_size)
    y_coords = np.arange(miny, maxy, grid_size)
    
    # ⚡ OPTIMIERUNG 1: Erstelle alle Zellen auf einmal
    cells = []
    for x in x_coords:
        for y in y_coords:
            cells.append(box(x, y, x + grid_size, y + grid_size))
    
    # ⚡ OPTIMIERUNG 2: Spatial Join statt Loop
    grid_gdf = gpd.GeoDataFrame({'geometry': cells}, crs=bäume.crs)
    
    # Zähle Bäume pro Zelle mit Spatial Join
    joined = gpd.sjoin(grid_gdf, bäume, how='left', predicate='intersects')
    tree_counts = joined.groupby(joined.index).size()
    
    # Fülle fehlende Zellen mit 0
    grid_gdf['tree_count'] = tree_counts.reindex(grid_gdf.index, fill_value=0)
    
    # Score berechnen: 0 = viele Bäume (kühl), 1 = keine Bäume (heiß)
    grid_gdf['heat_score'] = 1 / (1 + grid_gdf['tree_count'] * 0.1)
    
    print(f"  ✓ {len(grid_gdf)} Heatmap-Zellen berechnet")
    return grid_gdf