# -*- coding: utf-8 -*-
"""TFM_TAREA3_TIME_SERIES..ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14K-MEjOaw-BcFVXna5ZFcLTQEfMM4Owb
"""

import seaborn as sns

from google.colab import files

from scipy import stats

# Commented out IPython magic to ensure Python compatibility.
import pickle
import os

from datetime import datetime
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
# %matplotlib inline

from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import OrdinalEncoder

import xgboost as xgb

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from google.colab import drive

df = pd.read_pickle("/content/drive/MyDrive/Colab Notebooks/DSMarket/df_final_PK")

pd.__version__

xgb.__version__

import os

if pd.__version__ != "1.5.2":
    os.system("pip install pandas==1.5.2")

if xgb.__version__ != "1.3.3":
    os.system("pip install xgboost==1.3.3")

! pip install pandas==1.5.2

"""#DATA UNDERSTANDING"""

df.info()

df.head()

#eliminamos 'id' ya que solo tiene una fecha por registro

df.drop('id', axis = 1, inplace = True)

df["item"].nunique()

len(sorted(df['date'].unique()))

df.shape

df['date'].value_counts(ascending=False)

# Ventas Enero-2011 -> junio-2015 -- 54 Train
# Predicción julio-2015 -- Predict

df.describe(include =np.number).T

df.describe(exclude= np.number).T

df[df.duplicated()]

df.isnull().sum()

df['yearweek'] = df['yearweek'].apply(lambda x: x.replace('-', ''))

df['yearweek'].value_counts()

df['yearweek'] = df['yearweek'].astype(int)

df.info()

sample_ts = "ACCESORIES_1_001"

ts = df[df["item"] == sample_ts][["date", "sales_total", "sell_price"]]

ts

df.set_index("date").resample("3M")["sales_total"].sum()

MIN_DATE = df["date"].min()
MAX_DATE = df["date"].max()

print(f"Min date is {MIN_DATE}\nMax date is {MAX_DATE}")

df['item'].value_counts()

df[df["item"] == sample_ts].value_counts()

serie_temporal = df[df["item"] == sample_ts]
# Graficar la serie
plt.plot(serie_temporal["date"], serie_temporal["sales_total"])
plt.xlabel("date")
plt.ylabel("sales_total")
plt.show()

"""<a id='eda_global_sales'></a>
### --> 1. EDA: Global Sales
[Volver al índice](#index)<br>
"""

def plot_ts_acf_pacf(y, title):
    '''
    Plots the ts you pass and the acf and pacf.
    '''
    fig = plt.figure(figsize = (12, 10))
    ax1, ax2, ax3 = fig.subplots(3, 1)

    ax1.plot(y)
    plot_acf(x = y, ax = ax2, lags = 14)
    plot_pacf(x = y, ax = ax3, lags = 14)

    plt.suptitle(t = title, fontsize = 20)

y = df.set_index("date").resample("w")["sales_total"].sum()[:-1] # quitamos los registros de la ultima semana

plot_ts_acf_pacf(y = y, title = "Monthly Sales for all items in all shops");

(
    df.
    groupby(["region"])
    ["sales_total"].sum()
    .sort_values(ascending = False)
    .plot(kind = "bar", figsize = (12, 4))
);

(
    df.
    groupby(["category"])
    ["sales_total"].sum()
    .sort_values(ascending = False)
    .plot(kind = "bar", figsize = (12, 4))
);

"""Nuevas variables"""

df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

df["week"] = df["date"].dt.week

df['last_purchase_date'] = df['date'].max()
df['last_purchase_date'] = df['last_purchase_date'].astype(np.int64)

df.groupby(["region"])["sales_total"].sum()

gb_df=df.groupby(["region"])

df.select_dtypes(include= ['object']).describe().T

gb_df.get_group(('New York')).head()

len(gb_df)

regiontop_df= gb_df.get_group(('New York'))

regiontop_df_dia= regiontop_df[['date','sales_total']].groupby('date').sum()

regiontop_df_dia.index

regiontop_df_dia.index = pd.to_datetime(regiontop_df_dia.index)

regiontop_df_dia['sales_total'].plot()

