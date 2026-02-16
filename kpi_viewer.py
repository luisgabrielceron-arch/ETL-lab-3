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

class KPIViewerApp:
    """Interactive KPI viewer application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Technology Retail Analytics - KPI Viewer")
        self.root.geometry("1200x700")
        self.root.configure(bg="#f0f0f0")
        
        # Database path
        self.db_path = Path("data/warehouse/datawarehouse.db")
        self.conn = None
        
        # Connect to database
        if not self.connect_db():
            messagebox.showerror("Error", "Cannot connect to database")
            sys.exit(1)
        
        # Create GUI
        self.create_widgets()
        self.load_kpi1()
    
    def connect_db(self):
        """Connect to database"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header, 
            text="Technology Retail Analytics Dashboard",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title.pack(pady=10)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)
        self.tab4 = ttk.Frame(self.notebook)
        self.tab5 = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab1, text="KPI 1: Revenue by Category")
        self.notebook.add(self.tab2, text="KPI 2: Revenue by Channel")
        self.notebook.add(self.tab3, text="KPI 3: Monthly Trends")
        self.notebook.add(self.tab4, text="KPI 4: Brand Profitability")
        self.notebook.add(self.tab5, text="KPI 5: Geographic Distribution")
        
        # Bind tab change
        self.notebook.bind("<Change>", self.on_tab_change)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="#34495e",
            fg="white",
            anchor=tk.W,
            relief=tk.SUNKEN
        )
        status_bar.pack(fill=tk.X)
    
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
        
        # Create figure with subplots
        fig = Figure(figsize=(12, 5), dpi=100)
        
        # Revenue bar chart
        ax1 = fig.add_subplot(1, 2, 1)
        colors = plt.cm.viridis(range(len(df)))
        ax1.barh(df['category'], df['total_revenue'], color=colors)
        ax1.set_xlabel('Revenue ($)', fontweight='bold')
        ax1.set_title('Revenue by Category', fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Margin pie chart
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.pie(df['total_profit'], labels=df['category'], autopct='%1.1f%%', startangle=90)
        ax2.set_title('Profit Distribution', fontweight='bold')
        
        fig.tight_layout()
        
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
        colors = plt.cm.RdYlGn(range(len(top_df)))
        ax1.barh(top_df['brand'], top_df['brand_profit'], color=colors)
        ax1.set_xlabel('Profit ($)', fontweight='bold')
        ax1.set_title('Top 8 Brands by Profit', fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # Scatter: Revenue vs Profit
        ax2 = fig.add_subplot(1, 2, 2)
        scatter = ax2.scatter(df['brand_revenue'], df['brand_profit'], 
                             s=200, alpha=0.6, c=df['profit_margin_pct'], 
                             cmap='viridis', edgecolors='black')
        
        for idx, row in df.iterrows():
            ax2.annotate(row['brand'], 
                        (row['brand_revenue'], row['brand_profit']),
                        fontsize=8, alpha=0.7)
        
        ax2.set_xlabel('Revenue ($)', fontweight='bold')
        ax2.set_ylabel('Profit ($)', fontweight='bold')
        ax2.set_title('Revenue vs Profit by Brand', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        cbar = fig.colorbar(scatter, ax=ax2)
        cbar.set_label('Margin %', fontweight='bold')
        
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
        """Create a data table frame"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Create treeview
        columns = list(df.columns)
        tree = ttk.Treeview(table_frame, columns=columns, height=6, show='headings')
        
        # Define headings and columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80, anchor=tk.CENTER)
        
        # Add data
        for idx, row in df.iterrows():
            values = [str(row[col]) for col in columns]
            tree.insert('', 'end', values=values)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(xscroll=scrollbar.set)
        
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def clear_tab(self, tab):
        """Clear tab contents"""
        for widget in tab.winfo_children():
            widget.destroy()
    
    def __del__(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    root = tk.Tk()
    app = KPIViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
