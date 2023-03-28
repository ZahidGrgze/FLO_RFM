import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

df_ = pd.read_csv("hafta2(RFM_CRM)/flo_data_20k.csv", parse_dates=["first_order_date", "last_order_date", "last_order_date_online", "last_order_date_offline"])
df = df_.copy()


def prepare(dataframe, head=10):
    print("İlk 10 gözlem : ", dataframe.head())
    print("/n################################################")
    print("Değişken isimleri : ", dataframe.columns)
    print("/n################################################")
    print("Betimsel istatistik: ", dataframe.describe().T )
    print("/n################################################")
    print("Boş Değerler : ", dataframe.isnull().sum())

    dataframe["TotalPrice"] = dataframe["customer_value_total_ever_online"] + dataframe["order_num_total_ever_offline"]
    dataframe["TotalOrder"] = dataframe["order_num_total_ever_offline"] + dataframe["order_num_total_ever_online"].astype(int)

    return dataframe

prepare(df)

today_date = dt.datetime(2021, 6, 2)
df["last_order_date"].max()

rfm = pd.DataFrame()
rfm["customer_id"] = df["master_id"]
rfm["recency"] = (analysis_date - df["last_order_date"]).astype('timedelta64[D]')
rfm["frequency"] = df["order_num_total"]
rfm["monetary"] = df["customer_value_total"]

rfm.head()


rfm.columns = ["recency", "frequency", "monetary"]
rfm.head()

rfm["frequency"] = rfm["frequency"].astype(int)

rfm["recency_score"] = pd.qcut(rfm["recency"], q=5 , labels=[5, 4 ,3 ,2, 1])
rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["monetary"], q=5, labels=[1, 2, 3, 4, 5])

rfm.head()

rfm["RF_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)

rfm.groupby("segment")[["recency", "frequency", "monetary"]].mean()
df.head()
customers = rfm[(rfm["segment"] == "champions") | (rfm["segment"] == "loyal_customers")]

x = df[(df["master_id"].isin(customers.index)) & (df["interested_in_categories_12"].str.contains("KADIN"))]["master_id"]
x.to_csv("master_id.csv", index = False)

df["interested_in_categories_12"]
target_customers = rfm[(rfm["segment"] == "hibernating") | (rfm["segment"] == "cant_loose") | rfm["segment"] == "new_customers" ]

customer = df[(df["master_id"].isin(target_customers.index)) & (df["interested_in_categories_12"].str.contains("ERKEK")) | (df["interested_in_categories_12"].str.contains("COCUK"))]["master_id"]
customer.to_csv("y_master_id.csv", index=False)