# Colored geometry export utilities for visualizing changes as GLB/mesh outputs.
# Generates added/deleted/modified element meshes with color coding.


import ifcopenshell as ifc
import os
import core_ifc
import geometry
import storey
import trimesh
import json
import ifcopenshell.util.element as ut


def create_meshes_for_elements(ifc_path_v1: str, ifc_path_v2: str, guids: list[str],
                               added=False, deleted=False, modified=False, 
                               unmodified=False, other=False,
                               model1=None, model2=None):
    """
    create colored 3D meshes for visualization of element changes.
    Generates mesh objects for a list of element GUIDs and colors them based on
    their change type. This is used to create the colored 3D visualizations where
    you can see what was added (green), deleted (red), modified (blue), etc.
    Only ONE of the boolean flags should be True - it determines which color
    scheme to apply and which model version to use.
    
    Colors:
    - added: Green [0, 128, 0, 255]
    - deleted: Red [120, 40, 40, 255]
    - modified: Blue [40, 60, 100, 255]
    - unmodified: Default color (no change)
    - other: Default color (no change)
    
    Parameters:
        ifc_path_v1: Path to the first IFC model
        ifc_path_v2: Path to the second IFC model
        guids: List of element GUIDs to create meshes for
        added: If True, create green meshes for added elements (uses model2)
        deleted: If True, create red meshes for deleted elements (uses model1)
        modified: If True, create blue meshes for modified elements (uses model2)
        unmodified: If True, create default meshes for unchanged elements (uses model2)
        other: If True, create default meshes for context elements (uses model2)
        model1: Pre-loaded model 1 (optional)
        model2: Pre-loaded model 2 (optional)
    
    Returns:
        List of trimesh objects with appropriate colors applied.
        Empty list if no valid meshes generated.
    """
    model1 = model1 or ifc.open(ifc_path_v1)
    model2 = model2 or ifc.open(ifc_path_v2)
    
    mesh_list = []
    
    if added:
        for guid in guids:
            element = model2.by_guid(guid)
            mesh = geometry.generate_mesh_of_element(element)
            if mesh:
                mesh.visual.face_colors = [0, 128, 0, 255]  # Green
                mesh_list.append(mesh)
    
    elif deleted:
        for guid in guids:
            element = model1.by_guid(guid)
            mesh = geometry.generate_mesh_of_element(element)
            if mesh:
                mesh.visual.face_colors = [120, 40, 40, 255]  # Red
                mesh_list.append(mesh)
    
    elif modified:
        for guid in guids:
            element = model2.by_guid(guid)
            mesh = geometry.generate_mesh_of_element(element)
            if mesh:
                mesh.visual.face_colors = [40, 60, 100, 255]  # Blue
                mesh_list.append(mesh)
    
    elif unmodified:
        for guid in guids:
            element = model2.by_guid(guid)
            mesh = geometry.generate_mesh_of_element(element)
            if mesh:
                mesh_list.append(mesh)
    
    elif other:
        for guid in guids:
            element = model2.by_guid(guid)
            mesh = geometry.generate_mesh_of_element(element)
            if mesh:
                mesh_list.append(mesh)
    
    return mesh_list



