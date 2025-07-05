# Photo Post-Processing Test Suite

This directory contains comprehensive testing and analysis tools for the photo post-processing pipeline.

## 📁 Directory Structure

```
tests/
├── run_tests.py                    # Main test runner
├── preset_analysis/
│   └── compare_presets.py         # Preset comparison and analysis
├── raw_processing/
│   └── test_raw_quality.py        # RAW file processing tests
├── image_processing/
│   └── test_quality_impact.py     # Image enhancement quality tests
└── README.md                      # This file
```

## 🚀 Quick Start

### Run Main Test Suite
```bash
cd tests
python run_tests.py
```

### Individual Test Modules

#### 1. Preset Analysis
Compare and analyze all enhancement presets:
```bash
cd tests/preset_analysis
python compare_presets.py
```

**Features:**
- Compare all presets side-by-side
- Sports photography focused analysis
- Preset purpose and use case recommendations

#### 2. RAW Processing Tests
Test NEF file loading and quality:
```bash
cd tests/raw_processing
python test_raw_quality.py
```

**Features:**
- RAW file loading performance tests
- Metadata extraction
- RAW vs JPG quality comparison
- Batch processing tests

#### 3. Image Quality Impact
Analyze enhancement impact on images:
```bash
cd tests/image_processing
python test_quality_impact.py
```

**Features:**
- Before/after image analysis
- Processing time benchmarks
- Quality metrics measurement
- Preset effectiveness comparison

## 🎯 Test Categories

### 📊 Analysis Tools
1. **Preset Comparison** - Compare all enhancement presets
2. **RAW Quality Tests** - Test NEF file processing
3. **Enhancement Impact** - Measure processing effects

### ⚡ Quick Tests
4. **Sports Analysis** - Sports photography preset analysis
5. **RAW vs JPG** - Quality comparison
6. **Performance Benchmark** - Speed and efficiency tests

### 🧪 Full Test Suite
7. **Run All Tests** - Comprehensive analysis

## 📈 What Each Test Provides

### Preset Comparison
- **Parameter comparison table** for all presets
- **Sports photography recommendations**
- **Use case analysis** for each preset
- **Best practices** for different photo types

### RAW Processing Tests
- **Loading performance** metrics
- **Image quality** validation
- **Metadata extraction** testing
- **Error handling** verification

### Quality Impact Tests
- **Before/after analysis** of enhancements
- **Processing time** measurements
- **Quality metrics** (brightness, contrast, color)
- **Preset effectiveness** rankings

## 🏃‍♂️ Sports Photography Focus

Special attention to sports photography testing:

- **Sports Action preset validation**
- **Comparison with other presets**
- **Performance on action shots**
- **Color vibrancy testing**
- **Detail enhancement verification**

## 🔧 Requirements

All tests use the main project dependencies:
- PIL/Pillow for image processing
- rawpy for NEF file handling
- numpy for array operations

## 📝 Usage Notes

1. **Test Data**: Tests use images from the configured input directory
2. **Performance**: RAW file tests may take longer due to file size
3. **Output**: All tests provide detailed console output with analysis
4. **Safety**: Tests are read-only and don't modify original files

## 🎯 Recommended Test Workflow

For **sports photography setup**:
1. Run `Sports Photography Analysis` (Option 4)
2. Test RAW vs JPG quality (Option 5)
3. Run performance benchmark (Option 6)

For **general setup validation**:
1. Run comprehensive test suite (Option 7)

For **preset customization**:
1. Use preset comparison tools (Option 1)
2. Test quality impact (Option 3)

## 🐛 Troubleshooting

- **No test files found**: Ensure images are in the configured input directory
- **Import errors**: Run tests from the tests directory
- **RAW processing fails**: Check rawpy installation
- **Performance issues**: Test with smaller image sets first

## 📊 Output Examples

Tests provide rich console output including:
- ✅ Success/failure indicators
- 📊 Performance metrics
- 🎨 Quality comparisons
- 📈 Statistical analysis
- 🏆 Recommendations

Perfect for validating your photo processing pipeline and optimizing settings!