media_ventas_año = regiontop_df_dia['sales_total'].resample('Y').mean()

media_ventas_año.plot()

df.head(3)

# nuevas variables de lag y medias móviles

df["month_store_region_sell_price_lag1"] = df.groupby(['month', 'store', 'region'])["sell_price"].transform(
    lambda series: series.shift(1).backfill().ffill())

df["month_store_region_sell_price_ma1"] = df.groupby(['month', 'store', 'region'])["sell_price"].transform(
    lambda series: series.shift(1).rolling(1).mean().backfill().ffill())

df["store_region_sales_total_lag1"] = df.groupby([ 'store', 'region'])["sales_total"].transform(
    lambda series: series.shift(1).backfill().ffill())

df["store_region_sales_total_ma1"] = df.groupby([ 'store', 'region'])["sales_total"].transform(
    lambda series: series.shift(1).rolling(1).mean().backfill().ffill())

df["store_item_sell_price_lag1"] = df.groupby([ 'store', 'item'])["sell_price"].transform(
    lambda series: series.shift(1).backfill().ffill())

df["store_item_sell_price_ma1"] = df.groupby([ 'store', 'item'])["sell_price"].transform(
    lambda series: series.shift(1).rolling(1).mean().backfill().ffill())

df["category_item_sales_total_lag1"] = df.groupby([ 'category', 'item'])["sales_total"].transform(
    lambda series: series.shift(1).backfill().ffill())

df["category_item_sales_total_ma1"] = df.groupby([ 'category', 'item'])["sales_total"].transform(
    lambda series: series.shift(1).rolling(1).mean().backfill().ffill())

df["department_week_region_sales_total_lag1"] = df.groupby([ 'department','week', 'region'])["sales_total"].transform(
    lambda series: series.shift(1).backfill().ffill())

df["department_week_region_sales_total_ma2"] = df.groupby([ 'department','week', 'region'])["sales_total"].transform(
    lambda series: series.shift(1).rolling(1).mean().backfill().ffill())

#lag2 y ma2

df["month_store_region_sell_price_lag2"] = df.groupby(['month', 'store', 'region'])["sell_price"].transform(
    lambda series: series.shift(2).backfill().ffill())

df["month_store_region_sell_price_ma2"] = df.groupby(['month', 'store', 'region'])["sell_price"].transform(
    lambda series: series.shift(2).rolling(2).mean().backfill().ffill())

df["store_region_sales_total_lag2"] = df.groupby([ 'store', 'region'])["sales_total"].transform(
    lambda series: series.shift(2).backfill().ffill())

df["store_region_sales_total_ma2"] = df.groupby([ 'store', 'region'])["sales_total"].transform(
    lambda series: series.shift(2).rolling(2).mean().backfill().ffill())

df["category_item_sales_total_lag2"] = df.groupby([ 'category', 'item'])["sales_total"].transform(
    lambda series: series.shift(2).backfill().ffill())

df["department_week_region_sales_total_lag2"] = df.groupby([ 'department','week', 'region'])["sales_total"].transform(
    lambda series: series.shift(2).backfill().ffill())

df["category_item_sales_total_ma2"] = df.groupby([ 'category', 'item'])["sales_total"].transform(
    lambda series: series.shift(2).rolling(2).mean().backfill().ffill())

#lag3 y ma3

df["category_item_sales_total_lag3"] = df.groupby([ 'category', 'item'])["sales_total"].transform(
    lambda series: series.shift(3).backfill().ffill())

df["department_week_region_sales_total_lag3"] = df.groupby([ 'department','week', 'region'])["sales_total"].transform(
    lambda series: series.shift(3).backfill().ffill())

df["category_item_sales_total_ma3"] = df.groupby([ 'category', 'item'])["sales_total"].transform(
    lambda series: series.shift(3).rolling(3).mean().backfill().ffill())

df["department_week_region_sales_total_ma3"] = df.groupby([ 'department','week', 'region'])["sales_total"].transform(
    lambda series: series.shift(3).rolling(3).mean().backfill().ffill())

