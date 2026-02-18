"""
Generate interactive HTML dashboard from KPI data
Creates a self-contained HTML file with all charts and data
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

class HTMLDashboardGenerator:
    """Generate interactive HTML dashboard"""
    
    def __init__(self, db_path="data/warehouse/datawarehouse.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.output_dir = Path("visualization/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_kpi1(self):
        """KPI 1: Revenue by Category"""
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
        return pd.read_sql_query(query, self.conn)
    
    def get_kpi2(self):
        """KPI 2: Revenue by Channel"""
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
        return pd.read_sql_query(query, self.conn)
    
    def get_kpi3(self):
        """KPI 3: Monthly Trends"""
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
        return pd.read_sql_query(query, self.conn)
    
    def get_kpi4(self):
        """KPI 4: Brand Profitability"""
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
        return pd.read_sql_query(query, self.conn)
    
    def get_kpi5(self):
        """KPI 5: Geographic Distribution"""
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
        return pd.read_sql_query(query, self.conn)
    
    def generate_html(self):
        """Generate complete HTML dashboard"""
        df1 = self.get_kpi1()
        df2 = self.get_kpi2()
        df3 = self.get_kpi3()
        df4 = self.get_kpi4()
        df5 = self.get_kpi5()
        
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Technology Retail Analytics Dashboard</title>
    <link rel="icon" type="image/svg+xml" href="logo.svg">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            border-radius: 10px 10px 0 0;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 0;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #7f8c8d;
            font-size: 1.1em;
        }
        
        nav {
            background: white;
            padding: 0 30px;
            border-bottom: 1px solid #ecf0f1;
            display: flex;
            gap: 10px;
            box-shadow: 0 -2px 4px rgba(0,0,0,0.05);
        }
        
        nav button {
            background: none;
            border: none;
            padding: 15px 20px;
            cursor: pointer;
            font-size: 1em;
            color: #7f8c8d;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        
        nav button:hover {
            color: #2c3e50;
        }
        
        nav button.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: bold;
        }
        
        .content {
            background: white;
            border-radius: 0 0 10px 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 30px;
            margin-bottom: 30px;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            position: relative;
            height: 350px;
        }
        
        .chart-container h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
        }
        
        .data-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        .data-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        .data-table tr:hover {
            background: #ecf0f1;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .metric-card h4 {
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        
        .metric-card .value {
            font-size: 1.8em;
            font-weight: bold;
        }
        
        footer {
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 0.9em;
        }
        
        .kpi-title {
            color: #2c3e50;
            font-size: 1.3em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        
        @media (max-width: 768px) {
            .kpi-grid {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 1.8em;
            }
            
            nav {
                flex-wrap: wrap;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Technology Retail Analytics</h1>
            <p class="subtitle">Interactive KPI Dashboard - Q1 2026</p>
        </header>
        
        <nav>
            <button class="tab-btn active" onclick="showTab('tab1')">KPI 1: Categories</button>
            <button class="tab-btn" onclick="showTab('tab2')">KPI 2: Channels</button>
            <button class="tab-btn" onclick="showTab('tab3')">KPI 3: Trends</button>
            <button class="tab-btn" onclick="showTab('tab4')">KPI 4: Brands</button>
            <button class="tab-btn" onclick="showTab('tab5')">KPI 5: Geography</button>
        </nav>
        
        <div class="content">
            <!-- KPI 1 -->
            <div id="tab1" class="tab-content active">
                <h2 class="kpi-title">KPI 1: Sales Volume & Revenue by Product Category</h2>
                <div class="kpi-grid">
                    <div class="chart-container">
                        <h3>Revenue by Category</h3>
                        <canvas id="chart1a"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>Profit Distribution</h3>
                        <canvas id="chart1b"></canvas>
                    </div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Transactions</th>
                            <th>Quantity</th>
                            <th>Revenue</th>
                            <th>Profit</th>
                            <th>Avg Margin %</th>
                        </tr>
                    </thead>
                    <tbody id="table1"></tbody>
                </table>
            </div>
            
            <!-- KPI 2 -->
            <div id="tab2" class="tab-content">
                <h2 class="kpi-title">KPI 2: Revenue by Sales Channel</h2>
                <div class="kpi-grid">
                    <div class="chart-container">
                        <h3>Channel Revenue</h3>
                        <canvas id="chart2a"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>Revenue Distribution %</h3>
                        <canvas id="chart2b"></canvas>
                    </div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Channel</th>
                            <th>Transactions</th>
                            <th>Quantity</th>
                            <th>Revenue</th>
                            <th>Profit</th>
                            <th>Revenue %</th>
                            <th>Avg Transaction</th>
                        </tr>
                    </thead>
                    <tbody id="table2"></tbody>
                </table>
            </div>
            
            <!-- KPI 3 -->
            <div id="tab3" class="tab-content">
                <h2 class="kpi-title">KPI 3: Monthly Sales Trends</h2>
                <div class="kpi-grid">
                    <div class="chart-container" style="grid-column: 1 / -1;">
                        <h3>Monthly Revenue & Profit Trend</h3>
                        <canvas id="chart3"></canvas>
                    </div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Transactions</th>
                            <th>Total Units</th>
                            <th>Monthly Revenue</th>
                            <th>Monthly Profit</th>
                            <th>Avg Transaction</th>
                            <th>Margin %</th>
                        </tr>
                    </thead>
                    <tbody id="table3"></tbody>
                </table>
            </div>
            
            <!-- KPI 4 -->
            <div id="tab4" class="tab-content">
                <h2 class="kpi-title">KPI 4: Brand Profitability Ranking</h2>
                <div class="kpi-grid">
                    <div class="chart-container">
                        <h3>Top 8 Brands by Profit</h3>
                        <canvas id="chart4"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>Brand Profit Margin %</h3>
                        <canvas id="chart4b"></canvas>
                    </div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Brand</th>
                            <th>Transactions</th>
                            <th>Total Units</th>
                            <th>Revenue</th>
                            <th>Profit</th>
                            <th>Avg Margin %</th>
                            <th>Profit Margin %</th>
                        </tr>
                    </thead>
                    <tbody id="table4"></tbody>
                </table>
            </div>
            
            <!-- KPI 5 -->
            <div id="tab5" class="tab-content">
                <h2 class="kpi-title">KPI 5: Customer Geographic Distribution</h2>
                <div class="kpi-grid">
                    <div class="chart-container">
                        <h3>Revenue by Country</h3>
                        <canvas id="chart5a"></canvas>
                    </div>
                    <div class="chart-container">
                        <h3>Customers vs Transactions</h3>
                        <canvas id="chart5b"></canvas>
                    </div>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Country</th>
                            <th>Unique Customers</th>
                            <th>Transactions</th>
                            <th>Total Units</th>
                            <th>Revenue</th>
                            <th>Profit</th>
                            <th>Avg Transaction</th>
                            <th>Margin %</th>
                        </tr>
                    </thead>
                    <tbody id="table5"></tbody>
                </table>
            </div>
        </div>
        
        <footer>
            <p>Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p>Technology Retail Analytics Dashboard | Q1 2026 Data</p>
        </footer>
    </div>
    
    <script>
        // Tab switching
        let currentCharts = {};
        
        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
            
            // Destroy previous charts
            Object.values(currentCharts).forEach(chart => chart.destroy());
            currentCharts = {};
            
            // Create charts for the current tab
            createChartsForTab(tabId);
        }
        
        // Data
        const data1 = """ + json.dumps(df1.to_dict('records')) + """;
        const data2 = """ + json.dumps(df2.to_dict('records')) + """;
        const data3 = """ + json.dumps(df3.to_dict('records')) + """;
        const data4 = """ + json.dumps(df4.to_dict('records')) + """;
        const data5 = """ + json.dumps(df5.to_dict('records')) + """;
        
        // Populate tables
        function populateTable(elementId, data) {
            const tbody = document.getElementById(elementId);
            tbody.innerHTML = data.map(row => `
                <tr>
                    ${Object.values(row).map(val => `<td>${typeof val === 'number' ? val.toLocaleString('en-US', {maximumFractionDigits: 2}) : val}</td>`).join('')}
                </tr>
            `).join('');
        }
        
        populateTable('table1', data1);
        populateTable('table2', data2);
        populateTable('table3', data3);
        populateTable('table4', data4);
        populateTable('table5', data5);
        
        function createChartsForTab(tabId) {
            if (tabId === 'tab1') {
                createTab1Charts();
            } else if (tabId === 'tab2') {
                createTab2Charts();
            } else if (tabId === 'tab3') {
                createTab3Charts();
            } else if (tabId === 'tab4') {
                createTab4Charts();
            } else if (tabId === 'tab5') {
                createTab5Charts();
            }
        }
        
        function createTab1Charts() {
            // Chart 1a
            const ctx1a = document.getElementById('chart1a').getContext('2d');
            currentCharts['chart1a'] = new Chart(ctx1a, {
                type: 'bar',
                data: {
                    labels: data1.map(d => d.category),
                    datasets: [{
                        label: 'Revenue ($)',
                        data: data1.map(d => d.total_revenue),
                        backgroundColor: 'rgba(102, 126, 234, 0.7)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => `$${context.parsed.y.toLocaleString('en-US', {maximumFractionDigits: 2})}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => `$${(value/1000).toFixed(0)}K`
                            }
                        }
                    }
                }
            });
            
            // Chart 1b
            const ctx1b = document.getElementById('chart1b').getContext('2d');
            const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'];
            currentCharts['chart1b'] = new Chart(ctx1b, {
                type: 'doughnut',
                data: {
                    labels: data1.map(d => d.category),
                    datasets: [{
                        data: data1.map(d => d.total_profit),
                        backgroundColor: colors.slice(0, data1.length),
                        borderColor: 'white',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        function createTab2Charts() {
            // Chart 2a
            const ctx2a = document.getElementById('chart2a').getContext('2d');
            currentCharts['chart2a'] = new Chart(ctx2a, {
                type: 'bar',
                data: {
                    labels: data2.map(d => d.channel),
                    datasets: [{
                        label: 'Revenue ($)',
                        data: data2.map(d => d.total_revenue),
                        backgroundColor: ['#3498db', '#e74c3c', '#2ecc71'],
                        borderWidth: 2,
                        borderColor: 'rgba(0,0,0,0.2)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => `$${(value/1000).toFixed(0)}K`
                            }
                        }
                    }
                }
            });
            
            // Chart 2b
            const ctx2b = document.getElementById('chart2b').getContext('2d');
            currentCharts['chart2b'] = new Chart(ctx2b, {
                type: 'pie',
                data: {
                    labels: data2.map(d => d.channel),
                    datasets: [{
                        data: data2.map(d => d.total_revenue),
                        backgroundColor: ['#3498db', '#e74c3c', '#2ecc71'],
                        borderColor: 'white',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }
        
        function createTab3Charts() {
            // Chart 3
            const ctx3 = document.getElementById('chart3').getContext('2d');
            currentCharts['chart3'] = new Chart(ctx3, {
                type: 'line',
                data: {
                    labels: data3.map(d => d.month_name),
                    datasets: [
                        {
                            label: 'Monthly Revenue',
                            data: data3.map(d => d.monthly_revenue),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3
                        },
                        {
                            label: 'Monthly Profit',
                            data: data3.map(d => d.monthly_profit),
                            borderColor: '#2ecc71',
                            backgroundColor: 'rgba(46, 204, 113, 0.1)',
                            fill: true,
                            tension: 0.4,
                            borderWidth: 3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            ticks: {
                                callback: (value) => `$${(value/1000).toFixed(0)}K`
                            }
                        }
                    }
                }
            });
        }
        
        function createTab4Charts() {
            // Chart 4
            const topBrands = data4.slice(0, 8);
            const ctx4 = document.getElementById('chart4').getContext('2d');
            currentCharts['chart4'] = new Chart(ctx4, {
                type: 'bar',
                data: {
                    labels: topBrands.map(d => d.brand),
                    datasets: [{
                        label: 'Profit ($)',
                        data: topBrands.map(d => d.brand_profit),
                        backgroundColor: 'rgba(102, 126, 234, 0.7)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            ticks: {
                                callback: (value) => `$${(value/1000).toFixed(0)}K`
                            }
                        }
                    }
                }
            });
            
            // Chart 4b - Bar chart
            const ctx4b = document.getElementById('chart4b').getContext('2d');
            currentCharts['chart4b'] = new Chart(ctx4b, {
                type: 'bar',
                data: {
                    labels: data4.map(d => d.brand),
                    datasets: [{
                        label: 'Profit Margin %',
                        data: data4.map(d => d.profit_margin_pct),
                        backgroundColor: 'rgba(46, 204, 113, 0.7)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => `${value}%`
                            }
                        }
                    }
                }
            });
        }
        
        function createTab5Charts() {
            // Chart 5a
            const ctx5a = document.getElementById('chart5a').getContext('2d');
            currentCharts['chart5a'] = new Chart(ctx5a, {
                type: 'bar',
                data: {
                    labels: data5.map(d => d.country),
                    datasets: [{
                        label: 'Revenue ($)',
                        data: data5.map(d => d.country_revenue),
                        backgroundColor: ['#e74c3c', '#3498db', '#2ecc71'],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: (value) => `$${(value/1000).toFixed(0)}K`
                            }
                        }
                    }
                }
            });
            
            // Chart 5b
            const ctx5b = document.getElementById('chart5b').getContext('2d');
            currentCharts['chart5b'] = new Chart(ctx5b, {
                type: 'bar',
                data: {
                    labels: data5.map(d => d.country),
                    datasets: [
                        {
                            label: 'Unique Customers',
                            data: data5.map(d => d.unique_customers),
                            backgroundColor: '#9b59b6'
                        },
                        {
                            label: 'Transactions',
                            data: data5.map(d => d.total_transactions),
                            backgroundColor: '#f39c12'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // Initialize first tab
        createChartsForTab('tab1');
    </script>
</body>
</html>
        """
        
        return html
    
    def save_html(self):
        """Save HTML to file"""
        html = self.generate_html()
        output_path = self.output_dir / "dashboard.html"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"[OK] HTML Dashboard generated: {output_path}")
        return output_path


if __name__ == "__main__":
    generator = HTMLDashboardGenerator()
    path = generator.save_html()
    print(f"[OK] Open in browser: {path.resolve()}")
