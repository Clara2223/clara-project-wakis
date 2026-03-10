

import numpy as np


def check_subpixel_fraction(grid, surf):

    '''
    1. uses 'clip_surface' to find the intersection of the volume and the grid

    2.To get the volume per cell for 'Subpixel Smoothing':

        use probe or cell-based intersection: fx 'compute_derivative' or 'pack_labels'. however, for material properties, the 'Distance' to the surface is wanted.

    3. Converting point data to cell data to get 'Fill Fraction' (f) (This is a simplified subpixel smoothing factor (0 to 1)):

    4. # Mapping distances to 0-1 range where the surface is (Smoothing). Values < 0 are inside (1.0), values > 0 are outside (0.0)

    '''

    sampled_grid = grid.clip_surface(surf_finger, invert=False, compute_distance=True)

    grid_with_dist = grid.compute_implicit_distance(surf_finger)

    dist = grid_with_dist.point_data['implicit_distance']

    cell_dist = grid_with_dist.cell_data_to_point_data().point_data['implicit_distance']

    fill_fraction = np.clip(0.5 - (dist / np.max(spacing)), 0, 1)


    material_property = 1e4 # from  dict
    adjusted_property = fill_fraction * material_property 

    return adjusted_property