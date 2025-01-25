import streamlit as st
import json
import pandas as pd
import plotly.express as px


# Load and preprocess data
@st.cache_data
def load_and_preprocess_data():
    with open("all_calibers.json", "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data["results"])

    # Clean up and convert numerical columns
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Rounds"] = pd.to_numeric(df["Rounds"], errors="coerce")
    df["$/round"] = pd.to_numeric(df["$/round"], errors="coerce")

    return df


# Main Streamlit app
def main():
    st.title("🎯 Find Your Ammo!")
    st.markdown("### Your one-stop shop for the best ammo prices")

    # Load and preprocess data
    df = load_and_preprocess_data()

    # Display key metrics in two rows with fun emojis
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏷️ Total Deals Available", len(df))
        st.metric("🎯 Different Calibers", df["Caliber"].nunique())
    with col2:
        st.metric("💰 Average Cost per Round", f'${df["$/round"].mean():.3f}')
        st.metric("⭐ Most Popular Brand", df["Brand"].mode()[0])
    with col3:
        st.metric("📦 Typical Box Size", f'{df["Rounds"].median():.0f}')
        st.metric("🔫 Brass Cases", f'{(df["Casing"]=="brass").mean()*100:.1f}%')

    # Add price distribution chart
    st.subheader("💰 Price Check by Caliber")
    fig = px.box(
        df, x="Caliber", y="$/round", title="How Much Will Each Shot Cost You?"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

    # Add brand market share pie chart
    st.subheader("🏆 Top Brands Showdown")
    brand_counts = df["Brand"].value_counts().head(10)
    fig = px.pie(
        values=brand_counts.values,
        names=brand_counts.index,
        title="Most Popular Brands in the Game",
    )
    st.plotly_chart(fig)

    # Detailed data table
    st.subheader("🔍 Find Your Perfect Match")
    st.dataframe(
        df[
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


if __name__ == "__main__":
    main()
