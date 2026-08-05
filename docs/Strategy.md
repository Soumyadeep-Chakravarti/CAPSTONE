---
created: 2026-08-04
modified: 2026-08-04
type: design
tags:
  - projects
  - enki
  - architecture
  - input
status: draft
---

# ENKI Architecture v3 — The Hand State Model

> ENKI does not recognize gestures.
>
> ENKI understands hands.

---

## Philosophy

Most hand-tracking systems are built around one question:

> "What gesture is the user making?"

That is too limiting.

A gesture is not fundamental.

A **hand** is.

ENKI should understand the hand as a fully articulated mechanical system and expose that understanding to applications.

Gesture recognition then becomes one possible consumer of that data.

---

## The Core Idea

The camera is only the sensor.

TensorFlow Lite is only the detector.

Neither of these are ENKI.

ENKI begins **after landmark detection**.

Instead of thinking:

```text
Camera
    ↓
Gesture
```

Think:

```text
Camera
    ↓
Skeleton
    ↓
Hand State
    ↓
Applications
```

---

## The Pipeline

```mermaid
---
title: ENKI Processing Pipeline
config:
  layout: elk
---
flowchart LR

    Camera["Camera"]
    Capture["Frame Capture<br/>(v4l2 / libcamera)"]
    Palm["Palm Detection<br/>(TensorFlow Lite)"]
    Landmarks["Hand Landmark Detection<br/>(TensorFlow Lite)"]

    subgraph Core["ENKI Core"]
        Skeleton["Skeleton Builder"]
        Kinematics["Kinematics & Geometry"]
        HandState["HandState API"]
    end

    Gesture["Gesture Engine"]
    Uinput["uinput"]
    Oberon["Oberon Socket"]

    Camera --> Capture
    Capture --> Palm
    Palm --> Landmarks
    Landmarks --> Skeleton
    Skeleton --> Kinematics
    Kinematics --> HandState

    HandState --> Gesture
    HandState --> Uinput
    HandState --> Oberon

    classDef input fill:#fff7ed,stroke:#fb923c,stroke-width:2px;
    classDef core fill:#eef2ff,stroke:#6366f1,stroke-width:2px;
    classDef output fill:#ecfeff,stroke:#06b6d4,stroke-width:2px;

    class Camera,Capture,Palm,Landmarks input;
    class Skeleton,Kinematics,HandState core;
    class Gesture,Uinput,Oberon output;
```

The neural network only tells us where the joints are.

Everything after that is deterministic geometry.

---

## Layer 1 — Skeleton

The first internal representation is nothing more than an articulated skeleton.

```mermaid

flowchart LR
    Wrist((Wrist))

    subgraph Thumb["Thumb"]
        direction LR
        ThumbBase((Base)) --> ThumbMiddle((Middle)) --> ThumbTip((Tip))
    end

    subgraph Index["Index finger"]
        direction LR
        IndexBase((Base)) --> IndexMiddle1((Joint 1)) --> IndexMiddle2((Joint 2)) --> IndexTip((Tip))
    end

    subgraph Middle["Middle finger"]
        direction LR
        MiddleBase((Base)) --> MiddleMiddle1((Joint 1)) --> MiddleMiddle2((Joint 2)) --> MiddleTip((Tip))
    end

    subgraph Ring["Ring finger"]
        direction LR
        RingBase((Base)) --> RingMiddle1((Joint 1)) --> RingMiddle2((Joint 2)) --> RingTip((Tip))
    end

    subgraph Pinky["Pinky finger"]
        direction LR
        PinkyBase((Base)) --> PinkyMiddle1((Joint 1)) --> PinkyMiddle2((Joint 2)) --> PinkyTip((Tip))
    end

    Wrist --> ThumbBase
    Wrist --> IndexBase
    Wrist --> MiddleBase
    Wrist --> RingBase
    Wrist --> PinkyBase

    classDef wrist fill:#fdf4ff,stroke:#e879f9,stroke-width:3px,color:#701a75;
    classDef thumb fill:#fff7ed,stroke:#fb923c,stroke-width:2px,color:#7c2d12;
    classDef index fill:#eef2ff,stroke:#818cf8,stroke-width:2px,color:#312e81;
    classDef middle fill:#f0fdfa,stroke:#2dd4bf,stroke-width:2px,color:#134e4a;
    classDef ring fill:#f0f9ff,stroke:#38bdf8,stroke-width:2px,color:#0c4a6e;
    classDef pinky fill:#f0fdf4,stroke:#4ade80,stroke-width:2px,color:#14532d;

    class Wrist wrist;
    class ThumbBase,ThumbMiddle,ThumbTip thumb;
    class IndexBase,IndexMiddle1,IndexMiddle2,IndexTip index;
    class MiddleBase,MiddleMiddle1,MiddleMiddle2,MiddleTip middle;
    class RingBase,RingMiddle1,RingMiddle2,RingTip ring;
    class PinkyBase,PinkyMiddle1,PinkyMiddle2,PinkyTip pinky;
```

