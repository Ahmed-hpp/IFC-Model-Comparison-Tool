"""
usage: Run the script and enter your IFC file paths .
Configuration: Edit the CONFIG dictionary below to change analysis & visulisation settings.
"""

import os
import ifcopenshell
import time
from core_ifc import *
from semantics import create_element_graph
from geometry import *
from diffing import *
from storey import *
from reporting import *
from visualization import *


# =============================================================================
# parameters , change these parameters to control the analysis and visualisation settings
# =============================================================================
CONFIG = {
    'ifc_types': ["IfcBuildingElement"], # choose one or more ifctypes for tracking changes
    
    'check_semantic': True, # track  properties , quantities and relationshps
    'check_geometry': True, # track geometric discriptors (e.g. volume , centroids ,Area)
    'check_shape': True,   # analyse the shape if there is deviation or not 
    
    'Use_Trimesh_sampler' : False, # this is fatser than the custom grid sampler , but it depends on the triangle areas
    'sampling_count': 50, # choose lower samples with custome grid sampler
    'over_sampling': 2,
    
    #-- here choose what you want to see 
    'view_added': True,
    'view_deleted': True,
    'view_modified': True,
    'view_unmodified': True,
    'view_others': True,
}


# =============================================================================
# Main Program
# =============================================================================

def main():
    print("="*70)
    print("IFC MODEL COMPARISON TOOL")
    print("="*70)
    print()
    
    # Default file paths
    default_v1 = r"C:\Users\Ahmed Mohammed\Desktop\Test_project_v1.ifc"
    default_v2 = r"C:\Users\Ahmed Mohammed\Desktop\Test_project_v2_without_rotation.ifc"
    default_output = r"C:\Users\Ahmed Mohammed\Desktop\outs"
    
    # Get input paths from user
    print("Enter file paths (press Enter to use defaults):")
    print()
    
    path1 = input("IFC Version 1: ").strip().strip('"').strip("'")
    if not path1:
        path1 = default_v1
        print(f"  Using default: {default_v1}")
    
    path2 = input("IFC Version 2: ").strip().strip('"').strip("'")
    if not path2:
        path2 = default_v2
        print(f"  Using default: {default_v2}")
    
    output = input("Output folder: ").strip().strip('"').strip("'")
    if not output:
        output = default_output
        print(f"  Using default: {default_output}")
    
    print()
    
    # Check if files exist
    if not os.path.exists(path1):
        print(f"ERROR: File not found - {path1}")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists(path2):
        print(f"ERROR: File not found - {path2}")
        input("Press Enter to exit...")
        return
    
    os.makedirs(output, exist_ok=True)
    
    # Display configuration
    print("="*70)
    print(f"V1: {path1}")
    print(f"V2: {path2}")
    print(f"Output: {output}")
    print(f"Checks: Semantic={CONFIG['check_semantic']}, "
          f"Geometry={CONFIG['check_geometry']}, Shape={CONFIG['check_shape']}")
    print("="*70)
    print()
    
    # Load IFC models
    print("Loading IFC models...")
    model1 = ifcopenshell.open(path1)
    model2 = ifcopenshell.open(path2)
    print("Models loaded successfully.")
    print()
    
    # Run the analysis
    print("Running analysis (this may take some time)...")
    start_time = time.time()
    
    added, deleted, modified, unmodified = GenerateReportOfChanges(
        path1,
        path2,
        CONFIG['ifc_types'],
        output,
        use_trimesh_sampling=CONFIG['Use_Trimesh_sampler'],
        sampling_count=CONFIG['sampling_count'],
        over_sampling=CONFIG['over_sampling'],
        Check_Semantic=CONFIG['check_semantic'],
        Check_Geometry=CONFIG['check_geometry'],
        Check_Shape=CONFIG['check_shape'],
    )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Show results
    print()
    print("="*70)
    print("RESULTS:")
    print(f"  Added:      {len(added):4d} elements")
    print(f"  Deleted:    {len(deleted):4d} elements")
    print(f"  Modified:   {len(modified):4d} elements")
    print(f"  Unmodified: {len(unmodified):4d} elements")
    print(f"  Time:       {elapsed:.2f} seconds")
    print("="*70)
    print()
    
    # Create 3D visualization
    print("Generating 3D visualization...")
    export_colored_change_geometry(
        path1, path2, output,
        added, deleted, modified, unmodified,
        view_added=CONFIG['view_added'],
        view_delted=CONFIG['view_deleted'],
        view_modified=CONFIG['view_modified'],
        view_unmodifeid=CONFIG['view_unmodified'],
        view_others=CONFIG['view_others'],
        model1=model1,
        model2=model2
    )
    print("Visualization complete.")
    print()
    
    print(f"All results saved to: {output}")
    print("Done!")
    print()
    
   


if __name__ == "__main__":
    main()
