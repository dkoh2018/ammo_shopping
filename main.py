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

    df = load_and_preprocess_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎯 Ammo Listings Found", len(df))
        st.metric("💥 Caliber Varieties", df["Caliber"].nunique())
    with col2:
        st.metric("💸 Average Cost Per Shot", f'${df["$/round"].mean():.3f}')
        st.metric("🏆 Ammo King Brand", df["Brand"].mode()[0])
    with col3:
        st.metric("🎁 Rounds per Box", f'{df["Rounds"].median():.0f}')
        st.metric("✨ Premium Brass %", f'{(df["Casing"]=="brass").mean()*100:.1f}%')

    st.subheader("💰 Price Check by Caliber")
    fig = px.box(
        df, x="Caliber", y="$/round", title="How Much Will Each Shot Cost You?"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

    st.subheader("🏆 Top Brands Showdown")
    brand_counts = df["Brand"].value_counts().head(10)
    fig = px.pie(
        values=brand_counts.values,
        names=brand_counts.index,
        title="Most Popular Brands in the Game",
    )
    st.plotly_chart(fig)

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
