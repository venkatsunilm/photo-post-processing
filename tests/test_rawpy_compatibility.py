"""
RAW processing compatibility test and auto-detection of supported parameters.
"""

import rawpy
import os


def test_rawpy_parameters():
    """Test which rawpy parameters are supported in this version."""
    print("🔍 Testing rawpy parameter compatibility...")

    # Find a sample RAW file for testing
    test_dirs = [
        r"C:\Users\harit\Documents\temp\Input Photos",
        r"input",
        r"tests",
        "."
    ]

    test_file = None
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                if file.lower().endswith(('.nef', '.raw', '.cr2', '.arw')):
                    test_file = os.path.join(test_dir, file)
                    break
        if test_file:
            break

    if not test_file:
        print("❌ No RAW files found for parameter testing")
        return {}

    print(f"📸 Testing with: {os.path.basename(test_file)}")

    supported_params = {}

    try:
        with rawpy.imread(test_file) as raw:
            # Test basic parameters first
            base_params = {
                'output_bps': 8,
                'no_auto_bright': False,
                'use_camera_wb': True,
                'half_size': False,
                'four_color_rgb': False
            }

            # Test if basic processing works
            try:
                rgb_array = raw.postprocess(**base_params)
                supported_params.update(base_params)
                print("✅ Basic parameters supported")
            except Exception as e:
                print(f"❌ Basic parameters failed: {e}")
                return {}

            # Test advanced parameters one by one
            test_params = [
                ('bright', 1.2),
                ('auto_bright_thr', 0.01),
                ('exp_correc', True),
                ('exp_shift', 0.3),
                ('highlight', 1),
                ('no_auto_scale', False),
                ('user_wb', None),
                ('dcb_iterations', 0),
                ('dcb_enhance', False),
                ('fbdd_noise_reduction', 0),
                ('median_filter_passes', 0)
            ]

            for param_name, param_value in test_params:
                try:
                    test_param_dict = base_params.copy()
                    test_param_dict[param_name] = param_value
                    rgb_array = raw.postprocess(**test_param_dict)
                    supported_params[param_name] = param_value
                    print(f"✅ {param_name}: supported")
                except Exception as e:
                    print(f"❌ {param_name}: not supported ({e})")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return {}

    print(f"\n📊 Supported parameters: {len(supported_params)}")
    return supported_params


if __name__ == "__main__":
    supported = test_rawpy_parameters()
    print("\n🎯 COMPATIBLE PARAMETERS:")
    for param, value in supported.items():
        print(f"  • {param}: {value}")
