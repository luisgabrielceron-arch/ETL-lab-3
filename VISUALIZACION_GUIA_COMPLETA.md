# ETL Lab 3 - Technology Retail Analytics
## Proyecto Completado: Guía Completa de Visualización y Análisis

**Fecha de Finalización:** 16 de febrero de 2026  
**Estado:** ✅ COMPLETADO 100%

---

## 📊 RESUMEN EJECUTIVO

Se ha completado un **pipeline ETL completo** con visualización interactiva multinivel:

### Fase 1: ETL Pipeline ✅
- **Extract:** Lectura de 4 CSV (productos, clientes, ventas, canales)
- **Transform:** Creación de 4 dimensiones + 1 tabla de hechos con 240 registros
- **Load:** Base de datos SQLite con integridad referencial verificada

### Fase 2: Visualización ✅
- **Tkinter GUI:** Aplicación interactiva con 5 pestañas de KPIs
- **Dashboard HTML:** Página web interactiva con gráficos dinámicos
- **Jupyter Notebook:** Análisis completo con recomendaciones estratégicas
- **PNG Reports:** 5 gráficos profesionales + reporte ejecutivo txt

### Fase 3: Integridad de Datos ✅
- 0 registros huérfanos (verificado)
- 240 transacciones válidas
- 24 clientes de 3 países
- 40 productos en 5 categorías
- Márgenes de ganancia: 18.30% (óptimo)

---

## 🗂️ ESTRUCTURA DE ARCHIVOS GENERADOS

### Herramientas de Visualización
```
kpi_viewer.py                    [Aplicación Tkinter interactiva]
generate_html_dashboard.py       [Generador de Dashboard HTML]
analysis.ipynb                   [Jupyter Notebook con análisis completo]
```

### Outputs Visuales
```
visualization/output/
├── kpi1_revenue_by_category.png          (188 KB)
├── kpi2_revenue_by_channel.png           (194 KB)
├── kpi3_monthly_trends.png               (197 KB)
├── kpi4_brand_profitability.png          (132 KB)
├── kpi_dashboard_comprehensive.png       (471 KB)
├── dashboard.html                        [Página web interactiva]
└── kpi_summary_report.txt                [Reporte ejecutivo]
```

### Base de Datos
```
data/warehouse/
└── datawarehouse.db              (53 KB - SQLite con 5 tablas)
   ├── dim_date       (120 registros)
   ├── dim_product    (40 registros)
   ├── dim_customer   (24 registros)
   ├── dim_channel    (3 registros)
   └── fact_sales     (240 registros)
```

---

## 🚀 CÓMO USAR CADA VISUALIZACIÓN

### 1️⃣ TKINTER DASHBOARD (Interactivo - Recomendado)
```bash
python kpi_viewer.py
```
**Características:**
- ✅ 5 pestañas con KPIs principales
- ✅ Gráficos embebidos (matplotlib)
- ✅ Tablas de datos en tiempo real
- ✅ No requiere navegador
- ✅ Interfaz profesional con colores

**KPIs Disponibles:**
1. Revenue by Category (barras + pie chart)
2. Revenue by Channel (barras + pie chart)
3. Monthly Trends (líneas + barras)
4. Brand Profitability (ranking + scatter)
5. Geographic Distribution (barras + comparativa)

---

### 2️⃣ HTML DASHBOARD (Web - Moderno)
```bash
# Generar
python generate_html_dashboard.py

# Abrir en navegador
open visualization/output/dashboard.html
```
**Características:**
- ✅ Gráficos con Chart.js (interactivos)
- ✅ Pestañas navegables
- ✅ Responsive (funciona en mobile)
- ✅ Gradientes y estilos modernos
- ✅ No requiere servidor

**Datos Incluidos:**
- Todos los 5 KPIs con visualizaciones
- Tablas de datos completas
- Filtrado visual automático

---

### 3️⃣ JUPYTER NOTEBOOK (Análisis - Detallado)
```bash
jupyter notebook analysis.ipynb
```
**Contenido:**
- ✅ 10 secciones de análisis
- ✅ Visualizaciones con Matplotlib/Seaborn
- ✅ Cálculos estadísticos
- ✅ Executive summary
- ✅ Recomendaciones estratégicas

**Secciones:**
1. Importación de librerías
2. Conexión a BD
3-7. Un KPI por sección (análisis + visualización)
8. Resumen ejecutivo
9. Recomendaciones
10. Cierre de conexión

---

### 4️⃣ PNG VISUALIZATIONS (Estáticas - Reportes)
```
visualization/output/
├── kpi1_revenue_by_category.png       → Para presentaciones
├── kpi2_revenue_by_channel.png        → Para reportes
├── kpi3_monthly_trends.png            → Para PowerPoint
├── kpi4_brand_profitability.png       → Para emails
├── kpi_dashboard_comprehensive.png    → Dashboard 4-en-1
└── kpi_summary_report.txt             → Texto ejecutivo
```

---

## 📈 MÉTRICAS CLAVE (Resumen)

| Métrica | Valor |
|---------|-------|
| **Ingresos Totales** | $355,604.33 |
| **Ganancia Total** | $65,060.27 |
| **Margen Total** | 18.30% |
| **Transacciones** | 240 |
| **Clientes** | 24 |
| **Productos** | 40 |
| **Canales** | 3 |
| **Países** | 3 (Colombia, México, Chile) |
| **Período** | Q1 2026 (Ene-Abr) |
| **Transacción Promedio** | $1,481.68 |

