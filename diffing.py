# comparison logic that classifies elements as modified or unmodified.
# Combines semantic, geometric, and shape checks into final modification decisions.


import ifcopenshell as ifc
import networkx as nx
from networkx.utils import graphs_equal
from dictdiffer import diff
import core_ifc
import geometry
import semantics
import reporting
import numpy as np




# def is_element_modified(elemGraph1: nx.DiGraph, elemGraph2: nx.DiGraph, guid: str, ifc_path1: str,
#                          ifc_path2: str,Check_Semantic: bool ,Geometery_Check : bool ,Check_Shape:bool,
#                          use_trimesh_sampling : bool ,sampling_count:int ,over_sampling:int,
#                          model1=None, model2=None):
#     """
#     Analyzes an element for modifications and returns detailed check results.

#     This function performs up to three types of checks to determine if an element
#     has been modified. Its behavior is highly conditional based on the input flags.

#     1.  **Semantic Check:** Compares the element's data graphs (attributes, properties, quantities).
#     2.  **Geometry Check:** Compares high-level geometric properties (centroid, volume, etc.) via meshes.
#     3.  **Shape Check:** Performs a detailed comparison of the two meshes.

#     **IMPORTANT:** If `Check_Shape` is `True`, the function will return a single boolean
#     result from that check and will not include the results of the other checks.

#     Args:
#         elemGraph1 (nx.DiGraph): The data graph for the element from model V1.
#         elemGraph2 (nx.DiGraph): The data graph for the element from model V2.
#         guid (str): The GlobalId of the element to compare.
#         ifc_path1 (str): Path to the original IFC model (V1).
#         ifc_path2 (str): Path to the updated IFC model (V2).
#         Check_Semantic (bool): If True, performs the semantic (data graph) comparison.
#         Geometery_Check (bool): If True, performs the high-level geometric comparison.
#         Check_Shape (bool): If True, performs a detailed mesh shape comparison and
#             causes the function to return a single boolean value.
#         model1 (ifcopenshell.file, optional): Pre-opened model of V1.
#         model2 (ifcopenshell.file, optional): Pre-opened model of V2.

#     Returns:
#         Union[List[bool], bool]: The return type depends on the `Check_Shape` flag.
#         - If `Check_Shape` is `True`:
#             Returns a **single boolean**. `True` indicates the shapes are different.
#         - If `Check_Shape` is `False`:
#             Returns a **list of booleans** for each enabled check. A `True`
#             value in the list indicates a modification was detected. To check
#             if any modification occurred, use `any(return_value)`.
#     """
#     elem1 = (model1 or ifc.open(ifc_path1)).by_guid(guid)
#     elem2 = (model2 or ifc.open(ifc_path2)).by_guid(guid)
   
#     check_list=[]
#     if Check_Semantic:
#        check_list.append(not graphs_equal(elemGraph1, elemGraph2))
    
#     mesh1 = None
#     mesh2 = None
       

#     if Geometery_Check:
#      mesh1 = geometry.generate_mesh_of_element(elem1)
#      mesh2 = geometry.generate_mesh_of_element(elem2)
     

#      if mesh1 != False  and mesh2 !=False : 
      
#       geometery_data1 = geometry.extract_geometric_properties(mesh1)
#       geometery_data2 = geometry.extract_geometric_properties(mesh2)
      
#       check_list.append(not(geometery_data1 == geometery_data2))
      
#      else :
#         check_list.append(not (mesh1 == mesh2) )

#     if Check_Shape : 
#        check_list.append(geometry.are_meshes_different(mesh1 , mesh2  , use_trimesh_sampling , sampling_count ,
#                                                         over_sampling)) # the function here returns true if the meshes are different

#     return check_list


