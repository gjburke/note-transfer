# note-transfer 

## Initial Look 

Looking to build a (website/app/?, not totally sure, probably a website) that can transfer by notes from paper to digital (probably markdown). It'll be able to not only read the text, but also structure it in the same/similar way as one paper, as well as take any drawn elements.

I know I'll need some sort of text-recognition model, but about formatting and things like that I'm not sure. I wonder if there's models out there that already can do all of this in one step, but honestly I'd like to build my own pipeline. So I'm considering running a pass through to detect the formatting (segmentation of notes based on format?) and then for each of those pieces you run the writing to text. From there, based on the formatting and recieved text, you would be able to generate templetted markdown. 

Some problems that I'm thinking about right now that are just coming up:

- Ordering of each segmented components
- The speed of all of this (lots of models)
- Incorporating drawings straight from textbook (even text-labelled ones)
- Incorporating math equations and things like that, some LaTex insert or markdown equivalent?

The tech stack I'm thinking of right now:

- Relatively Lightweight Frontent: Svelte, Tailwind
- Backend: Python, FastAPI Now thats not really many technologies and I'm sure that it'll expand as I discover what I want this to be like. 
