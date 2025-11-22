import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import os
from pathlib import Path

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

def find_planting_locations(ausschlusszonen_dict, bounds, grid_spacing=20):
    """
    Erzeugt potenzielle Pflanzstandorte als Punktraster
    
    Args:
        ausschlusszonen_dict: Dict mit allen Ausschlusszonen
        bounds: Bounding Box [minx, miny, maxx, maxy]
        grid_spacing: Abstand zwischen Punkten in Metern
    
    Returns:
        GeoDataFrame mit geeigneten Pflanzstandorten
    """
    import numpy as np
    from shapely.geometry import Point, MultiPolygon
    
    print(f"\n🔍 Suche Pflanzstandorte (Raster: {grid_spacing}m)...")
    
    # Erstelle Punktraster
    minx, miny, maxx, maxy = bounds
    x_coords = np.arange(minx, maxx, grid_spacing)
    y_coords = np.arange(miny, maxy, grid_spacing)
    
    points = []
    for x in x_coords:
        for y in y_coords:
            points.append(Point(x, y))
    
    print(f"  → {len(points)} Testpunkte erstellt")
    
    # Kombiniere alle Ausschlusszonen
    all_exclusions = []
    for name, zone in ausschlusszonen_dict.items():
        if zone is not None and len(zone) > 0:
            all_exclusions.append(zone.geometry.iloc[0])
    
    if all_exclusions:
        from shapely.ops import unary_union
        combined_exclusions = unary_union(all_exclusions)
    else:
        combined_exclusions = None
    
    # Filtere Punkte: Behalte nur die AUSSERHALB der Ausschlusszonen
    suitable_points = []
    for point in points:
        if combined_exclusions is None or not combined_exclusions.contains(point):
            suitable_points.append(point)
    
    print(f"  ✓ {len(suitable_points)} geeignete Standorte gefunden")
    
    # Als GeoDataFrame zurückgeben
    if suitable_points:
        # CRS von der ersten Zone übernehmen
        crs = next(iter(ausschlusszonen_dict.values())).crs
        gdf = gpd.GeoDataFrame(geometry=suitable_points, crs=crs)
        return gdf
    else:
        return None