def is_element_modified(element_graph1: nx.DiGraph, element_graph2: nx.DiGraph, 
                        guid: str, ifc_path1: str, ifc_path2: str,
                        check_semantic: bool, geometry_check: bool, check_shape: bool,
                        use_trimesh_sampling: bool, sampling_count: int, over_sampling: int,
                        model1=None, model2=None):
    """
    check if an element was modified between two model versions.
    performs multiple types of modification checks based on enabled flags:
    semantic check , Geometry check & shape Check 
    
    Each enabled check adds a True/False result to the output list. True means
    that type of change was detected.
    
    parameters:
        element_graph1: NetworkX graph of element data from version 1
        element_graph2: NetworkX graph of element data from version 2
        guid: GlobalId of the element to compare
        ifc_path1: Path to the first IFC model
        ifc_path2: Path to the second IFC model
        check_semantic: If True, check for property/attribute changes
        geometry_check: If True, check for geometric property changes
        check_shape: If True, perform detailed mesh shape comparison
        use_trimesh_sampling: Sampling method for shape comparison
        sampling_count: Number of sample points for shape comparison
        over_sampling: Grid density for shape comparison
        model1: Pre-loaded model 1 (optional)
        model2: Pre-loaded model 2 (optional)
    
    returns:
        list of booleans, one for each enabled check.
        true in list = modification detected in that check.
        use any(result) to see if any modification was found.
    """
    element1 = (model1 or ifc.open(ifc_path1)).by_guid(guid)
    element2 = (model2 or ifc.open(ifc_path2)).by_guid(guid)
    
    modification_checks = []
    
    # check1: semantic Comparison (propertis, quantities, relationships)
    if check_semantic:
        semantic_changed = not graphs_equal(element_graph1, element_graph2)
        modification_checks.append(semantic_changed)
    
    mesh1 = None
    mesh2 = None
    
    #Check 2: geometric properties comparison
    if geometry_check:
        mesh1 = geometry.generate_mesh_of_element(element1)
        mesh2 = geometry.generate_mesh_of_element(element2)
        
        if mesh1 != False and mesh2 != False:
            # compare geometric properties
            geometry_data1 = geometry.extract_geometric_properties(mesh1)
            geometry_data2 = geometry.extract_geometric_properties(mesh2)
            geometry_changed = not (geometry_data1 == geometry_data2)
            modification_checks.append(geometry_changed)
        else:
            geometry_changed = not (mesh1 == mesh2)
            modification_checks.append(geometry_changed)
    
    #check3 shape comparison
    if check_shape:
        shape_changed = geometry.are_meshes_different(mesh1, mesh2, use_trimesh_sampling,
                                                       sampling_count, over_sampling)
        modification_checks.append(shape_changed)
    
    return modification_checks



def find_modified_elements_guids(ifc_path1: str, ifc_path2: str, ifc_type: str,
                                 semantic_check: bool, geometry_check: bool, 
                                 shape_check: bool, use_trimesh_sampling: bool,
                                 sampling_count: int, over_sampling: int, 
                                 model1=None, model2=None):
    """
    find all modified elements of a specific type between two IFC models.
    Identifies elements that exist in both versions and have been changed in some way.
    you control what counts as a "change" by enabling different check types.
    
    process:
    1-Find elements that exist in both models (shared elements)
    2_For each shared element, build its data graphs from both versions
    3_Run the enabled checks (semantic/geometry/shape)
    4- Collect GUIDs where any check detected a change
    
    Parameters:
        ifc_path1: Path to the first (older) IFC model
        ifc_path2: Path to the second (newer) IFC model
        ifc_type: IFC element type to analyze (e.g. 'IfcWall', 'IfcDoor')
        semantic_check: Check for property and attribute changes
        geometry_check: Check for position, size, and volume changes
        shape_check: Check for 3D shape changes 
        use_trimesh_sampling: Sampling method for shape check
        sampling_count: Number of sample points for shape check
        over_sampling: Grid density for shape check
        model1: Pre-loaded model 1 (optional, saves loading time)
        model2: Pre-loaded model 2 (optional, saves loading time)
    
    returns:
        list of GUIDs (strings) for modified elements.
        Empty list if no modifications found.
    """
    model1 = model1 or ifc.open(ifc_path1)
    model2 = model2 or ifc.open(ifc_path2)
    
    modified_guids = []

    shared_guids = core_ifc.get_shared_element_guids(ifc_path1, ifc_path2, ifc_type, 
                                                      model1=model1, model2=model2)
    
   
    for guid in shared_guids:  #check each shared element for modifications
        # Build element graphs from both versions
        graph_v1 = semantics.create_element_graph(guid, model1)
        graph_v2 = semantics.create_element_graph(guid, model2)
        checks = is_element_modified(graph_v1, graph_v2, guid, ifc_path1, ifc_path2,
                                     semantic_check, geometry_check, shape_check,
                                     use_trimesh_sampling, sampling_count, over_sampling,
                                     model1=model1, model2=model2)
        
        if len(checks) == 0:
            continue
       
        if any(checks):  #If any check detected a change, add to modified list
            modified_guids.append(guid)
    
    return modified_guids




