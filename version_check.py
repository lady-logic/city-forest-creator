"""
Prüfe installierte Package-Versionen
Führe aus mit: python version_check.py
"""

import sys

packages_to_check = {
    'streamlit': '1.39.0',
    'geopandas': '1.0.1',
    'fiona': '1.10.1',
    'folium': '0.18.0',
    'streamlit-folium': '0.22.2',
    'matplotlib': '3.9.2',
    'pyproj': '3.7.0',
    'shapely': '2.0.6',
    'numpy': '1.26.4',
    'branca': '0.8.1'
}

print("=" * 60)
print("PACKAGE VERSION CHECK")
print("=" * 60)

all_ok = True

for package, expected_version in packages_to_check.items():
    package_import = package.replace('-', '_')
    
    try:
        if package == 'streamlit-folium':
            import streamlit_folium
            installed = streamlit_folium.__version__
        else:
            module = __import__(package_import)
            installed = module.__version__
        
        status = "✅" if installed == expected_version else "⚠️"
        if installed != expected_version:
            all_ok = False
            
        print(f"{status} {package:20s} | Installed: {installed:10s} | Expected: {expected_version}")
        
    except ImportError:
        print(f"❌ {package:20s} | NOT INSTALLED")
        all_ok = False
    except AttributeError:
        print(f"⚠️  {package:20s} | Installed (version unknown)")

print("=" * 60)
print(f"Python Version: {sys.version}")
print("=" * 60)

if all_ok:
    print("✅ Alle Packages haben die erwarteten Versionen!")
else:
    print("\n⚠️  WARNUNG: Einige Packages haben abweichende Versionen!")
    print("Falls Probleme auftreten, installiere mit:")
    print("  pip install -r requirements.txt --force-reinstall")