# Posting the preprint

Files: `preprint.pdf` (24 pages) for TechRxiv or Zenodo, `arxiv_source.tar.gz` (LaTeX plus three figures, builds standalone) for arXiv.

## Where to post
1. TechRxiv (recommended). Free IEEE account, no endorsement, moderators approve in a few days, gives a DOI. https://www.techrxiv.org/submit
2. Zenodo (fastest). Sign in with GitHub, upload the PDF, DOI is issued at once. It can also archive the GitHub repo. https://zenodo.org/uploads/new
3. arXiv. New authors need an endorsement for cs.RO or cs.CV from someone who has published there, so this one depends on finding an endorser (a professor who replies to your email can do it). https://arxiv.org/submit

## Metadata to paste

Title:
Three Ways to Miss a Grasp: A Same-Metric Comparison of Rule-Based, Learned, and Zero-Shot Vision-Language Grasp Prediction, and a Test of Why the Language Model Fails

Author: Anish Talla (Lightridge High School and Academies of Loudoun, Virginia, USA), anish.talla99@gmail.com

Abstract (1,423 characters, under arXiv's 1,920 limit):
A robot cannot pick anything up until something decides where to place the fingers and at what angle. That decision can come from hand-written rules, from a model trained on labeled grasps, or from a general-purpose vision-language model never trained on grasping. I built one system of each kind and scored all of them with one implementation of the Cornell rectangle metric on the same held-out split of 123 images of 35 unseen objects. A fine-tuned ResNet passed on 84.0% of test images averaged over three seeds, a detector-plus-lookup-table heuristic on a post-hoc-corrected 57.7% (40.7% before the correction), and GPT-4o on 12.4% of 615 calls. Object-clustered resampling left the order unchanged. The three systems failed differently, and GPT-4o placed its grasp center outside the region spanned by all labeled grasps on 53.4% of calls, against about 7% for the others, which suggested it could see a grasp but not express it as coordinates. A fourth experiment tested that reading by showing the same model label-free candidate grasps drawn on the image and asking it to choose one by number. On three candidate menus, including one with every mark drawn the same size, its accuracy stayed at the random floor of the menu, and it kept preferring an end pinch along the object's long axis. The failure is in the grasp choice, not in emitting coordinates. Code, the data split, and every raw model reply are public.

Keywords: robotic grasping, Cornell Grasping Dataset, vision-language models, GPT-4o, Set-of-Mark prompting, zero-shot evaluation, clustered bootstrap

arXiv categories: primary cs.RO, cross-list cs.CV and cs.AI
TechRxiv category: Computing and Processing, then Robotics and Control Systems
Comments field: 24 pages, 6 figures, 7 tables. Code and data: https://github.com/anishtalla27/Vision-Based-Grasping
License: CC BY 4.0
Funding: none. Conflicts of interest: none.
Related submissions to declare if asked: a five-page version is under review at the IEEE BigData 2026 High School Symposium (preprints are allowed there), and a short version was sent to the Columbia Junior Science Journal.
