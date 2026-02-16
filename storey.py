# Storey-based filtering and reporting utilities for per-floor analysis.
# Handles extracting added/deleted/shared elements within a specific building storey..


import ifcopenshell as ifc
import ifcopenshell.util.element as ut
import json
import os
import core_ifc
import diffing
import reporting


def is_element_on_storey(guid: str, ifc_path: str, floor: str, model=None):
    """
    check if an IFC element is located on a specific building floor.
    searches up the spatial hierarchy to find which building storey (floor)
    the element belongs to. Comparison is case-insensitive.
    
    Parameters:
        guid: GlobalId of the element to check
        ifc_path: Path to the IFC file
        floor: Name of the floor/storey to check against (e.g. "Ground Floor")
        model: Pre-loaded IFC model (optional)
    
    Returns:
        True if element is on the specified floor.
        False if element is on a different floor.
        None if element not found or has no spatial location.
    """
    model = model or ifc.open(ifc_path)
    element = model.by_guid(guid)
    
    if not element:
        return None
   
    container = ut.get_container(element)  #elements spatial container
    
    while container: #climb up the spatial hierarchy to find the building storey
        if container.is_a("IfcBuildingStorey"):
            storey_name = (container.Name or "").strip().lower()
            floor_name = (floor or "").strip().lower()
            return storey_name == floor_name
        
        container = ut.get_container(container) # Move up one level in the hierarchy
    return None



def Get_Added_Deleted_Shared_Guids_In_SingleStorey(ifc_path1: str, ifc_path2: str, 
                                                    ifc_type_list: list, storey: str, 
                                                    model1=None, model2=None):
    """
    find added, deleted, and shared elements on a specific floor.
    compares two IFC models and identifies changes (added/deleted/shared elements)
    for given element types, then filters results to only include elements on
    the specified building storey/floor.
    This is useful when you only care about changes on one floor, like tracking
    modifications to "Ground Floor" or "Level 2".
    
    Parameters:
        ifc_path1: Path to the first (older) IFC model
        ifc_path2: Path to the second (newer) IFC model
        ifc_type_list: List of IFC types to track (e.g. ['IfcWall', 'IfcDoor'])
        storey: Name of the building storey to filter by (e.g. 'Ground Floor')
        model1: Pre-loaded model for ifc_path1 (optional, speeds up loading)
        model2: Pre-loaded model for ifc_path2 (optional, speeds up loading)
    
    Returns:
        Tuple of three lists (added_guids, deleted_guids, shared_guids):
        - added_guids: Elements added on this floor
        - deleted_guids: Elements deleted from this floor
        - shared_guids: Elements present on this floor in both versions
    """
    added_guids = []
    deleted_guids = []
    shared_guids = []

    for ifc_type in ifc_type_list:
        added = core_ifc.get_added_element_guids(ifc_path1, ifc_path2, ifc_type, 
                                                  model1=model1, model2=model2)
        deleted = core_ifc.get_deleted_element_guids(ifc_path1, ifc_path2, ifc_type, 
                                                      model1=model1, model2=model2)
        shared = core_ifc.get_shared_element_guids(ifc_path1, ifc_path2, ifc_type, 
                                                    model1=model1, model2=model2)
        
        added_guids.extend(added)
        deleted_guids.extend(deleted)
        shared_guids.extend(shared)
    
    # remove duplicates
    added_guids = list(set(added_guids))
    deleted_guids = list(set(deleted_guids))
    shared_guids = list(set(shared_guids))
    
    added_on_floor = []
    deleted_on_floor = []
    shared_on_floor = []
    
    #filtertion steps
    for guid in added_guids:  
        if is_element_on_storey(guid, ifc_path2, storey, model2):
            added_on_floor.append(guid)
    
    for guid in deleted_guids:
        if is_element_on_storey(guid, ifc_path1, storey, model1):
            deleted_on_floor.append(guid)
    
    for guid in shared_guids:
        if is_element_on_storey(guid, ifc_path2, storey, model2):
            shared_on_floor.append(guid)
    
    return added_on_floor, deleted_on_floor, shared_on_floor



