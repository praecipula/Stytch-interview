Title: Getting Started with Stytch B2B Authentication
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

---


# Getting Started: Python

## Overview:

In this guide we will illustrate inviting a user via an email address to an existing Organization. This flow has the effect of creating a new [Member](https://stytch.com/docs/b2b/api/member-object) using Stytch's API and a Magic Link, and storing this Member's login credentials in the local browser session. This will simulate a common method for sending a user-friendly, passwordless, and secure invitation for a user to join the Organization and be logged in afterwards.

Check out these guides for more background information about Stytch's [data model](https://stytch.com/docs/b2b/guides/multi-tenancy) and [Magic Links](https://stytch.com/docs/api/send-by-email) if you'd like more information about the models used in this tutorial.

## Prerequisites:

To run this quickstart, we will need:

* An Organization that has been created in Stytch's [Organizations dashboard](https://stytch.com/dashboard/organizations?env=test)
* An email address to which to send the Magic Link. You will need to be able to receive and access emails at this address.
* A development environment in which to implement the flow - shown here using Python and Flask to communicate and shepherd the user through the flow.

## Goals:

By the end of this quickstart, you will have learned how to:

* Set up a basic B2B Organization in Stytch
* Set up and run a Python / Flask application to integrate with Stytch's API
* Send an email inviting the user to an organization using a [Magic Link](https://stytch.com/docs/b2b/guides/magic-links/overview)
* Use Stytch's [Discovery Authentication flow](https://stytch.com/docs/b2b/guides/what-is-stytch-b2b-auth#discovery-authentication) to implement a two-stage process of logging in a user.
* Have a working basic app to iterate on with your own business logic.

## Implementation:

#### Install Stytch SDK and configure your API Keys

Create a Stytch B2B Project in your [Stytch Dashboard](https://stytch.com/dashboard). At this stage it is sufficient to make your test organization permissive by only supplying the required "name" and "slug" fields and using the unset defaults for the other configuration fields. In production Stytch strongly recommends modifying your [organization's settings](https://stytch.com/docs/b2b/guides/multi-tenancy#organization-settings) to configure security to your set of expected authorization flows.



Install our Python SDK in your Flask environment:

```bash
pip install stytch
```

Configure your Stytch Project's API keys as environment variables in your development environment (these are located in your project details [configuration dashboard](https://stytch.com/dashboard/project-settings?env=test). We recommend using the Test configuration for your credentials (set in the Dashboard's menu at the top of the page):

```bash

STYTCH_PROJECT_ID="YOUR_STYTCH_PROJECT_ID"
STYTCH_SECRET="YOUR_STYTCH_PROJECT_SECRET"

```

Set up a basic app using the framework of your choice--we're using Python and Flask--and initialize the Stytch client with the environment variables you set in the previous step. 
```


from flask import Flask, request, redirect, session, jsonify
from stytch import B2BClient
from stytch.core.response_base import StytchError
import os 

app = Flask(__name__)
# Flask requests a secret key for session management.
# As this is not production code, we'll use a random value.
app.secret_key="1234567890abcdef"

stytch_client = B2BClient(
        project_id=os.environ['STYTCH_PROJECT_ID'],
        secret=os.environ['STYTCH_SECRET'],
        environment="test"
        )  

if __name__ == '__main__':
  app.run(debug=True)
```

At this point it should be possible to run the app without errors, although it doesn't do much yet.

Let's start with a simple dashboard that allows us to see the state of whether we are logged in with some simple HTML, which helps us keep track of our app's state.

For now, we're not logged in, so this route will simply state that fact when visited. After a successful authentication flow, this route will try to fetch a stored token from our Flask session data, authenticate it with Stytch, and print whether our app and Stytch agree that the user is authenticated in an organization.

```python
@app.route('/dashboard')
def dashboard():
    """
    Generate a simple dashboard that tells us our logged-in state with some helpful links
    """
    stytch_session = session.get('stytch_session_token')
    if not stytch_session:
        # We're not logged in because we unset or never set a session at all. We should run the whole login flow.
        return f"""
            <p>No active session. Please <a href="/signup">submit an email address</a> to receive a magic link.</p>
        """

    try:
        # Try to authenticate with the token we fetched from the session
        resp = stytch_client.sessions.authenticate(session_token=stytch_session)
    except StytchError as e:
        # If there is an error (such as server-expired authentication or session error), clear the session variable.
        # This will have the effect of needing to fully re-login again.
        logout()
        return jsonify(dict(e.details))

    # We have successfully logged in based on data stored in our session.

    # Remember to reset the cookie session, as sessions.authenticate() will issue a new token on successful auth.
    session['stytch_session_token'] = resp.session_token
    return f"""
        <p><em>{resp.member.email_address}</em> is currently logged into {resp.organization.organization_name}.<p>
        <p><a href="/signup">Submit another email</a> to log in.</p>
        """
```

While we're at it, let's implement the `logout` function by adding a simple route to delete the session token. Visiting this logout endpoint will discard the login state

```python
@app.route('/logout')
def logout():
    """
    Log out the user.
    Simply pop the session token from the session so we'll have to reauthenticate.
    """
    session.pop("stytch_session_token")
    return """<p>Logged out.</p>
        <p><a href="/signup">Submit another email</a> to log in.</p>
        """

```

Now that we have some helper functions to inspect and manage our app's state, it's time to implement the magic link flow.

As a reminder, magic links with discovery flow work like this:

1. We request a magic link from Stytch to be sent to a given email address.
2. On receipt of this link, the user clicks the login button and is taken to Stytch to start the login flow. This represents a user intent to login.
3. Stytch responds to this intent with a redirect to our app to continue the flow. Our app takes a token from the redirect parameters and begins a token exchange process.
4. Using the Stytch discovery flow, we process the login request to create an intermediate session for the user, fetching a list of Organizations for which the user can login.
5. Based on app business logic or user input, we select one of these organizations and exchange it, and the intermediate session token, for a full session.

The user is now logged in to the given Organization.

Magic link authentication works best where we trust a user is authentic where access to their email account vouches for their identity. Logging in this way can be cumbersome for everyday login flows, but is a quite common method for sending "password reset" emails or emails for the initial signup process, which is what we'll simulate here.

We use a very basic no-frills form for this purpose:

```python
@app.route('/signup', methods=['GET'])
def sign_up():
    """
    Render a simple form for the user to start the signup/login flow in their browser
    """

    return """
    <form action="/request_magic_link" method="post">
        <p><label for="email">Please enter an email address to send a magic link to: </label></p>
        <p><input type="email" id="email" name="email"/><input type="submit" value="Send magic link"/></p>
    </form>
    """
```

Upon submission of this form, the browser sends the form data via POST to the /request_magic_link endpoint in our app which begins the authentication flow.

```python
@app.route('/request_magic_link', methods=['POST'])
def request_magic_link():
    """
    Start the magic link flow.
    Here we are using the discovery flow to log the user in; later we will check what organizations
    are available for them to log into.
    This method is the target of the POST request sent by submitting the form on the `/signup` page.
    """
    email = request.form['email']
    try:
        resp = stytch_client.magic_links.email.discovery.send(
                email_address=email
                )
        if resp.is_success:
            return f"""
            <h1>Success!</h1>
            <p>You should soon receive an email request to log in at {email}</p>
            <p>More info: response: {resp.json()}</p>
            """
    except StytchError as e:
        return jsonify(dict(e.details))

```
Upon success of this route, Stytch will send an email to the user asking them to log in.

Some short time later, when the user clicks the link, Stytch will continue the flow and send a redirect to our app. Here our app will exchange the token to create the intermediate session, choose a user-visible Organization to log into (for now, simply the first one), and perfom another exchange request with the intermediate token and our selected organization to create our session.

```python
@app.route('/authenticate', methods=['GET'])
def authenticate():
    """
    This is the Stytch-default route to redirect the user's browser to after Stytch validates and 
    checks authorization.
    (https://stytch.com/dashboard/redirect-urls?env=test)
    """
    token = request.args.get('token', None)
    token_type = request.args.get('stytch_token_type', None)

    # This redirect URL can be used for several different auth flows.
    # There is a distinct token_type included from Stytch for each auth flow
    # and it is a good practice to check this field to ensure you know which authenticate() method to use
    if token_type != 'discovery':
      return f"token_type: {token_type} not supported"

    try:
        # Discover which Organizations are valid for logging in this user
        response = stytch_client.magic_links.discovery.authenticate(
            discovery_magic_links_token=token,
            )
    except StytchError as e:
        return jsonify(dict(e.details))

    # Sessions are based on Memberships, but we don't yet know which organization to choose
    # for this user. The intermediate session token is valid for the half-session of only the
    # user data model that we have so far.
    ist = resp.intermediate_session_token
    discovered_orgs = resp.discovered_organizations
    if len(discovered_orgs) > 0:
      # email belongs to >= 1 organization, simply log into the first one for this example.
      # It may be more elegant, for users who belong in multiple Organizations, to display a choice to the
      # user to select which organization to login to.
        try:
            response = stytch_client.discovery.intermediate_sessions.exchange(
                    intermediate_session_token=ist,
                    organization_id=discovered_orgs[0].organization.organization_id,
                    )
        except StytchError as e:
            return jsonify(dict(e.details))
    else: # There are no discoverable / visible orgs to this user.
      return f"""<h1>Action needed:</h1>
        <p><em>Stytch was unable to locate any valid organizations for this user to join.</em></p>
        <p>Please double check the <a href="https://stytch.com/dashboard/organizations?env=test">Organizations</a> configuration for your account.</p>
        """

    # We made it to having a succesful response. Store the returned token in our session data.
    session['stytch_session_token'] = resp.session_token
    return f"""
    <h1>Success!</h1>
    <p>You are logged in as {resp.member.email_address}></p>
    <a href='/dashboard'>Go to dashboard</a>
    """

```

That completes the flow! At this point Stytch and our app agree that the user is logged in to a particular organization. Going to our dashboard route should now show our status as logged in.


Next steps:

Keep in mind that this example app uses some shortcuts, is built for the test environment, and only programs defensively for a few common errors. For more information how to extend this example, review the rest of Stytch's documents and follow best practices for configuring, and maintaining the security of, your application.

* Configure the Organization settings to limit users who can be added by, for example, whitelisting email domains
* Present a webpage with options for the Member to choose which organization to log into
* Adjust your redirect URL to point to a web server that clients can access over the Internet

Read more:

Full code:
