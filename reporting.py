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




# def Write_Added_Deleted_Modified_To_CSV(ifc_path1 : str ,ifc_path2 : str ,write_added : bool , 
#                                       write_deleted : bool , write_modified : bool ,  AddedGuids , DeletedGuids  ,
#                                    ModifiedGuids , output_dir: str , model1 =None , model2 = None ):
#    """
#     Generates CSV reports detailing added or deleted elements from a model comparison.

#     This function takes lists of GUIDs representing changes and writes their
#     properties to separate CSV files. It relies on the helper function
#     `Create_Dictionary_4Data_Of_elements` to extract the element data.

#     The output filenames are generated based on the change type,
#     IFC class, and storey, for example:
#     `Added__IfcWall__ElementsGround Floor.csv`

#     Args:
#         ifc_path1 (str): Path to the original model (V1), used to fetch data for deleted elements.
#         ifc_path2 (str): Path to the revised model (V2), used to fetch data for added elements.
#         write_added (bool): If True, a CSV report for added elements will be generated.
#         write_deleted (bool): If True, a CSV report for deleted elements will be generated.
#         AddedGuids (List[str]): A list of GUIDs for the elements that were added.
#         DeletedGuids (List[str]): A list of GUIDs for the elements that were deleted.
#         ifc_type (str): The IFC class being reported on (e.g., 'IfcDoor'), used in the filename.
#         output_dir (str): The directory where the CSV files will be saved.
#         storey (str): The storey name, used to make the output filename more specific.
#         model1 (ifc.file, optional): Pre-loaded ifcopenshell model of V1 for performance.
#         model2 (ifc.file, optional): Pre-loaded ifcopenshell model of V2 for performance."""

   
#    if write_added :
#        if AddedGuids:
#         AddedElementsDictionaries = extract_element_data(AddedGuids, ifc_path2, model2)
#         Added_CSV_name = 'Added_Elements.csv'
#         Added_FullPath = os.path.join(output_dir, Added_CSV_name)
#         if AddedElementsDictionaries:
#             with open(Added_FullPath, 'w', newline='', encoding='utf-8') as csvfile:
#                 writer = csv.DictWriter(csvfile, fieldnames=AddedElementsDictionaries[0].keys())
#                 writer.writeheader()
#                 writer.writerows(AddedElementsDictionaries)
#             print(f"Generated report: {Added_FullPath}") 

#    if write_deleted :
#        if DeletedGuids:
#         DeletedElementsDictionaries = extract_element_data(DeletedGuids, ifc_path1, model1)
#         Deleted_CSV_name = 'Deleted_Elements.csv'
#         Deleted_FullPath = os.path.join(output_dir, Deleted_CSV_name)
#         if DeletedElementsDictionaries:
#             with open(Deleted_FullPath, 'w', newline='', encoding='utf-8') as csvfile:
#                 writer = csv.DictWriter(csvfile, fieldnames=DeletedElementsDictionaries[0].keys())
#                 writer.writeheader()
#                 writer.writerows(DeletedElementsDictionaries)
#             print(f"Generated report: {Deleted_FullPath}")
       
#        if write_modified :
#           if ModifiedGuids : 
#              ModifiedElementsDictionaries =  extract_element_data(ModifiedGuids , ifc_path2 , model2)
#              Modified_CSV_name = 'Modified_Elements.csv'
#              Modified_FullPath = os.path.join(output_dir, Modified_CSV_name)
#              if ModifiedElementsDictionaries:
#                with open(Modified_FullPath, 'w', newline='', encoding='utf-8') as csvfile:
#                 writer = csv.DictWriter(csvfile, fieldnames=ModifiedElementsDictionaries[0].keys())
#                 writer.writeheader()
#                 writer.writerows(ModifiedElementsDictionaries)
#                print(f"Generated report: {Modified_FullPath}")
        

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







# def GenerateReportOfChanges(ifc_path1: str, ifc_path2: str, ifc_type_list: list, output_dir: str ,
#                              use_trimesh_sampling:bool , sampling_count :int ,over_sampling:int , 
#                              Check_Semantic:bool ,Check_Geometry : bool ,Check_Shape :bool):
#     """
#     Runs a complete comparison between two IFC models and generates detailed change reports.
    
#     This is the main function you'll use to analyze differences between model versions.
#     It handles the entire workflow from basic element categorization to detailed change analysis.
    
#     What it does:
#     1. Identifies what was added, deleted, and remains in both models
#     2. Creates CSV files listing added and deleted elements
#     3. Analyzes shared elements for modifications (properties, geometry, or shape)
#     4. Generates JSON and text reports showing exactly what changed for modified elements
    
#     The reports are saved in the specified output directory and include both machine-readable
#     (JSON) and human-readable (text) formats.
    
#     Args:
#         ifc_path1: Path to the original IFC model (older version)
#         ifc_path2: Path to the updated IFC model (newer version)
#         ifc_type: Type of elements to analyze (e.g., 'IfcWall', 'IfcWindow')
#         output_dir: Directory where all report files will be saved
#         Check_Semantic: If True, checks for changes in properties and quantities
#         Check_Geometry: If True, checks for changes in position and dimensions
#         Check_Shape: If True, performs detailed mesh comparison (slowest option)
        
#     Returns:
#         Tuple of four lists containing GUIDs:
#         - AddedGuids: Elements that only exist in the new model
#         - DeletedGuids: Elements that were removed from the old model  
#         - modified_guids: Elements that exist in both but were changed
#         - unmodified_guids: Elements that exist in both and weren't changed
        
#     Example:
#         >>> # Run a complete comparison for walls
#         >>> added, deleted, modified, unmodified = GenerateReportOfChanges(
#         ...     'project_v1.ifc', 'project_v2.ifc', 'IfcWall', 
#         ...     '/reports/wall_changes',
#         ...     Check_Semantic=True,
#         ...     Check_Geometry=True, 
#         ...     Check_Shape=False)
#     """
    
#     print(f"V1: {ifc_path1}")
#     print(f"V2: {ifc_path2}")
    
#     model1 = ifc.open(ifc_path1)
#     model2 = ifc.open(ifc_path2)
#     AddedGuids  =[]
#     DeletedGuids=[]
#     SharedGuids =[]

#     for ifc_type in ifc_type_list :
        
#        Added   = core_ifc.get_added_element_guids(ifc_path1, ifc_path2, ifc_type, model1=model1, model2=model2)
#        Deleted = core_ifc.get_deleted_element_guids(ifc_path1, ifc_path2, ifc_type, model1=model1, model2=model2)
#        Shared  = core_ifc.get_shared_element_guids(ifc_path1, ifc_path2, ifc_type, model1=model1, model2=model2)
#        AddedGuids.extend(Added)
#        DeletedGuids.extend(Deleted)
#        SharedGuids.extend(Shared)
   
#     AddedGuids = list(set(AddedGuids)) ## this way to remove repeated elements
#     DeletedGuids = list(set(DeletedGuids))
#     SharedGuids = list(set(SharedGuids))

#     print(f"Found {len(AddedGuids)} added, {len(DeletedGuids)} deleted, and {len(SharedGuids)} shared elements.")


#     if not Check_Semantic and not Check_Geometry and not Check_Shape:
#         return AddedGuids  , DeletedGuids , [] , []

#     modified_guids =[]
#     Unmodified_guids =[]
     
#     Final_Json_data = {}
#     print("Analyzing shared elements for modifications...")
#     print(len(SharedGuids))
#     i=0
    
#     for guid in SharedGuids:
#         changes_list = diffing.analyze_element_changes(
#             guid, ifc_path1, ifc_path2,use_trimesh_sampling ,sampling_count, over_sampling , 
#             Check_Geometry , Check_Semantic   , Check_Shape ,model1=model1, model2=model2 , 
#         )
#         print("Processing Element :" , i) 
#         i=i+1
#         if  changes_list:
#             element_changes_structure = {
                
#                 "Changes": changes_list
#             }  
             
#             elem = model1.by_guid(guid)
#             container = ut.get_container(elem)
#             name = elem.Name if elem.Name else "N/A"
#             level = container.Name if container and container.Name else "N/A"
#             key = f"GUID: {guid} | Level: {level} | Name: {name}"
#             Final_Json_data[key] = element_changes_structure
            
#             modified_guids.append(guid)
#         else:
#             Unmodified_guids.append(guid)
   
#     Write_Added_Deleted_Modified_To_CSV(ifc_path1 , ifc_path2 , True , True , True ,AddedGuids , DeletedGuids ,
#                                        modified_guids , output_dir ,model1 , model2)
                 
#     if Final_Json_data:
          
#         print(f"Found {len(Final_Json_data)} modified elements with reportable changes.")
#         Modified_Json_name = 'Modified_Elements.json'
#         Modified_FullPath = os.path.join(output_dir, Modified_Json_name)
#         with open(Modified_FullPath, "w", encoding='utf-8') as json_file:
#             json.dump(Final_Json_data, json_file, indent=4, ensure_ascii=False)
#         print(f"Generated report: {Modified_FullPath}")

#         # Also write a plain-text summary of the modified elements so changes are
#         # easily readable without opening the JSON file.
#         Modified_Text_name = 'Modified_Elements.txt'
#         Modified_Text_FullPath = os.path.join(output_dir, Modified_Text_name)
#         try:
#             with open(Modified_Text_FullPath, "w", encoding="utf-8") as txt_file:
#                 for key, val in Final_Json_data.items():
#                     txt_file.write(f"{key}\n")
#                     changes = val.get("Changes", [])
#                     if not changes:
#                         txt_file.write("  - No details available\n")
#                     else:
#                         for ch in changes:
#                             if isinstance(ch, (str, int, float)):
#                                 txt_file.write(f"  - {ch}\n")
#                             else:
#                                 try:
#                                     txt_file.write("  - " + json.dumps(ch, ensure_ascii=False) + "\n")
#                                 except Exception:
#                                     txt_file.write("  - " + str(ch) + "\n")
#                     txt_file.write("\n\n==============================================================================================================\n\n")
#             print(f"Generated text report: {Modified_Text_FullPath}")
#         except Exception as e:
#             print(f"Failed to write text report: {e}")

#     else:
        
#         print("No elements with reportable modifications were found.")
#     print("Comparison finished.")

#     return AddedGuids , DeletedGuids , modified_guids , Unmodified_guids 






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




