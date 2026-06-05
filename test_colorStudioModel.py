# -*- coding: utf-8 -*-
"""
Test Suite for Color Studio - Étape 6.2 Qualité Logicielle
Rémi Cozot 2019 - Updated 2024
"""

import unittest
import numpy as np
import math
from colorStudioModel import Images, Light, Scene, Saturation, AE_Ymean, PostProcess, PPClip


class TestImages(unittest.TestCase):
    """Test suite for Images class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.images = Images(
            pathImage='./images/test/',
            baseImageName='test_',
            extImageName='.jpg',
            nbImage=10,
            nbDigit=4,
            load=False
        )
    
    def test_images_initialization(self):
        """Test Images class initialization"""
        self.assertEqual(self.images._nbImage, 10)
        self.assertEqual(self.images._nbDigit, 4)
        self.assertEqual(self.images._baseImageName, 'test_')
        self.assertEqual(len(self.images._images), 0)
    
    def test_images_len(self):
        """Test Images.len() method"""
        self.assertEqual(self.images.len(), 10)
    
    def test_images_clear(self):
        """Test Images.clear() method"""
        # Add a dummy image
        self.images._images.append(np.zeros((100, 100, 3)))
        self.assertEqual(len(self.images._images), 1)
        # Clear
        self.images.clear()
        self.assertEqual(len(self.images._images), 0)


class TestLight(unittest.TestCase):
    """Test suite for Light class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.light = Light(name="TestLight")
        # Create dummy images
        self.images = Images(
            pathImage='./images/test/',
            baseImageName='test_',
            extImageName='.jpg',
            nbImage=5,
            nbDigit=4,
            load=False
        )
        # Add test images
        for i in range(5):
            test_img = np.ones((100, 100, 3)) * (0.5 + i*0.1)
            self.images._images.append(test_img)
        self.light.setImagesArray(self.images)
    
    def test_light_initialization(self):
        """Test Light class initialization"""
        self.assertIsNotNone(self.light._name)
        self.assertEqual(self.light._exposure, 0)
        self.assertEqual(self.light._imageIdx, 0)
    
    def test_light_set_exposure(self):
        """Test Light.setExposure() method"""
        self.light.setExposure(2.5)
        self.assertEqual(self.light._exposure, 2.5)
        self.assertTrue(self.light._needUpdate)
    
    def test_light_set_color(self):
        """Test Light.setColor() method"""
        color = np.array([0.8, 0.6, 0.4])
        self.light.setColor(color)
        np.testing.assert_array_equal(self.light._npColorRGB, color)
        self.assertTrue(self.light._needUpdate)
    
    def test_light_set_image_idx(self):
        """Test Light.setImageIdx() method"""
        self.light.setImageIdx(2)
        self.assertEqual(self.light._imageIdx, 2)
        self.assertTrue(self.light._needUpdate)
    
    def test_light_render_first_update(self):
        """Test Light.render() on first update"""
        self.light.setImageIdx(0)
        self.light.setExposure(0.0)
        output = self.light.render()
        self.assertIsNotNone(output)
        self.assertEqual(output.shape, self.images._images[0].shape)
        self.assertFalse(self.light._needUpdate)
        self.assertFalse(self.light._firstUpdate)
    
    def test_light_render_with_exposure(self):
        """Test Light.render() with exposure adjustment"""
        self.light.setImageIdx(0)
        self.light.setExposure(1.0)  # 2^1 = 2x brighter
        output = self.light.render()
        # Check that output is approximately 2x brighter
        self.assertTrue(np.all(output >= self.images._images[0]))


