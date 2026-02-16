# Geometry file for mesh generation, geometric features extraction, and shape comparison.
# All mesh (Hausdorff, movement detection, concatenation) is implemented here.


import ifcopenshell as ifc
import ifcopenshell.geom
import numpy as np
import trimesh
from trimesh.proximity import closest_point
# from trimesh.points import remove_close

settings = ifcopenshell.geom.settings()
settings.set("use-world-coords", True)
settings.set("weld-vertices", True)  
settings.set("unify-shapes", True)
settings.set(settings.USE_WORLD_COORDS, True)




def generate_mesh_of_element(ifc_element):
    """
    Convert an IFC element to a 3D trimesh object.
    
    Extracts the 3D geometry from an IFC element and creates a trimesh that
    can be used for visualization, geometric analysis, or shape comparison.
    Uses module-level settings for consistent coordinate systems and optimized meshes.
    
    Parameters:
        ifc_element: IFC element object (entity)
    
    Returns:
        trimesh.Trimesh object if conversion successful.
        False if element has no geometry or conversion fails.
    """
    if not ifc_element.Representation:
        return False
    
    try:
        shape = ifc.geom.create_shape(settings, ifc_element)
        
        # extract Vertices and faces from shape geometry
        vertices = shape.geometry.verts
        faces = shape.geometry.faces
        
        # reshape flat arrays into (N, 3) format for trimesh
        vertices_array = np.array(vertices).reshape((-1, 3))
        faces_array = np.array(faces).reshape((-1, 3))
        
        mesh = trimesh.Trimesh(vertices=vertices_array, faces=faces_array)
        return mesh
    
    except Exception as e:
        print(f"Error creating mesh: {e}")
        return False




def extract_geometric_properties(mesh):
    """
    Extract geometric descriptors from a mesh for comparison.
    
    Computes a standardized set of geometric descriptors including position,
    dimensions, volume, and surface area. All values are rounded to 3 decimal
    places for stable comparisons.
    
    Uses both axis-aligned (AABB) and oriented (OBB) bounding boxes. This helps
    detect rotations - if OBB stays the same but AABB changes, the element
    likely rotated without changing shape.
    
    Parameters:
        mesh: trimesh.Trimesh object to analyze, or False if mesh generation failed
    
    Returns:
        Dictionary with geometric properties if mesh is valid.
        None if mesh is False.
    
    Dictionary keys:
        - Position Of Center X/Y/Z: Centroid coordinates
        - Axis Aligned Bounding Box Dimension 1/2/3: AABB extents (sorted)
        - OBB Dimension 1/2/3: Oriented bounding box extents (sorted)
        - Volume: Mesh volume
        - Surface Area: Total surface area
        - Is Water_Tight: Whether mesh is watertight (boolean)
    """
    if mesh == False:
        return None
    
    geometry_data = {}
    
    # Extract position and bounding box information
    centroid = mesh.centroid
    aabb_extents = np.sort(mesh.extents)
    obb_extents = np.sort(mesh.bounding_box_oriented.extents)
    
    # centroid position
    geometry_data["X Center Coordinate"] = np.round(centroid[0], 3)
    geometry_data["Y Center Coordinate"] = np.round(centroid[1], 3)
    geometry_data["Z Center Coordinate"] = np.round(centroid[2], 3)
    
    # axis aligned bounding box dimensions (sorted smallest to largest)
    geometry_data["Axis Aligned Bounding Box Dimension 1"] = np.round(aabb_extents[0], 3)
    geometry_data["Axis Aligned Bounding Box Dimension 2"] = np.round(aabb_extents[1], 3)
    geometry_data["Axis Aligned Bounding Box Dimension 3"] = np.round(aabb_extents[2], 3)
    
    # Oriented bounding box dimensions (sorted smallest to largest)
    geometry_data["OBB Dimension 1"] = np.round(obb_extents[0], 3)
    geometry_data["OBB Dimension 2"] = np.round(obb_extents[1], 3)
    geometry_data["OBB Dimension 3"] = np.round(obb_extents[2], 3)
    
    # volume and Surface proprties
    geometry_data["Volume"] = np.round(mesh.volume, 3)
    geometry_data["Surface Area"] = np.round(mesh.area, 3)
    geometry_data["Is Water_Tight"] = mesh.is_watertight
    
    return geometry_data

     

