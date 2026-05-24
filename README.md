# 📚 Online Book store (Advanced Edition)

A professional-grade bookstore management and analytics system built with **Streamlit**, **SQLite**, and **Plotly**. This version is designed for serious business operations with real-time sales tracking and data visualization.

## 🚀 Advanced Features

- **📊 Business Intelligence Dashboard**:
  - Real-time revenue tracking and order counting.
  - Interactive charts for **Revenue by Category** and **Top Selling Books**.
  - Trend analysis for daily sales volume.
- **💰 Point of Sale (POS) System**:
  - Dedicated checkout interface for recording sales.
  - Automatic stock deduction upon transaction completion.
  - Stock validation to prevent over-selling.
- **🛡️ Inventory Control 2.0**:
  - Track books with **ISBN**, Category, and entry dates.
  - **CSV Export**: One-click download of the entire inventory for external use.
  - Bulk stock management and deletion tools.
- **🔍 Intelligent Search**:
  - Global search across titles, authors, categories, and ISBNs.
- **⚠️ Smart Alerts**:
  - Configurable low-stock threshold with high-visibility warnings.
- **✨ Modern UI**:
  - Dark-themed sidebar with interactive elements.
  - Responsive metric cards and custom CSS animations.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly Express
- **Backend**: Python (Logic) & SQLite (Relational Database)
- **Data Analysis**: Pandas

## 📦 Installation & Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Launch the platform**:
   ```bash
   python -m streamlit run app.py
   ```

## 📂 Project Structure

- `app.py`: The advanced multi-page Streamlit dashboard.
- `database.py`: relational database schema with Sales and Books tables.
- `bookstore.db`: SQLite production database.
- `requirements.txt`: Managed dependencies.

---
© 2026 Online Book store | Version 2.0