# def find_unmodified_elements_guids(ifc_path1 :str  , ifc_path2:str , ifcType:str , Semantic_check :bool
#                                    , Geometry_check :bool  , Shape_check : bool  , use_trimesh_sampling :bool ,
#                                      sampling_count :int,over_sampling : int ,model1 = None ,model2=None ):
#     """Finds elements that are "unmodified" between two versions of an IFC model.

#     This function lets you define what 'unmodified' means by enabling checks
#     for different types of changes:
#     - `Semantic_check`: For properties and attributes.
#     - `Geometry_check`: For location, placement, and rotation.
#     - `Shape_check`: For the detailed 3D mesh form.
    
#     Returns a list of GUIDs for elements that pass all enabled checks.
#     """
#     model1 = model1 or ifc.open(ifc_path1)
#     model2 = model2 or ifc.open(ifc_path2)
#     unmodified_guids =[]
#     Shared_guids = core_ifc.get_shared_element_guids(ifc_path1 , ifc_path2 , ifcType , model1, model2)
#     for guid in Shared_guids :
#        G1 = semantics.create_element_graph(guid , model1)
#        G2 = semantics.create_element_graph(guid , model2)
#        checks = is_element_modified(G1 , G2 , guid , ifc_path1 , ifc_path2 , Semantic_check , Geometry_check ,
#                                Shape_check ,use_trimesh_sampling , sampling_count , over_sampling ,model1 , model2)
#        if any(checks):
#           continue
#        else:
#           unmodified_guids.append(guid)

#     return unmodified_guids
    

def find_unmodified_elements_guids(ifc_path1: str, ifc_path2: str, ifc_type: str, 
                                   semantic_check: bool, geometry_check: bool, 
                                   shape_check: bool, use_trimesh_sampling: bool,
                                   sampling_count: int, over_sampling: int, 
                                   model1=None, model2=None):
    """
    Find all unmodifeid elements of a specific type between two IFC models.
    Identifies elements that exist in both versions and have NOT changed based
    on the enabled checks. This is the opposite of find_modified_elements_guids.
    An element is considered "unmodified" if ALL enabled checks show no changes.
    You control what counts as "unchanged" by choosing which checks to enable.
    
    params:
        ifc_path1: Path to the first IFC model
        ifc_path2: Path to the second IFC model
        ifc_type: IFC element type to analyze
        semantic_check: Check for property and attribute changes
        geometry_check: Check for position, size, and volume changes
        shape_check: Check for 3D shape changes 
        use_trimesh_sampling: Sampling method for shape check
        sampling_count: Number of sample points for shape check
        over_sampling: Grid density for shape check
        model1: Pre-loaded model 1 (optional, saves loading time)
        model2: Pre-loaded model 2 (optional, saves loading time)
    
    Returns:
        List of GUIDs (strings) for unmodified elements.
        empty List if all elements were modified.
    """
    model1 = model1 or ifc.open(ifc_path1)
    model2 = model2 or ifc.open(ifc_path2)
    
    unmodified_guids = []
    shared_guids = core_ifc.get_shared_element_guids(ifc_path1, ifc_path2, ifc_type, 
                                                      model1, model2)
    
    for guid in shared_guids:
        graph_v1 = semantics.create_element_graph(guid, model1)
        graph_v2 = semantics.create_element_graph(guid, model2)
        
        checks = is_element_modified(graph_v1, graph_v2, guid, ifc_path1, ifc_path2,
                                     semantic_check, geometry_check, shape_check,
                                     use_trimesh_sampling, sampling_count, over_sampling,
                                     model1, model2)

        if any(checks):
            continue
          
        unmodified_guids.append(guid)   # No changes detected - element is unmodified
    return unmodified_guids



