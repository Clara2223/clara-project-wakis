import numpy as np


def benchmark(voxelized_grid,spacing,surf,key):
    '''calculating volume inside and outside + area of PyvVista calculated surface of object'''
    true_vol = surf.volume
    true_area = surf.area
    xmin, xmax, ymin, ymax, zmin, zmax = surf.bounds
    '''if spacing==None:
        spacing = [(xmax - xmin) / 100, (ymax - ymin) / 100, (zmax - zmin) / 200]'''


    # 1. resolve PyVista mesh object (pv_grid)
    if hasattr(voxelized_grid, "cell_data"):
        pv_grid = voxelized_grid         #standard PyVista data object
    elif hasattr(voxelized_grid, "grid"):
        pv_grid = voxelized_grid.grid   # standard nested grid in GridFIT3D Wakis
    else:
        pv_grid = voxelized_grid # Assume it's a dict-like mesh

    # 2. Extract boolean mask 
    is_inside = None
    
    if key in pv_grid.cell_data:
        is_inside = pv_grid.cell_data[key].view(np.bool_)
        # Check dictionary-style access (fallback)
    elif key in pv_grid:
        is_inside = pv_grid[key].view(np.bool_)
            
  

    if is_inside is None:
        raise KeyError("Could not find 'mask' or 'shell' in any provided data format.")


    voxel_vol = np.prod(spacing)
    inside_count = np.sum(is_inside)
    masked_vol = inside_count * voxel_vol
    vol_error_percent = abs(masked_vol - true_vol) / true_vol * 100

    total_voxels = voxelized_grid.n_cells
    outside_count = total_voxels - inside_count
    masked_vol_outside = outside_count * voxel_vol
    total_bb_volume = (xmax - xmin) * (ymax - ymin) * (zmax - zmin)
    tot_vol_voxelized = masked_vol + masked_vol_outside
    true_vol_outside = total_bb_volume - true_vol

    #area----------------------------------------------------------
    tot_masked_area = pv_grid.extract_surface(algorithm='dataset_surface').area
    shell_cells = pv_grid.extract_cells(is_inside)
    masked_extract=shell_cells.extract_surface(algorithm='dataset_surface')
    masked_area_extract = masked_extract.area    
    masked_area_triangulate=masked_extract.triangulate().area
    masked_area_reconstruct=masked_extract.reconstruct_surface().area
    masked_area=[masked_area_extract, masked_area_triangulate, masked_area_reconstruct]
    area_error_percent = [abs(el - true_area) / true_area * 100 for el in masked_area]
    #area_error_percent = abs(masked_area_extract - true_area) / true_area * 100 

    '''masked_area_extract = masked_extract.smooth().area
    masked_area_triangulate=masked_extract.triangulate().smooth().area
    masked_area_reconstruct=masked_extract.reconstruct_surface().area   #'dangerous' bc. it can change the topology of the surface, but we want to test it anyway
    '''
    #Printing results----------------------------------------------
    '''print(f"surface area: {true_area:.6f}")
    print(f"masked surface area (extracted surface, triangulate, reconstructed_surface): {[f'{e:.6f}' for e in masked_area]}")
    print(f"Area Error %: {[f'{e:.2f}%' for e in area_error_percent]}")

    print(f"True volume: {true_vol:.6f}")
    print(f"masked inside volume: {masked_vol:.6f}")
    print(f"Volume Error: {vol_error_percent:.2f}%")

    print(f"masked outside volume: {masked_vol_outside:.6f}")
    print(f"true volume outside: {true_vol_outside:.6f}")
    print(f"Total voxelized Volume (Grid): {tot_vol_voxelized:.6f}")
    print(f"Total un-voxelized Volume (Grid): {total_bb_volume-tot_vol_voxelized:.6f}")'''

    return masked_vol,masked_area, vol_error_percent, area_error_percent 