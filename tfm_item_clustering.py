# -*- coding: utf-8 -*-
"""TFM_ITEM_CLUSTERING.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14H3WdhJV3i_IBCXccq50Jp-Q4FX5OTXW
"""

from google.colab import drive
drive.mount('/content/drive')

import numpy as np
import pandas as pd

pd.options.display.float_format = '{:,.2f}'.format
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

df = pd.read_pickle("/content/drive/MyDrive/Colab Notebooks/DSMarket/df_final_PK")

df.head()

df.info()

df['id'].value_counts()

df['item'].value_counts()



##posibles nuevas variables:
'''
-max_venta
-min_venta
-mean_venta
-fecha ultima compra
-mes_compra
-compra por semanas
-agrupando por ventas podemos sacar por ejem, los 15 items mas populares:
most_important_item = df.groupby(['item'])['sales_total'].size().sort_values().tail(15).index.tolist()
df['top_items']=df['item'].isin(most_important_item)
- agrupar los items por sell_price por fecha para ver como cambia a lo largo tiempo
##sell_price_evolution= df.groupby(['item', 'date'])['sell_price'].size().sort_values().tail(15).index.tolist()
df["sell_price_evolution"] = df.groupby(['item', 'date'])['sell_price'].transform(np.mean)
df["sell_price_evolution"] = df.groupby(['item', 'date'])['sales_total'].transform(np.sum)

-agrupando podemos sacar el weekday que mas se vende un item
'''

most_important_item = df.groupby(['item'])['sales_total'].size().sort_values().tail(15).index.tolist()

df['top_items']=df['item'].isin(most_important_item)

df['top_items'].value_counts()

less_important_items = df.groupby(['item'])['sales_total'].size().sort_values().head(15).index.tolist()
df['less_items']=df['item'].isin(less_important_items)

df['less_items'].value_counts()

df["sell_price_evolution"] = df.groupby(['item', 'date'])['sell_price'].transform(np.mean)

df['sell_price_evolution']. nunique()

df['sell_price'].nunique()

df.tail(3)

aggregated_Revenue = df.groupby('item').agg(
    max_Revenue = ('Revenue', 'max'),
    min_Revenue = ('Revenue', 'min'),
    mean_Revenue = ('Revenue', 'mean')

)

df = pd.merge(df, aggregated_Revenue, on = 'item')

df.head(3)

df['max_Revenue'].nunique()

df.info()

df["month_sale"] = df["date"].dt.month
df["year_sale"] = df["date"].dt.year

df["sales_total_evolution"] = df.groupby(['item', 'date'])['sales_total'].transform(np.sum)

df['last_sale_date'] = df['date'].max()

df['time_since_last_sale'] =\
df['last_sale_date'] - df['date']

df["time_since_last_sale"] = df["time_since_last_sale"].dt.days

df.head(3)

# Commented out IPython magic to ensure Python compatibility.
# silence warnings
import warnings
warnings.filterwarnings("ignore")

# operating system
import os

# time calculation to track some processes
import time

# numeric and matrix operations
import numpy as np
import pandas as pd

# loading ploting libraries
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

# python core library for machine learning and data science
import sklearn
from sklearn import set_config
set_config(transform_output = "pandas")

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import RobustScaler, MinMaxScaler
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.cluster import KMeans

print("Working with this sklearn version {}".format(sklearn.__version__))

df.info()

df.columns.tolist()

df.set_index("item", inplace = True)

lc = [
  'sell_price',
  'Revenue',
 'top_items',
 'less_items',
 'sell_price_evolution',
 'max_Revenue',
 'min_Revenue',
 'mean_Revenue',
 'month_sale',
 'year_sale',
 'sales_total_evolution',
  'sales_total',
  'time_since_last_sale']

df = df[lc]

def build_unique_id_features(X):
    aggregated_df = X.groupby(X.index).agg(
        n_sales=('sales_total', 'count'),
        amount_sales=('Revenue', 'sum'),
        avg_ticket=('Revenue', 'mean'),
        price_evol=('sell_price_evolution', 'mean'),

        last_sales = ('time_since_last_sale', 'min'),
        first_sales = ('time_since_last_sale', 'max'),

       most_popular_items=('top_items', 'sum'),
       less_popular_items=('less_items', 'sum')


    )
    return aggregated_df

## mean_sales_per_store=X[['store_code_BOS_1', 'store_code_BOS_2', 'store_code_BOS_3', 'store_code_NYC_1', 'store_code_NYC_2', 'store_code_NYC_3', 'store_code_NYC_4', 'store_code_PHI_1', 'store_code_PHI_2', 'store_code_PHI_3']].mean(),
    ##    max_seller_store=X[['store_code_BOS_1', 'store_code_BOS_2', 'store_code_BOS_3', 'store_code_NYC_1', 'store_code_NYC_2', 'store_code_NYC_3', 'store_code_NYC_4', 'store_code_PHI_1', 'store_code_PHI_2', 'store_code_PHI_3']].max()

ProductIdFeatureGenerator = FunctionTransformer(func = build_unique_id_features)

# separamos el pipeline del a loop, para no tener que volver a hacer los primeros 3 pasos para cada k de la loop
pipe = Pipeline(steps = [
    ("Imputer", KNNImputer()),
    ("CustomTransformer", ProductIdFeatureGenerator),
    ("RobustScaler", RobustScaler(quantile_range = (0, 99.0)))
])

df_scaled_transformed = pipe.fit_transform(df)

sse = {}

