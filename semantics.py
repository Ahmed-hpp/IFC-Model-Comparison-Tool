# # Semantic analysis using IFC relationships to build descriptive element graphs.
# # this is used afterwards for detecting logical/semantic modifications between model versions.


import ifcopenshell as ifc
import networkx as nx
import ifcopenshell.util.element as ut
import numpy as np


def create_element_graph(element_guid: str, model: ifc.file):
    """
    Build a graph representing an IFC element's properties and relationships.
    
    Creates a NetworkX graph where the element is the central node,
    connected to its properties, quantities, and parent/child relationships.
    This graph structure makes it easy to compare elements between model versions.
    
    Graph structure:
    - Central node: The element (with Name, IfcType, Space_container)
    - Property set nodes: Connected via edges, contain property key-value pairs
    - Quantity set nodes: Connected via edges, contain measurements
    - Child nodes: Elements this element is composed of
    - Parent nodes: Elements this element is part of
    
    Parameters:
        element_guid: GUID of the element to analyze
        model: Loaded IFC model containing the element
    
    Returns:
        NetworkX Graph representing the element's data structure.
        Returns empty graph if element not found.
    """
    elem = model.by_guid(element_guid)
    if not elem:
        return nx.DiGraph()
    
    graph = nx.DiGraph()
    
    # Add central element node
    parent = ut.get_container(elem)
    level = parent.Name if parent else "No Parent"
    graph.add_node(
        element_guid,
        Name=elem.Name if elem.Name else "un-named",
        IfcType=elem.is_a(),
        Space_container=level
    )
    
    # Extract property sets and quantity sets
    if hasattr(elem, 'IsDefinedBy') and elem.IsDefinedBy:
        for rel in elem.IsDefinedBy:
            if not rel or not rel.is_a('IfcRelDefinesByProperties'):
                continue
            
            definition = rel.RelatingPropertyDefinition
            
            # Handle property sets
            if definition.is_a('IfcPropertySet'):
                pset = definition
                pset_guid = pset.GlobalId
                pset_data = {}
                
                if hasattr(pset, 'HasProperties') and pset.HasProperties:
                    for prop in pset.HasProperties:
                        property_name = prop.Name
                        value = None
                        if hasattr(prop, 'NominalValue'):
                            if prop.NominalValue:  # Check if not None
                                value = prop.NominalValue.wrappedValue
                        pset_data[property_name] = value
                
                # Only keep properties with actual values
                clean_pset_data = {k: v for k, v in pset_data.items() if v is not None}
                graph.add_node(pset_guid, Name=pset.Name, type="IfcPropertySet", **clean_pset_data)
                graph.add_edge(element_guid, pset_guid)
            
            # Handle quantity sets
            elif definition.is_a('IfcElementQuantity'):
                qset = definition
                qset_guid = qset.GlobalId
                quantities = qset.Quantities
                quantity_data = {}
                
                # Supported quantity types
                quantity_types = [
                    'IfcQuantityLength', 'IfcQuantityArea', 'IfcQuantityCount',
                    'IfcQuantityTime', 'IfcQuantityVolume', 'IfcQuantityWeight'
                ]
                
                for qty in quantities:
                    if qty.is_a(quantity_types[0]):
                        quantity_data[qty.Name] = np.round(qty.LengthValue, 4)
                    elif qty.is_a(quantity_types[1]):
                        quantity_data[qty.Name] = np.round(qty.AreaValue, 4)
                    elif qty.is_a(quantity_types[2]):
                        quantity_data[qty.Name] = np.round(qty.CountValue, 4)
                    elif qty.is_a(quantity_types[3]):
                        quantity_data[qty.Name] = np.round(qty.TimeValue, 4)
                    elif qty.is_a(quantity_types[4]):
                        quantity_data[qty.Name] = np.round(qty.VolumeValue, 4)
                    elif qty.is_a(quantity_types[5]):
                        quantity_data[qty.Name] = np.round(qty.WeightValue, 4)
                
                graph.add_node(qset_guid, name=qset.Name, type=qset.is_a(), **quantity_data)
                graph.add_edge(element_guid, qset_guid)
    
    # Extract child elements (decomposition)
    if hasattr(elem, 'IsDecomposedBy') and elem.IsDecomposedBy:
        for rel in elem.IsDecomposedBy:
            if not rel or not rel.is_a('IfcRelAggregates'):
                continue
            
            if hasattr(rel, 'RelatedObjects'):
                for child_element in rel.RelatedObjects:
                    child_guid = child_element.GlobalId
                    graph.add_node(
                        child_guid,
                        Name=child_element.Name if child_element.Name else "un-named",
                        IfcType=child_element.is_a(),
                        relation="Child"
                    )
                    graph.add_edge(element_guid, child_guid)
    
    # Extract parent elements (aggregation)
    if hasattr(elem, 'Decomposes') and elem.Decomposes:
        for rel in elem.Decomposes:
            if not rel or not rel.is_a('IfcRelAggregates'):
                continue
            
            if hasattr(rel, 'RelatingObject'):
                parent_element = rel.RelatingObject
                parent_guid = parent_element.GlobalId
                graph.add_node(
                    parent_guid,
                    Name=parent_element.Name if parent_element.Name else "un-named",
                    IfcType=parent_element.is_a(),
                    Relation="Parent"
                )
                graph.add_edge(element_guid, parent_guid)
    
    return graph
