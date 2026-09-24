# Supplement: exact prompts used for GPT-4o (Systems C and D)

Model: openai/gpt-4o via OpenRouter, default temperature, no seed, 400-token cap for System C. Prompts were developed on 30 training images and frozen before the test split was called.

## System C, prompt version v1 

### System message

```
You are a robotic grasping assistant. You are shown a photograph from a fixed camera mounted above a table, and you decide where a two-fingered parallel-jaw gripper should close on the object in the photograph. You reply with a single JSON object and no other text.
```

### User prompt

```
This is a 640 x 480 RGB photograph of one object resting on a table,
taken from a fixed camera looking down at it. A two-fingered parallel-jaw
gripper will descend vertically and close on the object.

Decide where the two fingertips should make contact.

Coordinates are in pixels of this 640 x 480 image. x runs from 0 at the
left edge to 639 at the right edge. y runs from 0 at the top edge to 479
at the bottom edge. Report whole numbers.

Reply with exactly one JSON object and nothing else:

{
  "object": "<two or three words naming the object>",
  "reasoning": "<one sentence: which part of the object you are grasping, and why>",
  "finger_a": [x, y],
  "finger_b": [x, y],
  "jaw_width_px": <integer>,
  "force": "<low|medium|high>",
  "confidence": "<low|medium|high>"
}

Rules:
- finger_a and finger_b are the two points where the fingertips touch the
  object. The gripper closes along the line between them, so they must be
  on OPPOSITE sides of the part you are grasping. Do not put both points
  at the object's centre, and do not put both on the same side.
- The distance between finger_a and finger_b is how far the jaws open. It
  must be wider than the part being grasped and no more than 150 pixels.
- jaw_width_px is how much of the object the flat face of one fingertip
  covers, measured perpendicular to the closing direction. Usually 15 to 40.
- Grasp the object itself. Do not place a fingertip on the table, on the
  background, or on the object's shadow.
- If more than one grasp would work, choose the one most likely to hold:
  across a narrow part of the object, close to its centre of mass.
```

## System D, prompt version v2 

### System message

```
You are a robotic grasping assistant. You are shown a photograph of one object on a table, taken from a camera above it, with several candidate grasps drawn on the object as numbered coloured lines. You choose one candidate. You reply with a single JSON object and no other text.
```

### User prompt (full and sparse menus)

```
This photograph shows one object on a table, zoomed in. A two-fingered
parallel-jaw gripper will descend vertically and close on the object.

{k} candidate grasps are drawn on the image, each in its own colour with
a numbered circle beside it. Each candidate shows the gripper's two
fingertips as two short THICK bars. The thin line joining the two bars
is the direction the fingertips move: the arrowheads on that line point
inward, and the two fingertips slide toward each other along it until
they squeeze whatever lies between them. So a candidate grips the part
of the object that lies between its two thick bars.

Choose the candidate most likely to pick the object up and hold it:
usually one whose two bars sit on opposite sides of a narrow part of
the object, near its centre of mass, so that the fingertips squeeze the
object rather than closing on empty table.

Reply with exactly one JSON object and nothing else:

{{
  "object": "<two or three words naming the object>",
  "reasoning": "<one sentence: which part of the object lies between that candidate's two bars, and why it is a good grip>",
  "choice": <the number of the chosen candidate, 1 to {k}>,
  "confidence": "<low|medium|high>"
}}
```

### User prompt (equal-size menu)

```
This photograph shows one object on a table, zoomed in. A two-fingered
parallel-jaw gripper will descend vertically and close on the object.

{k} candidate grasps are drawn on the image, each in its own colour with
a numbered circle beside it. Each candidate shows the gripper's two
fingertips as two short THICK bars. The thin line joining the two bars
is the direction the fingertips move: the arrowheads on that line point
inward, and the two fingertips slide toward each other along it until
they squeeze whatever lies between them. All candidates are drawn at the same length, which is NOT to scale: a mark
shows only where the grip is centred and the direction the fingertips close
along. So a candidate grips the part of the object that the line between
its two bars crosses, at the marked centre.

Choose the candidate most likely to pick the object up and hold it:
usually one whose two bars sit on opposite sides of a narrow part of
the object, near its centre of mass, so that the fingertips squeeze the
object rather than closing on empty table.

Reply with exactly one JSON object and nothing else:

{{
  "object": "<two or three words naming the object>",
  "reasoning": "<one sentence: which part of the object lies between that candidate's two bars, and why it is a good grip>",
  "choice": <the number of the chosen candidate, 1 to {k}>,
  "confidence": "<low|medium|high>"
}}
```

