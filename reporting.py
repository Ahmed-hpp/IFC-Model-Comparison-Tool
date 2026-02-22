# Report generation for CSV, JSON, and text summaries of all detected changes.
# important for producing user-readable outputs of the comparison results.



import ifcopenshell as ifc
import ifcopenshell.util.element as ut
import json
import csv
import os
import core_ifc
import diffing
import storey



def extract_element_data(ListOfGuids: list, ifc_path: str, model=None):
    """Creates a list of dictionaries containing specific data for given element GUIDs.

    Args:
        ListOfGuids (list[str]): A list of GlobalIds for the elements to query.
        ifc_path (str): The file path to the IFC model containing the elements.
        model (ifcopenshell.file, optional): Pre-opened model.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary contains an
                    element's 'GlobalId', 'Name', 'Type', and 'Level'.
    """
    ElementDictionriesList = []
    model = model or ifc.open(ifc_path)
    for eleme in ListOfGuids:
        elemDict = {}
        elem = model.by_guid(eleme)
        if elem:
            elemDict["GlobalId"] = eleme
            elemDict["Name"] = elem.Name
            elemDict["Type"] = elem.is_a()
            elemDict["Space Container"] = ut.get_container(elem).Name
            ElementDictionriesList.append(elemDict)
    return ElementDictionriesList


def write_added_elements_to_json(AddedelementGuids: list, result_FilePath: str, ifc_path2: str, model2=None):
    """Serializes data for added elements into a JSON file as a valid JSON array."""
    dictionaryList = extract_element_data(AddedelementGuids, ifc_path2, model=model2)
    with open(result_FilePath, "w", encoding="utf-8") as file:
        json.dump(dictionaryList, file, indent=6, sort_keys=False, ensure_ascii=False)


def write_deleted_elements_to_json(DeletedelementGuids: list, result_FilePath: str, ifc_path1: str, model1=None):
    """Serializes data for deleted elements into a JSON file as a valid JSON array."""
    dictionaryList = extract_element_data(DeletedelementGuids, ifc_path1, model=model1)
    with open(result_FilePath, "w", encoding="utf-8") as file:
        json.dump(dictionaryList, file, indent=6, sort_keys=False, ensure_ascii=False)



        

def Write_Added_Deleted_Modified_To_CSV(ifc_path1: str, ifc_path2: str, 
                                        write_added: bool, write_deleted: bool, 
                                        write_modified: bool, AddedGuids, DeletedGuids,
                                        ModifiedGuids, output_dir: str, 
                                        model1=None, model2=None):
    """
    Write CSV reports for added, deleted, and modified elements.
    Takes lists of element GUIDs and exports their basic information (GUID, Name,
    Type, Location) to separate CSV files. Creates up to three files:
    - Added_Elements.csv
    - Deleted_Elements.csv  
    - Modified_Elements.csv
    Params:
        ifc_path1: Path to the first IFC model (for deleted elements)
        ifc_path2: Path to the second IFC model (for added/modified elements)
        write_added: If True, create CSV for added elements
        write_deleted: If True, create CSV for deleted elements
        write_modified: If True, create CSV for modified elements
        AddedGuids: List of GUIDs for added elements
        DeletedGuids: List of GUIDs for deleted elements
        ModifiedGuids: List of GUIDs for modified elements
        output_dir: Directory where CSV files will be saved
        model1: Pre-loaded model 1 (optional, saves loading time)
        model2: Pre-loaded model 2 (optional, saves loading time)
    
    returns:
        None. Creates CSV files in output_dir and prints confirmation messages.
    """
    
    # write added elements CSV
    if write_added:
        if AddedGuids:
            added_data = extract_element_data(AddedGuids, ifc_path2, model2)
            csv_filename = 'Added_Elements.csv'
            csv_path = os.path.join(output_dir, csv_filename)
            if added_data:
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=added_data[0].keys())
                    writer.writeheader()
                    writer.writerows(added_data)
                print(f"Generated report: {csv_path}")
    
    # write deleted elements CSV
    if write_deleted:
        if DeletedGuids:
            deleted_data = extract_element_data(DeletedGuids, ifc_path1, model1)
            csv_filename = 'Deleted_Elements.csv'
            csv_path = os.path.join(output_dir, csv_filename)
            
            if deleted_data:
                with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=deleted_data[0].keys())
                    writer.writeheader()
                    writer.writerows(deleted_data)
                print(f"Generated report: {csv_path}")
        
        # write modified elements CSV
        if write_modified:
            if ModifiedGuids:
                modified_data = extract_element_data(ModifiedGuids, ifc_path2, model2)
                csv_filename = 'Modified_Elements.csv'
                csv_path = os.path.join(output_dir, csv_filename)
                
                if modified_data:
                    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=modified_data[0].keys())
                        writer.writeheader()
                        writer.writerows(modified_data)
                    print(f"Generated report: {csv_path}")