def generate_categorized_meshes(ifc_path_v1: str, ifc_path_v2: str, 
                                added_guids, deleted_guids, modified_guids,
                                unmodified_guids, other_guids,
                                generate_added=True, generate_deleted=True, 
                                generate_modified=True, generate_unmodified=True, 
                                generate_other=True, model1=None, model2=None):
    """
    Generate colored meshes for all element categories.
    Takes pre-categorized lists of element GUIDs and creates colored 3D meshes
    for visualization. This is a wrapper that calls create_meshes_for_elements
    for each category with the appropriate settings.
    Use the boolean flags to control which categories to process. This is useful
    if you only want to visualize certain types of changes.
    
    Parameters:
        ifc_path_v1: Path to the first IFC model
        ifc_path_v2: Path to the second IFC model
        added_guids: List of GUIDs for added elements
        deleted_guids: List of GUIDs for deleted elements
        modified_guids: List of GUIDs for modified elements
        unmodified_guids: List of GUIDs for unchanged elements
        other_guids: List of GUIDs for context elements
        generate_added: If True, create green meshes for added elements
        generate_deleted: If True, create red meshes for deleted elements
        generate_modified: If True, create blue meshes for modified elements
        generate_unmodified: If True, create meshes for unchanged elements
        generate_other: If True, create meshes for context elements
        model1: Pre-loaded model 1 (optional)
        model2: Pre-loaded model 2 (optional)
    
    Returns:
        Tuple of five mesh lists (added, deleted, modified, unmodified, other).
        Each list contains trimesh objects for that category.
    """
    added_meshes = []
    deleted_meshes = []
    modified_meshes = []
    unmodified_meshes = []
    other_meshes = []
    
    if generate_added:
        added_meshes = create_meshes_for_elements(ifc_path_v1, ifc_path_v2, added_guids, 
                                                   added=generate_added,
                                                   model1=model1, model2=model2)
        print("Meshing Added Elements Done")
    
    if generate_deleted:
        deleted_meshes = create_meshes_for_elements(ifc_path_v1, ifc_path_v2, deleted_guids, 
                                                     deleted=generate_deleted,
                                                     model1=model1, model2=model2)
        print("Meshing Deleted Elements Done")
    
    if generate_modified:
        modified_meshes = create_meshes_for_elements(ifc_path_v1, ifc_path_v2, modified_guids, 
                                                      modified=generate_modified,
                                                      model1=model1, model2=model2)
        print("Meshing Modified Elements Done")
    
    if generate_unmodified:
        unmodified_meshes = create_meshes_for_elements(ifc_path_v1, ifc_path_v2, unmodified_guids, 
                                                        unmodified=generate_unmodified,
                                                        model1=model1, model2=model2)
        print("Meshing Unmodified Elements Done")
    
    if generate_other:
        other_meshes = create_meshes_for_elements(ifc_path_v1, ifc_path_v2, other_guids, 
                                                   other=generate_other,
                                                   model1=model1, model2=model2)
        print("Meshing Other Elements Done")
    
    return added_meshes, deleted_meshes, modified_meshes, unmodified_meshes, other_meshes


def export_colored_change_geometry(ifc_path1: str, ifc_path2: str, output_dir: str,
                                   added_guids: list, deleted_guids: list, 
                                   modified_guids: list, unmodified_guids: list,
                                   view_added=True, view_delted=True,
                                   view_modified=True, view_unmodifeid=True, 
                                   view_others=True, model1=None, model2=None):
    """
    Export a color-coded 3D visualization of model changes to a GLB file. Creates a single 3D model 
    file showing all changes between two IFC versions.
    each change type gets a distinct color for easy identification:
    - Added: Green
    - Deleted: Red
    - Modified: Blue
    - Unmodified: Default
    - Other context: Default
    
    The output is a GLB file that can be opened in any 3D viewer. On windows,
    it automatically opens in the default 3D viewer app.
    
    Parameters:
        ifc_path1: Path to the first IFC model
        ifc_path2: Path to the second IFC model
        output_dir: Directory where the GLB file will be saved
        added_guids: List of GUIDs for added elements
        deleted_guids: List of GUIDs for deleted elements
        modified_guids: List of GUIDs for modified elements
        unmodified_guids: List of GUIDs for unchanged elements
        view_added: If True, include added elements in visualization
        view_delted: If True, include deleted elements in visualization
        view_modified: If True, include modified elements in visualization
        view_unmodifeid: If True, include unmodified elements in visualization
        view_others: If True, include other context elements in visualization
        model1: Pre-loaded model 1 (optional)
        model2: Pre-loaded model 2 (optional)
    
    Returns:
        Combined trimesh object with all meshes, or None if no geometry generated.
    """
    model1 = model1 or ifc.open(ifc_path1)
    model2 = model2 or ifc.open(ifc_path2)
    
    # Get all building elements from version 2
    all_guids = core_ifc.Get_All_guids("IfcBuildingElement", ifc_path2, model2)
    
    # Find "other" elements (context elements not in our categorized lists)
    other_guids = list(set(all_guids) - set(added_guids + deleted_guids + modified_guids + unmodified_guids))
    
    # Generate colored meshes for each category
    added_meshes, deleted_meshes, modified_meshes, unmodified_meshes, other_meshes = generate_categorized_meshes(
        ifc_path1, ifc_path2, added_guids, deleted_guids, modified_guids,
        unmodified_guids, other_guids, view_added, view_delted, view_modified,
        view_unmodifeid, view_others, model1, model2
    )
    
    # Combine all meshes into a single geometry
    combined_geometry = geometry.concatenate_all_meshes(added_meshes, deleted_meshes, 
                                                         modified_meshes, unmodified_meshes, 
                                                         other_meshes)
    
    filename = "Geometry_v2.glb"
    
    if combined_geometry is None:
        print("No geometry to export (no elements matched the selected categories).")
        return None
    
    # Export to GLB file
    file_path = os.path.join(output_dir, filename)
    combined_geometry.export(file_path)
    
    # Try to open the file in the default 3D viewer (Windows)
    print(f"Exported GLB to: {file_path}")
    try:
        os.startfile(file_path)
        print("Opened GLB in default OS application (Windows 3D Viewer if associated).")
    except Exception as e:
        print(f"Could not auto open GLB with OS default app: {e}")
    
    return combined_geometry



