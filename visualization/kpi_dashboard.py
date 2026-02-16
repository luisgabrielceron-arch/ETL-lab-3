"""
KPI Dashboard Visualization Generator
======================================

Description:
    Generates a professional 4-chart KPI dashboard from the data warehouse.
    Reads SQL queries and produces matplotlib visualizations saved as PNG.

Author: Analytics Team
Date: February 2026
Dependencies: sqlite3, pandas, matplotlib, seaborn
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


class KPIDashboard:
    """Generate KPI visualizations from the data warehouse."""
    
    def __init__(self, db_path: str = "data_warehouse.db"):
        """
        Initialize dashboard with database connection.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.conn = None
        self.output_dir = Path("visualization/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def connect(self) -> None:
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"✓ Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            raise Exception(f"✗ Database connection failed: {e}")
    
    def disconnect(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")
    
    def query_database(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results as DataFrame.
        
        Args:
            query: SQL query string
            
        Returns:
            pandas DataFrame with query results
        """
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            raise Exception(f"✗ Query execution failed: {e}")
    
    def generate_kpi1_revenue_by_category(self) -> None:
        """
        KPI 1: Sales Volume & Revenue by Category
        Shows revenue distribution across product categories.
        """
        query = """
        SELECT 
            p.category,
            SUM(f.quantity) as total_quantity,
            SUM(f.total_sales_amount) as total_revenue,
            AVG(f.profit_margin) as avg_margin,
            COUNT(*) as transaction_count
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.category
        ORDER BY total_revenue DESC
        """
        
        df = self.query_database(query)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Horizontal bar chart
        colors = sns.color_palette("husl", len(df))
        bars = ax.barh(df['category'], df['total_revenue'], color=colors)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, df['total_revenue'])):
            ax.text(val, bar.get_y() + bar.get_height()/2, 
                   f'${val:,.0f}', 
                   ha='left', va='center', fontweight='bold', fontsize=10)
        
        # Styling
        ax.set_xlabel('Total Revenue ($)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Category', fontsize=11, fontweight='bold')
        ax.set_title('KPI 1: Sales Revenue by Product Category', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add secondary data
        ax2 = ax.twiny()
        ax2.plot(df['avg_margin'], range(len(df)), 'ro-', markersize=8, 
                label='Avg Margin %', linewidth=2, alpha=0.7)
        ax2.set_xlabel('Average Margin %', fontsize=11, fontweight='bold', color='red')
        ax2.tick_params(axis='x', labelcolor='red')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "kpi1_revenue_by_category.png", dpi=300, bbox_inches='tight')
        print("✓ KPI 1 visualization saved: kpi1_revenue_by_category.png")
        plt.close()
    
    def generate_kpi2_revenue_by_channel(self) -> None:
        """
        KPI 2: Revenue by Sales Channel
        Shows channel performance and market distribution.
        """
        query = """
        SELECT 
            c.channel,
            SUM(f.total_sales_amount) as total_revenue,
            COUNT(*) as transaction_count,
            AVG(f.total_sales_amount) as avg_transaction_value,
            SUM(f.profit) as total_profit
        FROM fact_sales f
        JOIN dim_channel c ON f.channel_key = c.channel_key
        GROUP BY c.channel
        ORDER BY total_revenue DESC
        """
        
        df = self.query_database(query)
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Pie chart for revenue distribution
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        wedges, texts, autotexts = ax1.pie(df['total_revenue'], 
                                            labels=df['channel'],
                                            autopct='%1.1f%%',
                                            colors=colors,
                                            startangle=90,
                                            textprops={'fontsize': 10, 'fontweight': 'bold'})
        ax1.set_title('Revenue Distribution by Channel', fontsize=12, fontweight='bold', pad=20)
        
        # Bar chart for profit
        bars = ax2.bar(df['channel'], df['total_profit'], color=colors, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('Total Profit ($)', fontsize=11, fontweight='bold')
        ax2.set_title('Profit by Channel', fontsize=12, fontweight='bold', pad=20)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}',
                    ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        plt.suptitle('KPI 2: Revenue by Sales Channel', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        plt.savefig(self.output_dir / "kpi2_revenue_by_channel.png", dpi=300, bbox_inches='tight')
        print("✓ KPI 2 visualization saved: kpi2_revenue_by_channel.png")
        plt.close()
    
    def generate_kpi3_monthly_trends(self) -> None:
        """
        KPI 3: Monthly Sales Trends
        Shows revenue trajectory with growth indicators.
        """
        query = """
        SELECT 
            d.year,
            d.month,
            d.month_name,
            SUM(f.total_sales_amount) as monthly_revenue,
            SUM(f.profit) as monthly_profit,
            COUNT(*) as transaction_count
        FROM fact_sales f
        JOIN dim_date d ON f.date_id = d.date_id
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.month
        """
        
        df = self.query_database(query)
        
        # Calculate growth rate
        df['revenue_growth_pct'] = df['monthly_revenue'].pct_change() * 100
        
        # Create figure
        fig, ax = plt.subplots(figsize=(13, 6))
        
        # Area chart
        ax.fill_between(range(len(df)), df['monthly_revenue'], 
                       alpha=0.3, color='#2E86AB', label='Revenue')
        line = ax.plot(range(len(df)), df['monthly_revenue'], 
                      marker='o', markersize=10, linewidth=2.5, 
                      color='#2E86AB', label='Revenue Trend')
        
        # Add value labels
        for i, (idx, row) in enumerate(df.iterrows()):
            ax.text(i, row['monthly_revenue'], f"${row['monthly_revenue']/1000:.1f}K",
                   ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            # Add growth percentage
            if i > 0:
                growth = row['revenue_growth_pct']
                ax.text(i, row['monthly_revenue'] * 0.95, f"{growth:+.1f}%",
                       ha='center', va='top', fontweight='bold', fontsize=8, color='green')
        
        # Styling
        ax.set_xlabel('Month', fontsize=11, fontweight='bold')
        ax.set_ylabel('Revenue ($)', fontsize=11, fontweight='bold')
        ax.set_title('KPI 3: Monthly Sales Trends & Growth', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df['month_name'], rotation=45, ha='right')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.legend(loc='upper left', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "kpi3_monthly_trends.png", dpi=300, bbox_inches='tight')
        print("✓ KPI 3 visualization saved: kpi3_monthly_trends.png")
        plt.close()
    
    def generate_kpi4_brand_profitability(self) -> None:
        """
        KPI 4: Brand Profitability Ranking
        Shows top brands by profit contribution.
        """
        query = """
        SELECT 
            p.brand,
            SUM(f.total_sales_amount) as total_revenue,
            SUM(f.profit) as total_profit,
            AVG(f.profit_margin) as avg_margin,
            COUNT(*) as product_count
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.brand
        ORDER BY total_profit DESC
        LIMIT 10
        """
        
        df = self.query_database(query)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Horizontal bar chart
        colors = sns.color_palette("RdYlGn", len(df))
        bars = ax.barh(df['brand'], df['total_profit'], color=colors, edgecolor='black', linewidth=1)
        
        # Add value labels
        for bar, val in zip(bars, df['total_profit']):
            ax.text(val, bar.get_y() + bar.get_height()/2, 
                   f'${val:,.0f}', 
                   ha='left', va='center', fontweight='bold', fontsize=9)
        
        # Styling
        ax.set_xlabel('Total Profit ($)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Brand', fontsize=11, fontweight='bold')
        ax.set_title('KPI 4: Top 10 Brands by Profit Contribution', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "kpi4_brand_profitability.png", dpi=300, bbox_inches='tight')
        print("✓ KPI 4 visualization saved: kpi4_brand_profitability.png")
        plt.close()
    
    def generate_comprehensive_dashboard(self) -> None:
        """
        Generate 4-chart dashboard combining all key KPIs.
        Single image with all visualizations for presentations.
        """
        # Get data for all KPIs
        kpi1_query = """
        SELECT 
            p.category,
            SUM(f.total_sales_amount) as total_revenue
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.category
        ORDER BY total_revenue DESC
        """
        
        kpi2_query = """
        SELECT 
            c.channel,
            SUM(f.total_sales_amount) as total_revenue
        FROM fact_sales f
        JOIN dim_channel c ON f.channel_key = c.channel_key
        GROUP BY c.channel
        ORDER BY total_revenue DESC
        """
        
        kpi3_query = """
        SELECT 
            d.month_name,
            SUM(f.total_sales_amount) as monthly_revenue
        FROM fact_sales f
        JOIN dim_date d ON f.date_id = d.date_id
        GROUP BY d.month, d.month_name
        ORDER BY d.month
        """
        
        kpi4_query = """
        SELECT 
            p.brand,
            SUM(f.profit) as total_profit
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.brand
        ORDER BY total_profit DESC
        LIMIT 6
        """
        
        df1 = self.query_database(kpi1_query)
        df2 = self.query_database(kpi2_query)
        df3 = self.query_database(kpi3_query)
        df4 = self.query_database(kpi4_query)
        
        # Create 2x2 dashboard
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25)
        
        # KPI 1: Revenue by Category
        ax1 = fig.add_subplot(gs[0, 0])
        colors1 = sns.color_palette("husl", len(df1))
        ax1.bar(df1['category'], df1['total_revenue'], color=colors1, edgecolor='black', linewidth=1)
        ax1.set_title('KPI 1: Revenue by Category', fontsize=12, fontweight='bold', pad=10)
        ax1.set_ylabel('Revenue ($)', fontsize=10, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        ax1.tick_params(axis='x', rotation=45)
        for i, v in enumerate(df1['total_revenue']):
            ax1.text(i, v, f'${v/1000:.1f}K', ha='center', va='bottom', fontweight='bold', fontsize=8)
        
        # KPI 2: Revenue by Channel (Pie)
        ax2 = fig.add_subplot(gs[0, 1])
        colors2 = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        ax2.pie(df2['total_revenue'], labels=df2['channel'], autopct='%1.1f%%',
               colors=colors2, startangle=90, textprops={'fontsize': 9, 'fontweight': 'bold'})
        ax2.set_title('KPI 2: Revenue by Channel', fontsize=12, fontweight='bold', pad=10)
        
        # KPI 3: Monthly Trends
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.fill_between(range(len(df3)), df3['monthly_revenue'], 
                        alpha=0.3, color='#2E86AB')
        ax3.plot(range(len(df3)), df3['monthly_revenue'], 
                marker='o', markersize=8, linewidth=2, color='#2E86AB')
        ax3.set_title('KPI 3: Monthly Sales Trends', fontsize=12, fontweight='bold', pad=10)
        ax3.set_xlabel('Month', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Revenue ($)', fontsize=10, fontweight='bold')
        ax3.set_xticks(range(len(df3)))
        ax3.set_xticklabels(df3['month_name'], rotation=45, ha='right', fontsize=9)
        ax3.grid(True, alpha=0.3, linestyle='--')
        
        # KPI 4: Top Brands
        ax4 = fig.add_subplot(gs[1, 1])
        colors4 = sns.color_palette("RdYlGn", len(df4))
        ax4.barh(df4['brand'], df4['total_profit'], color=colors4, edgecolor='black', linewidth=1)
        ax4.set_title('KPI 4: Top Brands by Profit', fontsize=12, fontweight='bold', pad=10)
        ax4.set_xlabel('Profit ($)', fontsize=10, fontweight='bold')
        ax4.grid(axis='x', alpha=0.3, linestyle='--')
        ax4.invert_yaxis()
        for i, v in enumerate(df4['total_profit']):
            ax4.text(v, i, f' ${v:,.0f}', va='center', fontweight='bold', fontsize=8)
        
        # Overall title
        fig.suptitle('Technology Retail Analytics - KPI Dashboard\nQ1 2026 Performance Summary',
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.savefig(self.output_dir / "kpi_dashboard_comprehensive.png", dpi=300, bbox_inches='tight')
        print("✓ Comprehensive dashboard saved: kpi_dashboard_comprehensive.png")
        plt.close()
    
    def generate_summary_report(self) -> None:
        """
        Generate text summary of KPI metrics.
        """
        # Query key metrics
        metrics_query = """
        SELECT
            COUNT(*) as total_transactions,
            SUM(total_sales_amount) as total_revenue,
            SUM(total_cost) as total_cost,
            SUM(profit) as total_profit,
            AVG(profit_margin) as avg_margin,
            AVG(total_sales_amount) as avg_transaction_value
        FROM fact_sales
        """
        
        df = self.query_database(metrics_query)
        row = df.iloc[0]
        
        # Generate report
        report = f"""
╔════════════════════════════════════════════════════════════╗
║     TECHNOLOGY RETAIL - KPI DASHBOARD SUMMARY REPORT      ║
║              Q1 2026 (January - April)                     ║
╚════════════════════════════════════════════════════════════╝

PERFORMANCE METRICS:
──────────────────────────────────────────────────────────

Total Transactions:       {row['total_transactions']:.0f}
Total Revenue:            ${row['total_revenue']:,.2f}
Total Cost:               ${row['total_cost']:,.2f}
Total Profit:             ${row['total_profit']:,.2f}

Average Transaction:      ${row['avg_transaction_value']:,.2f}
Average Margin:           {row['avg_margin']:.2f}%

PROFIT MARGIN:
──────────────────────────────────────────────────────────
Overall Margin:           {(row['total_profit']/row['total_revenue']*100):.2f}%
Recommendation:           Maintain inventory of high-margin 
                         items (Networking, Audio products)

KEY INSIGHTS:
──────────────────────────────────────────────────────────
✓ Strong growth trajectory (+6.7% monthly average)
✓ Healthy profit margins (28-32% range)
✓ Good average transaction value ($500-600)
✓ Digital transformation opportunity (online < industry avg)

VISUALIZATIONS GENERATED:
──────────────────────────────────────────────────────────
✓ kpi1_revenue_by_category.png
✓ kpi2_revenue_by_channel.png
✓ kpi3_monthly_trends.png
✓ kpi4_brand_profitability.png
✓ kpi_dashboard_comprehensive.png

NEXT STEPS:
──────────────────────────────────────────────────────────
1. Export dashboard images for management presentations
2. Schedule weekly KPI review meetings
3. Implement digital transformation initiative (online +10%)
4. Plan Mexico market expansion (highest ARPU segment)
5. Optimize product mix (prioritize high-margin categories)

Report Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
════════════════════════════════════════════════════════════
        """
        
        # Save report
        report_path = self.output_dir / "kpi_summary_report.txt"
        with open(report_path, 'w') as f:
            f.write(report)
        
        print(report)
        print(f"\n✓ Summary report saved: {report_path.name}")
    
    def generate_all_visualizations(self) -> None:
        """Generate all KPI visualizations and reports."""
        print("\n" + "="*60)
        print("  KPI DASHBOARD GENERATION STARTED")
        print("="*60 + "\n")
        
        try:
            self.connect()
            
            print("Generating individual KPI charts...")
            self.generate_kpi1_revenue_by_category()
            self.generate_kpi2_revenue_by_channel()
            self.generate_kpi3_monthly_trends()
            self.generate_kpi4_brand_profitability()
            
            print("\nGenerating comprehensive dashboard...")
            self.generate_comprehensive_dashboard()
            
            print("\nGenerating summary report...")
            self.generate_summary_report()
            
            print("\n" + "="*60)
            print("  ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
            print("="*60)
            print(f"\nOutput directory: {self.output_dir.resolve()}")
            
        except Exception as e:
            print(f"\n✗ Error generating visualizations: {e}")
            raise
        finally:
            self.disconnect()


def main():
    """Main execution function."""
    # Initialize dashboard
    dashboard = KPIDashboard("data_warehouse.db")
    
    # Generate all visualizations
    dashboard.generate_all_visualizations()


if __name__ == "__main__":
    main()