def GenerateReportOfChanges_for_storey(ifc_path1: str, ifc_path2: str, ifc_type_list: list, storey_ : str ,
                                        output_dir: str ,use_trimesh_sampling:bool ,sampling_count :int ,
                                        over_sampling:int ,Check_Semantic:bool ,Check_Geometry : bool , Check_Shape :bool):
    """
    Generates a detailed comparison report for a specific IFC type on a single storey.

    This function is a high-level wrapper that orchestrates the entire change
    detection and reporting process. It identifies added, deleted, and modified
    elements of a given type, but limits the analysis to a single specified storey.

    Process:
    1.  Identifies added, deleted, and shared GUIDs for the `ifc_type` located
        exclusively on the specified `storey`.
    2.  Generates CSV reports for the added and deleted elements.
    3.  If any modification checks (`Semantic_Check`, `Check_Geometry`, `Shape_Check`)
        are enabled, it proceeds to analyze the shared elements.
    4.  Iterates through shared elements, checking for changes and categorizing them
        as either modified or unmodified.
    5.  Generates a detailed JSON report for all modified elements.
    6.  If all modification checks are disabled, it performs an early exit after
        reporting added/deleted elements, returning empty lists for modified/unmodified.

    Args:
        ifc_path1 (str): Path to the original IFC model (V1).
        ifc_path2 (str): Path to the revised IFC model (V2).
        ifc_type (str): The IFC entity type to compare (e.g., 'IfcWall').
        storey (str): The name of the storey (e.g., 'Ground Floor') to which the
            comparison will be limited.
        output_dir (str): The directory where report files will be saved.
        Check_Semantic (bool): If True, compares element properties and quantities.
        Check_Geometry (bool): If True, compares element placement and transform.
        Check_Shape (bool): If True, performs a detailed shape comparison
            using voxelization (can be significantly slower).

    Returns:
        Tuple[List[str], List[str], List[str], List[str]]: A tuple containing four lists of GUIDs:
        - `Added_guid_in_Floor`: New elements in V2 on this storey.
        - `Deleted_guids_in_Floor`: Elements from V1 removed on this storey.
        - `modified_guids`: Shared elements on this storey that were modified.
        - `Unmodified_guids`: Shared elements on this storey that were not modified.

    """

    # print(f"Starting comparison for type: {ifc_type}")
    print(f"V1: {ifc_path1}")
    print(f"V2: {ifc_path2}")
    
    model1 = ifc.open(ifc_path1)
    model2 = ifc.open(ifc_path2)
    
    Added_guid_in_Floor,Deleted_guid_in_Floor,Shared_guid_in_Floor=storey.Get_Added_Deleted_Shared_Guids_In_SingleStorey(
       ifc_path1 , ifc_path2 , ifc_type_list , storey_ , model1 , model2)
  
    print(f"Found {len(Added_guid_in_Floor)} added, {len(Deleted_guid_in_Floor)} deleted, and {len(Shared_guid_in_Floor)} shared elements.")
    
    if not Check_Semantic and not Check_Geometry and not Check_Shape :
        return Added_guid_in_Floor , Deleted_guid_in_Floor , [] , []
    

    Final_Json_data = {}
    print("Analyzing shared elements for modifications...")
    print(len(Shared_guid_in_Floor))
    i=0

    modified_guids =[]
    Unmodified_guids =[]
    
    for guid in Shared_guid_in_Floor:
        changes_list = diffing.analyze_element_changes(
            guid, ifc_path1, ifc_path2,use_trimesh_sampling ,sampling_count ,over_sampling ,Check_Geometry , Check_Semantic   , Check_Shape ,model1=model1, model2=model2 , 
        )
        # print(i) 
        i=i+1
        if  changes_list:
            element_changes_structure = {
                
                "Changes": changes_list
            }          
            elem = model1.by_guid(guid)
            container = ut.get_container(elem)
            name = elem.Name if elem.Name else "N/A"
            level = container.Name if container and container.Name else "N/A"
            key = f"GUID: {guid} | Space Container : {level} | Name: {name}"
            Final_Json_data[key] = element_changes_structure
            
            modified_guids.append(guid)
        else:
            Unmodified_guids.append(guid)
    
    Write_Added_Deleted_Modified_To_CSV(ifc_path1 , ifc_path2 , True , True ,True ,
                                                  Added_guid_in_Floor ,
                                         Deleted_guid_in_Floor , modified_guids, 
                                         output_dir ,model1 , model2)
                
    if Final_Json_data:
          
        print(f"Found {len(Final_Json_data)} modified elements with reportable changes.")
        Modified_Json_name = 'Modified_Elements.json'
        Modified_FullPath = os.path.join(output_dir, Modified_Json_name)
        with open(Modified_FullPath, "w", encoding='utf-8') as json_file:
            json.dump(Final_Json_data, json_file, indent=4, ensure_ascii=False)
        print(f"Generated report: {Modified_FullPath}")
      
    else:
        
        print("No elements with reportable modifications were found.")
    print("Comparison finished.")

    return Added_guid_in_Floor , Deleted_guid_in_Floor , modified_guids , Unmodified_guids






