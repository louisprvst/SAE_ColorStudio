import unittest

import numpy as np

from colorStudioUtils import (
    colorWheel,
    image2Ymean,
    img2chromaVertices,
    imgRGB2chromaRG,
    inRange2D,
)


class ColorStudioUtilsTest(unittest.TestCase):
    def test_image2Ymean_returns_luminance_average(self):
        img = np.array(
            [
                [[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]],
                [[1.0, 1.0, 1.0], [0.0, 0.0, 0.0]],
            ]
        )

        self.assertAlmostEqual(image2Ymean(img), 0.5)

    def test_imgRGB2chromaRG_computes_rg_chromaticity(self):
        img = np.array(
            [
                [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
                [[0.0, 0.0, 1.0], [0.0, 0.0, 0.0]],
            ]
        )

        result = imgRGB2chromaRG(img)

        expected = np.array(
            [
                [1.0, 0.0],
                [0.0, 1.0],
                [0.0, 0.0],
                [0.0, 0.0],
            ]
        )
        np.testing.assert_allclose(result, expected)

    def test_img2chromaVertices_builds_rgba_vertices(self):
        img = np.array([[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]])

        result = img2chromaVertices(img)

        self.assertEqual(result.shape, (1, 2, 6))
        np.testing.assert_allclose(result[0, 0], [1.0, -1.0, 1.0, 0.0, 0.0, 1.0])
        np.testing.assert_allclose(result[0, 1], [-1.0, 1.0, 0.0, 1.0, 0.0, 1.0])

    def test_colorWheel_returns_rgb_square_with_white_center(self):
        result = colorWheel(3)

        self.assertEqual(result.shape, (7, 7, 3))
        np.testing.assert_allclose(result[3, 3], [1.0, 1.0, 1.0])
        np.testing.assert_allclose(result[0, 0], [0.01, 0.01, 0.01])

    def test_inRange2D_includes_rectangle_boundaries(self):
        self.assertTrue(inRange2D((0, 0), (0, 0), (10, 5)))
        self.assertTrue(inRange2D((10, 5), (0, 0), (10, 5)))
        self.assertFalse(inRange2D((11, 5), (0, 0), (10, 5)))
        self.assertFalse(inRange2D((10, 6), (0, 0), (10, 5)))


if __name__ == "__main__":
    unittest.main()