def sample_mesh_with_grid(mesh: trimesh.Trimesh, count: int, oversample: int = 2):
    """
    Sample points on a mesh surface using a 3D grid projection method.
    
    Creates a uniform 3D grid inside the mesh's bounding box, then projects
    each grid point onto the nearest point on the mesh surface. This gives
    more evenly distributed samples compared to random sampling methods.
    running it multiple times gives similar point distributions.
    
    Parameters:
        mesh: The mesh to sample points from
        count: How many sample points you want (approximately)
        oversample: Grid density multiplier - higher = more grid points = better
                    coverage but slower. default is 2.
    
    Returns:
        Array of (x, y, z) points on the mesh surface, shape (n, 3).
        The actual number n might be slightly different from count due to
        grid discretization and filtering invalid points.
    
    Note:
        Returns empty array if mesh has no area or invalid inputs.
    """
    # Handle edge cases
    if count <= 0 or mesh.area <= 0:
        return np.empty((0, 3), dtype=float)
    
    if oversample < 1:
        raise ValueError("oversample must be at least 1")
    
    # Get bounding box
    bounds = mesh.bounds
    min_corner = bounds[0]
    max_corner = bounds[1]
    bbox_size = max_corner - min_corner
    
    # Avoid division by 0
    epsilon = 1e-9
    bbox_size = np.maximum(bbox_size, epsilon)
    
    num_candidates = int(count * oversample)
    
    volume = float(bbox_size[0] * bbox_size[1] * bbox_size[2])
    cell_size = (volume / max(num_candidates, 1)) ** (1.0 / 3.0)
    
    # get number of grid cells per axis
    grid_resolution = np.maximum(1, np.ceil(bbox_size / cell_size).astype(int))
    nx, ny, nz = int(grid_resolution[0]), int(grid_resolution[1]), int(grid_resolution[2])
    
    spacing = bbox_size / grid_resolution
    
    x_coords = min_corner[0] + (np.arange(nx) + 0.5) * spacing[0]
    y_coords = min_corner[1] + (np.arange(ny) + 0.5) * spacing[1]
    z_coords = min_corner[2] + (np.arange(nz) + 0.5) * spacing[2]
    
    
    X, Y, Z = np.meshgrid(x_coords, y_coords, z_coords, indexing="xy")# building 3D grid by combining all coordinates
    grid_points = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    
    surface_points, _, _ = closest_point(mesh, grid_points) # here i project the point on the mesh using trimesh functions
    
    # Remove any invalid points (NaN))
    valid = np.isfinite(surface_points).all(axis=1)
    surface_points = surface_points[valid]
    
    if surface_points.size == 0:
        return surface_points.reshape((0, 3))
    
    return surface_points