def analyze_element_changes(guid: str, ifc_path1: str, ifc_path2: str, 
                            use_trimesh_sampling: bool, sampling_count: int, 
                            over_sampling: int, check_geometry=False,
                            check_semantic=True, check_shape=False,  
                            model1=None, model2=None):
    """
    gnerate a detailed report of all changes for a single element.
    Analyzes one element across two model versions and returns a list describing
    exactly what changed. The output format depends on what type of change was
    detected (added property sets, modified values, geometric changes, etc.).
    Note: Returns empty list for IfcBuildingElementProxy elements.
    
    Parameters:
        guid: GlobalId of the element to analyze
        ifc_path1: Path to the first IFC model
        ifc_path2: Path to the second IFC model
        use_trimesh_sampling: Sampling method for shape check
        sampling_count: Number of sample points for shape check
        over_sampling: Grid density for shape check
        check_geometry: If True, compare geometric properties (position, volume, etc.)
        check_semantic: If True, compare properties and quantities (default: True)
        check_shape: If True, perform mesh comparison
        model1: Pre-loaded model 1 (optional)
        model2: Pre-loaded model 2 (optional)
    
    Returns:
        List of changes detected. Each item can be:
        - {'Added': <data>} - Property/quantity set added in v2
        - {'Deleted': <data>} - Property/quantity set removed in v2
        - {<node_id>: <diff_list>} - Modified property/quantity set
        - <diff_list> - Geometric property changes
        - {'Shape OR Position Change': 'True'} - Shape difference detected
        
        Empty list if no changes or element is IfcBuildingElementProxy.
    """
    model1 = model1 or ifc.open(ifc_path1)
    model2 = model2 or ifc.open(ifc_path2)
    
    changes_list = []
    
    element = model1.by_guid(guid)
    
    # skip proxy elements
    if element.is_a("IfcBuildingElementProxy"):
        return changes_list
    
    # semantic check - compare properties, quantities, and relationships
    if check_semantic:
        graph_v1 = semantics.create_element_graph(guid, model1)
        graph_v2 = semantics.create_element_graph(guid, model2)
        
        graphs_are_equal = graphs_equal(graph_v1, graph_v2)
        
        if not graphs_are_equal:
            # find which nodes (property sets, quantity sets) were added/deleted/modified
            nodes_v1 = set(graph_v1)
            nodes_v2 = set(graph_v2)
            
            added_nodes = list(nodes_v2 - nodes_v1)
            deleted_nodes = list(nodes_v1 - nodes_v2)
            shared_nodes = list(nodes_v2 & nodes_v1)
            
            #record added property/quantity sets
            for node in added_nodes:
                added_dict = {"Added": dict(graph_v2.nodes[node])}
                changes_list.append(added_dict)
            
            #record deleted property/quantity sets
            for node in deleted_nodes:
                deleted_dict = {"Deleted": dict(graph_v1.nodes[node])}
                changes_list.append(deleted_dict)
            
            #check shared nodes(psets , qset ...) for modifications
            for node in shared_nodes:
                node_data_v1 = dict(sorted(graph_v1.nodes[node].items()))
                node_data_v2 = dict(sorted(graph_v2.nodes[node].items()))
                
                if node_data_v1 != node_data_v2:
                    changes_list.append({node: list(diff(node_data_v1, node_data_v2))})
    
    #geometry check compare position, dimensions, volume, etc.
    mesh1 = None
    mesh2 = None
    geometry_unchanged = None
    
    if check_geometry:
        element1 = model1.by_guid(guid)
        element2 = model2.by_guid(guid)
        
        mesh1 = geometry.generate_mesh_of_element(element1)
        mesh2 = geometry.generate_mesh_of_element(element2)
        
        if mesh1 and mesh2:
            geometry_data1 = geometry.extract_geometric_properties(mesh1)
            geometry_data2 = geometry.extract_geometric_properties(mesh2)
            
            geometry_unchanged = geometry_data1 == geometry_data2
            
            if not geometry_unchanged:
                changes_list.append(list(diff(geometry_data1, geometry_data2)))
    
    #shape check Mesh comparison
    shape_changed = None
    
    if check_shape:
        if mesh1 and mesh2:
            #Meshes already generated from geometry check
            shape_changed = geometry.are_meshes_different(mesh1, mesh2, use_trimesh_sampling,
                                                          sampling_count, over_sampling)
            if shape_changed:
                changes_list.append({"Shape OR Position Change": str(shape_changed)})
        else:
            # Meshes not generated yet generate them now
            element1 = model1.by_guid(guid)
            element2 = model2.by_guid(guid)
            
            mesh1 = geometry.generate_mesh_of_element(element1)
            mesh2 = geometry.generate_mesh_of_element(element2)
        
            if mesh1 and mesh2:
                shape_changed = geometry.are_meshes_different(mesh1, mesh2, use_trimesh_sampling,
                                                              sampling_count, over_sampling)
                if shape_changed:
                    changes_list.append({"Shape OR Position Change": str(shape_changed)})  
    return changes_list




