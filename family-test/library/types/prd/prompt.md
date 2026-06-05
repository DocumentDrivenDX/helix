# PRD authoring prompt

You are drafting a Product Requirements Document. Produce the sections listed
in `meta.yml.required_sections`, in order. Each section must be substantive;
"TBD" is not acceptable in any section.

Linkages: declare downstream edges (FEAT, test-plan, principles) in instance
frontmatter under `ddx.links:`. Do not embed those linkages in this template
or in prose; that's the methodology graph's job.