def export_colored_storey_change_geometry(ifc_path1 : str , ifc_path2 : str ,ifc_type :str ,storey_name : str , output_dir :str ,
                                    added_guids : list , deleted_guids :list ,modified_guids :list ,
                                      Unmodified_guids : list ,view_added :bool ,view_deleted :bool ,view_modified :bool,view_unmodified :bool
                                       ,view_others :bool , view_changes_in_v1 = False ,model1= None , model2 =None) :
   """Export a color-coded 3D visualization of changes on a specific floor.
      Similar to export_colored_change_geometry but filters to show only elements
      on a specific building storey/floor. This is useful when you want to focus
      on changes in one area of the building.

     The function also includes other building elements on the same floor for
     context, so you can see where the changes are relative to the rest of the floor.

     Color scheme:
      - Added: Green
      - Deleted: Red
      - Modified: Blue
      - Unmodified: Default
       - Other context: Default

    Parameters:
      ifc_path1: Path to the first IFC model
      ifc_path2: Path to the second IFC model
      ifc_type: IFC type being analyzed (e.g. 'IfcWall')
      storey_name: Name of the floor to visualize (e.g. 'Ground Floor', 'Level 2')
      output_dir: Directory where the GLB file will be saved
      added_guids: List of GUIDs for added elements on this floor
      deleted_guids: List of GUIDs for deleted elements on this floor
      modified_guids: List of GUIDs for modified elements on this floor
      unmodified_guids: List of GUIDs for unchanged elements on this floor
      view_added: If True, include added elements in visualization
      view_deleted: If True, include deleted elements in visualization
      view_modified: If True, include modified elements in visualization
      view_unmodified: If True, include unmodified elements in visualization
      view_others: If True, include other context elements on the floor
      view_changes_in_v1: If True, show changes in context of v1 (affects filename)
      model1: Pre-loaded model 1 (optional)
      model2: Pre-loaded model 2 (optional)

     Returns:
      Combined trimesh object with all floor meshes, or None if no geometry.
      The GLB file is saved as "Geometry_<storey_name>_v1.glb" or
      "Geometry_<storey_name>_v2.glb" depending on view_changes_in_v1 flag.
      """
   model1 = model1 or ifc.open(ifc_path1)
   model2 = model2 or ifc.open(ifc_path2)
 

   all_guids = core_ifc.get_shared_element_guids(ifc_path1 , ifc_path2 , "IfcBuildingElement" , model1 , model2)
   all_guids_in_Storey = []

   for guid in all_guids:
       is_inStorey = storey.is_element_on_storey(guid , ifc_path2 , storey_name ,  model2 ) 
       if is_inStorey :
           all_guids_in_Storey.append(guid)
        

   Other_guids = list(set(all_guids_in_Storey) - set(added_guids + deleted_guids + modified_guids + Unmodified_guids))

   added_Meshes ,deleted_Meshes ,modified_Meshes ,Unmodified_Meshess ,Other_Meshess =generate_categorized_meshes(
            ifc_path1 , ifc_path2 ,added_guids ,deleted_guids ,modified_guids , Unmodified_guids ,
            Other_guids , view_added ,view_deleted , view_modified , view_unmodified , view_others , view_changes_in_v1 ,model1 , model2 )

   Geometry = geometry.concatenate_all_meshes(added_Meshes , deleted_Meshes , modified_Meshes , Unmodified_Meshess , Other_Meshess)
  
   
                                       ## because it always export rotated 90 with glb format
                                       ## but with stl and ply it doesnt need transformation
   if view_changes_in_v1 :
     name = "Geometry_"+ storey_name + "_v1.glb"
   else:
       name = "Geometry_"+ storey_name + "_v2.glb"
   if Geometry is None:
    print("No geometry to export (no elements matched the selected categories).")
    return None
   FullPath = os.path.join(output_dir, name)
   Geometry.export(FullPath)

   #=================For openong the file dirctly (Windows 3D Viewer===================#
   
   print(f"Exported GLB to: {FullPath}")

   try:
    os.startfile(FullPath)
    print("Opened GLB in default OS application (Windows 3D Viewer if associated).")
   except Exception as e:
    print(f"Could not auto open GLB with OS default app: {e}")

   #=================Or we can use free online 3D viewrs===================#

   return Geometry