def get_modification_type(guid: str, ifc_path1: str, ifc_path2: str,use_trimesh_sampling:bool , 
                          sampling_count : int , over_sampling :int ,model1=None, model2=None) -> dict:
    """
    Determines the category of modification for a single element.

    This query function checks for semantic (data) and geometric (position/shape)
    changes and returns a dictionary indicating which types of changes were found.

    Args:
        guid (str): The GlobalId of the element to check.
        ifc_path1 (str): Path to the original IFC model (V1).
        ifc_path2 (str): Path to the updated IFC model (V2).
        model1 (ifcopenshell.file, optional): Pre-opened model of V1.
        model2 (ifcopenshell.file, optional): Pre-opened model of V2.

    Returns:
        dict: A dictionary with boolean flags for 'semantic' and 'geometric' changes.
              Example: {'semantic': True, 'geometric': False}
    """
    m1 = model1 or ifc.open(ifc_path1)
    m2 = model2 or ifc.open(ifc_path2)
    
    results = {"Semantic Change": False, 
               "Geometric Properties(e.g. Volume , position ... ) Change": False , 
             "Shape Or Position Change  " : False}

    # Semantic Check
    g1 = semantics.create_element_graph(guid, m1)
    g2 = semantics.create_element_graph(guid, m2)
    if not graphs_equal(g1, g2):
        results["Semantic Change"] = True

    # Geometric Check (using high level properties for speed)
    mesh1 = geometry.generate_mesh_of_element(m1.by_guid(guid))
    mesh2 = geometry.generate_mesh_of_element(m2.by_guid(guid))
    
    if mesh1 is not False and mesh2 is not False:
        geom_props1 = geometry.extract_geometric_properties(mesh1)
        geom_props2 = geometry.extract_geometric_properties(mesh2)
        if geom_props1 != geom_props2:
            results["Geometric Properties(e.g. Volume , position ... ) Change"] = True
    elif mesh1 is not mesh2: # Handles cases where one mesh fails to generate
        results["Geometric Properties(e.g. Volume , position ... ) Change"] = True


    differ = geometry.are_meshes_different(mesh1 , mesh2  , use_trimesh_sampling , sampling_count , over_sampling)
    if differ :
        results["Shape Or Position Change  "] = True

        
    return results






