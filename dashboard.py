import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set style seaborn
sns.set(style='dark')

# Menyiapkan data day_df
day_df = pd.read_csv("dashboard/day.csv")
day_df.head()

# Menghapus kolom yang tidak diperlukan
drop_col = ['windspeed']

for i in day_df.columns:
  if i in drop_col:
    day_df.drop(labels=i, axis=1, inplace=True)

# Mengubah nama judul kolom
day_df.rename(columns={
    'dteday': 'dateday',
    'yr': 'year',
    'mnth': 'month',
    'weathersit': 'weather_cond',
    'cnt': 'count'
}, inplace=True)

# Mengubah angka menjadi keterangan
day_df['month'] = day_df['month'].map({
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
})
day_df['season'] = day_df['season'].map({
    1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'
})
day_df['weekday'] = day_df['weekday'].map({
    0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'
})
day_df['weather_cond'] = day_df['weather_cond'].map({
    1: 'Clear/Partly Cloudy',
    2: 'Misty/Cloudy',
    3: 'Light Snow/Rain',
    4: 'Severe Weather'
})


# Menyiapkan daily_rent_df
def create_daily_rent_df(df):
    daily_rent_df = df.groupby(by='dateday').agg({
        'count': 'sum'
    }).reset_index()
    return daily_rent_df

# Menyiapkan daily_casual_rent_df
def create_daily_casual_rent_df(df):
    daily_casual_rent_df = df.groupby(by='dateday').agg({
        'casual': 'sum'
    }).reset_index()
    return daily_casual_rent_df

# Menyiapkan daily_registered_rent_df
def create_daily_registered_rent_df(df):
    daily_registered_rent_df = df.groupby(by='dateday').agg({
        'registered': 'sum'
    }).reset_index()
    return daily_registered_rent_df
    
# Menyiapkan season_rent_df
def create_season_rent_df(df):
    season_rent_df = df.groupby(by='season')[['registered', 'casual']].sum().reset_index()
    return season_rent_df

# Menyiapkan monthly_rent_df
def create_monthly_rent_df(df):
    monthly_rent_df = df.groupby(by='month').agg({
        'count': 'sum'
    })
    ordered_months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    monthly_rent_df = monthly_rent_df.reindex(ordered_months, fill_value=0)
    return monthly_rent_df

# Menyiapkan weekday_rent_df
def create_weekday_rent_df(df):
    weekday_rent_df = df.groupby(by='weekday').agg({
        'count': 'sum'
    }).reset_index()
    return weekday_rent_df

# Menyiapkan workingday_rent_df
def create_workingday_rent_df(df):
    workingday_rent_df = df.groupby(by='workingday').agg({
        'count': 'sum'
    }).reset_index()
    return workingday_rent_df

# Menyiapkan holiday_rent_df
def create_holiday_rent_df(df):
    holiday_rent_df = df.groupby(by='holiday').agg({
        'count': 'sum'
    }).reset_index()
    return holiday_rent_df

# Menyiapkan weather_rent_df
def create_weather_rent_df(df):
    weather_rent_df = df.groupby(by='weather_cond').agg({
        'count': 'sum'
    })
    return weather_rent_df

# Menghitung RFM
# Menghitung Recency, Frequency, Monetary
def calculate_rfm(df):
    # Mengubah dateday menjadi tipe datetime
    df['dateday'] = pd.to_datetime(df['dateday'])
    
    # Menghitung Recency
    snapshot_date = df['dateday'].max() + pd.DateOffset(days=1)  # Tanggal snapshot adalah tanggal terakhir + 1
    rfm_df = df.groupby('registered').agg({
        'dateday': lambda x: (snapshot_date - x.max()).days,  # Recency
        'count': 'sum'  # Frequency
    }).rename(columns={'dateday': 'Recency', 'count': 'Frequency'}).reset_index()
    
    # Monetary sama dengan Frequency (misalkan kita anggap sama)
    rfm_df['Monetary'] = rfm_df['Frequency']
    
    return rfm_df


# Membuat komponen filter
min_date = pd.to_datetime(day_df['dateday']).dt.date.min()
max_date = pd.to_datetime(day_df['dateday']).dt.date.max()
 
with st.sidebar:
    st.image('dashboard/logo.png') 
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value= min_date,
        max_value= max_date,
        value=[min_date, max_date]
    )

main_df = day_df[(day_df['dateday'] >= str(start_date)) & 
                (day_df['dateday'] <= str(end_date))]

