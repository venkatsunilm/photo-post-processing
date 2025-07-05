"""
Professional Photo Enhancement Tools - Photoshop-style processing options
This module provides advanced image enhancement capabilities similar to professional software
"""

from PIL import Image, ImageEnhance, ImageFilter
import numpy as np


class PhotoshopStyleEnhancer:
    """Professional photo enhancement tools similar to Photoshop/Lightroom"""

    def __init__(self, image):
        self.original = image.copy()
        self.working = image.copy()
        self.history = []

    def exposure_adjustment(self, exposure_value):
        """
        Adjust exposure similar to Lightroom (-2.0 to +2.0)
        exposure_value: -2.0 (very dark) to +2.0 (very bright)
        """
        factor = 2 ** exposure_value
        enhancer = ImageEnhance.Brightness(self.working)
        self.working = enhancer.enhance(factor)
        self.history.append(f"Exposure: {exposure_value:+.2f}")
        return self

    def brightness_adjustment(self, brightness_value):
        """
        Linear brightness adjustment (simpler than exposure)
        brightness_value: -100 to +100 (linear scaling)

        Difference from exposure:
        - Exposure: Exponential scaling (like camera stops)
        - Brightness: Linear scaling (simple multiply/add)
        """
        if brightness_value == 0:
            return self

        # Convert to factor: -100 = 0.0 (black), 0 = 1.0 (unchanged), +100 = 2.0 (double)
        if brightness_value > 0:
            # 0 to +100 -> 1.0 to 2.0
            factor = 1.0 + (brightness_value / 100.0)
        else:
            # -100 to 0 -> 0.0 to 1.0
            factor = 1.0 + (brightness_value / 100.0)
            factor = max(0.0, factor)  # Ensure we don't go negative

        enhancer = ImageEnhance.Brightness(self.working)
        self.working = enhancer.enhance(factor)
        self.history.append(f"Brightness: {brightness_value:+d}")
        return self

    def highlights_shadows(self, highlights=-20, shadows=+20, range_mask=50):
        """
        Selective highlights and shadows adjustment
        highlights: -100 to 0 (negative values darken highlights)
        shadows: 0 to +100 (positive values brighten shadows)
        """
        img_array = np.array(self.working).astype(np.float32) / 255.0

        # Calculate luminance
        luminance = 0.299 * img_array[:, :, 0] + 0.587 * \
            img_array[:, :, 1] + 0.114 * img_array[:, :, 2]

        # Create masks for highlights and shadows
        highlight_threshold = 0.7
        shadow_threshold = 0.3

        # Smooth transitions
        highlight_mask = np.clip(
            (luminance - highlight_threshold) / (1.0 - highlight_threshold), 0, 1)
        shadow_mask = np.clip(
            (shadow_threshold - luminance) / shadow_threshold, 0, 1)

        # Apply adjustments
        highlight_factor = 1.0 + (highlights / 100.0)
        shadow_factor = 1.0 + (shadows / 100.0)

        for c in range(3):
            # Adjust highlights
            img_array[:, :, c] = img_array[:, :, c] * (1 - highlight_mask) + \
                (img_array[:, :, c] * highlight_factor) * highlight_mask

            # Adjust shadows
            img_array[:, :, c] = img_array[:, :, c] * (1 - shadow_mask) + \
                (img_array[:, :, c] * shadow_factor) * shadow_mask

        img_array = np.clip(img_array, 0.0, 1.0)
        self.working = Image.fromarray((img_array * 255).astype(np.uint8))
        self.history.append(f"Highlights: {highlights}, Shadows: {shadows}")
        return self

    def vibrance_saturation(self, vibrance=0, saturation=0):
        """
        Smart vibrance and saturation adjustment
        vibrance: -100 to +100 (protects skin tones)
        saturation: -100 to +100 (affects all colors equally)
        """
        if saturation != 0:
            sat_factor = 1.0 + (saturation / 100.0)
            enhancer = ImageEnhance.Color(self.working)
            self.working = enhancer.enhance(sat_factor)

        if vibrance != 0:
            # Vibrance is more complex - it protects already saturated areas
            img_array = np.array(self.working).astype(np.float32) / 255.0

            # Calculate saturation for each pixel
            max_rgb = np.max(img_array, axis=2)
            min_rgb = np.min(img_array, axis=2)
            saturation_map = (max_rgb - min_rgb) / (max_rgb + 1e-6)

            # Vibrance affects less saturated areas more
            vibrance_mask = 1.0 - saturation_map
            vibrance_factor = 1.0 + (vibrance / 100.0) * \
                vibrance_mask[:, :, np.newaxis]

            # Apply vibrance
            mean_rgb = np.mean(img_array, axis=2, keepdims=True)
            img_array = mean_rgb + (img_array - mean_rgb) * vibrance_factor

            img_array = np.clip(img_array, 0.0, 1.0)
            self.working = Image.fromarray((img_array * 255).astype(np.uint8))

        self.history.append(f"Vibrance: {vibrance}, Saturation: {saturation}")
        return self

    def clarity_structure(self, clarity=0, structure=0):
        """
        Clarity (midtone contrast) and Structure (detail enhancement)
        clarity: -100 to +100 (midtone contrast)
        structure: -100 to +100 (fine detail enhancement)
        """
        if clarity != 0:
            # Clarity = unsharp mask with large radius
            radius = 20.0
            amount = abs(clarity) / 50.0

            blurred = self.working.filter(
                ImageFilter.GaussianBlur(radius=radius))

            if clarity > 0:
                # Positive clarity
                mask = ImageEnhance.Contrast(blurred).enhance(1.0 + amount)
                self.working = Image.blend(self.working, mask, amount)
            else:
                # Negative clarity (soften)
                self.working = Image.blend(self.working, blurred, amount)

        if structure != 0:
            # Structure = unsharp mask with small radius
            radius = 1.0
            amount = abs(structure) / 100.0
            threshold = 2

            if structure > 0:
                unsharp_filter = ImageFilter.UnsharpMask(
                    radius=radius,
                    percent=int(amount * 200),
                    threshold=threshold
                )
                self.working = self.working.filter(unsharp_filter)

        self.history.append(f"Clarity: {clarity}, Structure: {structure}")
        return self

    def color_temperature(self, temperature=0, tint=0):
        """
        Color temperature and tint adjustment
        temperature: -100 (cool/blue) to +100 (warm/yellow)
        tint: -100 (green) to +100 (magenta)
        """
        if temperature == 0 and tint == 0:
            return self

        img_array = np.array(self.working).astype(np.float32) / 255.0

        # Temperature adjustment (blue-yellow axis)
        if temperature != 0:
            temp_factor = temperature / 100.0
            if temp_factor > 0:  # Warmer (more yellow/red)
                img_array[:, :, 0] *= (1.0 + temp_factor * 0.1)  # Red
                img_array[:, :, 1] *= (1.0 + temp_factor * 0.05)  # Green
                img_array[:, :, 2] *= (1.0 - temp_factor * 0.1)  # Blue
            else:  # Cooler (more blue)
                img_array[:, :, 0] *= (1.0 + temp_factor * 0.1)  # Red
                img_array[:, :, 2] *= (1.0 - temp_factor * 0.1)  # Blue

        # Tint adjustment (green-magenta axis)
        if tint != 0:
            tint_factor = tint / 100.0
            if tint_factor > 0:  # More magenta
                img_array[:, :, 0] *= (1.0 + tint_factor * 0.05)  # Red
                img_array[:, :, 2] *= (1.0 + tint_factor * 0.05)  # Blue
                img_array[:, :, 1] *= (1.0 - tint_factor * 0.1)  # Green
            else:  # More green
                img_array[:, :, 1] *= (1.0 - tint_factor * 0.1)  # Green

        img_array = np.clip(img_array, 0.0, 1.0)
        self.working = Image.fromarray((img_array * 255).astype(np.uint8))
        self.history.append(f"Temperature: {temperature}, Tint: {tint}")
        return self

    def portrait_enhancements(self, skin_smoothing=0, eye_brightness=0, teeth_whitening=0):
        """
        Portrait-specific enhancements
        skin_smoothing: 0-100 (subtle skin smoothing)
        eye_brightness: 0-100 (brighten eye areas)
        teeth_whitening: 0-100 (whiten teeth areas)
        """
        if skin_smoothing > 0:
            # More natural skin smoothing approach
            smooth_factor = skin_smoothing / 100.0

            # Create a very subtle blur that preserves important details
            # Use smaller radius and lighter blending for more natural results
            blur_radius = max(0.5, smooth_factor * 1.5)  # Much smaller radius
            blurred = self.working.filter(
                ImageFilter.GaussianBlur(radius=blur_radius))

            # Blend much more subtly to preserve natural skin texture
            blend_amount = smooth_factor * 0.15  # Reduced from 0.3 to 0.15
            self.working = Image.blend(self.working, blurred, blend_amount)

            # Add back some fine detail to maintain natural look
            if smooth_factor > 0.3:  # Only for higher smoothing values
                detail_image = ImageEnhance.Sharpness(
                    self.working).enhance(1.1)
                self.working = Image.blend(self.working, detail_image, 0.2)

        self.history.append(f"Portrait: Smoothing: {skin_smoothing}")
        return self

    def apply_midtone_protection(self):
        """
        Apply intelligent midtone protection to prevent over-brightening of
        sand, ground, and other bright horizontal surfaces in sports photography.
        Only applies protection when bright midtones are detected.
        """
        import numpy as np

        # Convert to numpy array for analysis
        img_array = np.array(self.working)

        # Convert to HSV for better luminance analysis
        hsv_array = np.array(self.working.convert('HSV'))

        # Analyze the brightness distribution
        brightness = hsv_array[:, :, 2]  # V channel (brightness)

        # Detect potentially problematic bright midtones (sand/ground areas)
        # Focus on areas that are bright enough to be sand but not highlights
        bright_midtone_mask = (brightness > 140) & (brightness < 200)

        # Calculate what percentage of the image is bright midtones
        bright_midtone_percentage = np.sum(
            bright_midtone_mask) / brightness.size

        # Only apply protection if there's a significant amount of bright midtones
        # AND the overall image brightness suggests potential over-exposure
        overall_brightness = np.mean(brightness)

        should_protect = (
            bright_midtone_percentage > 0.15 and  # At least 15% bright midtones
            overall_brightness > 120               # Overall bright image
        )

        if should_protect:
            # Create a more targeted protection for very bright midtones
            # Focus on the brightest midtones (160-200 range) which are most likely sand
            target_mask = (brightness > 160) & (brightness < 200)

            if np.any(target_mask):
                # Apply gentle darkening factor for sand protection
                darkening_factor = 0.94  # Reduce brightness by 6%

                # Apply the darkening only to the detected areas
                protected_brightness = brightness.copy().astype(np.float32)
                protected_brightness[target_mask] *= darkening_factor

                # Ensure values stay within valid range
                protected_brightness = np.clip(
                    protected_brightness, 0, 255).astype(np.uint8)

                # Apply the protected brightness back to the image
                hsv_array[:, :, 2] = protected_brightness

                # Convert back to RGB
                protected_img = Image.fromarray(
                    hsv_array, 'HSV').convert('RGB')

                # Blend with original for natural transition
                self.working = Image.blend(self.working, protected_img, 0.5)

                self.history.append(
                    f"Midtone Protection: Applied ({bright_midtone_percentage*100:.1f}% bright areas)")
            else:
                self.history.append(
                    "Midtone Protection: No target areas found")
        else:
            reason = "low bright areas" if bright_midtone_percentage <= 0.15 else "image not bright enough"
            self.history.append(f"Midtone Protection: Skipped ({reason})")

        return self

    def get_result(self):
        """Get the final processed image"""
        return self.working

    def get_history(self):
        """Get processing history"""
        return self.history

    def reset(self):
        """Reset to original image"""
        self.working = self.original.copy()
        self.history = []
        return self


