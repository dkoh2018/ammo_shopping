import streamlit as st
import json
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Find Your Ammo!", page_icon="🎯", layout="wide")


@st.cache_data
def load_and_preprocess_data():
    with open("all_calibers.json", "r") as f:
        data = json.load(f)
        df = pd.DataFrame(data["results"])
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df["Rounds"] = pd.to_numeric(df["Rounds"], errors="coerce")
        df["$/round"] = pd.to_numeric(df["$/round"], errors="coerce")
    return df


def main():
    st.title("🎯 Find Your Ammo!")
    st.markdown("### Your one-stop shop for the best ammo prices")

    # Load the data
    df = load_and_preprocess_data()

    # Create a horizontal layout for filters
    col1, col2, col3 = st.columns(3)
    with col1:
        # Brand Dropdown
        unique_brands = sorted(df["Brand"].unique().tolist())
        selected_brand = st.selectbox("Select Brand:", ["All Brands"] + unique_brands)

    if selected_brand == "All Brands":
        price_min, price_max = int(df["Price"].min()), int(df["Price"].max())
        round_price_min, round_price_max = df["$/round"].min(), df["$/round"].max()
    else:
        brand_df = df[df["Brand"] == selected_brand]
        price_min, price_max = int(brand_df["Price"].min()), int(
            brand_df["Price"].max()
        )
        round_price_min, round_price_max = (
            brand_df["$/round"].min(),
            brand_df["$/round"].max(),
        )

    with col2:
        # Price Range Slider
        price_range = st.slider(
            "Price ($):",
            min_value=price_min,
            max_value=price_max,
            value=(price_min, price_max),
        )

    with col3:
        # Price per Round Slider
        round_price_range = st.slider(
            "Price per Round ($/rd):",
            min_value=round_price_min,
            max_value=round_price_max,
            value=(round_price_min, round_price_max),
            format="%.3f",  # Keep 3 decimal places for $/round slider
        )

    # Apply filters
    filtered_df = df[
        (df["Price"] >= price_range[0])
        & (df["Price"] <= price_range[1])
        & (df["$/round"] >= round_price_range[0])
        & (df["$/round"] <= round_price_range[1])
    ]

    # Brand filter (if not 'All Brands')
    if selected_brand != "All Brands":
        filtered_df = filtered_df[filtered_df["Brand"] == selected_brand]

    # Metrics columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🎯 Ammo Listings Found", len(filtered_df))
        st.metric("💥 Caliber Varieties", filtered_df["Caliber"].nunique())

    with col2:
        st.metric("💸 Average Cost Per Shot", f'${filtered_df["$/round"].mean():.3f}')
        st.metric(
            "🏆 Ammo King Brand",
            filtered_df["Brand"].mode()[0] if not filtered_df.empty else "N/A",
        )

    with col3:
        st.metric("🎁 Rounds per Box", f'{filtered_df["Rounds"].median():.0f}')
        st.metric("✨ Brass %", f'{(filtered_df["Casing"]=="brass").mean()*100:.1f}%')

    # Find Your Perfect Match - MOVED HERE
    st.subheader("🔍 Find Your Perfect Match")
    st.dataframe(
        filtered_df[
            [
                "Retailer",
                "Description",
                "Caliber",
                "Brand",
                "Casing",
                "Price",
                "Rounds",
                "$/round",
                "Link",
            ]
        ]
    )

    # Price Check by Caliber
    st.subheader("💰 Price Check by Caliber")
    fig = px.box(
        filtered_df,
        x="Caliber",
        y="$/round",
        title="How Much Will Each Shot Cost You?",
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

    # Top Brands Showdown
    st.subheader("🏆 Top Brands Showdown")
    brand_counts = filtered_df["Brand"].value_counts().head(10)
    fig = px.pie(
        values=brand_counts.values,
        names=brand_counts.index,
        title="Most Popular Brands in the Game",
    )
    st.plotly_chart(fig)


if __name__ == "__main__":
    main()
