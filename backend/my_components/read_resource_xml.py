import xml.etree.ElementTree as ET

def resource_xml(xmL_object):
    tree = ET.parse(xmL_object)
    root = tree.getroot()
    print(root)
