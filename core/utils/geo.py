import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def is_utm_coordinate(x: float, y: float) -> bool:
    if pd.isna(x) or pd.isna(y):
        return False
    return abs(x) > 180 or abs(y) > 90

def utm13n_to_latlon(
    df: pd.DataFrame,
    x_col: str = 'longitud',
    y_col: str = 'latitud'
) -> pd.DataFrame:
    mask = df[x_col].notna() & df[y_col].notna()
    if mask.sum() == 0:
        return df

    utm_mask = mask & df.apply(lambda row: is_utm_coordinate(row[x_col], row[y_col]), axis=1)

    if utm_mask.sum() == 0:
        return df

    points = [
        Point(xy) for xy in zip(df.loc[utm_mask, x_col], df.loc[utm_mask, y_col])
    ]
    gdf = gpd.GeoDataFrame(df.loc[utm_mask], geometry=points, crs='EPSG:32613')
    gdf = gdf.to_crs(epsg=4326)

    df.loc[utm_mask, x_col] = gdf.geometry.x
    df.loc[utm_mask, y_col] = gdf.geometry.y

    return df
