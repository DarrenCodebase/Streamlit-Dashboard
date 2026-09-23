# Retail Sales Dashboard

An interactive Streamlit dashboard for exploring retail sales performance — built on a synthetic transaction dataset with realistic seasonal patterns, pricing, and customer behavior.

## Overview

This project generates a synthetic retail sales dataset (`retail_sales_v2.csv`) and visualizes it through a multi-tab Streamlit dashboard, deployed from Google Colab using `ngrok`.

**Live features:**
- Sidebar filters for date range, region, product category, customer segment, sales channel, and order status
- 6 KPI cards: total revenue, orders, average order value, units sold, return rate, unique customers
- **Sales Trends** — monthly revenue trend, revenue by sales channel, day-of-week revenue, order status breakdown
- **Product Analysis** — revenue by category and subcategory, discount vs. revenue by category
- **Regional Analysis** — revenue by region and state, region/store treemap
- **Customer Insights** — revenue by customer segment and payment method, top 10 customers by spend
- **Raw Data** — searchable, filterable data table with CSV export

## Dataset

`retail_sales_v2.csv` contains 6,000 synthetic orders spanning January 2023 – December 2024, generated with:
- Seasonal demand patterns (holiday surge, back-to-school bump, weekend spikes)
- Realistic per-category price distributions (Electronics, Apparel, Home Goods, Books, Sporting Goods, Beauty & Health)
- Customer segments (Consumer, Corporate, Home Office), sales channels (Online, In-Store), payment methods, shipping costs, and order status (Completed, Returned, Cancelled)

## Project Structure

```
├── Group02_Learn_by_Teaching_Streamlit_Demo_Enhanced.ipynb   # Full Colab notebook (data gen + deployment)
├── generate_data.py                                          # Standalone data generation script
├── streamlit_app.py                                          # Standalone Streamlit app
└── README.md
```

## Getting Started

### Option 1: Run in Google Colab
1. Open the `.ipynb` notebook in Colab.
2. Add an `ngrok` authtoken to Colab secrets under the name `NGROK_AUTH_TOKEN` (sign up free at [ngrok.com](https://ngrok.com)).
3. Run the data generation cell, then the deployment cell.
4. Open the printed `ngrok` URL to view the live dashboard.

### Option 2: Run locally
```bash
pip install streamlit plotly pandas numpy
python generate_data.py
streamlit run streamlit_app.py
```
The app will open at `http://localhost:8501`.

## Tech Stack
- **Python** — Pandas, NumPy for data generation and processing
- **Streamlit** — dashboard framework
- **Plotly Express** — interactive charts
- **ngrok** — tunneling for Colab deployment

## Notes
- The dataset is fully synthetic and regenerated each run (seeded with `np.random.seed(42)` for reproducibility).
- Deselecting all values in any sidebar filter will empty the dataset; the app will prompt you to widen your selection.
