import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def utm13n_to_latlon(
    df: pd.DataFrame,
    x_col: str = 'longitud',
    y_col: str = 'latitud'
) -> pd.DataFrame:
    """Convierte coordenadas UTM Zona 13N (EPSG:32613) a WGS84 (EPSG:4326)."""
    mask = df[x_col].notna() & df[y_col].notna()
    if mask.sum() == 0:
        return df

    points = [
        Point(xy) for xy in zip(df.loc[mask, x_col], df.loc[mask, y_col])
    ]
    gdf = gpd.GeoDataFrame(df.loc[mask], geometry=points, crs='EPSG:32613')
    gdf = gdf.to_crs(epsg=4326)

    df.loc[mask, x_col] = gdf.geometry.x
    df.loc[mask, y_col] = gdf.geometry.y

    return df
