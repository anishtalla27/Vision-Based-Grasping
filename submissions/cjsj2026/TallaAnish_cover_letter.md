19 September 2026

To the editors of the Columbia Junior Science Journal,

I am a senior at Lightridge High School and the Academies of Loudoun in Virginia, and I am submitting my original research paper, "Three Ways to Miss a Grasp: Comparing Rules, a Trained Network, and GPT-4o on the Same Robot Grasping Test," for the 2026-27 volume.

The paper asks how a robot should decide where to grasp an object when all it has is one color photo. I built three systems that answer that question in different ways (hand-written rules, a fine-tuned ResNet, and GPT-4o with no grasp training) and scored them on the same held-out objects from the Cornell Grasping Dataset with the same code. The trained network got 84.0% of test images right, the rules 57.7%, and GPT-4o 12.4% of its calls. GPT-4o's mistakes looked like a problem with writing pixel coordinates, so I ran a fourth experiment where it only had to pick a numbered grasp drawn on the image. It still did no better than chance. I think that result is the most useful part of the paper, because it shows the problem is in how the model judges a grasp and not in how it reports one.

Your guidelines ask for disclosure of AI use, and there are two kinds here. First, GPT-4o (openai/gpt-4o through the OpenRouter API, default temperature) is the thing being tested. Its exact prompts are printed in the paper's appendix. Second, I used Anthropic's Claude Code between July and September 2026 as a coding and writing assistant. It helped me write and debug the Python code, made a first pass at sorting photos by object, which I then checked by hand, and helped draft and edit the text. OpenAI Codex helped shorten an earlier version. The research question, the experimental design, the decisions along the way, and the checking of every number are mine. The same disclosure is in the Acknowledgment.

I should also tell you that a five page conference version of this work was submitted to the IEEE ICDM 2026 Teen Research Symposium on 30 August 2026. [Before sending: add one sentence with the ICDM decision, and mention the IEEE BigData High School Symposium if you submit there.] If another venue accepts the work, I will let you know right away, as your FAQ asks.

I worked without a research mentor, so the mentor fields on the Permission to Publish form are marked N/A, which your FAQ allows. The files are TallaAnish_paper.docx, TallaAnish_figures.pptx, and TallaAnish_form.pdf.

Thank you for reading it.

Anish Talla
Lightridge High School and Academies of Loudoun, Class of 2027
anish.talla99@gmail.com