---

## 🎯 TOP PERFORMERS

### 📌 Categoría Líder
- **Laptops:** $115,872.54 (32.6% del ingreso)
- Margen promedio: 18.92%

### 📌 Canal Principal  
- **Physical Stores:** 85%+ del ingreso
- Oportunidad: Expandir online

### 📌 Marca Top
- **Apple:** Máxima rentabilidad
- Desempeño consistente

### 📌 Mercado Líder
- **Colombia:** Mayor ingreso
- Chile muestra potencial de crecimiento

### 📌 Tendencia
- **Crecimiento:** +6.7% MoM promedio
- Marzo fue el mes con mejor desempeño

---

## 🔧 REQUISITOS TÉCNICOS

### Dependencias Instaladas
```
pandas         → Procesamiento de datos
numpy          → Cálculos numéricos
matplotlib     → Gráficos estáticos
seaborn        → Visualizaciones estadísticas
sqlite3        → Base de datos (incluido en Python)
tkinter        → GUI (incluido en Python)
```

### Verificar Instalación
```bash
python -c "import pandas, matplotlib, tkinter; print('[OK] All dependencies installed')"
```

---

## 💾 ARCHIVOS DE ENTRADA (Fuentes)

```
data/raw/
├── products.csv        (40 productos)
├── customers.csv       (24 clientes)
├── sales.csv          (240 transacciones)
└── channels.csv       (3 canales)
```

---

## 📝 SCRIPTS DE PIPELINE

```
ETL/
├── extract.py          → Lectura de CSV + validación
├── transform.py        → Creación de dimensiones y hechos
├── load.py            → Carga a SQLite + integridad
└── proto.ipynb        → Notebook original (34 celdas)

sql/
├── create_tables.sql  → DDL del warehouse
└── queries.sql        → 9 queries (6 KPIs + 3 bonus)

run.py                 → Orquestador principal del pipeline
```

---

## 🎓 ANÁLISIS GENERABLE

### Desde TKINTER (`kpi_viewer.py`)
```
KPI 1: Revenue by Category
├── Gráfico de barras horizontales
├── Gráfico de pastel (distribución de ganancia)
└── Tabla con datos completos

KPI 2: Revenue by Channel
├── Gráfico de barras comparativas
├── Gráfico de pastel (% por canal)
└── Análisis de valor promedio de transacción

KPI 3: Monthly Trends
├── Gráfico de línea (evolución)
├── Gráfico de barras (revenue vs profit)
└── Cálculo de crecimiento MoM

KPI 4: Brand Profitability
├── Top 8 brands ranking
├── Scatter plot (revenue vs profit)
└── Análisis de márgenes

KPI 5: Geographic Distribution
├── Revenue por país
├── Clientes vs transacciones
└── Análisis de penetración de mercado
```

---

## ⚡ GUÍA RÁPIDA

### Opción 1: Visualización Completa de Una Vez
```bash
# Ejecutar pipeline completo
python run.py

# Generar todas las visualizaciones
python visualization/kpi_dashboard.py

# Generar dashboard web
python generate_html_dashboard.py

# Abrir aplicación Tkinter
python kpi_viewer.py
```

### Opción 2: Análisis Interactivo (Recomendado)
```bash
# Abrir Jupyter
jupyter notebook analysis.ipynb

# O ejecutar Tkinter
python kpi_viewer.py

# O ver web
open visualization/output/dashboard.html
```

### Opción 3: Consultar BD Directamente
```bash
sqlite3 data/warehouse/datawarehouse.db

# Dentro de SQLite:
SELECT * FROM fact_sales LIMIT 10;
SELECT * FROM dim_product;
.quit
```

---

## ✅ CHECKLIST DE ENTREGA

- [x] Pipeline ETL completo (Extract → Transform → Load)
- [x] Base de datos SQLite con integridad referencial
- [x] 5 KPIs implementados y verificados
- [x] Dashboard Tkinter interactivo (5 pestañas)
- [x] Dashboard HTML web moderno con Chart.js
- [x] Jupyter Notebook con análisis completo
- [x] 5 visualizaciones PNG de alta calidad
- [x] Reporte ejecutivo en texto
- [x] Documentación completa (este archivo)
- [x] 0 errores de Unicode en Windows
- [x] 0 registros huérfanos en BD
- [x] Todas las recomendaciones de negocio

---

## 🎯 SIGUIENTES PASOS (Opcional)

1. **Predicción:** Implementar ARIMA para forecast mensual
2. **Segmentación:** Análisis de RFM para segmentación de clientes
3. **Alertas:** Configurar notificaciones para cambios KPI
4. **Automatización:** Scheduler para actualizar reportes diarios
5. **API:** Exponer KPIs mediante REST API

---

## 📞 SOPORTE

Para visualizar los datos:
1. **Recomendado:** `python kpi_viewer.py` (más interactivo)
2. **Alternativa:** Abrir `visualization/output/dashboard.html` en navegador
3. **Análisis Profundo:** `jupyter notebook analysis.ipynb`

---

**Proyecto completado exitosamente el 16 de febrero de 2026**  
**Cumple 100% de requisitos del curso ETL Lab 3**
