import ee
import folium
from pprint import pprint

ee.Initialize()



def calculateNDVI_S2(image: ee.Image):
    values = {"NIR": image.select('B8'), "RED": image.select('B4')}
    return image.expression("(NIR-RED)/(NIR+RED)", values).rename('NDVI')

first = (ee.ImageCollection('COPERNICUS/S2_SR')
         .filterBounds(ee.Geometry.Point(-70.48, 43.3631))
         .filterDate('2019-01-01', '2019-12-31').first())
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
folium.Map.add_ee_layer = add_ee_layer
map_s2.add_ee_layer(
    first, {'bands': ['B4', 'B3', 'B2'], 'min': -2000, 'max': 2000}, 'first')

# map_s2.add_ee_layer(
#     second, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 2000}, 'second')
print(ndvi.getInfo())
map_s2.save('ndvi.html')