# Preset configurations for different photo types
PHOTOSHOP_PRESETS = {
    'portrait_subtle': {
        'exposure': 0.05,               # Very slight brightness
        'highlights': -5,               # Minimal highlight recovery
        'shadows': 8,                   # Gentle shadow lift
        'vibrance': 5,                  # Very subtle color enhancement
        'saturation': 0,                # No extra saturation
        'clarity': 2,                   # Very minimal depth
        'structure': 5,                 # Minimal detail enhancement
        'temperature': 2,               # Slight warmth
        'skin_smoothing': 8             # Gentle smoothing
    },
    'portrait_subtle_raw': {
        # Much more conservative exposure (was 0.08)
        'exposure': 0.02,
        # Very gentle highlight recovery (was -8)
        'highlights': -3,
        'shadows': 5,                   # Much less shadow lift (was 12)
        'vibrance': 3,                  # Reduced color enhancement (was 8)
        'saturation': 0,                # No extra saturation
        'clarity': 1,                   # Minimal clarity (was 3)
        'structure': 3,                 # Much less detail enhancement (was 8)
        'temperature': 1,               # Very slight warmth (was 3)
        'skin_smoothing': 5             # Reduced smoothing (was 8)
    },
    'portrait_natural': {
        'exposure': 0.1,
        'highlights': -10,
        'shadows': 15,
        'vibrance': 10,
        'saturation': 0,
        'clarity': 5,
        'structure': 10,
        'temperature': 5,
        'skin_smoothing': 15
    },
    'portrait_dramatic': {
        'exposure': 0.08,               # Slightly more brightness for drama
        'highlights': -8,               # Gentler highlight recovery (was -12)
        'shadows': 20,                  # Keep shadow lift for drama
        # More vibrance for color drama (was 12)
        'vibrance': 15,
        'saturation': 0,                # Keep saturation neutral
        # Much less clarity to avoid artificial look (was 8)
        'clarity': 3,
        # Reduced structure to avoid over-sharpening (was 12)
        'structure': 8,
        # More warmth for appealing look (was 3)
        'temperature': 5,
        # Much less smoothing to preserve natural texture (was 12)
        'skin_smoothing': 5
    },
    'landscape': {
        'exposure': 0.0,
        'highlights': -15,
        'shadows': 10,
        'vibrance': 20,
        'saturation': 10,
        'clarity': 20,
        'structure': 15,
        'temperature': -5
    },
    'studio_portrait': {
        'exposure': 0.2,
        'highlights': -5,
        'shadows': 5,
        'vibrance': 5,
        'saturation': 0,
        'clarity': 0,
        'structure': 5,
        'temperature': 10,
        'skin_smoothing': 20
    },
    'overexposed_recovery': {
        'exposure': -0.1,               # Very gentle exposure reduction
        'highlights': -20,              # Moderate highlight recovery
        'shadows': 10,                  # Gentle shadow lift
        'vibrance': 8,                  # Subtle color enhancement
        'saturation': 0,                # No global saturation change
        'clarity': 3,                   # Minimal mid-tone contrast
        'structure': 5,                 # Light detail enhancement
        'temperature': 0,               # Keep original color temperature
        'skin_smoothing': 0             # No smoothing for wildlife
    },
    'natural_wildlife': {
        'exposure': 0.05,               # Very slight brightness boost
        'highlights': -12,              # Gentle highlight recovery
        'shadows': 15,                  # Lift shadows to show detail
        'vibrance': 12,                 # Enhance natural colors
        'saturation': 0,                # No artificial saturation
        'clarity': 6,                   # Enhance fur/feather texture
        'structure': 10,                # Bring out natural details
        'temperature': 2,               # Very slight warmth
        'skin_smoothing': 0             # No smoothing - preserve natural texture
    },
    'sports_action': {
        # Reduced for sand/ground protection (was 0.06)
        'exposure': 0.04,
        # Stronger highlight recovery to protect bright sand (was -12)
        'highlights': -18,
        # Reduced shadow lift to prevent ground brightening (was 15)
        'shadows': 10,
        'vibrance': 12,                 # Keep natural vibrance
        'saturation': 2,                # Minimal saturation boost
        'clarity': 8,                   # Moderate clarity for natural sharpness
        'structure': 10,                # Gentler detail enhancement
        'temperature': 2,               # Subtle warmth
        'skin_smoothing': 0,            # No smoothing - preserve athletic detail
        'midtone_protection': True      # Protect bright midtones like sand/ground
    },
    'sports_action_raw': {
        # Further reduced for sand protection (was 0.03)
        'exposure': 0.02,
        # Better highlight recovery for bright areas (was -5)
        'highlights': -10,
        # Minimal shadow lift to avoid ground brightening (was 8)
        'shadows': 5,
        'vibrance': 5,                  # Very subtle color enhancement
        'saturation': 0,                # No saturation boost
        'clarity': 2,                   # Minimal clarity
        'structure': 5,                 # Very light detail enhancement
        'temperature': 0,               # Keep neutral temperature
        'skin_smoothing': 0,            # No smoothing - preserve athletic detail
        'midtone_protection': True      # Protect bright midtones like sand/ground
    },
    'portrait_dramatic_raw': {
        'exposure': 0.12,               # More exposure headroom for RAW
        'highlights': -15,              # Stronger highlight recovery
        'shadows': 25,                  # More aggressive shadow lift
        'vibrance': 20,                 # Higher vibrance for RAW
        'saturation': 5,                # Some saturation for drama
        'clarity': 8,                   # Moderate clarity for natural look
        'structure': 12,                # More structure for RAW detail
        'temperature': 8,               # More warmth for appealing look
        'skin_smoothing': 3             # Minimal smoothing
    },
    'portrait_natural_raw': {
        'exposure': 0.15,               # More exposure for RAW
        'highlights': -18,              # Stronger highlight recovery
        'shadows': 22,                  # More aggressive shadow lift
        'vibrance': 15,                 # Higher vibrance for RAW
        'saturation': 3,                # Some saturation boost
        'clarity': 8,                   # Moderate clarity
        'structure': 15,                # More structure for RAW
        'temperature': 8,               # More warmth
        'skin_smoothing': 12            # Moderate smoothing
    },
    'landscape_raw': {
        'exposure': 0.05,               # Slight exposure boost
        'highlights': -25,              # Strong highlight recovery for skies
        'shadows': 15,                  # Moderate shadow lift
        'vibrance': 30,                 # High vibrance for landscape colors
        'saturation': 15,               # More saturation for impact
        'clarity': 25,                  # High clarity for landscape detail
        'structure': 20,                # Strong detail enhancement
        'temperature': -3,              # Slightly cooler for landscapes
        'skin_smoothing': 0             # No smoothing for landscapes
    },
    'natural_wildlife_raw': {
        'exposure': 0.08,               # Slight brightness boost
        'highlights': -18,              # Moderate highlight recovery
        'shadows': 20,                  # Good shadow detail
        'vibrance': 18,                 # Enhanced natural colors
        'saturation': 3,                # Minimal artificial saturation
        'clarity': 12,                  # Good fur/feather texture
        'structure': 18,                # Strong natural details
        'temperature': 5,               # Slight warmth for natural look
        'skin_smoothing': 0             # No smoothing - preserve texture
    }
}


def apply_photoshop_preset(image, preset_name):
    """Apply a Photoshop-style preset to an image"""
    if preset_name not in PHOTOSHOP_PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}")

    enhancer = PhotoshopStyleEnhancer(image)
    preset = PHOTOSHOP_PRESETS[preset_name]

    # Apply all adjustments in the preset
    enhancer.exposure_adjustment(preset.get('exposure', 0))
    enhancer.highlights_shadows(
        highlights=preset.get('highlights', 0),
        shadows=preset.get('shadows', 0)
    )
    enhancer.vibrance_saturation(
        vibrance=preset.get('vibrance', 0),
        saturation=preset.get('saturation', 0)
    )
    enhancer.clarity_structure(
        clarity=preset.get('clarity', 0),
        structure=preset.get('structure', 0)
    )
    enhancer.color_temperature(
        temperature=preset.get('temperature', 0),
        tint=preset.get('tint', 0)
    )
    enhancer.portrait_enhancements(
        skin_smoothing=preset.get('skin_smoothing', 0)
    )

    # Apply midtone protection if specified (for sports photography)
    if preset.get('midtone_protection', False):
        enhancer.apply_midtone_protection()

    return enhancer.get_result(), enhancer.get_history()
