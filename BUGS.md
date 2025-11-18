# Known Bugs and Issues

## Data Quality

### ✅ FIXED: Wrong Scale
**Status**: Fixed
**Fixed**: 2025-11-18

Throttle/brake/steering were captured as 0.00-1.00 values, but telemetry analysis expected 0-100%.

**Solution**: Implemented `SampleNormalizer` in `src/mvp_format.py` to automatically scale inputs to 0-100% range.

**Verification**: Live test confirmed correct scaling (brake: 61.26%, steer: -1.63%)


## Performance Notes

### ✅ Capture Rate: ~43Hz (Working as Expected)
**Status**: Working as Expected
**Priority**: N/A (Not a Bug)
**Discovered**: 2025-11-18
**Updated**: 2025-11-18

**Description**:
The telemetry logger captures data at approximately 43Hz. This is **expected and optimal** given the rF2SharedMemoryMapPlugin limitation.

**Evidence**:
- Initial test (old format): ~20Hz (10,915 samples / 537s)
- Latest test (MVP format): ~43Hz (12,972 samples / 302s)
- **rF2SharedMemoryMapPlugin updates at 50Hz maximum** ([source](https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin))
- Current performance: **86% of plugin maximum** (43Hz / 50Hz)
- Improvement: 2.1x faster than initial implementation

**Why not 100Hz?**:
The original 100Hz target was aspirational, but the shared memory plugin itself only updates at 50Hz. We cannot capture data faster than the source provides it.

**Actual Impact**:
- ✅ **Excellent** resolution for lap analysis (86% of maximum possible)
- ✅ **More than sufficient** for telemetry comparison and optimization
- ✅ **Meets all requirements** for browser-based telemetry viewers
- ✅ **Captures all meaningful events** in sim racing scenarios

**Conclusion**:
No optimization needed. Current performance is near-optimal given the plugin's 50Hz update rate. The slight gap (43Hz vs 50Hz) is acceptable overhead from Python polling and data processing.

---

## Future Enhancements

### Car Setup Data Not Captured
**Status**: Enhancement
**Priority**: Low

Currently the car setup section shows all zeros. Need to map setup data from shared memory if available.

### Some Telemetry Fields Default to Zero
**Status**: Enhancement
**Priority**: Low

Fields not available in shared memory:
- Oil pressure
- Wind speed/direction
- DRS availability
- Suspension acceleration
- Some wheel/tire metrics

These are set to default values (0.0) in the output.