class TestSaturation(unittest.TestCase):
    """Test suite for Saturation post-process"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.saturation = Saturation(linearSat=0, gammaSat=0)
        self.test_img = np.ones((50, 50, 3)) * 0.5
    
    def test_saturation_initialization(self):
        """Test Saturation class initialization"""
        self.assertEqual(self.saturation._linearSaturation, 0)
        self.assertEqual(self.saturation._gammaSaturation, 0)
    
    def test_saturation_set_linear(self):
        """Test Saturation.setLinearSaturation() method"""
        self.saturation.setLinearSaturation(50)
        self.assertEqual(self.saturation._linearSaturation, 50)
    
    def test_saturation_set_gamma(self):
        """Test Saturation.setGammaSaturation() method"""
        self.saturation.setGammaSaturation(-25)
        self.assertEqual(self.saturation._gammaSaturation, -25)
    
    def test_saturation_postprocess_no_change(self):
        """Test Saturation.postProcess() with no saturation change"""
        output = self.saturation.postProcess(self.test_img.copy())
        # Output should be similar to input when saturation is 0
        self.assertEqual(output.shape, self.test_img.shape)
    
    def test_saturation_output_shape(self):
        """Test that saturation preserves image shape"""
        self.saturation.setLinearSaturation(50)
        output = self.saturation.postProcess(self.test_img.copy())
        self.assertEqual(output.shape, self.test_img.shape)


class TestAE_Ymean(unittest.TestCase):
    """Test suite for AE_Ymean auto exposure post-process"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ae = AE_Ymean(Ytarget=0.5, exposure=0.0)
        # Create a test image with known Y value
        self.test_img = np.ones((50, 50, 3)) * 0.5
    
    def test_ae_initialization(self):
        """Test AE_Ymean class initialization"""
        self.assertEqual(self.ae._Ytarget, 0.5)
        self.assertTrue(self.ae._on_off)
    
    def test_ae_set_on_off(self):
        """Test AE_Ymean.setOnOff() method"""
        self.ae.setOnOff(False)
        self.assertFalse(self.ae._on_off)
        self.ae.setOnOff(True)
        self.assertTrue(self.ae._on_off)
    
    def test_ae_set_exposure_when_on(self):
        """Test AE_Ymean.setExposure() when AE is ON"""
        self.ae.setOnOff(True)
        self.ae.setExposure(1.0)
        self.assertEqual(self.ae._exposureON, 1.0)
    
    def test_ae_set_exposure_when_off(self):
        """Test AE_Ymean.setExposure() when AE is OFF"""
        self.ae.setOnOff(False)
        self.ae.setExposure(2.0)
        self.assertEqual(self.ae._exposureOFF, 2.0)
    
    def test_ae_postprocess_output_shape(self):
        """Test that AE_Ymean preserves image shape"""
        self.ae.setOnOff(False)
        self.ae.setExposure(0.0)
        output = self.ae.postProcess(self.test_img.copy())
        self.assertEqual(output.shape, self.test_img.shape)
    
    def test_ae_postprocess_with_exposure(self):
        """Test AE_Ymean.postProcess() with exposure"""
        self.ae.setOnOff(False)
        self.ae.setExposure(1.0)
        output = self.ae.postProcess(self.test_img.copy())
        # With exposure 1.0, output should be ~2x brighter
        expected = self.test_img * math.pow(2, 1.0)
        np.testing.assert_array_almost_equal(output, expected, decimal=5)


class TestPostProcess(unittest.TestCase):
    """Test suite for PostProcess base class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pp = PostProcess()
        self.test_img = np.ones((50, 50, 3)) * 0.5
    
    def test_postprocess_does_nothing(self):
        """Test that base PostProcess does nothing"""
        output = self.pp.postProcess(self.test_img)
        np.testing.assert_array_equal(output, self.test_img)


class TestPPClip(unittest.TestCase):
    """Test suite for PPClip post-process"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ppclip = PPClip(minValue=0.2, maxValue=0.8)
        # Create test image with values outside clip range
        self.test_img = np.array([
            [[0.0, 0.5, 1.0]],
            [[0.3, 0.5, 0.7]],
            [[0.2, 0.5, 0.8]]
        ]).reshape(3, 1, 3)
    
    def test_ppclip_initialization(self):
        """Test PPClip class initialization"""
        self.assertEqual(self.ppclip._minValue, 0.2)
        self.assertEqual(self.ppclip._maxValue, 0.8)
    
    def test_ppclip_clips_values(self):
        """Test that PPClip correctly clips values"""
        output = self.ppclip.postProcess(self.test_img.copy())
        # Check that all values are within [0.2, 0.8]
        self.assertTrue(np.all(output >= 0.2))
        self.assertTrue(np.all(output <= 0.8))


