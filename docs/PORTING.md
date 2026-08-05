# ENKI Porting Tracker

C++ → Rust migration. C++ is the specification. Behavioral parity first, elegance later.

Reference commit: `c322d2a` (initial C++ source)

## Behavior Checklist (Orchestrator)

- [ ] Frame timing: 30fps target (33333μs per frame)
- [ ] Idle timeout: 30s of no hands → release input
- [ ] Cursor smoothing: exponential moving average, factor 0.3
- [ ] Cursor scaling: sensitivity 10, multiplied by 100
- [ ] Two-hand click: index + middle finger confidence > 0.5
- [ ] Click debounce: 300ms between clicks
- [ ] State tracking: smooth_x/y, last_x/y, tracking_initialized
- [ ] Idle counter: increments each frame with no hands, resets on hands

## Subsystem Status

| Subsystem          | C++ | Rust | Status                                     |
| ------------------ | --- | ---- | ------------------------------------------ |
| Orchestrator       | ✅  | ✅   | Done — compiles, runs, idle counting works |
| V4L2 camera        | ✅  | ⏳   | Not started                                |
| Mock camera        | ✅  | ✅   | Done                                       |
| ML pipeline (stub) | ✅  | ✅   | Done                                       |
| Gesture classifier | ✅  | ⏳   | Stub only                                  |
| uinput output      | ✅  | ⏳   | Stub only                                  |
| Oberon socket      | ❌  | ⏳   | New work                                   |
| Logging output     | ❌  | ✅   | Done — logs mouse events via log::debug    |
| Config system      | ✅  | ⏳   | Not started                                |
| Ring buffer        | ✅  | ⏳   | Not started                                |
| Debug helpers      | ✅  | ⏳   | Not started                                |