def hausdorff_distance_between_meshes(mesh1: trimesh.Trimesh, mesh2: trimesh.Trimesh,
                                      sampling_count: int, over_sampling: int, 
                                      use_trimesh_sampling: bool):
    """
    Calculate how different two mesh shapes are using Hausdorff distance.

    Samples points on both meshes and measures the maximum distance between
    corresponding closest points. Higher values = more different shapes.
    
    How it works:
    1. Sample points on both mesh surfaces
    2. For each point on mesh1, find distance to closest point on mesh2
    3. For each point on mesh2, find distance to closest point on mesh1
    4. Return the maximum of all these distances
    
    This tells you the "worst case" deviation between the two shapes.
    
    Parameters:
        mesh1: First mesh to compare
        mesh2: Second mesh to compare
        sampling_count: Number of points to sample on each mesh
        over_sampling: Grid density factor 
        use_trimesh_sampling: If True, use trimesh's area-weighted sampling (faster).
                              If False, use custom grid-based sampling (more uniform).
    
    Returns:
        Float representing the Hausdorff distance between meshes.
        Larger values = bigger shape difference.
        Returns None if either mesh is invalid or False.
    """
    if not mesh1 or not mesh2:
        return None
    
    # sample points on both mesh surfaces
    if use_trimesh_sampling:
        # use trimesh's built-in sampler (faster, area-weighted --> depends on the tringulation e.g. if the element is the same but but different tringulations it will give highr distance) 
        samples_mesh1, _ = trimesh.sample.sample_surface_even(mesh1, sampling_count, seed=0)
        samples_mesh2, _ = trimesh.sample.sample_surface_even(mesh2, sampling_count, seed=0)
    else:
        # use custom grid-based sampler (more uniform coverage)
        samples_mesh1 = sample_mesh_with_grid(mesh1, sampling_count, over_sampling)
        samples_mesh2 = sample_mesh_with_grid(mesh2, sampling_count, over_sampling)
    
    samples_mesh1 = np.array(samples_mesh1) # np array is better for vectorisation
    samples_mesh2 = np.array(samples_mesh2)
    
    num_samples1 = len(samples_mesh1)
    num_samples2 = len(samples_mesh2)
    
    all_distances = []
    
    # for each point on mesh1 find closest point on mesh2 (here i represnt the meshes by those lists of samples e.g. samples_mesh1)
    for i in range(num_samples1):
        point = samples_mesh1[i]
        distances_to_mesh2 = samples_mesh2 - point
        distances_to_mesh2 = np.linalg.norm(distances_to_mesh2, axis=1)
        closest_distance = min(distances_to_mesh2)
        all_distances.append(closest_distance)
    
    # or Each Point on mesh2 find closest point on mesh1
    for i in range(num_samples2):
        point = samples_mesh2[i]
        distances_to_mesh1 = samples_mesh1 - point
        distances_to_mesh1 = np.linalg.norm(distances_to_mesh1, axis=1)
        closest_distance = min(distances_to_mesh1)
        all_distances.append(closest_distance)
    
    # Hausdorff distance is the maximum of all closest distances
    hausdorff_dist = np.max(all_distances)
    
    return hausdorff_dist



def are_meshes_different(mesh1, mesh2, use_trimesh_sampling: bool, sampling_count: int,
                         over_sampling: int, tolerance=1e-2):
    """
    Check if two meshes have different shapes.
    Uses Hausdorff distance to measure shape difference and compares it to a
    threshold.
    
    Parameters:
        mesh1: First mesh to compare
        mesh2: Second mesh to compare
        use_trimesh_sampling: Sampling method (True = trimesh, False = grid-based)
        sampling_count: Number of points to sample on each mesh
        over_sampling: Grid density factor
        tolerance: Maximum allowed difference 
                   Lower values = more sensitive to small changes
    
    Returns:
        True if meshes are different (distance > tolerance).
        False if meshes are similar or if comparison fails.
    """
    distance = hausdorff_distance_between_meshes(mesh1, mesh2, sampling_count, 
                                                   over_sampling, use_trimesh_sampling)
    
    if distance is None:
        return False
    
    return distance > tolerance


def concatenate_all_meshes(added_meshes, deleted_meshes, modified_meshes, 
                           unmodified_meshes, other_meshes):
    """
    Combine multiple mesh lists into a single mesh for export.
    
    Merges all the colored meshes (added, deleted, modified, etc.) into one
    combined mesh and applies a coordinate transformation to match the GLB
    export format (swaps Y and Z).
    
    Parameters:
        added_meshes: List of meshes for added elements
        deleted_meshes: List of meshes for deleted elements
        modified_meshes: List of meshes for modified elements
        unmodified_meshes: List of meshes for unchanged elements
        other_meshes: List of meshes for context elements
    
    Returns:
        single combined trimesh object with all meshes merged.
        returns None if all input lists are empty.
    """

    all_meshes = (added_meshes + deleted_meshes + modified_meshes + 
                  unmodified_meshes + other_meshes)
    
    if not all_meshes:
        return None
    combined_mesh = trimesh.util.concatenate(all_meshes)
    #apply Cordinate transformation
    transform_matrix = [[1, 0, 0, 0],
                        [0, 0, 1, 0],
                        [0, 1, 0, 0],
                        [0, 0, 0, 1]]
    combined_mesh.apply_transform(transform_matrix)
    
    return combined_mesh
