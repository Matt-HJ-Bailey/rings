#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 12:07:09 2019
Module to perform integration tests
of the ring finding algorithms.
@author: matthew-bailey
"""

from ring_finder import RingFinder
from periodic_ring_finder import PeriodicRingFinder
from shape import Shape, node_list_to_edges

import math
import pytest
import networkx as nx
import matplotlib
import numpy as np
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from collections import Counter

def generate_polygon(num_sides: int, radius:float = 1.0, centre=np.zeros(2),
                     edge_offset = 0):
    angle: float = 2 * math.pi / num_sides
    coordinates = dict()
    edges = []
    for i in range(num_sides):
        edges.append((i + edge_offset, (i + 1) % num_sides + edge_offset))
        this_coord = np.array((radius * math.sin(i * angle), 
                          radius * math.cos(i * angle)))
        coordinates[i] = this_coord + centre
    return coordinates, edges

class TestRingFinder:
    def test_one_ring(self):
        """
        Test whether we successfully identify one ring.
        """
        G = nx.Graph()
        hex_coords, hex_edges = generate_polygon(6)
        G.add_edges_from(hex_edges)
        rf = RingFinder(graph=G, coords_dict=hex_coords)
        assert len(rf.current_rings) == 1

    def test_hex_size(self):
        """
        Test whether we successfully identify
        a hexagon as having six sides.
        """
        G = nx.Graph()
        hex_coords, hex_edges = generate_polygon(6)
        G.add_edges_from(hex_edges)
        rf = RingFinder(graph=G, coords_dict=hex_coords)
        hexagon = rf.current_rings.pop()
        assert len(hexagon) == 6

    def test_two_squares(self):
        """
        Test if we correctly identify two squares
        connected by a common edge.
        """
        G = nx.Graph()
        G.add_edges_from([[0, 1], [1, 2], [2, 3], [3, 0], [2, 5],
                         [4, 5], [3, 4]])
        coords_dict = {0: np.array([0, 0]),
                       1: np.array([0, 1.0]),
                       2: np.array([1.0, 1.0]),
                       3: np.array([1.0, 0]),
                       4: np.array([2.0, 0]),
                       5: np.array([2.0, 1.0])}
        rf = RingFinder(graph=G, coords_dict=coords_dict)
        assert len(rf.current_rings) == 2
        for ring in rf.current_rings:
            assert len(ring) == 4
        for ring in rf.perimeter_rings:
            assert len(ring) == 6
            
class TestPeriodicRingFinder:
    def test_one_ring(self):
        """
        Test whether we successfully identify one ring.
        """
        G = nx.Graph()
        hex_coords, hex_edges = generate_polygon(6)
        G.add_edges_from(hex_edges)
        rf = RingFinder(graph=G, coords_dict=hex_coords)
        assert len(rf.current_rings) == 1
        
    def test_three_squares(self):
        """
        Test if we correctly identify three squares,
        which is actually just a periodic two squares.
        """
        G = nx.Graph()
        G.add_edges_from([[0, 1], [1, 2], [2, 3], [3, 0], [2, 5],
                         [4, 5], [3, 4], [5, 1], [4, 0]])
        coords_dict = {0: np.array([0, 0]),
                       1: np.array([0, 1.0]),
                       2: np.array([1.0, 1.0]),
                       3: np.array([1.0, 0]),
                       4: np.array([2.0, 0]),
                       5: np.array([2.0, 1.0])}
        rf = PeriodicRingFinder(graph=G, coords_dict=coords_dict,
                                cell=np.array([2.5, 2.5]))
        assert len(rf.current_rings) == 3
        for ring in rf.current_rings:
            assert len(ring) == 4
        
    def test_2d_squares(self):
        """
        Test if we correctly identify a 2d grid of squares
        as containing 9 squares (4 real, 4 across periodic edges)
        """
        G = nx.Graph()
        G.add_edges_from([[0, 1], [1, 2], [2, 3], [3, 0], [2, 5],
                         [4, 5], [3, 4], [5, 1], [4, 0],
                         [1, 6], [2, 7], [5, 8],
                         [6, 0], [7, 3], [8, 4],
                         [8, 6], [8, 7], [7, 6]])
        coords_dict = {0: np.array([0, 0]),
                       1: np.array([0, 1.0]),
                       2: np.array([1.0, 1.0]),
                       3: np.array([1.0, 0]),
                       4: np.array([2.0, 0]),
                       5: np.array([2.0, 1.0]),
                       6: np.array([0.0, 2.0]),
                       7: np.array([1.0, 2.0]),
                       8: np.array([2.0, 2.0])}
        rf = PeriodicRingFinder(graph=G, coords_dict=coords_dict,
                                cell=np.array([3.0, 3.0]))
        assert len(rf.current_rings) == 9
        for ring in rf.current_rings:
            assert len(ring) == 4

class TestRealData:
    """
    Class to check against real results, making sure
    we still give the same output.
    """
    def test_procrystalline(self):
        """
        Test one of David Ormrod Morley's procrystalline
        lattices.
        """
        G = nx.Graph()
        with open("./data/procrystal_edges.dat", "r") as fi:
            for line in fi.readlines():
                x, y = [int(item) for item in line.split()]
                G.add_edge(x, y)
    
        COORDS_DICT = {}
        with open("./data/procrystal_coords.dat", "r") as fi:
            for i, line in enumerate(fi.readlines()):
                line = line.split()
                x, y = float(line[0]), float(line[1])
                COORDS_DICT[i] = np.array([x, y])
                
        with open("./data/procrystal_rings.dat", "r") as fi:
            rings = []
            for line in fi.readlines():
                rings.append(len(line.split()))

        correct_counter = Counter(rings)
        ring_finder = PeriodicRingFinder(G,
                                         COORDS_DICT,
                                         np.array([10.0,
                                                   10.0]))
        this_counter = Counter([len(ring) for ring in ring_finder.current_rings])
        for item in this_counter.keys():
            assert correct_counter[item] == this_counter[item]
    
    def test_collagen(self):
        """
        Test on one of my collagen networks, using output
        from David Ormrod Morley's program to check.
        """
        G = nx.Graph()
        with open("./data/coll_edges.dat", "r") as fi:

            for line in fi.readlines():
                if line.startswith("#"):
                    continue
                x, y = [int(item) for item in line.split(", ")]
                print(f"Adding edge {x}, {y}")
                G.add_edge(x, y)
    
        COORDS_DICT = {}
        with open("./data/coll_coords.dat", "r") as fi:
            for i, line in enumerate(fi.readlines()):
                if line.startswith("#"):
                    continue
                line = line.split(", ")
                node_id, x, y = int(line[0]), float(line[1]), float(line[2])
                COORDS_DICT[node_id] = np.array([x, y])
                
        with open("./data/coll_rings.dat", "r") as fi:
            rings = []
            for line in fi.readlines():
                rings.append(len(line.split()))

        print(COORDS_DICT)
        correct_counter = Counter(rings)
        ring_finder = PeriodicRingFinder(G,
                                         COORDS_DICT,
                                         np.array([100.0,
                                                   100.0]))
        this_counter = Counter([len(ring) for ring in ring_finder.current_rings])
        for item in this_counter.keys():
            assert correct_counter[item] == this_counter[item]
    