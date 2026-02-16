#!/usr/bin/env python3
"""
run.py - Orquestador del Pipeline ETL
========================================
Punto de entrada único para ejecutar todo el proceso ETL:
  1. Generar datos sintéticos (si no existen)
  2. Extraer datos de CSV
  3. Transformar a modelo dimensional
  4. Cargar en Data Warehouse
  5. Generar visualizaciones (opcional)

Uso:
  python run.py                    # Ejecutar todo
  python run.py --skip-gen         # Sin generar datos
  python run.py --skip-viz         # Sin visualizaciones
  python run.py --rebuild          # Borrar BD y reconstruir
  python run.py --help             # Ver opciones

Estructura esperada:
  data/raw/            # Datos fuente (CSV)
  data/warehouse/      # Base de datos (SQLite)
  ETL/extract.py       # Módulo de extracción
  ETL/transform.py     # Módulo de transformación
  ETL/load.py          # Módulo de carga
  sql/create_tables.sql    # DDL
  visualization/kpi_dashboard.py   # Visualizaciones
"""

import sys
import os
import argparse
import sqlite3
import webbrowser
from pathlib import Path
from datetime import datetime

# Add ETL directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ETL'))

try:
    from extract import DataExtractor
    from transform import DataTransformer
    from load import DataWarehouseLoader
except ImportError as e:
    print(f"ERROR: No se pueden importar módulos ETL: {e}")
    print("Asegúrate de que los archivos extract.py, transform.py y load.py existan en la carpeta ETL/")
    sys.exit(1)


