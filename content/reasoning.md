Title: Background Reasoning behind Quickstart Guide
Date: 2024-10-23
Category: Take home

### Meta
Goal
: Motivate developers to try to make their first "does something real" request with Stytch.
: Provide context for an MVP using Stytch to help the audience when they try to scope integrations.
: Highlight some key concepts in an experiential approach to development.

Audience
: Primary: B2B developers (more on this audience below)
: Secondary: Stytch team who are evaluating this draft for the interview take-home (naturally)

Channel
: Github Pages / some free hosting site that allows me to author in Markdown

Timeline
: Wednesday, Oct 33

Stakeholders
: Individual work (no other stakeholders)


About B2B developers:

In my experience, there is a moderate variance in the experience level of "B2B developers", but what a "B2B developer" *is* actually can vary quite a bit. It could be:

* Senior engineer who is backend-leaning or full stack (specified in the takehome) and is planning on doing the coding.
* Senior engineer or engineering manager who is only a stakeholder, not the implementer, and evaluating Stytch's solutions.
* Lesser-experienced or new-to-the-team engineer who is reading the documentation for training or pair programming purposes
* Engineers who aren't planning on using Stytch but just heard the name and are learning about the concept (e.g. "What is an "email magic link"? Stytch might have some more information if I can read their guide on how it works...)
* PMs who are similarly scoping and costing what using Stytch will be like to work with.

All of these are team members who could be at some B2B corporation and who are looking at Stytch's documentation.

This allows us to elide some things from the scope of this article, sticking to statements like "set these environment variables" and "run this Flask app" - we can assume that people who would try to do these things, the implementers, will probably know what we mean by that. 

However, we do have the opportunity to be more clear and a bit hand-holdy on the concepts of the app and what the code is doing even for casual readers of the guide who are using the chance to learn more about Stytch from a code-first perspective. Even though "the person building the thing" is the primary audience, the fact that these other viewers can exist informs how we crete the tone and specificity of the document.

To that end, in general I'll aim for these qualities in the quickstart:

Clear
: I'll assume that this won't be the very first time the person reading the page has considered authentication, but I think topic-specific terms like "Email Magic Links" could use at least a little definition or reminder for those who are less familiar. The goal here is to prevent a bounce off the page or loss of focus while they look up terms. So it's worth being clear what we mean, and providing ample links to more information where relevant.

Correct (well, at least not incorrect)
: I have a whole blog post in mind for this, but when it comes to documentation, it's more useful to be accurate than precise--that is, docs that are close enough, and get developers to the goal successfully with only the understanding of the basics, are more valuable than docs that get into the weeds and drill into every precise detail.

: There are some judgment calls to make here, especially when it comes to code, because we want to exemplify programming at least a little defensively. In general, my approach is to consider that the code might be *run right away* without the developer really reading the whole document... so there are e.g. general-purpose exception catches but also more specific messages along the lines of "You may have missed a prerequisite step at this point, go back and read the prerequisites." Enforcing this in code with a nice error message helps this type of developer stay in flow.

Concise
: For most of the audiences, "how far do I have to scroll" is the zeroth-order metric for "how difficult will this be", so keeping the documentation concise can provide a psychological feeling of straightforwardness. In addition, documentation tends to "creep" away and get stale as the API evolves. This can be minimized by staying fairly focused on the specific documentation task at hand without trying to over-build.

: That being said: what exactly the tone and style guide would be for developer documentation is out of scope for this exercise, but in general, I am of the opinion that a narrative form where the tone feels conversational keeps the discussion from feeling business-jargony and overly shorthand, which can be a distraction to readers.

Non-trivial
: I'm a bit torn on this one, so I would love to test this theory and/or get other opinions. My feeling is that there's an advantage if the example is not quite as simple as "log in an existing username and password" because one of the goals is to drive a small amount of "A-Ha, Stytch can do hard things quite easily" during the process of implementing the app.

: Logging in with username and password, while useful and easy to understand, doesn't highlight how Stytch is better than a language's own login-with-database libraries. There is a solid counterargument in that this leads to a slightly larger scope and showing something that is quite trivial might allow developers to focus on the "other parts" (ensuring libraries installed correctly, configuration in Stytch is correct, etc...) which would be the fastest 0-to-1 way to approach a quickstart.

: Where I settled is that I agree with the magic login flow that Stytch currently uses for its quickstarts. It generates a good narrative for how to start at the beginning and improve the app incrementally: build a flow that represents a industry-approved signup flow, then iterate from there to make that login flow robust, then iterate more to everyday login flows for existing users like OpenID or passkeys: a series of pieces that takes people from nothing (the quickstart) through a story of a user signup to a full app built on Stytch.

