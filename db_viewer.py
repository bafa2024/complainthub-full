#!/usr/bin/env python3
"""
Simple Database Viewer for ComplaintHub
Shows all tables and their data in a web interface
"""

from flask import Flask, render_template_string, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database path
DB_PATH = "backend/voicebot.db"

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_table_names():
    """Get all table names from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_data(table_name, limit=50):
    """Get data from a specific table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    
    # Convert to list of dictionaries
    data = []
    for row in rows:
        row_dict = {}
        for i, column in enumerate(columns):
            value = row[i]
            if isinstance(value, datetime):
                value = value.isoformat()
            row_dict[column] = value
        data.append(row_dict)
    
    conn.close()
    return columns, data

def get_table_count(table_name):
    """Get row count for a table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    conn.close()
    return count

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ComplaintHub Database Viewer</title>
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
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .nav {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .nav-tabs {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .nav-tab {
            padding: 12px 24px;
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            text-decoration: none;
            color: #495057;
            font-weight: 500;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .nav-tab:hover, .nav-tab.active {
            background: #007bff;
            color: white;
            border-color: #007bff;
            transform: translateY(-2px);
        }
        
        .content {
            padding: 30px;
        }
        
        .table-container {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .table-header {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .table-header h3 {
            margin: 0;
            color: #2c3e50;
            font-size: 1.5em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        th {
            background: #f8f9fa;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            color: #495057;
            border-bottom: 2px solid #e9ecef;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: top;
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        td:hover {
            white-space: normal;
            word-wrap: break-word;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .loading {
            text-align: center;
            padding: 50px;
            color: #6c757d;
        }
        
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗄️ ComplaintHub Database Viewer</h1>
            <p>View all tables and data in your SQLite database</p>
        </div>
        
        <div class="nav">
            <div class="nav-tabs" id="nav-tabs">
                <!-- Table tabs will be loaded here -->
            </div>
        </div>
        
        <div class="content">
            <div id="overview" class="tab-content">
                <div class="stats" id="stats">
                    <!-- Stats will be loaded here -->
                </div>
                <div class="table-container">
                    <div class="table-header">
                        <h3>📊 Database Overview</h3>
                    </div>
                    <p style="padding: 20px; color: #6c757d;">
                        Select a table from the navigation above to view its data.
                    </p>
                </div>
            </div>
            
            <div id="table-content" class="tab-content" style="display: none;">
                <div class="table-container">
                    <div class="table-header">
                        <h3 id="table-title">Table Data</h3>
                    </div>
                    <div id="table-data">
                        <div class="loading">Loading table data...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentTable = null;
        
        function loadTables() {
            fetch('/api/tables')
                .then(response => response.json())
                .then(data => {
                    updateNavTabs(data.tables);
                    updateStats(data.stats);
                })
                .catch(error => {
                    console.error('Error loading tables:', error);
                });
        }
        
        function updateNavTabs(tables) {
            const navTabs = document.getElementById('nav-tabs');
            let html = '<a href="#" class="nav-tab active" onclick="showOverview()">📊 Overview</a>';
            
            tables.forEach(table => {
                html += `<a href="#" class="nav-tab" onclick="showTable('${table.name}')">📋 ${table.name} (${table.count})</a>`;
            });
            
            navTabs.innerHTML = html;
        }
        
        function updateStats(stats) {
            const statsDiv = document.getElementById('stats');
            let html = '';
            
            stats.forEach(stat => {
                html += `
                    <div class="stat-card">
                        <div class="stat-number">${stat.count}</div>
                        <div class="stat-label">${stat.table}</div>
                    </div>
                `;
            });
            
            statsDiv.innerHTML = html;
        }
        
        function showOverview() {
            document.getElementById('overview').style.display = 'block';
            document.getElementById('table-content').style.display = 'none';
            
            // Update active tab
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        function showTable(tableName) {
            currentTable = tableName;
            
            document.getElementById('overview').style.display = 'none';
            document.getElementById('table-content').style.display = 'block';
            
            document.getElementById('table-title').textContent = `📋 ${tableName}`;
            document.getElementById('table-data').innerHTML = '<div class="loading">Loading table data...</div>';
            
            // Update active tab
            document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
            event.target.classList.add('active');
            
            loadTableData(tableName);
        }
        
        function loadTableData(tableName) {
            fetch(`/api/table/${tableName}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('table-data').innerHTML = `<div class="error">${data.error}</div>`;
                    } else {
                        updateTableData(data.columns, data.data);
                    }
                })
                .catch(error => {
                    console.error('Error loading table data:', error);
                    document.getElementById('table-data').innerHTML = '<div class="error">Error loading table data.</div>';
                });
        }
        
        function updateTableData(columns, data) {
            if (data.length === 0) {
                document.getElementById('table-data').innerHTML = '<p style="padding: 20px; color: #6c757d;">No data found in this table.</p>';
                return;
            }
            
            let html = '<table><thead><tr>';
            
            // Header row
            columns.forEach(column => {
                html += `<th>${column}</th>`;
            });
            html += '</tr></thead><tbody>';
            
            // Data rows
            data.forEach(row => {
                html += '<tr>';
                columns.forEach(column => {
                    const value = row[column];
                    html += `<td title="${value}">${value || 'NULL'}</td>`;
                });
                html += '</tr>';
            });
            
            html += '</tbody></table>';
            
            document.getElementById('table-data').innerHTML = html;
        }
        
        // Load tables on page load
        window.onload = function() {
            loadTables();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/tables')
def api_tables():
    try:
        tables = get_table_names()
        table_stats = []
        
        for table in tables:
            count = get_table_count(table)
            table_stats.append({
                'name': table,
                'count': count
            })
        
        return jsonify({
            'tables': table_stats,
            'stats': table_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/table/<table_name>')
def api_table(table_name):
    try:
        columns, data = get_table_data(table_name)
        return jsonify({
            'columns': columns,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting ComplaintHub Database Viewer...")
    print("📊 Open your browser and go to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("Please make sure the database file exists.")
        exit(1)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 