# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 13:18:34 2019

@author: mallyagirish
"""

import unittest
import numpy as np
from potential_swaps_for3pixelComponents import get_potential_swaps

class TestGetPotentials(unittest.TestCase):

    def test_result(self):
        grid = np.uint8(np.array([
                        [3, 6, 1, 2],   #0
                        [4, 7, 7, 4],   #1
                        [5, 3, 4, 7],   #2
                        [1, 7, 2, 6],   #3
                        [4, 1, 1, 7],   #4
                        [2, 2, 7, 6]])) #5
                        #0 #1 #2 #3
        val_of_interest = 7
        expected_result = [((2, 3), (1, 3)),
                           ((3, 1), (2, 1)),                                                  
                           ((2, 3), (2, 2))] # ((source_rowInd, source_colInd), (dest_rowInd, dest_colInd)
        
        # Test if the results are as expected. Order of the tuples in the list does not matter
        self.assertCountEqual(get_potential_swaps(grid, val_of_interest), expected_result)

if __name__ == '__main__':
    unittest.main()