for k in range(2, 15):

    print(f"Fitting pipe with {k} clusters")

    clustering_model = KMeans(n_clusters = k)
    clustering_model.fit(df_scaled_transformed)

    sse[k] = clustering_model.inertia_

#elbow curve

fig = plt.figure(figsize = (16, 8))
ax = fig.add_subplot()

x_values = list(sse.keys())
y_values = list(sse.values())

ax.plot(x_values, y_values, label = "Inertia/dispersión de los clústers")
fig.suptitle("Variación de la dispersión de los clústers en función de la k", fontsize = 16);

pipe = Pipeline(steps = [
    ("Imputer", KNNImputer()),
    ("CustomTransformer", ProductIdFeatureGenerator),
    ("RobustScaler", RobustScaler(quantile_range = (0, 99.0))),
    ("Clustering", KMeans(n_clusters = 5, random_state = 175))
])

df.shape

pipe.fit(df)

X_processed = pipe[:2].transform(df)

labels = pipe.predict(df)

# le asignamos al DataFrame procesado el clúster.
# si lo hacemos al df escalado será más díficil de interpretar los resultados porque los números están escalados
X_processed["cluster"] = labels

X_processed.shape

"""FICHA

"""

ficha_df = pd.DataFrame()

#for i, col in enumerate(["amount_sales", "last_purchase", "most_popular_items"]):
    #resumen_data = X_processed[["cluster", col]].groupby("cluster").describe().T[1:]
    #ficha_df = ficha_df.append(resumen_data)

resumen_data_list = []
for i, col in enumerate(["amount_sales", "last_sales", "most_popular_items", "less_popular_items"]):
    resumen_data = X_processed[["cluster", col]].groupby("cluster").describe().T[1:]
    resumen_data_list.append(resumen_data)

ficha_df = pd.concat(resumen_data_list, ignore_index=True)

# generamos nuestro multiindex

out_index = [
    "Monetarios",
    "Frecuencia",
    "Popularidad",
    "Popularidad"
]

inner_index = [
    "Importe",
    "tiempo última venta",
    "Top ventas",
    "Peores ventas"

]

estadisticos = ["Media", "Desviación", "Mínimo", "Perc. 25", "Perc. 50", "Perc. 75", "Máximo"]

new_multi_index = []

for oi, ii, in zip(out_index, inner_index):
    for es in estadisticos:
        new_multi_index.append((oi, ii, es))

def generate_multiindex(list_of_tuples, names):
    return pd.MultiIndex.from_tuples(list_of_tuples, names = names)

names = ["Grupo Indicadores", "Indicador", "Estadístico"]
index_ficha = generate_multiindex(new_multi_index, names)
ficha_df.set_index(index_ficha, inplace = True)

ficha_df = ficha_df.rename(columns = {
    0 : "items mayores ingresos",
    1 : "items Menos ppopulares",
    2 : "items Mas populares",
    3 : "items menor stock",
    4 : "Items mayor stock"
})

ficha_df.head(29)

(
    X_processed
    .groupby("cluster")
    .describe()
    .T
    .style.background_gradient(cmap = 'Blues', axis = 1)
)

tamaño_clusters = X_processed.groupby("cluster").size().to_frame().T
tamaño_clusters.set_index(generate_multiindex([("General", "Clúster", "Tamaño")] , names), inplace = True)

tamaño_clusters.head(15)

#ficha_df = tamaño_clusters.append(ficha_df)

#ficha_df = pd.concat([ficha_df, tamaño_clusters], ignore_index=True)

ficha_df = ficha_df.rename(columns = {
    0 : "items mayores ingresos",
    1 : "items Menos ppopulares",
    2 : "items Mas populares",
    3 : "items menor stock",
    4 : "Items mayor stock"
})

ficha_df.style.background_gradient(cmap = 'Blues', axis = 1)



"""# Nueva sección

Conclusiones
"""

#El primer cluster aglutina los items con mas ingresos , mejor ticket promedio y con el precio promedio mas alto,
# el segundo aglutina los items menos vendidos,
# el tercero los mas  vendidos,
# el cuarto es un grupo que aglutina los items con mayor flujo de stock(menor tiempo stock) y con una rango de precios mayor,
# el quinto grupo aglutina una gran cantidad de items que tiene un mayor tiempo en stock (min=0).

X_processed

gb_df= X_processed.groupby('cluster')

X_processed.sort_values(by='cluster', ascending=False).head(20)

X_processed['cluster'].value_counts()

menos_populares =(X_processed['cluster']=='1')

filtered_data = X_processed[X_processed['cluster'] == 1]

filtered_data

filtered_data2 = X_processed[X_processed['cluster'] == 2]
filtered_data2

filtered_data0 = X_processed[X_processed['cluster'] == 0]
filtered_data0

for index in filtered_data0.index:
    item_value = filtered_data0.loc[index, 'cluster']  # Reemplaza 'columna1' con el nombre de la columna que te interesa
    print(f"Índice: {index}, Valor: {item_value}")

filtered_data3 = X_processed[X_processed['cluster'] == 3]

for index in filtered_data3.index:
    item_value = filtered_data3.loc[index, 'cluster']  # Reemplaza 'columna1' con el nombre de la columna que te interesa
    print(f"Índice: {index}, Valor: {item_value}")

filtered_data4 = X_processed[X_processed['cluster'] == 4]

for index in filtered_data4.index:
    item_value = filtered_data4.loc[index, 'cluster']  # Reemplaza 'columna1' con el nombre de la columna que te interesa
    print(f"Índice: {index}, Valor: {item_value}")