# Menyiapkan berbagai dataframe
daily_rent_df = create_daily_rent_df(main_df)
daily_casual_rent_df = create_daily_casual_rent_df(main_df)
daily_registered_rent_df = create_daily_registered_rent_df(main_df)
season_rent_df = create_season_rent_df(main_df)
monthly_rent_df = create_monthly_rent_df(main_df)
weekday_rent_df = create_weekday_rent_df(main_df)
workingday_rent_df = create_workingday_rent_df(main_df)
holiday_rent_df = create_holiday_rent_df(main_df)
weather_rent_df = create_weather_rent_df(main_df)


# Membuat Dashboard secara lengkap

# Membuat judul
st.header('Bike Rental Dashboard 🚲')


# Membuat jumlah penyewaan harian
st.subheader('Daily Rentals')
col1, col2, col3 = st.columns(3)

with col1:
    daily_rent_casual = daily_casual_rent_df['casual'].sum()
    st.metric('Casual User', value= daily_rent_casual)

with col2:
    daily_rent_registered = daily_registered_rent_df['registered'].sum()
    st.metric('Registered User', value= daily_rent_registered)
 
with col3:
    daily_rent_total = daily_rent_df['count'].sum()
    st.metric('Total User', value= daily_rent_total)

# Membuat jumlah penyewaan bulanan
st.subheader('Monthly & Year Rentals')

# Menambahkan kolom kategori untuk bulan dengan urutan
day_df['month'] = pd.Categorical(day_df['month'], categories=[
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 
    ordered=True)

# Menghitung jumlah penyewaan per bulan dan tahun
monthly_counts = day_df.groupby(by=["month", "year"]).agg({
    "count": "sum"
}).reset_index()

# Membuat plot dengan seaborn
fig, ax = plt.subplots(figsize=(24, 8))
sns.lineplot(
    data=monthly_counts,
    x="month",
    y="count",
    hue="year",
    palette="rocket",
    marker="o",
    ax=ax
)

# Menambahkan angka di setiap titik
for _, row in monthly_counts.iterrows():
    ax.text(row['month'], row['count'], str(row['count']), 
            ha='center', va='bottom', fontsize=10)

# Menambahkan judul dan mengatur label
ax.set_title("Jumlah total sepeda yang disewakan berdasarkan Bulan dan Tahun")
ax.set_xlabel(None)
ax.set_ylabel(None)
ax.legend(title="Tahun", loc="upper right")

# Menampilkan plot di Streamlit
st.pyplot(fig)

# Membuah jumlah rata-rata penyewaan berdasarkan kondisi cuaca
st.subheader('Average Weatherly Rentals')

# Menghitung rata-rata penyewaan berdasarkan kondisi cuaca
average_weather_rent_df = day_df.groupby('weather_cond').agg({
    'count': 'mean'  # Menghitung rata-rata
}).reset_index()

# Membuat bar plot
fig, ax = plt.subplots(figsize=(16, 8))

# Warna untuk setiap kondisi cuaca
colors = ["tab:blue", "tab:orange", "tab:green", "tab:red"]

# Membuat barplot
sns.barplot(
    x='weather_cond',
    y='count',
    data=average_weather_rent_df,
    palette=colors,
    ax=ax
)

# Menambahkan angka di atas setiap batang
for index, row in enumerate(average_weather_rent_df['count']):
    ax.text(index, row + 0.1, f"{row:.2f}", ha='center', va='bottom', fontsize=12)

# Mengatur label dan judul
ax.set_xlabel('Kondisi Cuaca', fontsize=20)
ax.set_ylabel('Rata-rata Jumlah Pengguna Sepeda', fontsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.tick_params(axis='y', labelsize=15)
plt.title('Jumlah Rata-rata Pengguna Sepeda berdasarkan Kondisi Cuaca', fontsize=24)

# Menampilkan plot di Streamlit
st.pyplot(fig)

# Membuat Scatter Plots
st.subheader('Scatter Plots of Temperature and Humidity vs Count')

# Set up the figure for the scatter plots
plt.figure(figsize=(14, 6))

# Scatter plot untuk 'temp' vs 'count'
plt.subplot(1, 3, 1)
sns.scatterplot(
    x='temp',
    y='count',
    data=day_df,
    alpha=0.5
)
plt.title('Temperature vs Count')

# Scatter plot untuk 'atemp' vs 'count'
plt.subplot(1, 3, 2)
sns.scatterplot(
    x='atemp',
    y='count',
    data=day_df,
    alpha=0.5
)
plt.title('Feels Like Temperature vs Count')

# Scatter plot untuk 'hum' vs 'count'
plt.subplot(1, 3, 3)
sns.scatterplot(
    x='hum',
    y='count',
    data=day_df,
    alpha=0.5
)
plt.title('Humidity vs Count')

# Menampilkan plot di Streamlit
st.pyplot(plt)

# Reset the current figure to avoid overlaps in subsequent plots
plt.clf()  # Clear the figure

# Membuat jumlah penyewaan berdasarkan season
st.subheader('Seasonly Rentals')

fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(
    x='season',
    y='registered',
    data=season_rent_df,
    label='Registered',
    color='tab:blue',
    ax=ax
)

sns.barplot(
    x='season',
    y='casual',
    data=season_rent_df,
    label='Casual',
    color='tab:orange',
    ax=ax
)

for index, row in season_rent_df.iterrows():
    ax.text(index, row['registered'], str(row['registered']), ha='center', va='bottom', fontsize=12)
    ax.text(index, row['casual'], str(row['casual']), ha='center', va='bottom', fontsize=12)

ax.set_xlabel(None)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20, rotation=0)
ax.tick_params(axis='y', labelsize=15)
ax.legend()
st.pyplot(fig)


# Membuat jumlah penyewaan berdasarkan weekday, working dan holiday
st.subheader('Weekday, Workingday, and Holiday Rentals')

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(15,10))

