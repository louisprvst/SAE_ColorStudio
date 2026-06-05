import unittest

import numpy as np

from colorStudioModel import AE_Ymean, Images, Light, PPClip, Scene


def images_with_arrays(*arrays):
    images = Images("", "img", ".png", len(arrays), 1, load=False)
    images._images = list(arrays)
    return images


class LightTest(unittest.TestCase):
    def test_render_applies_selected_image_color_and_exposure(self):
        img0 = np.ones((1, 1, 3)) * 0.25
        img1 = np.ones((1, 1, 3)) * 0.5
        light = Light("Key")
        light.setImagesArray(images_with_arrays(img0, img1))
        light.setImageIdx(1)
        light.setColor(np.array([1.0, 0.5, 0.25]))
        light.setExposure(1.0)

        result = light.render()

        np.testing.assert_allclose(result, [[[1.0, 0.5, 0.25]]])

    def test_toXML_serializes_light_configuration(self):
        light = Light("Fill")
        light.setImagesArray(Images("renders/", "light_", ".jpg", 12, 3, load=False))
        light.setImageIdx(4)
        light.setExposure(-1.0)
        light.setColor(np.array([0.2, 0.4, 0.6]))

        xml = light.toXML()

        self.assertIn('<LIGHT name="Fill">', xml)
        self.assertIn('ext=".jpg"', xml)
        self.assertIn('max="12"', xml)
        self.assertIn('digit="3"', xml)
        self.assertIn("renders/light_", xml)
        self.assertIn("<IDXPOS>4</IDXPOS>", xml)
        self.assertIn("<EXP>-1.0</EXP>", xml)
        self.assertIn("<R>0.2</R>", xml)


class SceneTest(unittest.TestCase):
    def test_render_adds_lights_and_clips_non_hdr_output(self):
        light_a = Light("A")
        light_a.setImagesArray(images_with_arrays(np.ones((1, 1, 3)) * 0.75))
        light_b = Light("B")
        light_b.setImagesArray(images_with_arrays(np.ones((1, 1, 3)) * 0.5))
        scene = Scene(hdr=False)
        scene.addLight(light_a)
        scene.addLight(light_b)

        result = scene.render()

        np.testing.assert_allclose(result, [[[1.0, 1.0, 1.0]]])

    def test_render_keeps_values_above_one_in_hdr_mode(self):
        light_a = Light("A")
        light_a.setImagesArray(images_with_arrays(np.ones((1, 1, 3)) * 0.75))
        light_b = Light("B")
        light_b.setImagesArray(images_with_arrays(np.ones((1, 1, 3)) * 0.5))
        scene = Scene(hdr=True)
        scene.addLight(light_a)
        scene.addLight(light_b)

        result = scene.render()

        np.testing.assert_allclose(result, [[[1.25, 1.25, 1.25]]])


class PostProcessTest(unittest.TestCase):
    def test_PPClip_clips_image_between_min_and_max(self):
        img = np.array([[[-1.0, 0.5, 2.0]]])

        result = PPClip(0.0, 1.0).postProcess(img)

        np.testing.assert_allclose(result, [[[0.0, 0.5, 1.0]]])

    def test_AE_Ymean_off_mode_applies_manual_exposure(self):
        img = np.ones((1, 1, 3)) * 0.25
        post_process = AE_Ymean(exposure=1.0)
        post_process.setOnOff(False)

        result = post_process.postProcess(img)

        np.testing.assert_allclose(result, np.ones((1, 1, 3)) * 0.5)


if __name__ == "__main__":
    unittest.main()