def ClassifyChangesForGivenGuidList(  ifc_path_v1 : str, ifc_path_v2 : str ,output_dir : str  ,
                                    use_trimesh_sampling:bool , sampling_count:int ,over_sampling:int ,
                                    check_semantics :bool, check_geometry : bool , check_shape : bool ,guids_path :str =None ,
                                    guids : list  =None ,model1 =None , model2=None):
   """Analyzes a specific list of GUIDs and classifies the changes between two IFC models.

    This function takes a predefined list of element GUIDs and determines their
    status by comparing two versions of an IFC file. It categorizes each GUID
    into one of four groups: Added, Deleted, Modified, or Unmodified.

    The criteria for what constitutes a "modification" can be controlled using
    the boolean check flags. As a side-effect, this function also generates and
    saves a CSV report of the findings to the specified output directory.

    Args:
        ifc_path_v1 (str): The file path for the original (version 1) IFC model.
        ifc_path_v2 (str): The file path for the revised (version 2) IFC model.
        output_dir (str): The directory where the summary CSV report will be saved.
        guids (list[str]): The specific list of element GlobalIds to be analyzed.
        check_semantics (bool): If True, check for changes in properties and attributes.
        check_geometry (bool): If True, check for changes in location and placement.
        check_shape (bool): If True, check for changes in the 3D shape representation.
        model1 (ifcopenshell.file, optional): A pre-loaded model for v1 to improve performance.
        model2 (ifcopenshell.file, optional): A pre-loaded model for v2.

    Returns:
        tuple[list, list, list, list]: 
            A tuple containing four lists of GUIDs, in this order:
            (Added_guids, Deleted_guids, modified_guids, unmodified_guids).
    """
   
   model1 = model1 or ifc.open(ifc_path_v1)
   model2 = model2 or ifc.open(ifc_path_v2)
   Added_guids = []
   Deleted_guids = []
   Shared_guids = []

   guids_list = guids or core_ifc.read_guids_from_txt(guids_path)

   for guid in guids_list :
      in_v1 = core_ifc.guid_exists(guid, ifc_path_v1, model1)
      in_v2 = core_ifc.guid_exists(guid, ifc_path_v2, model2) 

      if in_v1 and not in_v2:
         Deleted_guids.append(guid)
      
      elif  in_v2 and not in_v1:
         Added_guids.append(guid)
      elif  in_v1 and  in_v2:
         Shared_guids.append(guid)
   
   modified_guids = []
   unmodified_guids = []
   i = 0 
   for guid in Shared_guids:
      print(i) 
      i+= 1
      G1 = semantics.create_element_graph(guid , model1)
      G2 = semantics.create_element_graph(guid , model2)
      
      if any(is_element_modified(G1 , G2 ,guid, ifc_path_v1 , ifc_path_v2 , check_semantics , 
                                 check_geometry , check_shape ,use_trimesh_sampling ,sampling_count,over_sampling ,model1 ,model2)):
         modified_guids.append(guid)
      else:
         unmodified_guids.append(guid)
    
   reporting.Write_Added_Deleted_Modified_To_CSV(ifc_path_v1 , ifc_path_v2 , True , True ,
                                                 True ,  Added_guids , Deleted_guids , 
                                    modified_guids , output_dir , model1 , model2)
    
   return Added_guids , Deleted_guids , modified_guids ,unmodified_guids



def check_if_element_moved(
    guid: str,
    ifc_path1: str,
    ifc_path2: str,
    tolerance: float = 0.01,
    model1=None,
    model2=None,
) -> bool:
    """
    Check if an element has rigidly moved between two IFC versions
    using its mesh bounding boxes instead of centroids.

    The method:
    - Builds the axis-aligned bounding box (AABB) of the element in
      both models.
    - Computes how the min and max corners moved.
    - If both corners moved by (approximately) the same vector and the
      length of that vector is greater than ``tolerance``, the element
      is considered moved.
    - If the movement vectors differ, we assume the element changed
      shape/size or rotated rather than simply translating, and return
      False.

    """
    m1 = model1 or ifc.open(ifc_path1)
    m2 = model2 or ifc.open(ifc_path2)

    elem1 = m1.by_guid(guid)
    elem2 = m2.by_guid(guid)

    if elem1 is None or elem2 is None:
        return False

    mesh1 = geometry.generate_mesh_of_element(elem1)
    mesh2 = geometry.generate_mesh_of_element(elem2)

    if mesh1 is None or mesh2 is None:
        return False

    # AABBs: bounds = [[min_X, min_Y, min_z], [max_x, max_y, max_z]]
    bounds1 = mesh1.bounds
    bounds2 = mesh2.bounds

    min1, max1 = bounds1
    min2, max2 = bounds2

   
    v_min = min2 - min1
    v_max = max2 - max1

    # for a pure translation, both corners should move by the same vector
    if not np.allclose(v_min, v_max, atol=1e-4):
        return False

    # Take that common translation vector and measure its length
    translation = 0.5 * (v_min + v_max)
    move_dist = np.linalg.norm(translation)

    return move_dist > tolerance
