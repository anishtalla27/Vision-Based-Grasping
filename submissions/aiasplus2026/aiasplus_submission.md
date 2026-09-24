# AIAS+ 2026 Student Poster Showcase, registration form content

Form: https://www.aiasplus.org/call-for-student-posters-form
Deadline: 18 September 2026. Notification: 5 October 2026.
Student participation is free; the chaperone fee is shown on the form.

## Project title

Can a Vision-Language Model Choose Where to Grasp? A Same-Metric Test of GPT-4o Against Rule-Based and Learned Robot Grasp Prediction

## Abstract (250 words max; this one is exactly 250)

Before a robot can pick anything up, something must decide where the fingers land and at what angle. That decision can come from hand-written rules, from a neural network trained on labeled grasps, or from a general-purpose vision-language model that has never seen a grasping dataset. I built one system of each kind and scored all three on the same 123 held-out images of 35 unseen household objects from the Cornell Grasping Dataset with one implementation of the standard rectangle metric. A fine-tuned ResNet passed on 84.0% of images averaged over three training seeds. A detector-plus-lookup-table heuristic passed on 57.7%. GPT-4o, asked for fingertip coordinates and sampled five times per image, passed on 12.4% of calls. The three failed differently. The heuristic could not express diagonal grasps, the network usually got the angle and missed the placement, and GPT-4o placed its grasp center outside the region spanned by every labeled grasp on 53% of calls, against about 7% for the other two. That suggested the model could see the grasp but not write it as coordinates. A fourth experiment tested this: the same model was shown label-free candidate grasps drawn on the image and asked to pick one by number. On three menus, one with every mark drawn the same size, its accuracy stayed at the menu's random floor, and it kept preferring an end pinch along the object's long axis, which looks narrow from above but is not. The failure is in the grasp choice, not in emitting coordinates.

## Why this project matters (optional statement, about 120 words)

Vision-language models are being wired into robots quickly because prompting one costs almost nothing compared with collecting a labeled dataset. Most published systems that use them hand the final geometry to something else, so the model's own spatial judgment is rarely isolated and measured. This project measures it under the same test as two conventional systems, samples the model enough times to see its own variance, and then runs the experiment that the obvious explanation calls for. The explanation turned out to be wrong: taking away the coordinate output did not help. Knowing that a general model reasons poorly about grasps from a single top-down view, rather than merely struggling to express them, tells engineers where the next fix belongs, likely in depth input or a stronger three-dimensional prior.

## Form fields

- Student: Anish Talla, grade [GRADE], [SCHOOL NAME], [CITY, STATE]
- Team: solo
- Chaperoning adult: [NAME], [relationship: parent / teacher / mentor], [EMAIL], [PHONE]
- Poster theme: AI for Science (machine learning for robotics)

## Poster plan (only needed if accepted; vertical/portrait, printed)

Sections in order: motivation (one paragraph, the three ways to decide a grasp), methods (shared split, shared metric, four systems in one diagram), results (accuracy bar chart with object-clustered intervals; failure taxonomy table; the center-outside-hull numbers), the System D test (one marked test image, the three-menu table, floor and ceiling), next steps (depth input, 3-D prior, robot trials). Headline numbers on the poster: 84.0 / 57.7 / 12.4, then 53% vs 7%, then 18.7% vs 20.1% floor.
