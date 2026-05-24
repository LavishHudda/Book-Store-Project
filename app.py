import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import Database
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Online Book store",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
db = Database()

# Custom CSS for "Aggressive" UI
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    [data-testid="stSidebar"] {
        background-color: #1a1c23;
        color: white;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .metric-card {
        background-color: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7;
        text-align: left;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #2d3748;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .warning-box {
        background-color: #fff5f5;
        border-left: 5px solid #feb2b2;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("📚 Online Book store")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "MANAGEMENT SYSTEM",
    ["📊 Dashboard", "💰 Point of Sale (POS)", "📦 Inventory", "📈 Sales Reports", "🔍 Global Search"]
)

# Sidebar Info
st.sidebar.markdown("---")
with st.sidebar.expander("⚙️ Settings"):
    low_stock_limit = st.number_input("Low Stock Alert Threshold", min_value=1, value=5)

# Helper for warnings
def get_low_stock_alerts():
    low_stock = db.get_low_stock_books(threshold=low_stock_limit)
    return low_stock

# --- Dashboard ---
if menu == "📊 Dashboard":
    st.title("🚀 Business Analytics")
    
    # Low Stock Alerts at the top
    low_stock_data = get_low_stock_alerts()
    if not low_stock_data.empty:
        with st.expander(f"⚠️ LOW STOCK ALERTS ({len(low_stock_data)})", expanded=True):
            for _, row in low_stock_data.iterrows():
                st.markdown(f'<div class="warning-box"><b>{row["title"]}</b> is critically low: <b>{row["stock"]}</b> units left.</div>', unsafe_allow_html=True)

    # Key Metrics
    all_books = db.get_all_books()
    sales_report = db.get_sales_report()
    
    total_revenue = sales_report['total_price'].sum() if not sales_report.empty else 0
    total_orders = len(sales_report)
    total_stock = all_books['stock'].sum() if not all_books.empty else 0
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Revenue</div><div class="metric-value">${total_revenue:,.2f}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Orders</div><div class="metric-value">{total_orders}</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Unique Titles</div><div class="metric-value">{len(all_books)}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Inventory Units</div><div class="metric-value">{total_stock}</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Charts
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Revenue by Category")
        rev_by_cat = db.get_revenue_by_category()
        if not rev_by_cat.empty:
            fig = px.pie(rev_by_cat, values='revenue', names='category', hole=.4, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data to display.")

    with c2:
        st.subheader("Top 5 Selling Books")
        top_books = db.get_top_selling_books()
        if not top_books.empty:
            fig = px.bar(top_books, x='total_sold', y='title', orientation='h',
                         color='total_sold', color_continuous_scale='Blues')
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sales data to display.")

# --- Point of Sale (POS) ---
elif menu == "💰 Point of Sale (POS)":
    st.title("💸 Instant Checkout")
    
    all_books = db.get_all_books()
    if all_books.empty:
        st.warning("Please add books to the inventory first.")
    else:
        with st.container():
            st.subheader("Create New Order")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_book_name = st.selectbox("Select Book", all_books['title'].tolist())
                book_details = all_books[all_books['title'] == selected_book_name].iloc[0]
                
            with col2:
                qty = st.number_input("Quantity", min_value=1, max_value=int(book_details['stock']), value=1)
            
            st.info(f"Price: ${book_details['price']:.2f} | Available Stock: {book_details['stock']}")
            total_cost = book_details['price'] * qty
            st.markdown(f"### Total Amount: `${total_cost:.2f}`")
            
            if st.button("Complete Transaction", type="primary"):
                success, message = db.record_sale(book_details['id'], qty)
                if success:
                    st.success(message)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(message)

# --- Inventory ---
elif menu == "📦 Inventory":
    st.title("🛡️ Inventory Control")
    
    tab1, tab2, tab3 = st.tabs(["📚 Full Inventory", "➕ Add New Book", "✏️ Manage Stock"])
    
    with tab1:
        all_books = db.get_all_books()
        if not all_books.empty:
            st.dataframe(all_books, use_container_width=True, hide_index=True)
            # Export
            csv = all_books.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Inventory to CSV",
                csv,
                "inventory_export.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("Inventory is empty.")

    with tab2:
        with st.form("add_book_form"):
            st.subheader("Book Details")
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Title")
                author = st.text_input("Author")
                isbn = st.text_input("ISBN (Optional)")
            with c2:
                category = st.selectbox("Category", ["Fiction", "Non-Fiction", "Science", "Tech", "History", "Children", "Business"])
                price = st.number_input("Unit Price ($)", min_value=0.0, step=0.01)
                stock = st.number_input("Initial Stock", min_value=0, step=1)
            
            if st.form_submit_button("Save to Inventory"):
                if title and author:
                    db.add_book(title, author, isbn, price, stock, category)
                    st.success(f"'{title}' added successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Title and Author are required.")

    with tab3:
        all_books = db.get_all_books()
        if not all_books.empty:
            book_to_update = st.selectbox("Select book to update", all_books['title'].tolist(), key='update_sel')
            target_book = all_books[all_books['title'] == book_to_update].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                new_stock = st.number_input("Update Stock Level", value=int(target_book['stock']))
            with col2:
                if st.button("Update Stock", use_container_width=True):
                    db.update_stock(target_book['id'], new_stock)
                    st.success("Stock updated!")
                    time.sleep(1)
                    st.rerun()
            
            st.markdown("---")
            if st.button("🗑️ Delete Book from System", type="secondary"):
                db.delete_book(target_book['id'])
                st.success("Book deleted.")
                time.sleep(1)
                st.rerun()

# --- Sales Reports ---
elif menu == "📈 Sales Reports":
    st.title("💹 Sales Intelligence")
    reports = db.get_sales_report()
    
    if not reports.empty:
        st.subheader("Historical Transactions")
        st.dataframe(reports, use_container_width=True, hide_index=True)
        
        # Summary Analytics
        st.markdown("---")
        st.subheader("Daily Sales Volume")
        reports['sale_date'] = pd.to_datetime(reports['sale_date'])
        daily_sales = reports.groupby(reports['sale_date'].dt.date)['total_price'].sum().reset_index()
        fig = px.line(daily_sales, x='sale_date', y='total_price', title="Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No transactions recorded yet.")

# --- Search Books ---
elif menu == "🔍 Global Search":
    st.title("🔎 Intelligent Search")
    q = st.text_input("Search titles, authors, categories, or ISBN...")
    if q:
        results = db.search_books(q)
        if not results.empty:
            st.success(f"Found {len(results)} matches")
            st.dataframe(results, use_container_width=True, hide_index=True)
        else:
            st.warning("No results found.")
    else:
        st.info("Enter a keyword to search the entire catalog.")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption(f"System Version: 2.0 (Advanced)")
st.sidebar.caption(f"Last sync: {datetime.now().strftime('%H:%M:%S')}")
