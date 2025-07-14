def get_mode_prefix(preset_name: str) -> str:
    """
    Generate a 3-letter prefix string for a given preset or mode name.

    Args:
        preset_name: The name of the preset or processing mode.

    Returns:
        A 3-letter string prefix for use in filenames or directory names.
        Defaults to 'prc' if the name is not recognized.
    """
    mode_prefixes = {
        "portrait_subtle": "sub",
        "portrait_natural": "nat",
        "portrait_dramatic": "drm",
        "studio_portrait": "std",
        "overexposed_recovery": "ovr",
        "natural_wildlife": "wld",
        "sports_action": "spt",
        "enhanced_mode": "ehm",  # Enhanced mode for challenging lighting
        "enhanced": "enh",  # Legacy enhanced mode
        "resize_watermark": "rsz",
        "watermark": "wtm",
        "resize_only": "res",
        "custom": "cst",
    }
    # Default to 'prc' for process
    return mode_prefixes.get(preset_name, "prc")
