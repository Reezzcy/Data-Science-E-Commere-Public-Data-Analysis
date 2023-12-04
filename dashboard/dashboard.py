import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import geopandas as gpd

def create_seller_response_df(df):
    seller_response = df.groupby("response_category").agg({
    "response_time_hour": "count"
    })
    return seller_response

def create_review_rate_df(df):
    review_rate = df.groupby("product_category_name_english").agg({
    "review_score": "mean"
    }).sort_values(by="review_score", ascending=False)
    return review_rate

def create_user_location_df(df):
    seller_location_df = df[['seller_id', 'role_seller', 'seller_city', 'geolocation_lat_seller', 'geolocation_lng_seller']].rename(columns={'seller_id': 'user_id', 'role_seller': 'role', 'geolocation_lat_seller': 'Latitude', 'geolocation_lng_seller': 'Longitude'}).drop_duplicates()
    customer_location_df = df[['customer_id', 'role_customer', 'customer_city','geolocation_lat_customer', 'geolocation_lng_customer']].rename(columns={'customer_id': 'user_id', 'role_customer': 'role', 'geolocation_lat_customer': 'Latitude', 'geolocation_lng_customer': 'Longitude'}).drop_duplicates()
    user_location_df = pd.concat([seller_location_df, customer_location_df], ignore_index=True)
    return user_location_df

def create_orders_df(main_df):
    orders = main_df["response_time_hour"]
    return orders

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for cloumn in datetime_columns:
    all_df[cloumn] = pd.to_datetime(all_df[cloumn])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:

    start_date, end_date = st.date_input(
        label= 'Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

orders = create_orders_df(main_df)
seller_response = create_seller_response_df(main_df)
review_rate = create_review_rate_df(main_df)
user_location_df = create_user_location_df(main_df)

st.header('Proyek Analisis Data: E-Commere Public')

st.write('- Nama: Nicolas Debrito')
st.write('- Email: nicolas.debrito66@gmail.com')
st.write('- Id Dicoding: reezzy')

st.subheader('Seller Response Performance')

col1, col2 = st.columns(2)

with col1:
    avg_response_perfomance = round(orders.mean(), 1)
    avg_response_perfomance = "Cepat" if avg_response_perfomance <= 2 else ("Normal" if avg_response_perfomance < 12 else "Lambat")
    st.metric("Average Response Performence", value=avg_response_perfomance)

with col2:
    avg_response = round(orders.mean(), 1)
    st.metric("Average Response in Hour", value=avg_response)

seller_response.rename(columns={
    "response_time_hour": "response_count"
}, inplace=True)

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

plt.figure(figsize=(10, 5))

sns.barplot(
    y="response_count", 
    x="response_category",
    data=seller_response.sort_values(by="response_count", ascending=False),
    palette=colors
)

plt.title("Seller Response Performance", loc="center", fontsize=15)
plt.ylabel("Total Response")
plt.xlabel("Response Category")
plt.tick_params(axis='x', labelsize=12)

st.pyplot(plt)

st.subheader('Best and Worst Performing Product by Number of Sales')

col1, col2 = st.columns(2)

with col1:
    best_product = review_rate.review_score.max()
    st.metric("Best Rating", value=best_product)

with col2:
    avg_rating = round(review_rate.review_score.mean(), 2)
    st.metric("Average Rating", value=avg_rating)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="review_score", y="product_category_name_english", data=review_rate.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="review_score", y="product_category_name_english", data=review_rate.sort_values(by="review_score", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

plt.suptitle("Best and Worst Performing Product by Number of Sales", fontsize=20)

st.pyplot(plt)

st.subheader('Distribution of Sellers and Customers')

a = user_location_df.groupby(by="seller_city").agg({
    "user_id": "count"
}).sort_values(by="user_id", ascending=False)
b = user_location_df.groupby(by="customer_city").agg({
    "user_id": "count"
}).sort_values(by="user_id", ascending=False)

col1, col2 = st.columns(2)

with col1:
    highest_sellers = a.index[0]
    st.metric("Highest Sellers City Location", value=highest_sellers)

with col2:
    highest_customers = b.index[0]
    st.metric("Highest Customers City Location", value=highest_customers)

geometry = gpd.points_from_xy(user_location_df['Longitude'], user_location_df['Latitude'])
gdf = gpd.GeoDataFrame(user_location_df, geometry=geometry)

gdf_seller = gdf[gdf['role'] == 'seller']
gdf_customer = gdf[gdf['role'] == 'customer']

fig, ax = plt.subplots(1, 2, figsize=(15, 6))
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

world.plot(ax=ax[0], color='lightgrey')
gdf_seller.plot(ax=ax[0], color='blue', marker='o', markersize=1)
ax[0].set_title('Peta Penjual')

world.plot(ax=ax[1], color='lightgrey')
gdf_customer.plot(ax=ax[1], color='green', marker='o', markersize=1)
ax[1].set_title('Peta Pembeli')

plt.tight_layout()

st.pyplot(plt)

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="user_id", y="seller_city", data=a.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Persebaran Penjual", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)

sns.barplot(x="user_id", y="customer_city", data=b.sort_values(by="user_id", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Persebaran Pembeli", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

plt.suptitle("Jumlah Persebaran Penjual dan Pembeli", fontsize=20)

st.pyplot(plt)