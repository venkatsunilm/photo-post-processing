"""
🏃‍♂️ SPORTS PRESET SAND/GROUND BRIGHTNESS IMPROVEMENTS

Summary of changes made to address sand/ground over-brightening in sports photography:

## PROBLEM IDENTIFIED:
- Sand, grass, and ground surfaces were appearing unnaturally bright after processing
- This was caused by aggressive shadow lifting and exposure adjustments
- Some photos looked good, others had over-bright ground areas

## SOLUTIONS IMPLEMENTED:

### 1. REDUCED EXPOSURE VALUES
Before:
- sports_action: exposure = 0.06
- sports_action_raw: exposure = 0.03

After:
- sports_action: exposure = 0.04 (33% reduction)
- sports_action_raw: exposure = 0.02 (33% reduction)

### 2. REDUCED SHADOW LIFTING
Before:
- sports_action: shadows = 15
- sports_action_raw: shadows = 8

After:
- sports_action: shadows = 10 (33% reduction)
- sports_action_raw: shadows = 5 (37% reduction)

### 3. STRONGER HIGHLIGHT RECOVERY
Before:
- sports_action: highlights = -12
- sports_action_raw: highlights = -5

After:
- sports_action: highlights = -18 (50% stronger)
- sports_action_raw: highlights = -10 (100% stronger)

### 4. INTELLIGENT MIDTONE PROTECTION
Added new feature that:
- Detects images with >15% bright midtones (160-200 brightness range)
- Only applies protection to overall bright images (>120 average brightness)
- Selectively darkens problematic sand/ground areas by 6%
- Uses smart blending to maintain natural look

## WHEN IT HELPS:
✅ Images with bright sand, grass, or concrete surfaces
✅ Outdoor sports with strong lighting
✅ Photos where ground takes up significant portion
✅ Beach, field, court, or track sports

## WHEN IT DOESN'T INTERFERE:
✅ Indoor sports (no bright ground areas)
✅ Close-up action shots (minimal ground visible)
✅ Darker outdoor conditions
✅ Images that don't meet brightness thresholds

## USAGE:
The improvements are automatically applied when using:
- Option 7: Sports Action (auto-detects JPEG vs RAW)
- Both JPEG and RAW files get appropriate protection levels

## RESULT:
- More natural-looking ground surfaces
- Preserved subject enhancement
- Better balance between subject and background
- Protection only applies when needed (smart detection)
"""

print(__doc__)
