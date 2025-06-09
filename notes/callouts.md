Callouts are Obsidian’s “fancy block-quotes.” By prefixing a block with a special marker like > [!note], you get a colored panel with an icon, optional title, collapsible toggle, and full Markdown support. They’re ideal for emphasizing tips, warnings, FAQs, summaries, or anything you want to tuck away without breaking the flow of a note. Below is an end-to-end guide—syntax, folding behavior, available types, CSS tweaks, and a handful of real-world examples—so you can start sprinkling callouts through your vault with confidence.

⸻

1 · Anatomy of a Callout

> [!info] Quick heads-up
> This block accepts **Markdown**, [[wikilinks]], images, embeds, and more.

	•	info is the type identifier that sets the color and icon.
	•	Anything after the brackets becomes an optional title line.
	•	Every following > line is the body of the callout. It renders just like ordinary Markdown.

Use callouts when you need to highlight or hide supplementary material—summaries, key take-aways, small print, or contextual asides.

⸻

2 · Supported Types & Aliases

Obsidian ships with a dozen+ built-ins (aliases in parentheses):

Purpose	Syntax
Neutral note	[!note]
FYI / abstract	[!abstract] (summary, tldr)
Information	[!info]
Tip / hint	[!tip] (hint, important)
Success	[!success] (check, done)
Question	[!question] (help, faq)
Warning	[!warning] (caution, attention)
Danger / error	[!danger] (error)
Failure / missing	[!failure] (fail)
Example	[!example]
Quote	[!quote] (cite)


⸻

3 · Folding & Default State

Add a plus (+) or minus (-) directly after the type identifier:

> [!tip]+ Always open, but collapsible
> Helpful details live here…

> [!warning]- Starts collapsed
> Proceed with caution!

	•	+ → expanded on load, but users can fold it.
	•	- → collapsed on load.
Reddit users confirm the same rule of thumb.

Note: There’s currently no core command to “collapse all callouts” at once; forum contributors suggest it would require a community plugin or manual folding. ￼

⸻

4 · Nesting & Mixed Content

Callouts can nest indefinitely:

> [!question] Can I nest?
> > [!todo]- Absolutely
> > > [!example] Even three levels!

Nested blocks inherit folding toggles and accept every kind of Markdown, including images and embeds.  Collapsed callouts hide embedded images until opened—occasionally leading to render quirks reported on the forum.

Outliner-style bullet folding still works inside a callout, though the click-target is slightly offset.

⸻

5 · Creating Callouts Quickly
	•	Command palette: press ⌘/Ctrl + P → “Insert callout” to scaffold > [!note] Title for you.
	•	Autocomplete: typing > then [! shows a dropdown of available types in the default theme.

⸻

6 · Customizing Look & Feel

6.1 CSS Snippets

Drop a .css file in .obsidian/snippets/, enable it in Settings → Appearance, and target callouts by their data-callout attribute:

/* Lavender “idea” callout */
.callout[data-callout="idea"] {
  --callout-color: 150, 125, 255;      /* R,G,B */
  --callout-icon: lucide-lightbulb;    /* any Lucide icon or inline SVG */
}

Now you can write:

> [!idea] Bright thought
> Record your eureka moments here…

6.2 Parameterized or Themed Variants

Community snippets show how to vary color or padding with additional keywords—e.g., [!customcallout|purple]—by reading the attribute in CSS.

⸻

7 · Gotchas & Work-arounds

Issue	Work-around / Status
Callout won’t fold	Make sure you used + or - after the type and that you’re on Obsidian 1.4 +.
Want one-click “collapse all”	Not built in; requires plugin or manual folding. ￼
Custom icons/titles	Hide default icon and inject emoji/SVG via CSS.


⸻

8 · Quick Reference Examples

> [!abstract]- TL;DR
> Three-line executive summary.

> [!question] Frequently Asked
> **Q:** Where are my files?<br>
> **A:** In your vault folder.

> [!danger]- Heads-up!
> Deleting this folder is irreversible.


⸻

Bottom line

Callouts are a flexible, zero-plugin way to add structure, emphasis, and toggleable detail to your notes. Master the [!type], the optional + / -, and a sprinkle of CSS, and you can craft anything from collapsible revision cards to bright “idea” boxes tailored to your own workflow.