# note-transfer

## Current Progress

You can find the website at <https://note-transfer-gjburke.vercel.app/>

Have a website that has the proper pipelines/structure set up,
but is very bad at transferring written notes to markdown.
It still needs a lot of work on model training and fine-tuning, but
the structure around the models is set up for them to be usable
(with some more polish, checks, and testing needed of course).

The current note transfer pipeline looks like this, with a scanned note as input:

1. **Segmentation**
   1. **Larger Sections** - Segments into the larger "sections" of notes, essentially what is separated by whitespace (header and section classes)
   2. **By Line** - Segments by line, detecting what is written: bullet points, text, and figures (coming soon).
2. **Parse Segmentation Structure** - Organizes the segmentations into a tree structure
3. **Text Recognition** - Reads all of the text portions of the document
4. **Conversion to Markdown** - Reads the tree structure and converts it to markdown

The markdown output is then displayed to the user, where they can copy it.

Tech Stack

- Frontend: Svelte, TypeScript, Tailwind
- Backend: Python, FastAPI, Uvicorn, Docker
- Modelling: Ultralytics YOLO, HuggingFace, Microsoft TrOCR

Next Focus

- Ability to parse pages in multi-page context
- Better handwriting detection, training on top of the base model from Microsoft
- Better sectioning: more data, labelling, training, testing for the YOLO models

Future Plans

- Want to get the models good enough that it makes relatively few mistakes
- Refine the backend structure so that it's more flexible
- Substitute my traditional models with multi-modal LLM(s), learn to build a "harness" around it for essentially one-shotting this problem

## Initial Plans

Looking to build a (website/app/?, not totally sure, probably a website) that can transfer by notes from paper to digital (probably markdown). It'll be able to not only read the text, but also structure it in the same/similar way as one paper, as well as take any drawn elements.

I know I'll need some sort of text-recognition model, but about formatting and things like that I'm not sure. I wonder if there's models out there that already can do all of this in one step, but honestly I'd like to build my own pipeline. So I'm considering running a pass through to detect the formatting (segmentation of notes based on format?) and then for each of those pieces you run the writing to text. From there, based on the formatting and received text, you would be able to generate templetted markdown.

Some problems that I'm thinking about right now that are just coming up:

- Ordering of each segmented components
- The speed of all of this (lots of models)
- Incorporating drawings straight from textbook (even text-labelled ones)
- Incorporating math equations and things like that, some LaTex insert or markdown equivalent?

The tech stack I'm thinking of right now:

- Relatively Lightweight Frontend: Svelte, Tailwind
- Backend: Python, FastAPI Now thats not really many technologies and I'm sure that it'll expand as I discover what I want this to be like.
