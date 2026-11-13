# Practice Guide generation prompt

Write a guide to one practice for the people responsible for a system. The first reader owns or sponsors the
system and is not a specialist in the practice. The others are the four reader views: Risk & Compliance,
Finance, IT Operations and Apps Dev.

Write a guide only for a practice that no technology assessment covers. Where an assessment covers the subject,
explain the practice at the front of that assessment, so that a reader is handed one document per subject and
the advice is stated once.

Work in this order.

1. Gather the evidence first, in notes kept outside the guide: what each public source says, and whether a
   benefit is argued, reported from use, or measured. A guide is not the place for that record.
2. Write the guide from those notes, to the template. Say only what the notes support. Where the support is
   reasoning, write the reasoning. State no measured effect that nobody measured.
3. Put no citation, link, source list, document identifier or repository path in the guide, and no word about
   how it was researched, reviewed or built.
4. Use the `human-facing` voice (`workflows/voice.yml`) and the writing pass
   (`workflows/references/writing-pass.md`). Open with the point: two sentences on what the practice is and what
   teams use it for. Never open by describing the reader or the guide. Speak to the reader as "you" and "your
   team".
5. Write connected paragraphs under plain headings. A guide written as slogans reads as machine-made: avoid a
   bold phrase followed by a clipped sentence, one-line paragraphs for effect, and "X, not Y". Bold a term only
   where it is defined. Keep lists for the steps and the questions.
6. In Reference setup, name what to stand up: what the application does, the shared service the organization
   runs, and where the result ends up. Say what the shared service buys and what it costs, and give the smallest
   version a single team can start with. Name a product only as an example of a kind of tool, with a clause
   saying what it is. A choice between products belongs in a technology assessment.
7. In Views, answer each of the four readers' first question as it applies to this practice, under the headings
   Risk & Compliance, Finance, IT Operations and Apps Dev. Say Not applicable, with the reason, where one does
   not arise.
8. Aim for about 1,000 words. Render the guide and read every page before showing it to anyone.
