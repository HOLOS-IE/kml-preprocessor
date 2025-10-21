# FULL OKAY CODE


import os
import random
from pykml import parser
from pykml.factory import KML_ElementMaker as KML
from lxml import etree


def extract_details_from_kml(file_path):
    print(f"Reading file: {file_path}")
    with open(file_path, encoding='utf-8') as f:
        doc = parser.parse(f)
    
    polygons = {}
    
    # Iterate through all Placemark elements in the KML file
    for placemark in doc.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        # Get placemark name
        placemark_name_element = placemark.find('{http://www.opengis.net/kml/2.2}name')
        placemark_name = placemark_name_element.text.strip() if placemark_name_element is not None else "Unnamed Placemark"
        
        # print(f"Found placemark: {placemark_name}")  # Debug output
        
        # Check if the placemark contains a polygon (either direct or in MultiGeometry)
        polygon = placemark.find('.//{http://www.opengis.net/kml/2.2}Polygon')
        if polygon is not None:
            # Extract coordinates of the polygon
            coordinates_element = polygon.find('.//{http://www.opengis.net/kml/2.2}coordinates')
            if coordinates_element is not None:
                coordinates = coordinates_element.text.strip()
                
                # Handle both space-separated and comma-separated coordinate formats
                if ' ' in coordinates:
                    # Space-separated points (like in your sample)
                    points = coordinates.split()
                else:
                    # Single line of coordinates - split by spaces after cleaning
                    points = coordinates.split()
                
                polygon_points = []
                for point in points:
                    if ',' in point:
                        coords = point.split(',')
                        if len(coords) >= 2:
                            lon, lat = coords[0], coords[1]
                            polygon_points.append((float(lon), float(lat)))
                
                # Store the placemark name and associated polygon points
                if polygon_points:  # Only store if we have valid points
                    polygons[placemark_name] = polygon_points
                    # print(f"Stored polygon for '{placemark_name}' with {len(polygon_points)} points")

    print(f'Total polygons found: {len(polygons)}')
    
    # # Check if we found polygons
    # if len(polygons) == 0:
    #     print("No polygons found in the KML file.")
    # else:
    #     # Print all placemark names for verification
    #     print("Placemark names found:")
    #     for name in polygons.keys():
    #         print(f"  - {name}")
    
    return polygons


def create_kml_from_placemark_polygons(placemark_data, file_path):
    # Create a KML document
    filename = os.path.basename(file_path)
    kml_doc = KML.kml(
        KML.Document(
            KML.name(filename)
        )
    )
    index = 1
    # Iterate through the placemark data and create placemarks with polygons
    for placemark_name, polygon_coordinates in placemark_data.items():
        # Create placemark element - keep original name instead of using index
        placemark = KML.Placemark(
            KML.name(placemark_name),  # Use original name like "842"
            KML.ExtendedData(),
            KML.Polygon(
                KML.outerBoundaryIs(
                    KML.LinearRing(
                        KML.coordinates(' '.join([f'{lon},{lat},0.0' for lon, lat in polygon_coordinates]))
                    )
                )
            )
        )
        # Append placemark to the document
        kml_doc.Document.append(placemark)
        index += 1

    # Create an ElementTree object and serialize it to a string
    kml_string = etree.tostring(kml_doc, pretty_print=True, encoding='utf-8', xml_declaration=True)

    # Save the KML string to a file
    with open(file_path, 'wb') as f:
        f.write(kml_string)

    print("KML file saved as " + filename)


def get_placemark_names(polygons_dict):
    """
    Helper function to get just the placemark names from the extracted data
    """
    names = list(polygons_dict.keys())
    return names
    
if __name__ == "__main__":
    folder_name = 'data'
    script_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.dirname(script_directory)
    folder_path = os.path.join(parent_directory, folder_name)
    unprocessed_map_path = os.path.join(folder_path, "Small_area_maps")

    processed_map_path = os.path.join(folder_path, "processed_map")
    if not os.path.exists(processed_map_path):
        os.makedirs(processed_map_path)

    files = [os.path.join(unprocessed_map_path, f) for f in os.listdir(unprocessed_map_path) if os.path.isfile(os.path.join(unprocessed_map_path, f))]
    
    for file_path in files:
        filename = os.path.basename(file_path)
        print(f"\nProcessing: {filename}")
        
        # Extract data from KML
        data = extract_details_from_kml(file_path)
        
        # Get just the names if you need them separately
        # placemark_names = get_placemark_names(data)
        # print(f"Placemark names: {placemark_names}")
        
        # Process and save
        save_file_path = os.path.join(processed_map_path, filename)
        create_kml_from_placemark_polygons(data, save_file_path)