colors1=["tab:blue", "tab:orange"]
colors2=["tab:blue", "tab:orange"]
colors3=["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple", "tab:brown", "tab:pink"]

# Berdasarkan workingday
sns.barplot(
    x='workingday',
    y='count',
    data=workingday_rent_df,
    palette=colors1,
    ax=axes[0])

for index, row in enumerate(workingday_rent_df['count']):
    axes[0].text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)

axes[0].set_title('Number of Rents based on Working Day')
axes[0].set_ylabel(None)
axes[0].tick_params(axis='x', labelsize=15)
axes[0].tick_params(axis='y', labelsize=10)

# Berdasarkan holiday
sns.barplot(
  x='holiday',
  y='count',
  data=holiday_rent_df,
  palette=colors2,
  ax=axes[1])

for index, row in enumerate(holiday_rent_df['count']):
    axes[1].text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)

axes[1].set_title('Number of Rents based on Holiday')
axes[1].set_ylabel(None)
axes[1].tick_params(axis='x', labelsize=15)
axes[1].tick_params(axis='y', labelsize=10)

# Berdasarkan weekday
sns.barplot(
  x='weekday',
  y='count',
  data=weekday_rent_df,
  palette=colors3,
  ax=axes[2])

for index, row in enumerate(weekday_rent_df['count']):
    axes[2].text(index, row + 1, str(row), ha='center', va='bottom', fontsize=12)

axes[2].set_title('Number of Rents based on Weekday')
axes[2].set_ylabel(None)
axes[2].tick_params(axis='x', labelsize=15)
axes[2].tick_params(axis='y', labelsize=10)

plt.tight_layout()
st.pyplot(fig)

# Menghitung RFM DataFrame
rfm_result = calculate_rfm(day_df)

# Visualisasi RFM dengan Scatter Plot
st.subheader('RFM Scatter Plot')

plt.figure(figsize=(10, 6))
sns.scatterplot(
    x='Recency',
    y='Frequency',
    size='Monetary',
    sizes=(20, 200),
    data=rfm_result,
    alpha=0.5
)

plt.title('RFM Scatter Plot')
plt.xlabel('Recency (days)')
plt.ylabel('Frequency (count)')
st.pyplot(plt)
# Segmentasi Pengguna berdasarkan RFM
st.subheader('RFM Segmentation')

# Menyegmentasikan pengguna
rfm_result['R'] = pd.qcut(rfm_result['Recency'], 4, labels=[4, 3, 2, 1])  # 1: paling baru
rfm_result['F'] = pd.qcut(rfm_result['Frequency'], 4, labels=[1, 2, 3, 4])  # 4: paling sering
rfm_result['M'] = pd.qcut(rfm_result['Monetary'], 4, labels=[1, 2, 3, 4])  # 4: paling banyak

# Menghitung skoring akhir
rfm_result['RFM_Score'] = rfm_result['R'].astype(str) + rfm_result['F'].astype(str) + rfm_result['M'].astype(str)

# Tampilkan segmentasi RFM
st.dataframe(rfm_result[['registered', 'Recency', 'Frequency', 'Monetary', 'RFM_Score']])


st.caption('Copyright (c) Rama Syailana Dewa 2024')