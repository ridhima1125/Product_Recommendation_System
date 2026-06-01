import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="Product Recommender",
    page_icon="🛍️",
    layout="wide"
)

st.title("Product Recommendation System")
st.caption("MySQL + Machine Learning + Streamlit")

# ---------------- DATABASE ---------------- #

@st.cache_resource
def get_engine():
    return create_engine(
        "mysql+pymysql://root:iamidiot@localhost/rec_db"
    )

@st.cache_data
def load():
    engine = get_engine()

    products = pd.read_sql(
        "SELECT * FROM products",
        engine
    )

    ratings = pd.read_sql(
        "SELECT user_id, product_id, rating FROM ratings",
        engine
    )

    return products, ratings

# ---------------- CONTENT BASED MODEL ---------------- #

@st.cache_data
def build_sim(products):

    tfidf = TfidfVectorizer(stop_words="english")

    matrix = tfidf.fit_transform(
        products["description"].fillna("")
    )

    similarity = cosine_similarity(matrix, matrix)

    return similarity

# ---------------- LOAD DATA ---------------- #

df_p, df_r = load()
sim = build_sim(df_p)

# ---------------- KPI CARDS ---------------- #

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Products",
    f"{len(df_p):,}"
)

c2.metric(
    "Users",
    f"{df_r['user_id'].nunique():,}"
)

c3.metric(
    "Total Ratings",
    f"{len(df_r):,}"
)

c4.metric(
    "Avg Rating",
    f"{df_p['rating'].mean():.1f}"
)

# ---------------- CATEGORY TABLE ---------------- #

st.subheader("Category Overview")

cat = (
    df_p.groupby("category")
    .agg(
        Count=("product_id", "count"),
        Avg_Price=("price", "mean"),
        Avg_Rating=("rating", "mean")
    )
    .reset_index()
)

cat["Avg_Price"] = cat["Avg_Price"].round(0)
cat["Avg_Rating"] = cat["Avg_Rating"].round(2)

st.dataframe(
    cat,
    use_container_width=True
)

# ---------------- TABS ---------------- #

t1, t2 = st.tabs(
    ["Similar Products", "For You (Collaborative)"]
)

# =====================================================
# TAB 1 : SIMILAR PRODUCTS
# =====================================================

with t1:

    prod = st.selectbox(
        "Choose your Product:",
        df_p["name"].tolist()
    )

    n = st.slider(
        "How many?",
        3,
        10,
        5
    )

    if st.button("Search Similar"):

        product_index = (
            df_p[df_p["name"] == prod]
            .index[0]
        )

        scores = list(
            enumerate(sim[product_index])
        )

        scores = sorted(
            scores,
            key=lambda x: x[1],
            reverse=True
        )

        scores = scores[1:n+1]

        recommended_indices = [
            x[0] for x in scores
        ]

        rec = (
            df_p[
                [
                    "name",
                    "category",
                    "brand",
                    "price",
                    "rating"
                ]
            ]
            .iloc[recommended_indices]
            .reset_index(drop=True)
        )

        rec.index += 1

        st.success(
            f"{n} products like '{prod}'"
        )

        st.dataframe(
            rec,
            use_container_width=True
        )

# =====================================================
# TAB 2 : COLLABORATIVE FILTERING
# =====================================================

with t2:

    uid = st.selectbox(
        "User ID:",
        sorted(df_r["user_id"].unique())
    )

    if st.button("Recommend for User"):

        user_product = df_r.pivot_table(
            index="user_id",
            columns="product_id",
            values="rating",
            fill_value=0
        )

        user_similarity = cosine_similarity(
            user_product
        )

        similarity_df = pd.DataFrame(
            user_similarity,
            index=user_product.index,
            columns=user_product.index
        )

        similar_users = (
            similarity_df[uid]
            .sort_values(ascending=False)
            .iloc[1:11]
            .index
        )

        already_rated = set(
            df_r[
                df_r["user_id"] == uid
            ]["product_id"]
        )

        recommendations = []

        for user in similar_users:

            products = set(
                df_r[
                    df_r["user_id"] == user
                ]["product_id"]
            )

            recommendations.extend(
                list(products - already_rated)
            )

        result = (
            df_p[
                df_p["product_id"].isin(
                    recommendations[:5]
                )
            ][
                [
                    "name",
                    "category",
                    "price",
                    "rating"
                ]
            ]
            .reset_index(drop=True)
        )

        result.index += 1

        st.success(
            f"Top 5 recommendations for User {uid}"
        )

        st.dataframe(
            result,
            use_container_width=True
        )