"""###  Time Series Features

def build_ts_vars(df, gb_list, target_column, agg_func, agg_func_name):

    assert "date" in df.columns.tolist(), "Date must be in df columns"

    new_name = "_".join(gb_list + [target_column] + [agg_func_name])

    gb_df_ = (
        df
        .set_index("date")
        .groupby(gb_list)
        .resample("M")[target_column]
        .apply(agg_func)
        .to_frame()
        .reset_index()
        .rename(
            columns = {
                target_column : new_name
            }
        )
    )

    gb_df_[f"{new_name}_lag1"] = gb_df_.groupby(gb_list)[new_name].transform(
        lambda series: series.shift(1).backfill().ffill()
    )
    gb_df_[f"{new_name}_lag2"] = gb_df_.groupby(gb_list)[new_name].transform(
        lambda series: series.shift(2).backfill().ffill())
    gb_df_[f"{new_name}_lag3"] = gb_df_.groupby(gb_list)[new_name].transform(
        lambda series: series.shift(3).backfill().ffill())


    gb_df_[f"{new_name}_ma1"] = gb_df_.groupby(gb_list)[new_name].transform(
        lambda series: series.shift(1).rolling(1).mean().backfill().ffill())
    gb_df_[f"{new_name}_ma2"] = gb_df_.groupby(gb_list)[new_name].transform(
        lambda series: series.shift(2).rolling(2).mean().backfill().ffill())
    gb_df_[f"{new_name}_ma3"] = gb_df_.groupby(gb_list)[new_name].transform(
        lambda series: series.shift(3).rolling(3).mean().backfill().ffill())


    print(f"Dropping columns that might cause target leakage {new_name}")
    gb_df_.drop(new_name, inplace = True, axis = 1)

    return gb_df_

GB_LIST = ['month', 'store', 'region']
TARGET_COLUMN = "sell_price"
AGG_FUNC = np.sum
AGG_FUNC_NAME = "sum"

vars_ts_ = build_ts_vars(
    df = df,
    gb_list = GB_LIST,
    target_column = TARGET_COLUMN,
    agg_func = AGG_FUNC,
    agg_func_name =  AGG_FUNC_NAME

)

vars_ts_.head(10)
"""

#vars_ts_.head(3)

"""<a id='join_ts_features'></a>
### Join TS Features

"""

df.head()

"""## Data Preparation

"""

def OHE(dataframe, column_name):
    _dummy_dataset = pd.get_dummies(dataframe[column_name], prefix=column_name)
    dataframe = pd.concat([dataframe, _dummy_dataset], axis=1)
    return dataframe.drop(column_name, axis=1)

ohe_list=['category', 'department', 'store', 'store_code', 'region']

for column in ohe_list:
  df = OHE(df, column)

print(df.shape)

df.dropna(axis=1, inplace=True)

df.info()

"""<a id='train_test_split'></a>
### Train Test Split
[Volver al índice](#index)<br>
"""

df.columns.tolist()

COLUMNS_TO_DROP = ['Revenue',
]

df.drop(COLUMNS_TO_DROP, inplace = True, axis = 1)

df.set_index("item", inplace = True)

df.sample(5)

print(df.shape)

df.isnull().sum().sum()

train_index = sorted(list(df["date"].unique()))[:-200]

valida_index = [sorted(list(df["date"].unique()))[-200: -50]]

test_index = [sorted(list(df["date"].unique()))[-50:]]

print(f"Our train index is {train_index[:2]} - ... - {train_index[-2:]}\n")
print(f"Our validation index is {valida_index}\n")
print(f"Our test/prediction index is {test_index}\n")

"""Rebalanceo"""

# Extrae todas las fechas únicas
fechas_unicas = sorted(list(df["date"].unique()))

# Define el tamaño de los conjuntos de entrenamiento, validación y prueba
num_train = 200
num_valida = 150
num_test = 50

# Crea los índices de entrenamiento y prueba
train_index = fechas_unicas[:num_train]
test_index = fechas_unicas[-num_test:]

# Crea el índice de validación repitiendo las muestras
valida_index = []
for fecha in fechas_unicas[-num_valida:]:
    valida_index.append(fecha)  # Añadir una vez para cada muestra
    valida_index.append(fecha)  # Repetir dos veces para triplicar el número de muestras
