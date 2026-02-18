"""
Interactive KPI Dashboard Viewer
Visualizes data warehouse KPIs with tkinter GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pathlib import Path
import sys
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image, ImageTk
import io

class KPIViewerApp:
    """Interactive KPI viewer application"""


    def __init__(self, root):
        self.root = root
        self.root.title("Technology Retail Analytics - KPI Viewer")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f8f9fa")

        # Conexión a la base de datos
        self.conn = sqlite3.connect("data/warehouse/datawarehouse.db")

        # Set high DPI for crisp graphics
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        # Configure matplotlib for high quality
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 150
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['figure.titlesize'] = 14

        # Set custom window icon
        self.set_window_icon()

        # Create all widgets (fix blank screen)
        self.create_widgets()

    
    def set_window_icon(self):
        """Set custom window icon from SVG logo"""
        try:
            logo_path = Path("visualization/output/logo.svg")
            if logo_path.exists():
                # Convert SVG to PNG using svglib and reportlab
                drawing = svg2rlg(str(logo_path))
                # Scale the drawing to 64x64
                drawing.width = 64
                drawing.height = 64
                drawing.scale(64/drawing.width, 64/drawing.height)
                
                # Render to PNG in memory
                png_data = renderPM.drawToString(drawing, fmt='PNG')
                
                # Convert PNG data to PIL Image
                png_image = Image.open(io.BytesIO(png_data))
                
                # Convert to PhotoImage for Tkinter
                self.icon_photo = ImageTk.PhotoImage(png_image)
                
                # Set as window icon
                self.root.iconphoto(True, self.icon_photo)
        except Exception as e:
            print(f"Could not set custom icon: {e}")
            # Fallback to default icon
            pass
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Modern header with gradient
        header = tk.Frame(self.root, bg="#667eea", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Header content container
        header_content = tk.Frame(header, bg="#667eea")
        header_content.pack(expand=True, fill=tk.X, padx=30, pady=15)

        # Title with logo
        title_frame = tk.Frame(header_content, bg="#667eea")
        title_frame.pack(anchor=tk.CENTER)

        # Create logo canvas
        logo_canvas = tk.Canvas(
            title_frame,
            width=50, height=50,
            bg="#667eea",
            highlightthickness=0
        )
        logo_canvas.pack(side=tk.LEFT, padx=(0, 15))

        # Draw logo elements
        self.draw_logo(logo_canvas)

        title = tk.Label(
            title_frame,
            text="Technology Retail Analytics Dashboard",
            font=("Segoe UI", 20, "bold"),
            bg="#667eea",
            fg="white"
        )
        title.pack(side=tk.LEFT)

        # Subtitle
        subtitle = tk.Label(
            header_content,
            text="Interactive KPI Analysis - Q1 2026",
            font=("Segoe UI", 11),
            bg="#667eea",
            fg="#e8f4fd"
        )
        subtitle.pack(anchor=tk.CENTER, pady=(5, 0))

        # Modern notebook styling
        style = ttk.Style()
        style.configure("TNotebook", background="#f8f9fa", borderwidth=0)
        style.configure("TNotebook.Tab", background="#ffffff", padding=[15, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                 background=[("selected", "#667eea")],
                 foreground=[("selected", "white")])

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))

        # Create tabs with better styling
        self.tab1 = ttk.Frame(self.notebook, style="TFrame")
        self.tab2 = ttk.Frame(self.notebook, style="TFrame")
        self.tab3 = ttk.Frame(self.notebook, style="TFrame")
        self.tab4 = ttk.Frame(self.notebook, style="TFrame")
        self.tab5 = ttk.Frame(self.notebook, style="TFrame")

        self.notebook.add(self.tab1, text="📈 Revenue by Category")
        self.notebook.add(self.tab2, text="🏪 Revenue by Channel")
        self.notebook.add(self.tab3, text="📅 Monthly Trends")
        self.notebook.add(self.tab4, text="🏷️ Brand Profitability")
        self.notebook.add(self.tab5, text="🌍 Geographic Distribution")

        # Bind tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Modern status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="#2c3e50",
            fg="white",
            anchor=tk.CENTER,
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            padx=10,
            pady=8
        )
        status_bar.pack(fill=tk.X)
    
    def draw_logo(self, canvas):
        """Draw the TechRetail logo on canvas"""
        # Background circle with gradient effect (simulated)
        canvas.create_oval(2, 2, 48, 48, fill="#667eea", outline="#5a6fd8", width=2)

        # Inner circle for depth
        canvas.create_oval(4, 4, 46, 46, fill="#7c3aed", outline="")

        # Shopping cart body (white)
        canvas.create_rectangle(12, 22, 32, 34, fill="white", outline="white", width=1)

        # Cart handle
        canvas.create_line(14, 22, 14, 16, 18, 16, 18, 22, fill="white", width=2, smooth=True)

        # Cart wheels
        canvas.create_oval(10, 32, 16, 38, fill="white", outline="white", width=1)
        canvas.create_oval(28, 32, 34, 38, fill="white", outline="white", width=1)

        # Products in cart (colored rectangles)
        canvas.create_rectangle(14, 24, 18, 28, fill="#e74c3c", outline="#c0392b", width=1)  # Red product
        canvas.create_rectangle(20, 24, 24, 28, fill="#f39c12", outline="#e67e22", width=1)  # Orange product
        canvas.create_rectangle(26, 24, 30, 28, fill="#27ae60", outline="#229954", width=1)  # Green product

        # Tech elements (small circles)
        canvas.create_oval(38, 10, 42, 14, fill="#e74c3c", outline="#c0392b", width=1)
        canvas.create_oval(42, 16, 46, 20, fill="#f39c12", outline="#e67e22", width=1)
        canvas.create_oval(40, 22, 44, 26, fill="#9b59b6", outline="#8e44ad", width=1)
    
    def on_tab_change(self, event=None):
        """Handle tab change"""
        selected_tab = self.notebook.select()
        tab_index = self.notebook.index(selected_tab)
        
        if tab_index == 0:
            self.load_kpi1()
        elif tab_index == 1:
            self.load_kpi2()
        elif tab_index == 2:
            self.load_kpi3()
        elif tab_index == 3:
            self.load_kpi4()
        elif tab_index == 4:
            self.load_kpi5()
    
    def load_kpi1(self):
        """Load KPI 1: Revenue by Category"""
        self.clear_tab(self.tab1)
        self.status_var.set("Loading KPI 1: Revenue by Category...")
        self.root.update()
        
        query = """
        SELECT 
            p.category,
            COUNT(f.sales_key) as transactions,
            SUM(f.quantity) as total_quantity,
            ROUND(SUM(f.total_sales_amount), 2) as total_revenue,
            ROUND(SUM(f.profit), 2) as total_profit,
            ROUND(AVG(f.profit_margin), 2) as avg_margin
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.category
        ORDER BY total_revenue DESC
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Create figure with high quality settings
        fig = Figure(figsize=(14, 6), dpi=120, facecolor='white')
        fig.suptitle('KPI 1: Revenue by Category', fontsize=16, fontweight='bold', y=0.98)

        # Revenue bar chart
        ax1 = fig.add_subplot(1, 2, 1)
        colors = plt.cm.viridis([i/(len(df)-1) if len(df)>1 else 0.5 for i in range(len(df))])
        bars = ax1.barh(df['category'], df['total_revenue'], color=colors, alpha=0.8, height=0.7)
        ax1.set_xlabel('Total Revenue ($)', fontsize=12, fontweight='bold', labelpad=10)
        ax1.set_title('Revenue by Product Category', fontsize=14, fontweight='bold', pad=20)
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax1.set_axisbelow(True)

        # Add values on bars with better formatting
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2,
                    f'${width:,.0f}', va='center', fontweight='bold', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        # Profit pie chart
        ax2 = fig.add_subplot(1, 2, 2)
        wedges, texts, autotexts = ax2.pie(df['total_profit'], labels=df['category'], autopct='%1.1f%%',
               colors=colors, startangle=90, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
        ax2.set_title('Profit Distribution by Category', fontsize=14, fontweight='bold', pad=20)

        # Improve text styling
        for text in texts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
            autotext.set_color('white')

        fig.tight_layout(pad=3.0)
        
        # Embed matplotlib in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.tab1)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Data table
        self.create_data_table(self.tab1, df)
        
        self.status_var.set(f"KPI 1 loaded - {len(df)} categories")
    
    def load_kpi2(self):
        """Load KPI 2: Revenue by Channel"""
        self.clear_tab(self.tab2)
        self.status_var.set("Loading KPI 2: Revenue by Channel...")
        self.root.update()
        
        query = """
        SELECT 
            c.channel,
            COUNT(f.sales_key) as transactions,
            SUM(f.quantity) as total_quantity,
            ROUND(SUM(f.total_sales_amount), 2) as total_revenue,
            ROUND(SUM(f.profit), 2) as total_profit,
            ROUND(100 * SUM(f.total_sales_amount) / 
                (SELECT SUM(total_sales_amount) FROM fact_sales), 2) as revenue_pct,
            ROUND(AVG(f.total_sales_amount), 2) as avg_transaction
        FROM fact_sales f
        JOIN dim_channel c ON f.channel_key = c.channel_key
        GROUP BY c.channel
        ORDER BY total_revenue DESC
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Create figure
        fig = Figure(figsize=(12, 5), dpi=100)
        
        # Revenue comparison
        ax1 = fig.add_subplot(1, 2, 1)
        colors = ['#3498db', '#e74c3c', '#2ecc71'][:len(df)]
        bars = ax1.bar(df['channel'], df['total_revenue'], color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Revenue ($)', fontweight='bold')
        ax1.set_title('Revenue by Channel', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        # Add values on bars
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}',
                    ha='center', va='bottom', fontweight='bold')
        
        # Pie chart
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.pie(df['total_revenue'], labels=df['channel'], autopct='%1.1f%%', 
               colors=colors, startangle=90)
        ax2.set_title('Revenue Distribution', fontweight='bold')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.tab2)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_data_table(self.tab2, df)
        
        self.status_var.set(f"KPI 2 loaded - {len(df)} channels")
    
    def load_kpi3(self):
        """Load KPI 3: Monthly Trends"""
        self.clear_tab(self.tab3)
        self.status_var.set("Loading KPI 3: Monthly Trends...")
        self.root.update()
        
        query = """
        SELECT 
            d.month,
            d.month_name,
            COUNT(f.sales_key) as transactions,
            SUM(f.quantity) as total_units,
            ROUND(SUM(f.total_sales_amount), 2) as monthly_revenue,
            ROUND(SUM(f.profit), 2) as monthly_profit,
            ROUND(AVG(f.total_sales_amount), 2) as avg_transaction,
            ROUND((SUM(f.profit) / SUM(f.total_sales_amount) * 100), 2) as margin_pct
        FROM fact_sales f
        JOIN dim_date d ON f.date_id = d.date_id
        GROUP BY d.month, d.month_name
        ORDER BY d.month
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Create figure
        fig = Figure(figsize=(12, 5), dpi=100)
        
        # Line chart
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.plot(df['month_name'], df['monthly_revenue'], marker='o', linewidth=2, 
                markersize=8, color='#3498db', label='Revenue')
        ax1.fill_between(range(len(df['month_name'])), df['monthly_revenue'], alpha=0.3)
        ax1.set_ylabel('Revenue ($)', fontweight='bold')
        ax1.set_title('Monthly Revenue Trend', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Profit comparison
        ax2 = fig.add_subplot(1, 2, 2)
        x = range(len(df))
        width = 0.35
        ax2.bar([i - width/2 for i in x], df['monthly_revenue'], width, label='Revenue', color='#3498db', alpha=0.7)
        ax2.bar([i + width/2 for i in x], df['monthly_profit'], width, label='Profit', color='#2ecc71', alpha=0.7)
        ax2.set_ylabel('Amount ($)', fontweight='bold')
        ax2.set_title('Revenue vs Profit', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['month_name'], rotation=45)
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.tab3)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_data_table(self.tab3, df)
        
        self.status_var.set(f"KPI 3 loaded - {len(df)} months")
    
    def load_kpi4(self):
        """Load KPI 4: Brand Profitability"""
        self.clear_tab(self.tab4)
        self.status_var.set("Loading KPI 4: Brand Profitability...")
        self.root.update()
        
        query = """
        SELECT 
            p.brand,
            COUNT(f.sales_key) as transactions,
            SUM(f.quantity) as total_units,
            ROUND(SUM(f.total_sales_amount), 2) as brand_revenue,
            ROUND(SUM(f.profit), 2) as brand_profit,
            ROUND(AVG(f.profit_margin), 2) as avg_margin,
            ROUND((SUM(f.profit) / SUM(f.total_sales_amount) * 100), 2) as profit_margin_pct
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.brand
        ORDER BY brand_profit DESC
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Create figure
        fig = Figure(figsize=(12, 5), dpi=100)
        
        # Top 8 brands
        top_df = df.head(8)
        
        # Profit ranking
        ax1 = fig.add_subplot(1, 2, 1)
        colors = plt.cm.RdYlGn([0.3 + i * (0.6/(len(top_df)-1)) if len(top_df)>1 else 0.6 for i in range(len(top_df))])
        bars = ax1.barh(top_df['brand'], top_df['brand_profit'], color=colors, alpha=0.8, height=0.7)
        ax1.set_xlabel('Profit ($)', fontsize=12, fontweight='bold', labelpad=10)
        ax1.set_title('Top 8 Brands by Profit', fontsize=14, fontweight='bold', pad=20)
        ax1.grid(axis='x', alpha=0.3, linestyle='--')
        ax1.set_axisbelow(True)

        # Add values on bars
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + (width * 0.01), bar.get_y() + bar.get_height()/2,
                    f'${width:,.0f}', va='center', fontweight='bold', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # Scatter: Revenue vs Profit
        ax2 = fig.add_subplot(1, 2, 2)
        scatter = ax2.scatter(df['brand_revenue'], df['brand_profit'],
                             s=100, alpha=0.7, c=df['profit_margin_pct'],
                             cmap='viridis', edgecolors='white', linewidth=1)

        # Add brand labels with better positioning to avoid overlaps
        # Only label top brands to avoid clutter
        top_brands_for_labels = df.nlargest(6, 'brand_profit')  # Top 6 brands

        for idx, row in top_brands_for_labels.iterrows():
            # Calculate offset based on data range
            x_range = df['brand_revenue'].max() - df['brand_revenue'].min()
            y_range = df['brand_profit'].max() - df['brand_profit'].min()
            x_offset = x_range * 0.03  # 3% of x range
            y_offset = y_range * 0.02  # 2% of y range

            ax2.annotate(row['brand'],
                        (row['brand_revenue'] + x_offset, row['brand_profit'] + y_offset),
                        fontsize=9, fontweight='bold', alpha=0.9,
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.9, edgecolor="gray", linewidth=0.5))

        # Add a note about unlabeled points
        if len(df) > 6:
            ax2.text(0.02, 0.98, 'Only top 6 brands labeled',
                    transform=ax2.transAxes, fontsize=8, alpha=0.7,
                    verticalalignment='top', bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
        ax2.set_xlabel('Revenue ($)', fontsize=12, fontweight='bold', labelpad=10)
        ax2.set_ylabel('Profit ($)', fontsize=12, fontweight='bold', labelpad=10)
        ax2.set_title('Revenue vs Profit by Brand', fontsize=14, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_axisbelow(True)

        # Format axis labels with thousands separator
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        cbar = fig.colorbar(scatter, ax=ax2, shrink=0.8)
        cbar.set_label('Profit Margin %', fontsize=11, fontweight='bold', labelpad=10)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.tab4)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_data_table(self.tab4, df)
        
        self.status_var.set(f"KPI 4 loaded - {len(df)} brands")
    
    def load_kpi5(self):
        """Load KPI 5: Geographic Distribution"""
        self.clear_tab(self.tab5)
        self.status_var.set("Loading KPI 5: Geographic Distribution...")
        self.root.update()
        
        query = """
        SELECT 
            c.country,
            COUNT(DISTINCT c.customer_key) as unique_customers,
            COUNT(f.sales_key) as total_transactions,
            SUM(f.quantity) as total_units,
            ROUND(SUM(f.total_sales_amount), 2) as country_revenue,
            ROUND(SUM(f.profit), 2) as country_profit,
            ROUND(AVG(f.total_sales_amount), 2) as avg_transaction,
            ROUND((SUM(f.profit) / SUM(f.total_sales_amount) * 100), 2) as margin_pct
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        GROUP BY c.country
        ORDER BY country_revenue DESC
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Create figure
        fig = Figure(figsize=(12, 5), dpi=100)
        
        # Revenue by country
        ax1 = fig.add_subplot(1, 2, 1)
        colors = ['#e74c3c', '#3498db', '#2ecc71'][:len(df)]
        bars = ax1.bar(df['country'], df['country_revenue'], color=colors, alpha=0.7, edgecolor='black')
        ax1.set_ylabel('Revenue ($)', fontweight='bold')
        ax1.set_title('Revenue by Country', fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)
        
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}',
                    ha='center', va='bottom', fontweight='bold')
        
        # Transactions vs Customers
        ax2 = fig.add_subplot(1, 2, 2)
        x = range(len(df))
        width = 0.35
        ax2.bar([i - width/2 for i in x], df['unique_customers'], width, 
               label='Unique Customers', color='#9b59b6', alpha=0.7)
        ax2.bar([i + width/2 for i in x], df['total_transactions'], width, 
               label='Transactions', color='#f39c12', alpha=0.7)
        ax2.set_ylabel('Count', fontweight='bold')
        ax2.set_title('Customers vs Transactions', fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df['country'])
        ax2.legend()
        ax2.grid(axis='y', alpha=0.3)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.tab5)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.create_data_table(self.tab5, df)
        
        self.status_var.set(f"KPI 5 loaded - {len(df)} countries")
    
    def create_data_table(self, parent, df):
        """Create a modern data table frame"""
        # Container frame with padding
        container = tk.Frame(parent, bg="#f8f9fa")
        container.pack(fill=tk.BOTH, expand=False, padx=10, pady=(10, 20))

        # Title
        title_label = tk.Label(
            container,
            text="📋 Detailed Data Table",
            font=("Segoe UI", 12, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # Table frame with border
        table_frame = tk.Frame(container, bg="white", relief=tk.RIDGE, borderwidth=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Configure treeview style
        style = ttk.Style()
        style.configure("Modern.Treeview",
                       background="white",
                       foreground="#2c3e50",
                       rowheight=25,
                       fieldbackground="white",
                       font=("Segoe UI", 9))
        style.configure("Modern.Treeview.Heading",
                       background="#667eea",
                       foreground="white",
                       font=("Segoe UI", 10, "bold"),
                       padding=[5, 5])
        style.map("Modern.Treeview.Heading",
                 background=[("active", "#5a6fd8")])

        # Create treeview
        columns = list(df.columns)
        tree = ttk.Treeview(table_frame, columns=columns, height=8, show='headings', style="Modern.Treeview")

        # Define headings and columns with better formatting
        for col in columns:
            # Format column names
            display_name = col.replace('_', ' ').title()
            tree.heading(col, text=display_name, anchor=tk.CENTER)

            # Set column width based on content
            max_length = max(len(str(val)) for val in df[col])
            width = min(max(max_length * 8, 80), 150)  # Min 80, max 150 pixels
            tree.column(col, width=width, anchor=tk.CENTER, stretch=False)

        # Add data with alternating row colors
        for idx, row in df.iterrows():
            values = []
            for col in columns:
                val = row[col]
                # Format numbers nicely
                if isinstance(val, (int, float)) and not pd.isna(val):
                    if col in ['total_revenue', 'total_profit', 'brand_revenue', 'brand_profit', 'country_revenue', 'country_profit', 'monthly_revenue', 'monthly_profit', 'avg_transaction']:
                        values.append(f"${val:,.2f}")
                    elif col in ['revenue_pct', 'margin_pct', 'profit_margin_pct', 'avg_margin']:
                        values.append(f"{val:.2f}%")
                    elif isinstance(val, int):
                        values.append(f"{int(val):,}")
                    else:
                        values.append(f"{val:.2f}")
                else:
                    values.append(str(val))

            # Alternate row colors
            tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)
            tree.insert('', 'end', values=values, tags=tags)

        # Configure row colors
        tree.tag_configure('evenrow', background='#f8f9fa')
        tree.tag_configure('oddrow', background='white')

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscroll=v_scrollbar.set, xscroll=h_scrollbar.set)

        # Pack elements
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
    
    def clear_tab(self, tab):
        """Clear tab contents"""
        for widget in tab.winfo_children():
            widget.destroy()
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()


def main():
    root = tk.Tk()
    app = KPIViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
