# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 18:29:58 2019

@author: zepman85

Given a 2D grid of pixels and a value of interest,
this code looks for every pixel of that value (called "source") that is situated 
such that a swap with 1 of its 4-conn neighbours (called "destination") 
would result in a 3-pixel 4-connected component of that value being created.

A "source" can have multiple "destinations" and multiple "sources" can have the
same "destination". This code computes every possible source-destination pair.

Example:
##########
Consider the following grid (column and row indices marked).
[3, 6, 1, 2] r0
[4, 7, 7, 4] r1
[5, 3, 4, 7] r2
[1, 7, 2, 6] r3
[4, 1, 1, 7] r4
[2, 2, 7, 6] r5
c0 c1 c2 c3

If the value of interest is 7, then the following are the swap options 
to create a 4-connected component of 3 pixels of value 7.
(r3, c1) <-> (r2, c1)
(r2, c3) <-> (r1, c3)
(r2, c3) <-> (r2, c2)
##########

"""

import numpy as np
import cv2

# Test data
val_of_interest = 7
grid = np.uint8(np.array([
        [3, 6, 1, 2],   #0
        [4, 7, 7, 4],   #1
        [5, 7, 4, 7],   #2
        [1, 7, 2, 6],   #3
        [4, 1, 1, 7],   #4
        [2, 2, 7, 6]])) #5
        #0 #1 #2 #3


nRows = grid.shape[0]
nCols = grid.shape[1]

# Predefine the lists of source and destination coordinates
candidate_source_coords = []
candidate_destination_coords = []

# 1. Convert grid to binary mask, where foreground is the value of interest, and the rest is background
mask = np.uint8(grid == val_of_interest)

# Define kernel that looks at the 4-neighbours of a given pixel
ker = np.float32(np.array([
        [0,1,0],
        [1,0,1],
        [0,1,0]]))

# 2. Filter mask with the kernel.
# In the result, each pixel value indicates the number of foreground 4-neighbours in every pixel in the mask
mask_filt = cv2.filter2D(mask,ddepth=-1,kernel=ker,borderType=cv2.BORDER_CONSTANT)

# Create copy with background pixels set to 0. 
# The result indicates how many foreground 4-neighbours each foreground pixel in mask has
mask_filt_temp = np.copy(mask_filt)
mask_filt_temp[mask == 0] = 0

# 3. Filter the filtered result with the kernel
# In the result, each pixel value is the total number of foreground 4-neighbours of the foreground 4-neighbours of that pixel
# i.e., look at each foreground 4-neighbours of a pixel, and then the foreground 4-neighbours of those
mask_filt_filt = cv2.filter2D(mask_filt_temp,ddepth=-1,kernel=ker,borderType=cv2.BORDER_CONSTANT)

# 4. Find candidate destination indices. 
# These are indices of non-val_of_interest pixels in grid to which 
# adjacent val_of_interest pixels can be swapped in order to complete the pattern.
# Specifically, these are indices of pixels in mask that have
# - 3 or more foreground 4-neighbours OR
# - 2 foreground 4-neighbours and at least 1 of those has a foreground 4-neighbour
candidate_destination_indices = np.nonzero(((mask_filt >= 3) | ((mask_filt == 2) & (mask_filt_filt > 0))) & (mask == 0))

# 5. For every candidate destination, find the candidate source(s)
# condition 1 - if the candidate destination has >=3 foreground pixels in its 4-neighbourhood, 
#               then each of those neighbours is a candidate source
# OR
# condition 2 - if the candidate destination has 2 foreground pixels in its 4-neighbourhood,
#               then every neighbour that has the least number of foreground pixels in its own 4-neighbourhood is a candidate source
num_destination_candidates = len(candidate_destination_indices[0])
if num_destination_candidates != 0:
    for i in range(num_destination_candidates):
        iRow = candidate_destination_indices[0][i]
        iCol = candidate_destination_indices[1][i]
        
        if mask_filt[iRow,iCol] >= 3:
            for iNRow in list(filter(lambda x: (x >= 0 and x < nRows), [iRow-1,iRow+1])):            
                if mask[iNRow,iCol]:
                    candidate_source_coords.append((iNRow,iCol))
                    candidate_destination_coords.append((iRow,iCol))  
                    
            for iNCol in list(filter(lambda y: (y >= 0 and y < nCols), [iCol-1,iCol+1])):
                if mask[iRow,iNCol]:
                    candidate_source_coords.append((iRow,iNCol))
                    candidate_destination_coords.append((iRow,iCol))
        else:
            neighbour_filt_vals = []
            neighbour_coords = []
            
            # first find min neighbour val
            for iNRow in list(filter(lambda x: (x >= 0 and x < nRows), [iRow-1,iRow+1])):
                if mask[iNRow,iCol]:
                    neighbour_filt_vals.append(mask_filt[iNRow,iCol])
                    neighbour_coords.append((iNRow,iCol))
            
            for iNCol in list(filter(lambda y: (y >= 0 and y < nCols), [iCol-1,iCol+1])):
                if mask[iRow,iNCol]:
                    neighbour_filt_vals.append(mask_filt[iRow,iNCol])
                    neighbour_coords.append((iRow,iNCol))
                    
            min_indices = np.where(neighbour_filt_vals ==  np.min(neighbour_filt_vals))[0]
            for j in range(len(min_indices)):
                candidate_source_coords.append(neighbour_coords[min_indices[j]])
                candidate_destination_coords.append((iRow,iCol))

print("Candidate sources          - ", candidate_source_coords)
print("Corresponding destinations - ", candidate_destination_coords)