def GenerateReportOfChanges(ifc_path1: str, ifc_path2: str, ifc_type_list: list, 
                            output_dir: str, use_trimesh_sampling: bool, 
                            sampling_count: int, over_sampling: int,
                            Check_Semantic: bool, Check_Geometry: bool, Check_Shape: bool):
    """
    Complete IFC model comparison with detailed reports.
    This is the main analysis function. It compares two IFC models and generates
    comprehensive reports showing what was added, deleted, and modified.
    The function creates:
    - CSV files for added, deleted, and modified elements (basic info)
    - JSON file with detailed change descriptions for modified elements
    - Text file with human-readable change summary

    Parameters:
        ifc_path1: Path to the first (older) IFC model
        ifc_path2: Path to the second (newer) IFC model
        ifc_type_list: List of IFC types to analyze 
        output_dir: Directory where all reports will be saved
        use_trimesh_sampling: Sampling method for shape comparison
        sampling_count: Number of sample points for shape comparison
        over_sampling: Grid density for shape comparison
        Check_Semantic: If True, detect property and attribute changes
        Check_Geometry: If True, detect geometric descriptors changes
        Check_Shape: If True, perform shape comparison (slow)
    
    Returns:
        tuple of four lists (added, deleted, modified, unmodified):
        - added: GUIDs of elements added in version 2
        - deleted: GUIDs of elements removed from version 1
        - modified: GUIDs of elements that changed
        - unmodified: GUIDs of elements that stayed the same

    """
    
    print(f"V1: {ifc_path1}")
    print(f"V2: {ifc_path2}")
    
    model1 = ifc.open(ifc_path1)
    model2 = ifc.open(ifc_path2)
    
    added_guids = []
    deleted_guids = []
    shared_guids = []
    
    #bring added, deleted, and shared elements for all requested types
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
    
    #remove duplicates
    added_guids = list(set(added_guids))
    deleted_guids = list(set(deleted_guids))
    shared_guids = list(set(shared_guids))
    
    print(f"Found {len(added_guids)} added, {len(deleted_guids)} deleted, and {len(shared_guids)} shared elements.")

    if not Check_Semantic and not Check_Geometry and not Check_Shape:
        return added_guids, deleted_guids, [], []
    
    modified_guids = []
    unmodified_guids = []
    json_data = {}
    
    print("Analyzing shared elements for modifications...")
    # print(len(shared_guids))
    i = 0
    
    # Analyze each shared element for modifications
    for guid in shared_guids:
        changes_list = diffing.analyze_element_changes(
            guid, ifc_path1, ifc_path2, use_trimesh_sampling, sampling_count, over_sampling,
            Check_Geometry, Check_Semantic, Check_Shape, model1=model1, model2=model2,
        )
        
        print("Processing Element :", i)
        i = i + 1
        
        if changes_list:
            # Element has changes - record them
            element_changes_structure = {
                "Changes": changes_list
            }
            
            elem = model1.by_guid(guid)
            container = ut.get_container(elem)
            name = elem.Name if elem.Name else "N/A"
            level = container.Name if container and container.Name else "N/A"
            key = f"GUID: {guid} | Level: {level} | Name: {name}"
            json_data[key] = element_changes_structure
            
            modified_guids.append(guid)
        else:
            unmodified_guids.append(guid)
    
    # Write CSV reports for added, deleted, and modified elements
    Write_Added_Deleted_Modified_To_CSV(ifc_path1, ifc_path2, True, True, True,
                                        added_guids, deleted_guids, modified_guids,
                                        output_dir, model1, model2)
    
    # Write detailed JSON report for modified elements
    if json_data:
        print(f"Found {len(json_data)} modified elements with reportable changes.")
        
        json_filename = 'Modified_Elements.json'
        json_path = os.path.join(output_dir, json_filename)
        with open(json_path, "w", encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)
        print(f"Generated report: {json_path}")
        
        # Also write a plain-text summary for easier reading
        text_filename = 'Modified_Elements.txt'
        text_path = os.path.join(output_dir, text_filename)
        try:
            with open(text_path, "w", encoding="utf-8") as txt_file:
                for key, val in json_data.items():
                    txt_file.write(f"{key}\n")
                    changes = val.get("Changes", [])
                    if not changes:
                        txt_file.write("  - No details available\n")
                    else:
                        for ch in changes:
                            if isinstance(ch, (str, int, float)):
                                txt_file.write(f"  - {ch}\n")
                            else:
                                try:
                                    txt_file.write("  - " + json.dumps(ch, ensure_ascii=False) + "\n")
                                except Exception:
                                    txt_file.write("  - " + str(ch) + "\n")
                    txt_file.write("\n\n==============================================================================================================\n\n")
            print(f"Generated text report: {text_path}")
        except Exception as e:
            print(f"Failed to write text report: {e}")
    
    else:
        print("No elements with reportable modifications were found.")
    
    print("Comparison finished.")
    
    return added_guids, deleted_guids, modified_guids, unmodified_guids