Each landmark becomes a joint.

Each connection becomes a bone.

No gestures.

No clicks.

No mouse movement.

Only structure.

---

## Layer 2 — Kinematics

The skeleton alone is just points.

The next layer derives meaningful physical information.

Examples include:

- joint angles
- bone lengths
- fingertip velocity
- fingertip acceleration
- wrist orientation
- palm normal
- hand velocity
- angular velocity
- confidence values

This layer is pure mathematics.

It knows nothing about applications.

---

## Layer 3 — Hand State

This is where geometry becomes semantics.

Instead of exposing only raw landmarks, ENKI builds a semantic description of the hand.

Example:

```rust
pub struct HandState {
    pub wrist: Pose,

    pub thumb: FingerState,
    pub index: FingerState,
    pub middle: FingerState,
    pub ring: FingerState,
    pub pinky: FingerState,

    pub palm_normal: Vec3,
    pub hand_velocity: Vec3,

    pub confidence: f32,
}
```

Each finger contains higher-level information.

```rust
pub struct FingerState {
    pub joints: [Joint; 4],

    pub curl: f32,
    pub spread: f32,

    pub velocity: Vec3,

    pub extended: bool,
}
```

Applications no longer need to calculate angles themselves.

ENKI already understands the hand.

---

## Layer 4 — Gesture Engine

Gestures are NOT the foundation.

They are built on top of HandState.

Instead of analyzing camera frames, the gesture engine simply asks questions.

```text
Is the index finger extended?

Is the thumb touching the index finger?

Is the palm facing upward?

Is the hand stationary?
```

A pinch becomes

```rust
thumb.tip.distance(index.tip) < PINCH_DISTANCE
&& index.extended
```

A fist becomes

```rust
all_fingers.curled()
```

A peace sign becomes

```rust
index.extended
&& middle.extended
&& ring.curled
&& pinky.curled
```

The gesture engine is therefore small, deterministic, and easy to extend.

---

## Why This Matters

Traditional systems collapse an entire hand into one label.

```text
Open Hand

Peace

Fist

Thumbs Up
```

This throws away nearly all available information.

ENKI keeps the complete hand model available.

Applications are free to decide what "gesture" means.

---

## Multiple Consumers

The Hand State is the central API.

Everything else becomes a consumer.

```mermaid

flowchart LR
    HandState(["HandState API"]) --> Gesture(["Gesture Engine"])
    Gesture -->|Virtual input events| UInput(["uinput"])
    Gesture -->|Gesture messages| Oberon(["Oberon socket"])

    UInput -->|Mouse and keyboard events| Legacy
    Oberon -->|Native integration| Blender
    Oberon -->|Native integration| CAD
    Oberon -->|Assistive controls| Accessibility

    subgraph Applications["Target applications"]
        direction TB
        Legacy(["Legacy applications"])
        Blender(["Blender"])
        CAD(["CAD"])
        Accessibility(["Accessibility tools"])
    end

    classDef api fill:#eef2ff,stroke:#818cf8,stroke-width:2px,color:#312e81;
    classDef engine fill:#f5f3ff,stroke:#a78bfa,stroke-width:2px,color:#4c1d95;
    classDef transport fill:#f0fdfa,stroke:#2dd4bf,stroke-width:2px,color:#134e4a;
    classDef application fill:#ecfeff,stroke:#22d3ee,stroke-width:1.5px,color:#164e63;
    classDef group fill:#f8fafc,stroke:#94a3b8,stroke-width:1.5px,stroke-dasharray:4 4,color:#334155;

    class HandState api;
    class Gesture engine;
    class UInput,Oberon transport;
    class Legacy,Blender,CAD,Accessibility application;
    class Applications group;
```

