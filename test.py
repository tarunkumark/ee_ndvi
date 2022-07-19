import ee
import folium
from pprint import pprint
import json
import collections
collections.Callable = collections.abc.Callable

ee.Initialize()

geometry = ee.Geometry.Polygon([[[11.080417771330582, 76.86697184464953],[11.081091615882327, 77.04275308325141],[10.955055789956816, 76.98232828248202]]])
# geometry = ee.Geometry.Point([11.080417771330582, 76.86697184464953])
def calculateNDVI_S2(image: ee.Image, geometry: ee.Geometry):
    values = {"NIR": image.select('B8'), "RED": image.select('B4')}
    ndvi =  image.expression("(NIR-RED)/(NIR+RED)", values).rename('NDVI')
    ndvi2 = image.normalizedDifference(['B8','B4']).rename('NDVI')
    return image.addBands(ndvi2.clip(geometry))
def calculateNDWI_S2(image: ee.Image):
    values = {"GREEN": image.select('B3'), "NIR": image.select('B8')}
    return image.expression("(GREEN-NIR)/(GREEN+NIR)", values).rename('NDWI')

def calculateNDMI_S2(image: ee.Image):
    values = {"SWIR": image.select('B11'), "NIR": image.select('B8')}
    return image.expression("(NIR-SWIR)/(NIR+SWIR)", values).rename('NDMI')

first = (ee.ImageCollection('COPERNICUS/S2_SR')
         .filterBounds(geometry)
         .filterDate('2022-05-20', '2022-12-30').first())
second = (ee.ImageCollection('COPERNICUS/S2_SR')
         .filterBounds(ee.Geometry.Point(-70.48, 43.3631))
         .filterDate('2019-01-02', '2019-12-31').first())

def add_ee_layer(self, ee_image_object, vis_params, name):
  map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
  folium.raster_layers.TileLayer(
      tiles=map_id_dict['tile_fetcher'].url_format,
      attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
      name=name,
      overlay=True,
      control=True
  ).add_to(self)
ndvi=calculateNDVI_S2(first, geometry)
folium.Map.add_ee_layer = add_ee_layer

map_s2 = folium.Map(location=[11.080417771330582, 76.86697184464953], zoom_start=11)
# map_s2.add_ee_layer(ndvi,{'bands': 'NDVI', 'min':1,'max':'5',"palette":['black', 'yellow', 'green']}, 'NDVI image')


# map_s2.save('map_s2.html')

# nir = first.select('B5')
# red = first.select('B4')
# ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
# ndviParams = {min: -1, max: 1, 'palette': ['blue', 'white', 'green', 'red', 'yellow']}
# Map.addLayer(ndvi, ndviParams, 'NDVI image');

# map_s2.add_ee_layer(
#     second, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 2000}, 'second')

def get_ndvi_value_at_location(location, image):
    return image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=location,
        scale=30,
        bestEffort=True
    ).getInfo()

ndvi_values = get_ndvi_value_at_location(ee.Geometry.Polygon([[[11.080417771330582, 76.86697184464953],[11.081091615882327, 77.04275308325141],[10.955055789956816, 76.98232828248202]]]), ndvi)
# print(type(ndvi.geometry().getInfo()))
# ndvi2 = ndvi.where(ndvi.gt(0.0) and (ndvi.lte(0.2)), 2).where(ndvi.gt(0.2) and (ndvi.lte(0.4)), 3).where(ndvi.gt(0.4) and (ndvi.lte(0.6)), 4).where(ndvi.gt(0.6), 5)
ndvi2 = ndvi.clip(geometry)
map_s2.add_ee_layer(ndvi2,{'bands': 'NDVI','min':'0','max':'2000'}, 'NDVI image')
map_s2.add_child(folium.LayerControl())
print(ndvi2.getInfo())
with open("sample.json", "w") as outfile:
    json.dump(ndvi2.geometry().getInfo(), outfile)
map_s2.save('ndvi.html')
