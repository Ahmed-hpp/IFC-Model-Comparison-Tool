# Core IFC utilities for extracting GUID sets and basic element information.
# These functions provide the foundation for all comparison and classification operations,...
import ifcopenshell as ifc
import re
from typing import List

def get_added_element_guids(ifc_path_v1: str, ifc_path_v2: str, ifc_type: str, model1=None, model2=None):
    """
    Find elements that were added between two IFC model versions.
    
    Compares two IFC files and returns the GUIDs of elements that exist in 
    version 2 but not in version 1. Uses set difference for efficient comparison.
    
    Parameters:
        ifc_path_v1: Path to the first (older) IFC file
        ifc_path_v2: Path to the second (newer) IFC file
        ifc_type: IFC element type to check (e.g. 'IfcWall', 'IfcDoor')
        model1: Pre-loaded model for v1 (optional, saves loading time)
        model2: Pre-loaded model for v2 (optional, saves loading time)
    
    Returns:
        List of GUIDs (strings) for elements added in v2.
        Returns empty list if nothing was added.
    
    Example:
        new_walls = get_added_element_guids('old.ifc', 'new.ifc', 'IfcWall')
    """
    model1 = model1 or ifc.open(ifc_path_v1)
    model2 = model2 or ifc.open(ifc_path_v2)
    
    guids_v1 = {elem.GlobalId for elem in model1.by_type(ifc_type)}
    guids_v2 = {elem.GlobalId for elem in model2.by_type(ifc_type)}
    
    added_guids = list(guids_v2 - guids_v1)
    
    return added_guids


def get_deleted_element_guids(ifc_path_v1: str, ifc_path_v2: str, ifc_type: str, model1=None, model2=None):
    """
    Find elements that were deleted between two IFC model versions.
    
    Compares two IFC files and returns the GUIDs of elements that existed in
    version 1 but are missing from version 2. Uses set difference to find
    elements that were removed.
    
    Parameters:
        ifc_path_v1: Path to the first (older) IFC file
        ifc_path_v2: Path to the second (newer) IFC file
        ifc_type: IFC element type to check (e.g. 'IfcWall', 'IfcDoor')
        model1: Pre-loaded model for v1 (optional, saves loading time)
        model2: Pre-loaded model for v2 (optional, saves loading time)
    
    Returns:
        List of GUIDs (strings) for elements deleted from v2.
        Returns empty list if nothing was deleted.
    
    Example:
        removed_doors = get_deleted_element_guids('old.ifc', 'new.ifc', 'IfcDoor')
    """
    model1 = model1 or ifc.open(ifc_path_v1)
    model2 = model2 or ifc.open(ifc_path_v2)
    
    guids_v1 = {elem.GlobalId for elem in model1.by_type(ifc_type)}
    guids_v2 = {elem.GlobalId for elem in model2.by_type(ifc_type)}
    
    deleted_guids = list(guids_v1 - guids_v2)
    
    return deleted_guids


def get_shared_element_guids(ifc_path_v1: str, ifc_path_v2: str, ifc_type: str,
                              model1=None, model2=None):
    """
    Find elements that exist in both IFC model versions.
    
    Compares two IFC files and returns the GUIDs of elements that are present
    in both versions. Uses set intersection to find common elements. The result
    is sorted for consistent ordering.
    
    Parameters:
        ifc_path_v1: Path to the first IFC file
        ifc_path_v2: Path to the second IFC file
        ifc_type: IFC element type to check (e.g. 'IfcWall', 'IfcDoor')
        model1: Pre-loaded model for v1 (optional, saves loading time)
        model2: Pre-loaded model for v2 (optional, saves loading time)
    
    Returns:
        Sorted list of GUIDs (strings) for elements present in both models.
        Returns empty list if no common elements found.
    
    Example:
        common_walls = get_shared_element_guids('v1.ifc', 'v2.ifc', 'IfcWall')
    """
    model1 = model1 or ifc.open(ifc_path_v1)
    model2 = model2 or ifc.open(ifc_path_v2)
    
    guids_v1 = {elem.GlobalId for elem in model1.by_type(ifc_type)}
    guids_v2 = {elem.GlobalId for elem in model2.by_type(ifc_type)}
    
    shared_guids = list(guids_v1 & guids_v2)
    shared_guids.sort()
    
    return shared_guids


def Get_All_guids(ifc_type: str, ifc_path: str, model=None):
    """
    Get all GUIDs for a specific IFC element type from a model.
    
    Extracts the GlobalId of every element matching the specified IFC type.
    Filters out any elements without a valid GUID.
    
    Parameters:
        ifc_type: IFC class name to search for (e.g. 'IfcWall', 'IfcDoor')
        ifc_path: Path to the IFC file
        model: Pre-loaded IFC model (optional, if provided ifc_path is ignored)
    
    Returns:
        List of GUID strings for all matching elements.
        Returns empty list if no elements found or if elements have no GUIDs.
    
    Example:
        wall_guids = Get_All_guids('IfcWall', 'model.ifc')
    """
    model = model or ifc.open(ifc_path)
    elements = model.by_type(ifc_type)
    
    all_guids = []
    for element in elements:
        guid = element.GlobalId
        if guid:
            all_guids.append(guid)
    
    return all_guids



def guid_exists(guid: str, ifc_path: str, model=None) -> bool:
    """
    Check if a GUID exists in an IFC model.
    
    Safely checks whether a given GUID corresponds to a valid element in the
    IFC model. Handles cases where the GUID lookup might fail or return None.
    
    Parameters:
        guid: The GlobalId string to search for
        ifc_path: Path to the IFC file
        model: Pre-loaded IFC model (optional)
    
    Returns:
        True if the GUID exists and points to a valid element.
        False if the GUID doesn't exist or lookup fails.
    
    Example:
        if guid_exists('1xkN_OcsdhshZl3dHpslmr', 'model.ifc'):
            print("Element found")
    """
    model = model or ifc.open(ifc_path)
    
    try:
        element = model.by_guid(guid)
        return element is not None
    except Exception:
        # If GUID is invalid or lookup fails for any reason
        return False

    

def read_guids_from_txt(txt_path: str, deduplicate: bool = True) -> List[str]:
    """
    Read GUIDs from a text file.
    
    Flexible text parser that handles various formats:
    - One GUID per line or multiple GUIDs on the same line
    - Separators: spaces, commas, semicolons
    - Comments starting with '#' are ignored
    - Quotes around GUIDs are automatically removed
    - Empty lines are skipped
    
    Parameters:
        txt_path: Path to the text file containing GUIDs
        deduplicate: If True, removes duplicate GUIDs while preserving order.
                     If False, returns all GUIDs including duplicates.
    
    Returns:
        List of GUID strings extracted from the file.
    """
    with open(txt_path, "r", encoding="utf-8-sig") as f:
        lines = f.read().splitlines()
    
    guids: List[str] = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Remove inline comments
        if "#" in line:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
        
        # Split by comma, semicolon, or whitespace
        for token in re.split(r"[,\s;]+", line):
            token = token.strip().strip('"').strip("'")
            if token:
                guids.append(token)
    
    if not deduplicate:
        return guids
    
    # Remove duplicates while preserving order
    seen = set()
    unique_guids: List[str] = []
    for guid in guids:
        if guid not in seen:
            seen.add(guid)
            unique_guids.append(guid)
    
    return unique_guids