This allows different applications to use the same tracking data in different ways.

---

## Why Not Output Gestures Directly?

Suppose Blender wants to rotate a model based on wrist orientation.

A gesture system can only say

```text
Rotate
```

A Hand State can say

```text
Palm normal

Wrist quaternion

Finger curl

Thumb position

Angular velocity
```

The Blender plugin can implement its own controls.

No changes to ENKI are required.

---

## Relation to Linux Philosophy

Linux input devices expose events.

They do not expose intentions.

A keyboard reports

```text
KEY_A
```

not

```text
User is writing an email.
```

Likewise, ENKI should expose the hand.

Not assumptions about the user's intent.

The gesture engine is simply one interpreter of the hand state.

---

## Frame Rates

Different parts of the pipeline operate at different rates.

| Stage              | Recommended Rate         |
| ------------------ | ------------------------ |
| Camera Capture     | 30 FPS                   |
| Landmark Detection | 30 FPS                   |
| Skeleton Update    | 30 FPS                   |
| Hand State Update  | 30 FPS                   |
| Gesture Engine     | 5–15 FPS or Event Driven |
| uinput Cursor      | 60+ Hz interpolation     |
| Oberon Socket      | Configurable             |

Cursor movement requires continuous updates.

Gestures do not.

This separation reduces CPU usage while maintaining responsiveness.

---

## Future Possibilities

Once ENKI produces a reliable Hand State, entirely new capabilities become possible.

- Continuous finger tracking
- Custom gesture languages
- Gesture recording and playback
- Per-application gesture mappings
- Accessibility input systems
- CAD manipulation
- Blender sculpting
- Robotics control
- Remote hand streaming
- VR/AR integrations
- Sign language research
- Multi-hand collaboration

None of these require changes to the tracking pipeline.

Only new consumers.

---

## Design Principle

ENKI is **not** a gesture recognizer.

ENKI is a **hand understanding engine**.

Everything else is built on top of that.

---

## The Final Architecture

```mermaid
flowchart LR

    Camera["Camera"]
    Capture["Frame Capture<br/>(v4l2 / libcamera)"]
    Palm["Palm Detection<br/>(TensorFlow Lite)"]
    Landmarks["Hand Landmark Detection<br/>(TensorFlow Lite)"]

    subgraph Core["ENKI Core"]
        direction TB

        Skeleton["Skeleton Builder"]
        Kinematics["Kinematics & Geometry"]
        HandState["HandState API"]

        Skeleton --> Kinematics
        Kinematics --> HandState
    end

    Gesture["Gesture Engine"]
    UInput["uinput"]
    Oberon["Oberon Socket"]

    subgraph Consumers["Consumers"]
        direction LR

        Desktop["Desktop Applications"]
        CAD["CAD / Blender"]
        Accessibility["Accessibility"]
    end

    Camera --> Capture
    Capture --> Palm
    Palm --> Landmarks
    Landmarks --> Skeleton

    HandState --> Gesture
    HandState --> UInput
    HandState --> Oberon

    Oberon --> Desktop
    Oberon --> CAD
    Oberon --> Accessibility

    classDef input fill:#fff7ed,stroke:#fb923c,stroke-width:2px,color:#431407;
    classDef core fill:#eef2ff,stroke:#6366f1,stroke-width:2px,color:#1e1b4b;
    classDef output fill:#ecfeff,stroke:#06b6d4,stroke-width:2px,color:#083344;
    classDef consumer fill:#f0fdf4,stroke:#22c55e,stroke-width:2px,color:#14532d;
    classDef group fill:#f8fafc,stroke:#94a3b8,stroke-dasharray:4 4;

    class Camera,Capture,Palm,Landmarks input;
    class Skeleton,Kinematics,HandState core;
    class Gesture,UInput,Oberon output;
    class Desktop,CAD,Accessibility consumer;
    class Core,Consumers group;
```

---

## One Sentence Mission

> ENKI transforms camera input into a high-fidelity, semantic representation of the human hand, providing Linux with a universal, hardware-agnostic hand input layer upon which gestures, applications, and future interaction models can be built.
> ↗ Up: [ENKI](ENKI.md)

## See also

- [[Design|ENKI — Design Iterations]]
- [[Architecture|ENKI Architecture v2 — The Two-Layer Split]]