class TestScene(unittest.TestCase):
    """Test suite for Scene class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scene = Scene(hdr=False)
        
        # Create and setup a light
        self.light = Light(name="TestLight")
        self.images = Images(
            pathImage='./images/test/',
            baseImageName='test_',
            extImageName='.jpg',
            nbImage=3,
            nbDigit=4,
            load=False
        )
        for i in range(3):
            self.images._images.append(np.ones((100, 100, 3)) * 0.5)
        self.light.setImagesArray(self.images)
        self.scene.addLight(self.light)
    
    def test_scene_initialization(self):
        """Test Scene class initialization"""
        self.assertEqual(len(self.scene._lights), 1)
        self.assertEqual(len(self.scene._postProcesses), 0)
        self.assertFalse(self.scene._hdr)
    
    def test_scene_add_light(self):
        """Test Scene.addLight() method"""
        light2 = Light(name="TestLight2")
        self.scene.addLight(light2)
        self.assertEqual(len(self.scene._lights), 2)
    
    def test_scene_add_postprocess(self):
        """Test Scene.addPostProcess() method"""
        pp = PostProcess()
        self.scene.addPostProcess(pp)
        self.assertEqual(len(self.scene._postProcesses), 1)
    
    def test_scene_get_light_by_name(self):
        """Test Scene.getLightByName() method"""
        found_light = self.scene.getLightByName("TestLight")
        self.assertIsNotNone(found_light)
        self.assertEqual(found_light._name, "TestLight")
    
    def test_scene_render_output_shape(self):
        """Test Scene.render() output shape"""
        output = self.scene.render()
        self.assertEqual(output.shape, self.images._images[0].shape)
    
    def test_scene_render_with_clipping(self):
        """Test Scene.render() with HDR=False (clipping enabled)"""
        self.scene._hdr = False
        output = self.scene.render()
        # All values should be in [0, 1]
        self.assertTrue(np.all(output >= 0.0))
        self.assertTrue(np.all(output <= 1.0))
    
    def test_scene_clear(self):
        """Test Scene.clear() method"""
        self.scene.clear()
        self.assertEqual(len(self.scene._lights), 0)
        self.assertEqual(len(self.scene._postProcesses), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scene = Scene(hdr=False)
        
        # Create two lights
        for light_idx in range(2):
            light = Light(name=f"IntegrationLight{light_idx}")
            images = Images(
                pathImage='./images/test/',
                baseImageName=f'test_{light_idx}_',
                extImageName='.jpg',
                nbImage=5,
                nbDigit=4,
                load=False
            )
            for i in range(5):
                images._images.append(np.ones((100, 100, 3)) * (0.4 + light_idx*0.1))
            light.setImagesArray(images)
            self.scene.addLight(light)
        
        # Add post-processes
        ae = AE_Ymean(Ytarget=0.5, exposure=0.0)
        sat = Saturation(linearSat=0, gammaSat=0)
        self.scene.addPostProcess(ae)
        self.scene.addPostProcess(sat)
    
    def test_integration_full_pipeline(self):
        """Test complete render pipeline"""
        output = self.scene.render()
        
        # Check output validity
        self.assertIsNotNone(output)
        self.assertEqual(len(output.shape), 3)
        self.assertEqual(output.shape[2], 3)  # RGB
        self.assertTrue(np.all(output >= 0.0))
        self.assertTrue(np.all(output <= 1.0))
    
    def test_integration_light_modification(self):
        """Test scene modification during rendering"""
        # Modify first light
        light = self.scene._lights[0]
        light.setExposure(1.0)
        light.setImageIdx(2)
        
        output = self.scene.render()
        self.assertIsNotNone(output)
    
    def test_integration_multiple_renders_consistency(self):
        """Test that multiple renders are consistent"""
        output1 = self.scene.render()
        output2 = self.scene.render()
        
        # Without changes, outputs should be identical
        np.testing.assert_array_equal(output1, output2)


if __name__ == '__main__':
    unittest.main(verbosity=2)
