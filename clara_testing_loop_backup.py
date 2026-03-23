import numpy as np
from wakis import GridFIT3D 
import pyvista as pv
from benchmark import benchmark


methods = ['wakis', 'enclosed_points', 'implicit_distance', 'voxelize_rectlinear']
results = {}
resolutions = ['175x175x350','150x150x300','125x125x250','100x100x200', '50x50x100', '25x25x50'] 
results = {m: {} for m in methods}

for r in resolutions:
    Nx, Ny, Nz = int(r.split('x')[0]), int(r.split('x')[1]), int(r.split('x')[2]) 
    spacing=[(xmax - xmin) / Nx, (ymax - ymin) / Ny, (zmax - zmin) / Nz]
    x,y,z = np.linspace(xmin, xmax, Nx), np.linspace(ymin, ymax, Ny), np.linspace(zmin, zmax, Nz)
    stl_tolerance = np.min([np.min(np.diff(x)), np.min(np.diff(y)), np.min(np.diff(z))]) *stl_tol

    grid = pv.RectilinearGrid(x, y, z)

    print(f"----- Resolution: {r} -----")
    for m in methods:
        print(f"----- Benchmarking Method: {m} -----")
        
        test_grid = grid.copy()  
        
        if m == 'wakis':
            test_grid['mask'] = GridFIT3D(xmin, xmax, ymin, ymax, zmin, zmax, Nx, Ny, Nz, stl_solids=stl_solids, stl_materials=stl_materials,stl_scale=1.0)
            test_grid._mark_cells_in_stl()
            pass 

        elif m == 'interior_points':  #test to see if same results as Wakis
            select = test_grid.select_interior_points(surf_shell, check_surface=False)
            test_grid['mask'] = select.point_data_to_cell_data()['selected_points'] > 0.5 
            #test_grid['mask'] = select.point_data_to_cell_data()['selected_points'] > stl_tolerance #TO DO

        elif m == 'enclosed_points':
            select = test_grid.select_enclosed_points(surf_shell, tolerance=stl_tolerance)
            test_grid['mask'] = select.point_data_to_cell_data()['selected_points'] > 0.5
            #test_grid['mask'] = select.point_data_to_cell_data()['selected_points'] > stl_tolerance #To Do

        elif m == 'implicit_distance':   #To DO: choose which threshold for the mask
            # Computes distance to surface; negative is inside
            dist = test_grid.compute_implicit_distance(surf_shell)
            #test_grid['mask'] = dist['implicit_distance'] < 0
            test_grid['mask'] = dist.point_data_to_cell_data()['implicit_distance'] < 0
            #test_grid['mask'] = dist.point_data_to_cell_data()['implicit_distance'] < stl_tolerance

        elif m == 'voxelize_rectlinear':
            # PyVista built-in voxelization
            # Note: voxelize returns a new grid, which will be used directly
            vox = surf_shell.voxelize_rectilinear(spacing=spacing)
            test_grid = vox
            #test_grid['mask'] = np.ones(test_grid.n_cells, dtype=bool)

        vol, area, errvol, errarea = benchmark(test_grid, spacing, surf_shell)
        
        results[m][r] = {'vol': vol, 'vol_err': errvol, 'area': area, 'area_err': errarea}