# Crea el índice de train repitiendo las muestras
train_index = []
for fecha in fechas_unicas[-num_train:]:
    train_index.append(fecha)  # Añadir una vez para cada muestra
    train_index.append(fecha)  # Repetir dos veces para triplicar el número de muestras

# Crea el índice de test repitiendo las muestras
test_index = []
for fecha in fechas_unicas[-num_test:]:
    test_index.append(fecha)  # Añadir una vez para cada muestra
    test_index.append(fecha)  # Repetir dos veces para triplicar el número de muestras


# Convierte los índices a listas (opcional)
train_index = list(train_index)
valida_index = list(valida_index)
test_index = list(test_index)

# Usa los índices para obtener los subconjuntos de datos
train_data = df[df["date"].isin(train_index)]
valida_data = df[df["date"].isin(valida_index)]
test_data = df[df["date"].isin(test_index)]

X_train = df[df["date"].isin(train_index)].drop(['sales_total', "date"], axis=1)
Y_train = df[df["date"].isin(train_index)]['sales_total']

X_valida = df[df["date"].isin(valida_index)].drop(['sales_total', "date"], axis=1)
Y_valida = df[df["date"].isin(valida_index)]['sales_total']

X_test = df[df["date"].isin(test_index)].drop(['sales_total', "date"], axis = 1)
Y_test = df[df["date"].isin(test_index)]['sales_total']

"""<a id='model_train'></a>
### Model Train
"""

model = xgb.XGBRegressor(eval_metric = "rmse", seed = 175, early_stopping_rounds=15)

model.fit(X_train, Y_train, eval_set = [(X_train, Y_train), (X_valida, Y_valida)], verbose = True,
)
early_stopping_rounds=15

"""### Model Evaluation"""

fig, ax = plt.subplots(figsize = (10, 15))
xgb.plot_importance(model, importance_type = "gain", ax = ax);

"""### Prediction"""

if "sales_total" in X_test.columns:
    X_test.drop("sales_total", axis = 1, inplace = True)

Y_test_predict = model.predict(X_test)
X_test["sales_total"] = Y_test_predict

X_test.reset_index(inplace = True)

Y_train_predict = model.predict(X_train)
Y_valida_predict = model.predict(X_valida)

rmse_train = np.sqrt(
    mean_squared_error(
        y_true = Y_train,
        y_pred = Y_train_predict
    )
)

rmse_valida = np.sqrt(
    mean_squared_error(
        y_true = Y_valida,
        y_pred = Y_valida_predict
    )
)

rmse_train= str(round(rmse_train, 3)).replace(".", "_")
rmse_valida = str(round(rmse_valida, 3)).replace(".", "_")

print(f"Train RMSE: {rmse_train}")
print(f"Validation RMSE: {rmse_valida}")

# Accede a las predicciones y objetivos para la comparación
predicciones = X_test["ventas_total_predichas"] if "ventas_total_predichas" in X_test.columns else Y_test_predict  # Maneja la ausencia potencial de "ventas_total_predichas"
objetivos = Y_test

# Realiza comparaciones (ejemplos):
print("Ejemplo de Predicciones:", predicciones[:5])  # Imprime las primeras 5 predicciones
print("Ejemplo de Objetivos:", objetivos[:5])  # Imprime los primeros 5 objetivos reales
print("Error Absoluto Medio (MAE):", np.mean(np.abs(predicciones - objetivos)))
print("Error Cuadrático Medio (MSE):", np.mean((predicciones - objetivos) ** 2))
print

# Create a DataFrame for comparison
comparison_df = pd.DataFrame({
    "Index": range(len(predicciones)),  # Assuming predictions and targets have the same length
    "Actual": Y_test,
    "Predicted": predicciones,
    })

# Display the DataFrame
print(comparison_df.head())

# Dado que la escala de valores que tenemos en los últimos años de la muestra de datos es pequeña, el error en la prediccion es alto
# a pesar del rebalanceo, sin embargo en el primer año la escala de valores es bastante mayor y por tanto ahí la dimensión del error ya no es tan significativa.