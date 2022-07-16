import ee
import folium
from pprint import pprint
import json
import collections
collections.Callable = collections.abc.Callable

ee.Initialize()



def calculateNDVI_S2(image: ee.Image):
    values = {"NIR": image.select('B8'), "RED": image.select('B4')}
    ndvi =  image.expression("(NIR-RED)/(NIR+RED)", values).rename('NDVI')
    ndvi2 = image.normalizedDifference(['B8','B4']).rename('NDVI')
    return ndvi2
def calculateNDWI_S2(image: ee.Image):
    values = {"GREEN": image.select('B3'), "NIR": image.select('B8')}
    return image.expression("(GREEN-NIR)/(GREEN+NIR)", values).rename('NDWI')

def calculateNDMI_S2(image: ee.Image):
    values = {"SWIR": image.select('B11'), "NIR": image.select('B8')}
    return image.expression("(NIR-SWIR)/(NIR+SWIR)", values).rename('NDMI')

first = (ee.ImageCollection('COPERNICUS/S2_SR')
         .filterBounds(ee.Geometry.LinearRing([[11.080417771330582, 76.86697184464953],[11.081091615882327, 77.04275308325141],[10.955055789956816, 76.98232828248202]]))
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

map_s2 = folium.Map(location=[11.080417771330582, 76.86697184464953], zoom_start=11)
ndvi=calculateNDVI_S2(first)
# nir = first.select('B5')
# red = first.select('B4')
# ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
# ndviParams = {min: -1, max: 1, 'palette': ['blue', 'white', 'green', 'red', 'yellow']}
# Map.addLayer(ndvi, ndviParams, 'NDVI image');
folium.Map.add_ee_layer = add_ee_layer
map_s2.add_ee_layer(ndvi,{'bands': ['NDVI'], 'min': -2000, 'max': 2000, "palette":['FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163', '99B718', '74A901', '66A000', '529400', '3E8601', '207401', '056201', '004C00', '023B01', '012E01', '011D01', '011301']}, 'NDVI image')

# map_s2.add_ee_layer(
#     second, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 2000}, 'second')
print(ndvi.getInfo())
with open("sample.json", "w") as outfile:
    json.dump(first.getInfo(), outfile)
map_s2.save('ndvi.html')