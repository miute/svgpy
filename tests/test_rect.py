#!/usr/bin/env python3

import sys
import unittest

sys.path.extend(['.', '..'])

from svgpy import Rect


class RectTestCase(unittest.TestCase):
    def test_eq01(self):
        a = Rect()
        b = Rect()
        f = a == b
        self.assertTrue(f)

    def test_eq02(self):
        a = Rect(0, 0)
        b = Rect()
        f = a != b
        self.assertTrue(f)

    def test_eq03(self):
        a = Rect()
        b = Rect(0, 0)
        f = a != b
        self.assertTrue(f)

    def test_eq04(self):
        a = Rect(10, 20)
        b = Rect(10, 20)
        f = a == b
        self.assertTrue(f)

    def test_eq05(self):
        a = Rect(10, 20, 100, 200)
        b = Rect(10, 20, 100, 200)
        f = a == b
        self.assertTrue(f)

    def test_eq06(self):
        a = Rect(10, 20, 100, 200)
        b = Rect(15, 20, 100, 200)
        f = a != b
        self.assertTrue(f)

    def test_eq07(self):
        a = Rect(10, 20, 100, 200)
        b = Rect(10, 25, 100, 200)
        f = a != b
        self.assertTrue(f)

    def test_eq08(self):
        a = Rect(10, 20, 100, 200)
        b = Rect(15, 25, 100, 200)
        f = a != b
        self.assertTrue(f)

    def test_eq09(self):
        a = Rect(10, 20, 100, 200)
        b = Rect(10, 20, 105, 200)
        f = a != b
        self.assertTrue(f)

    def test_eq10(self):
        a = Rect(10, 20, 100, 200)
        b = Rect(10, 20, 100, 205)
        f = a != b
        self.assertTrue(f)

    def test_eq11(self):
        a = Rect(10, 20, 100, 200)
        b = Rect(10, 20, 105, 205)
        f = a != b
        self.assertTrue(f)

    def test_intersect00(self):
        # valid rectangle AND invalid rectangle
        w = 10
        h = 20
        xa = 100
        ya = 100
        a = Rect(xa, ya, w, h)
        b = Rect()
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect01(self):
        # invalid rectangle AND valid rectangle
        w = 10
        h = 20
        xb = 100
        yb = 100
        a = Rect()
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = None
        expected_y = None
        expected_w = 0
        expected_h = 0
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect02(self):
        # left-upper
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect03(self):
        # left-upper overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w / 2
        expected_h = h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect04(self):
        # upper
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya - h
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect05(self):
        # upper overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect06(self):
        # right-upper overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w / 2
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa + w / 2
        expected_y = ya
        expected_w = w / 2
        expected_h = h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect07(self):
        # right-upper
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect08(self):
        # left
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect09(self):
        # left overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w / 2
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect10(self):
        # same position
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect11(self):
        # right overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w / 2
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa + w / 2
        expected_y = ya
        expected_w = w / 2
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect12(self):
        # right
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect13(self):
        # left-lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect14(self):
        # left-lower overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya + h / 2
        expected_w = w / 2
        expected_h = h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect15(self):
        # lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya + h
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect16(self):
        # lower overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya + h / 2
        expected_w = w
        expected_h = h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect17(self):
        # right-lower overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w / 2
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa + w / 2
        expected_y = ya + h / 2
        expected_w = w / 2
        expected_h = h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersect18(self):
        # right-lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a & b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_intersected_invalid_invalid(self):
        a = Rect()
        b = Rect()
        c = a.intersect(b)
        self.assertTrue(c.isempty())
        self.assertTrue(not c.isvalid())

    def test_intersected_invalid_valid(self):
        a = Rect()
        b = Rect(30, 50, 100, 200)
        c = a.intersect(b)
        self.assertTrue(c.isempty())
        self.assertTrue(not c.isvalid())
        self.assertTrue(a.isempty())
        self.assertTrue(not a.isvalid())
        self.assertEqual((b.x, b.y, b.width, b.height), (30, 50, 100, 200))

    def test_intersected_valid_invalid(self):
        a = Rect(30, 50, 100, 200)
        b = Rect()
        c = a.intersect(b)
        self.assertTrue(not c.isempty())
        self.assertTrue(c.isvalid())
        self.assertEqual((c.x, c.y, c.width, c.height), (30, 50, 100, 200))
        self.assertEqual((a.x, a.y, a.width, a.height), (30, 50, 100, 200))
        self.assertTrue(b.isempty())
        self.assertTrue(not b.isvalid())

    def test_unite_point01(self):
        # left-upper
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xb
        expected_y = yb
        expected_w = w + w / 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point02(self):
        # upper-left
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xb
        expected_y = yb
        expected_w = w
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point03(self):
        # upper-right
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xa
        expected_y = yb
        expected_w = w
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point04(self):
        # right-upper
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w + w / 2
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xa
        expected_y = yb
        expected_w = w + w / 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point05(self):
        # left
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xb
        expected_y = ya
        expected_w = w + w / 2
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point06(self):
        # center
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w / 2
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point07(self):
        # right
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w + w / 2
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xa
        expected_y = ya
        expected_w = w + w / 2
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point08(self):
        # left-lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya + h + h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xb
        expected_y = ya
        expected_w = w + w / 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point09(self):
        # lower-left
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya + h + h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point10(self):
        # lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w / 2
        yb = ya + h + h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point11(self):
        # lower-right
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w
        yb = ya + h + h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_point12(self):
        # right-lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w + w / 2
        yb = ya + h + h / 2
        a = Rect(xa, ya, w, h)
        c = a.unite(xb, yb)
        expected_x = xa
        expected_y = ya
        expected_w = w + w / 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, c))
        self.assertEqual(c.y, expected_y, msg=(a, c))
        self.assertEqual(c.width, expected_w, msg=(a, c))
        self.assertEqual(c.height, expected_h, msg=(a, c))

    def test_unite_rect01(self):
        # left-upper
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xb
        expected_y = yb
        expected_w = w * 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect02(self):
        # left-upper overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xb
        expected_y = yb
        expected_w = w + w / 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect03(self):
        # upper
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya - h
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xb
        expected_y = yb
        expected_w = w
        expected_h = h * 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect04(self):
        # upper overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xb
        expected_y = yb
        expected_w = w
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect05(self):
        # right-upper overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w / 2
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = yb
        expected_w = w + w / 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect06(self):
        # right-upper
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w
        yb = ya - h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = yb
        expected_w = w * 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect07(self):
        # left
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xb
        expected_y = ya
        expected_w = w * 2
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect08(self):
        # left overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xb
        expected_y = ya
        expected_w = w + w / 2
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect09(self):
        # same position
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect10(self):
        # right overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w / 2
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = ya
        expected_w = w + w / 2
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect11(self):
        # right
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w
        yb = ya
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = ya
        expected_w = w * 2
        expected_h = h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect12(self):
        # left-lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xb
        expected_y = ya
        expected_w = w * 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect13(self):
        # left-lower overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa - w / 2
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xb
        expected_y = ya
        expected_w = w + w / 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect14(self):
        # lower overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect15(self):
        # lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa
        yb = ya + h
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = ya
        expected_w = w
        expected_h = h + h
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect16(self):
        # right-lower overlapped
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w / 2
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = ya
        expected_w = w + w / 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_unite_rect17(self):
        # right-lower
        w = 10
        h = 20
        xa = 100
        ya = 100
        xb = xa + w
        yb = ya + h / 2
        a = Rect(xa, ya, w, h)
        b = Rect(xb, yb, w, h)
        c = a | b
        expected_x = xa
        expected_y = ya
        expected_w = w * 2
        expected_h = h + h / 2
        self.assertEqual(c.x, expected_x, msg=(a, b, c))
        self.assertEqual(c.y, expected_y, msg=(a, b, c))
        self.assertEqual(c.width, expected_w, msg=(a, b, c))
        self.assertEqual(c.height, expected_h, msg=(a, b, c))

    def test_united_invalid_invalid(self):
        a = Rect()
        b = Rect()
        c = a.unite(b.x, b.y, b.width, b.height)
        self.assertTrue(c.isempty())
        self.assertTrue(not c.isvalid())

    def test_united_invalid_valid(self):
        a = Rect()
        b = Rect(30, 50, 100, 200)
        c = a.unite(b.x, b.y, b.width, b.height)
        self.assertTrue(not c.isempty())
        self.assertTrue(c.isvalid())
        self.assertEqual((c.x, c.y, c.width, c.height), (30, 50, 100, 200))
        self.assertTrue(a.isempty())
        self.assertTrue(not a.isvalid())
        self.assertEqual((b.x, b.y, b.width, b.height), (30, 50, 100, 200))

    def test_united_valid_invalid(self):
        a = Rect(30, 50, 100, 200)
        b = Rect()
        c = a.unite(b.x, b.y, b.width, b.height)
        self.assertTrue(not c.isempty())
        self.assertTrue(c.isvalid())
        self.assertEqual((a.x, a.y, a.width, a.height), (30, 50, 100, 200))
        self.assertTrue(b.isempty())
        self.assertTrue(not b.isvalid())


if __name__ == '__main__':
    unittest.main()
