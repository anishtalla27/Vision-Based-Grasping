import pathlib
p=pathlib.Path("preprint.tex"); s=p.read_text(); misses=[]
def rep(a,b):
    global s
    if a in s: s=s.replace(a,b,1)
    else: misses.append(a[:60])
# ---- Introduction
rep("exactly why it is tempting, and exactly why it deserves to be measured\nrather than assumed.",
    "the reason it is tempting. It is also the reason it should be measured\nbefore it is trusted.")
rep("Comparisons across those three families are rarer than you might\nexpect.",
    "Comparisons across those three families are rare.")
rep("That produces useful leaderboards but does not tell you what you gain\nor give up by changing approach entirely.",
    "That produces useful leaderboards, but it does not show what is gained\nor lost by changing approach entirely.")
rep("The question is plain. Which approach actually works, and where does\neach one break down? The second half matters at least as much as the\nfirst. An accuracy number tells you a system is wrong. The shape of its\nerrors tells you why, and that is the part that transfers to whatever\nsomebody builds next.",
    "I ask two questions. Which approach works, and where does each one\nbreak down? I treat the second question as equal to the first, because\nan accuracy number only says that a system was wrong, while the pattern\nof its errors points to a cause that the next designer can act on.")
rep("The measuring apparatus is borrowed rather than invented, which matters\nmore than it might seem.",
    "The measuring apparatus is borrowed, not invented, and that choice was\ndeliberate.")
rep("One thing this paper is not. It does not beat state-of-the-art grasp\ndetection and does not try to.",
    "This paper does not try to beat state-of-the-art grasp detection.")
rep("What it does establish can be stated plainly. The three systems ran on",
    "What the paper does establish is the following. The three systems ran on")
# ---- Methods and discussion
rep("which is exactly what System C is built to test.", "which is what System C is built to test.")
rep("object's mask; principal component analysis of that mask gives its", "object's mask, and principal component analysis of that mask gives its")
rep("segmentation mask and so no candidates; they count as misses for", "segmentation mask and so no candidates. They count as misses for")
rep("It still beat GPT-4o\n(System C) by 11 points, which I did not expect.", "It still beat GPT-4o\n(System C) by 11 points, which I did not expect to see.")
# ---- Limitations
rep("This test was limited to using a single split of the dataset relative\nto the five-fold cross-validation that is used by most published\nresults using the Cornell dataset.",
    "This study used a single split of the dataset, whereas most published\nCornell results use five-fold cross-validation.")
rep("so the results for\nthose objects are not as precise as they could be.", "so the results for\nthose objects are imprecise.")
rep("not steer any choice, but two openings are still two. The round-1\nnumbers rest on one seed each; the round-2 numbers on three. Jacquard, considered\nas a second dataset source, was unavailable during this study, so no\nresults were performed to test the generalization of these techniques\nacross datasets.",
    "not steer any choice, but it remains a second opening. The round-1\nnumbers rest on one seed each and the round-2 numbers on three. Jacquard,\nwhich I considered as a second dataset, was not available to me during\nthis study, so generalization across datasets was not tested.")
rep("The three systems did not receive comparable engineering effort, which\ncuts against reading this as a controlled comparison.",
    "The three systems did not receive comparable engineering effort, which\nweakens any reading of this as a fully controlled comparison.")
rep("System C's potential contamination by the dataset was examined. While\nthe dataset is a publicly available dataset that is mirrored by many\norganizations, a test of ten images of objects of various categories\nasked the language model to identify the source of the images returned\nno recognitions. This is a weak indicator of contamination of the model\nby the dataset, but contamination of the language model would only have\nled to an increase in System C's score, which is already the lowest of\nthe three systems. So the failure of System C in comparison to the\nother models holds even in the worst-case scenario of contamination of\nthe model by the dataset.",
    "I checked whether GPT-4o might have seen the dataset during training.\nCornell is public and widely mirrored, so this is possible. When asked\nto name the source of ten test images from different object categories,\nthe model recognized none of them. That is weak evidence against\ncontamination. Contamination could only have raised System C's score,\nwhich is already the lowest of the three, so its ranking holds even in\nthe worst case.")
rep("Every interval and significance test reported here treats its unit of\nanalysis as independent, and none of them are.",
    "Every image-level and call-level interval and significance test reported\nhere treats its unit of analysis as independent, and these units are\nnot independent.")
rep("The findings of the results relative to the orientation of the objects\nwas based on a sample size of only 20 objects. Additionally, the other\nfindings of this test were made of one model, one method of posing the\nquestion to that model, and the one aspect of the task of grasping that\nis examined, the coordinates of the grasp, so these results describe\nthat one setup rather than vision-language models generally.",
    "The orientation analysis rests on only 20 diagonal images. The\nvision-language results come from one model and one way of posing the\nquestion, so they describe that setup and should not be extended to\nvision-language models in general.")
rep("All of the inputs to the models used in this test were images in RGB\nformat only. No depth information from the objects was used as an input\nto any of the tested models.",
    "Every system received RGB images only. No depth information was used\nby any of them.")
# ---- Results
rep("single-seed figure; the three-seed round-2 figure is 84.0 [73.9,", "single-seed figure, and the three-seed round-2 figure is 84.0 [73.9,")
rep("close to some valid orientation on the image; the second says how", "close to some valid orientation on the image. The second says how")
rep("splits; the second round below shows that gap was noise.", "splits. The second round below shows that gap was noise.")
rep("a 24.6\\% random floor; with every mark the same size, 22.3\\% against", "a 24.6\\% random floor. With every mark the same size it scored 22.3\\% against")
p.write_text(s); print("misses:",misses)
