"""Tone pass over preprint_v2.tex (run once, after make_v2.py).

Whitespace-insensitive replacements; prints any pattern that did not match
exactly once and leaves the text unchanged for that pattern.
"""
import pathlib, re, textwrap

F = pathlib.Path(__file__).with_name("preprint_v2.tex")
t = F.read_text()

PAIRS = [
# ---------------------------------------------------------------- introduction
("Every piece of motion that follows depends on that choice being roughly right.",
 "Every subsequent motion depends on that choice being approximately correct."),
("A robot arm can be mechanically excellent and still fail constantly if the component that tells it where to grip is wrong, which makes grasp prediction one of the places where a small accuracy difference turns into a large behavioral difference.",
 "A mechanically capable arm will still fail often if the component that selects the grasp is wrong, so grasp prediction is a stage at which a small difference in accuracy produces a large difference in behavior."),
("It is also a problem that has to be solved from thin information. In most real settings a robot gets a camera image and little else, with no model of the object, no label saying what it is, and no annotation marking the handle.",
 "The decision must also be made from limited information. In most practical settings the robot has a camera image and little else: no model of the object, no label identifying it, and no annotation marking a handle."),
("There are three broadly different ways to make that decision, and they are not variations on a single method. A programmer can write the rule directly, saying that mugs get grasped by the handle and bottles around the neck.",
 "Three broadly different approaches exist, and they are not variations on a single method. A programmer can encode rules directly, for example that a mug is grasped by its handle and a bottle around its neck."),
("Or a general-purpose vision-language model, trained on web text and images and never shown a grasping dataset, can be asked in plain language where to grip. Each is a bet about where the useful intelligence in a robot's perception stack should live, whether in a person's explicit rules, in weights fitted to task-specific data, or in a large model's general knowledge of the world.",
 "Alternatively, a general-purpose vision-language model, trained on web text and images and never shown a grasping dataset, can be asked in natural language where to grip. Each approach places the relevant knowledge in a different part of the perception stack: in a person's explicit rules, in weights fitted to task-specific data, or in a large model's general knowledge."),
("That third option is new enough that the field has not settled how to use it. Foundation models arrived in robotics quickly, and the literature is still working out which parts of a manipulation pipeline they should own.",
 "The third option is recent, and the field has not settled how to use it. Foundation models entered robotics quickly, and the literature has not yet established which parts of a manipulation pipeline they should handle."),
("Prompting a hosted vision-language model needs an API key and almost no setup, which is the reason it is tempting. It is also the reason it should be measured before it is trusted.",
 "Prompting a hosted vision-language model requires only an API key and minimal setup. That convenience makes the approach attractive, and it is also why the approach should be measured before it is relied on."),
("That produces useful leaderboards, but it does not show what is gained or lost by changing approach entirely.",
 "Such benchmarks are useful, but they do not show what is gained or lost by changing approach entirely."),
("This project is a comparison where all three sit on the same test images, produce the same kind of output, and are scored by the same code.",
 "This study places all three on the same test images, requires the same kind of output from each, and scores them with the same code."),
("The measuring apparatus is borrowed, not invented, and that choice was deliberate.",
 "The evaluation protocol is adopted from prior work, and that choice was deliberate."),
("An external answer key was chosen deliberately.",
 "An external ground truth was used for a specific reason."),
("and given no task-specific training whatsoever.",
 "and given no task-specific training."),
("This paper does not try to beat state-of-the-art grasp detection. Published pixel-wise systems reach accuracies this work is not competing with. What this paper does is measure, under conditions held as close to identical as the design allows, how three families of technique fail, and argue that the shape of each failure carries information the accuracy number does not.",
 "This paper does not attempt to improve on state-of-the-art grasp detection, and published pixel-wise systems reach higher accuracies than any system evaluated here. Its aim is to measure, under conditions held as close to identical as the design allows, how three families of technique fail, and to show that the pattern of each failure carries information that the accuracy figure does not."),
("are prior work and are used, not claimed:",
 "are prior work and are used here without any claim of originality:"),
# --------------------------------------------------------------------- methods
("Object identity was the hardest problem in building the split.",
 "Reconstructing object identity was the most difficult step in building the split."),
("which is the error direction this design accepts on purpose.",
 "which is the direction of error this design deliberately accepts."),
("before the detector was found to be boxing background clutter. The guard",
 "before the detector was found to be drawing boxes around background clutter. The guard"),
("since re-rolling malformed content would quietly convert a single-shot baseline into a best-of-N one.",
 "since resampling malformed replies would implicitly convert a single-shot baseline into a best-of-N one."),
("System D is the test that the coordinate-binding reading calls for.",
 "System D tests the coordinate-binding account directly."),
("choice. So the same model was shown the same test images",
 "choice. The same model was therefore shown the same test images"),
("return the number of the one it would use. It never emits a coordinate.",
 "return the number of the one it would use. In this setting the model never emits a coordinate."),
("Two further runs close it.", "Two further runs address it."),
("and System C has no structural position on the question at all.",
 "and System C's design makes no prediction in either direction."),
# --------------------------------------------------------------------- results
("Table~\\ref{tab:summary} collects the headline numbers,",
 "Table~\\ref{tab:summary} collects the main results,"),
("The table was evaluated once at 40.7\\% before the detector was found to be boxing background clutter.",
 "The table was evaluated once at 40.7\\% before the detector was found to be drawing boxes around background clutter."),
("Both figures stay on record.", "Both figures are reported."),
("Neither of these is the headline figure.", "Neither is the primary figure."),
("and every non-parsing call counts as a miss in the headline figure.",
 "and every non-parsing call counts as a miss in the primary figure."),
("Self-agreement carries usable signal.", "Self-agreement carries some usable information."),
("The match with System A's single-prediction 57.7\\% is a coincidence.",
 "The match with System A's single-prediction 57.7\\% is coincidental."),
("images, does not survive: the two are level.",
 "images, is not supported: the two architectures perform equally within noise."),
("so the gain belongs to the menu and not to the model.",
 "so the gain is attributable to the menu and not to the model."),
# ------------------------------------------------------------------ discussion
("System D ran that test, and the prediction failed.",
 "System D ran that test, and the prediction was not borne out."),
("VLAD-Grasp is the comparison that most complicates System C's result, but two things keep it from being a number that can be set directly against 12.4\\%. It does not just ask for a picture instead of a coordinate. It then predicts depth,",
 "VLAD-Grasp is the published result most relevant to System C, but two differences prevent a direct comparison with 12.4\\%. First, it does not only replace a coordinate with a picture. It then predicts depth,"),
("to. It also counts a grasp correct on overlap alone,",
 "to. Second, it counts a grasp correct on overlap alone,"),
("It is also a different model, not the same one, since the current revision of that paper names GPT-5 as its primary model, so it evidences what",
 "The model also differs, since the current revision of that paper names GPT-5 as its primary model, so it shows what"),
("One works and one does not, and the one that works also adds depth,",
 "Only VLAD-Grasp succeeds, and it also adds depth,"),
("System D's failure is specific. On the full menu",
 "System D's failure follows a specific pattern. On the full menu"),
("straddling the end of an elongated object do look like they pinch a narrow part.",
 "straddling the end of an elongated object appear to pinch a narrow part."),
("so none of this is new by itself. Putting a number on that last weakness, on a standard benchmark against two baselines, and then testing the most natural account of it and finding it wrong, is what this experiment adds.",
 "so none of these observations is new in isolation. The contribution of this experiment is to quantify the last weakness on a standard benchmark against two baselines, and then to test the most natural account of it and find it insufficient."),
("A one-million-parameter network built from scratch never learned the task by any reasonable standard, reaching 23.6\\% after",
 "A one-million-parameter network trained from scratch did not learn the task adequately, reaching 23.6\\% after"),
# ----------------------------------------------------------------- limitations
("from that check, but it should be disclosed.",
 "from that check, but it is disclosed here for completeness."),
("So 12.4\\% measures what one un-iterated prompt achieves, not a ceiling for zero-shot GPT-4o.",
 "The 12.4\\% figure therefore measures what a single, un-iterated prompt achieves, and it is not a ceiling for zero-shot GPT-4o."),
# ------------------------------------------------------------------ conclusion
("GPT-4o fails earlier than either.", "GPT-4o fails at an earlier stage than either."),
]


def wrap(s):
    return "\n".join(textwrap.wrap(s, 72, break_long_words=False, break_on_hyphens=False))


missed = 0
for old, new in PAIRS:
    pat = r"\s+".join(re.escape(w) for w in old.split())
    n = len(re.findall(pat, t))
    if n != 1:
        missed += 1
        print(f"[{n} matches] {old[:80]}")
        continue
    t = re.sub(pat, lambda m: wrap(new), t, count=1)

F.write_text(t)
print(f"applied {len(PAIRS) - missed} of {len(PAIRS)}")
