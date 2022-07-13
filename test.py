import ee
import folium
from pprint import pprint

import collections
collections.Callable = collections.abc.Callable

ee.Initialize()



def calculateNDVI_S2(image: ee.Image):
    values = {"NIR": image.select('B8'), "RED": image.select('B4')}
    return image.expression("(NIR-RED)/(NIR+RED)", values).rename('NDVI')

def calculateNDWI_S2(image: ee.Image):
    values = {"GREEN": image.select('B3'), "NIR": image.select('B8')}
    return image.expression("(GREEN-NIR)/(GREEN+NIR)", values).rename('NDWI')

def calculateNDMI_S2(image: ee.Image):
    values = {"SWIR": image.select('B11'), "NIR": image.select('B8')}
    return image.expression("(NIR-SWIR)/(NIR+SWIR)", values).rename('NDMI')

first = (ee.ImageCollection('COPERNICUS/S2_SR')
         .filterBounds(ee.Geometry.Polygon([[-70.48, 43.3631],[70.48, 43.3631],[-70.48, -43.3631]]))
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

map_s2 = folium.Map(location=[43.7516, -70.8155], zoom_start=11)
ndvi=calculateNDVI_S2(first)
# nir = first.select('B5')
# red = first.select('B4')
# ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
# ndviParams = {min: -1, max: 1, 'palette': ['blue', 'white', 'green', 'red', 'yellow']}
# Map.addLayer(ndvi, ndviParams, 'NDVI image');
folium.Map.add_ee_layer = add_ee_layer
map_s2.add_ee_layer(ndvi, ndviParams, 'NDVI image')

# map_s2.add_ee_layer(
#     second, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 2000}, 'second')
print(ndvi.getInfo())
map_s2.save('ndvi.html')