class ETLOrchestrater:
    """Orquestador principal del pipeline ETL"""
    
    def __init__(self, skip_gen=False, skip_viz=False, rebuild=False, verbose=True):
        """
        Inicializar el orquestador
        
        Args:
            skip_gen: Saltar generación de datos
            skip_viz: Saltar visualización
            rebuild: Borrar y reconstruir la BD
            verbose: Mostrar mensajes detallados
        """
        self.skip_gen = skip_gen
        self.skip_viz = skip_viz
        self.rebuild = rebuild
        self.verbose = verbose
        
        # Rutas
        self.project_root = Path(__file__).parent
        self.data_raw = self.project_root / "data" / "raw"
        self.data_warehouse = self.project_root / "data" / "warehouse"
        self.db_path = self.data_warehouse / "datawarehouse.db"
        
        # Crear directorio warehouse si no existe
        self.data_warehouse.mkdir(parents=True, exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Mostrar mensaje en consola"""
        if self.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prefix = {
                "INFO": "[*]",
                "OK": "[OK]",
                "ERROR": "[ERROR]",
                "WARN": "[WARN]"
            }.get(level, "[*]")
            print(f"{prefix} {message}")
    
    def section(self, title: str):
        """Mostrar encabezado de sección"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}\n")
    
    def check_prerequisites(self) -> bool:
        """Verificar que todos los archivos necesarios existan"""
        self.section("VERIFICACIÓN DE REQUISITOS")
        
        required_files = {
            "data/raw/products.csv": "Productos",
            "data/raw/customers.csv": "Clientes",
            "data/raw/sales.csv": "Ventas",
            "data/raw/channels.csv": "Canales",
            "ETL/extract.py": "Módulo Extract",
            "ETL/transform.py": "Módulo Transform",
            "ETL/load.py": "Módulo Load",
            "sql/create_tables.sql": "Schema DDL",
        }
        
        missing = []
        for file_path, description in required_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log(f"{description:30s} -> {file_path}", "OK")
            else:
                self.log(f"{description:30s} -> {file_path} (FALTA)", "ERROR")
                missing.append(file_path)
        
        if missing:
            self.log(f"\nArchivos faltantes: {', '.join(missing)}", "ERROR")
            return False
        
        self.log("Todos los requisitos satisfechos", "OK")
        return True
    
    def handle_rebuild(self) -> bool:
        """Borrar base de datos existente si se solicita rebuild"""
        if not self.rebuild:
            return True
        
        self.section("RECONSTRUCCIÓN DE BASE DE DATOS")
        
        if self.db_path.exists():
            try:
                self.db_path.unlink()
                self.log(f"Base de datos eliminada: {self.db_path.name}", "OK")
                return True
            except Exception as e:
                self.log(f"Error al eliminar BD: {str(e)}", "ERROR")
                return False
        else:
            self.log("La base de datos no existe (no hay nada que eliminar)", "WARN")
            return True
    
    def generate_data(self) -> bool:
        """Generar datos sintéticos si no existen"""
        if self.skip_gen:
            self.log("Saltando generación de datos (--skip-gen)", "WARN")
            return True
        
        # Verificar si los datos ya existen
        required_csvs = ["products.csv", "customers.csv", "sales.csv", "channels.csv"]
        all_exist = all((self.data_raw / csv).exists() for csv in required_csvs)
        
        if all_exist and not self.rebuild:
            self.log("Datos sintéticos ya existen en data/raw/", "OK")
            return True
        
        self.section("GENERACIÓN DE DATOS SINTÉTICOS")
        
        try:
            # Los datos ya existen en el proyecto, así que solo verificamos
            self.log(f"Verificando datos en: {self.data_raw}", "INFO")
            
            for csv in required_csvs:
                csv_path = self.data_raw / csv
                if csv_path.exists():
                    size = csv_path.stat().st_size / 1024  # KB
                    rows = len(open(csv_path).readlines()) - 1  # Restar encabezado
                    self.log(f"{csv:20s} -> {rows} registros ({size:.1f} KB)", "OK")
                else:
                    self.log(f"{csv:20s} -> NO ENCONTRADO", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"Error en generación de datos: {str(e)}", "ERROR")
            return False
    
    def extract(self) -> dict:
        """Ejecutar fase EXTRACT"""
        self.section("FASE 1: EXTRACCIÓN (EXTRACT)")
        
        try:
            extractor = DataExtractor(str(self.data_raw))
            extracted = extractor.extract_all()
            
            self.log(f"Extracción completada exitosamente", "OK")
            self.log(f"Datos extraídos: {len(extracted)} tablas", "INFO")
            
            return extracted
            
        except Exception as e:
            self.log(f"Error en extracción: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return None
    
    def transform(self, extracted_data: dict) -> dict:
        """Ejecutar fase TRANSFORM"""
        self.section("FASE 2: TRANSFORMACIÓN (TRANSFORM)")
        
        try:
            transformer = DataTransformer(extracted_data)
            transformed = transformer.transform_all()
            
            self.log(f"Transformación completada exitosamente", "OK")
            self.log(f"Dimensiones creadas:", "INFO")
            for table, df in transformed.items():
                if table.startswith("dim_"):
                    self.log(f"  {table:20s} -> {len(df)} registros", "INFO")
            
            for table, df in transformed.items():
                if table.startswith("fact_"):
                    self.log(f"Tabla de hechos:", "INFO")
                    self.log(f"  {table:20s} -> {len(df)} registros", "INFO")
            
            return transformed
            
        except Exception as e:
            self.log(f"Error en transformación: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return None
    
    def load(self, transformed_data: dict) -> bool:
        """Ejecutar fase LOAD"""
        self.section("FASE 3: CARGA (LOAD)")
        
        try:
            loader = DataWarehouseLoader(str(self.db_path))
            
            self.log(f"Conectando a base de datos: {self.db_path.name}", "INFO")
            loader.connect()
            
            self.log(f"Creando schema de base de datos...", "INFO")
            loader.create_schema()
            
            self.log(f"Cargando datos en warehouse...", "INFO")
            loader.load_all(transformed_data)
            
            loader.disconnect()
            
            self.log(f"Carga completada exitosamente", "OK")
            self.log(f"Base de datos creada: {self.db_path.name}", "INFO")
            
            # Mostrar estadísticas
            size_mb = self.db_path.stat().st_size / (1024 * 1024)
            self.log(f"Tamaño de BD: {size_mb:.2f} MB", "INFO")
            
            return True
            
        except Exception as e:
            self.log(f"Error en carga: {str(e)}", "ERROR")
            import traceback
            traceback.print_exc()
            return False
    
    def visualize(self) -> bool:
        """Ejecutar visualizaciones (opcional)"""
        if self.skip_viz:
            self.log("Saltando visualización (--skip-viz)", "WARN")
            return True
        
        self.section("FASE 4: VISUALIZACIÓN")
        
        try:
            viz_path = self.project_root / "visualization" / "kpi_dashboard.py"
            
            if not viz_path.exists():
                self.log(f"Script de visualización no encontrado: {viz_path}", "WARN")
                return True
            
            self.log(f"Ejecutando visualizador KPI...", "INFO")
            
            # Ejecutar el script de visualización
            import subprocess
            result = subprocess.run(
                [sys.executable, str(viz_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log(f"Visualización completada exitosamente", "OK")
                # Mostrar últimas líneas del output
                lines = result.stdout.strip().split('\n')
                for line in lines[-3:]:
                    if line.strip():
                        self.log(f"  {line}", "INFO")
                return True
            else:
                self.log(f"Error en visualización: {result.stderr}", "WARN")
                return True  # No es crítico
                
        except Exception as e:
            self.log(f"Error al ejecutar visualización: {str(e)}", "WARN")
            return True  # No es crítico
    
    def run_pipeline(self) -> bool:
        """Ejecutar el pipeline completo"""
        
        print(f"\n{'*'*70}")
        print(f"*  ETL PIPELINE ORCHESTRATOR - TECHNOLOGY RETAIL ANALYTICS")
        print(f"*  Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'*'*70}\n")
        
        # 1. Verificar requisitos
        if not self.check_prerequisites():
            self.log("Pipeline abortado: requisitos no cumplidos", "ERROR")
            return False
        
        # 2. Manejar rebuild
        if not self.handle_rebuild():
            return False
        
        # 3. Generar datos
        if not self.generate_data():
            self.log("Pipeline abortado: error en generación de datos", "ERROR")
            return False
        
        # 4. Extract
        extracted = self.extract()
        if extracted is None:
            self.log("Pipeline abortado: error en extracción", "ERROR")
            return False
        
        # 5. Transform
        transformed = self.transform(extracted)
        if transformed is None:
            self.log("Pipeline abortado: error en transformación", "ERROR")
            return False
        
        # 6. Load
        if not self.load(transformed):
            self.log("Pipeline abortado: error en carga", "ERROR")
            return False
        
        # 7. Visualize (opcional)
        self.visualize()
        
        # Success summary
        print(f"\n{'*'*70}")
        print(f"*  PIPELINE COMPLETADO EXITOSAMENTE")
        print(f"*  Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'*'*70}\n")
        
        # Open dashboard in browser
        self.open_dashboard()
        
        return True
    
    def open_dashboard(self):
        """Open the HTML dashboard in the default browser"""
        dashboard_path = self.project_root / "visualization" / "output" / "dashboard.html"
        
        if dashboard_path.exists():
            try:
                print(f"[*] Abriendo dashboard en navegador...")
                # Use file:// URI for local files
                dashboard_uri = dashboard_path.resolve().as_uri()
                webbrowser.open(dashboard_uri)
                print(f"[OK] Dashboard abierto: {dashboard_path.name}\n")
            except Exception as e:
                print(f"[WARN] No se pudo abrir navegador: {e}")
                print(f"[INFO] Abre manualmente: {dashboard_path}\n")
        else:
            print(f"[INFO] Generando dashboard HTML antes de abrir...\n")
            try:
                # Try to generate the dashboard
                import importlib.util
                spec = importlib.util.spec_from_file_location(
                    "generate_html_dashboard",
                    self.project_root / "generate_html_dashboard.py"
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Generate HTML
                    generator = module.HTMLDashboardGenerator()
                    generator.save_html()
                    
                    # Try to open again
                    if dashboard_path.exists():
                        dashboard_uri = dashboard_path.resolve().as_uri()
                        webbrowser.open(dashboard_uri)
                        print(f"[OK] Dashboard generado y abierto\n")
            except Exception as e:
                print(f"[WARN] Error generando dashboard: {e}")
                print(f"[INFO] Ejecuta: python generate_html_dashboard.py\n")


def main():
    """Función principal"""
    
    # Parsear argumentos
    parser = argparse.ArgumentParser(
        description="Orquestador del Pipeline ETL - Data Warehouse Construction",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run.py                    # Ejecutar todo
  python run.py --skip-gen         # Saltar generación de datos
  python run.py --skip-viz         # Saltar visualización
  python run.py --rebuild          # Eliminar y reconstruir BD
  python run.py --skip-gen --skip-viz --quiet  # Modo silencioso
        """
    )
    
    parser.add_argument(
        "--skip-gen",
        action="store_true",
        help="Saltar generación de datos sintéticos"
    )
    
    parser.add_argument(
        "--skip-viz",
        action="store_true",
        help="Saltar generación de visualizaciones"
    )
    
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Borrar BD existente y reconstruir desde cero"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Modo silencioso (menos output)"
    )
    
    args = parser.parse_args()
    
    # Crear orquestrador
    orchestrater = ETLOrchestrater(
        skip_gen=args.skip_gen,
        skip_viz=args.skip_viz,
        rebuild=args.rebuild,
        verbose=not args.quiet
    )
    
    # Ejecutar pipeline
    try:
        success = orchestrater.run_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nPipeline interrumpido por el usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\nError no controlado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
