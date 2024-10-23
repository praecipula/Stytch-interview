Title: Getting Started with Stytch B2B Authentication
Date: 2024-10-23
Category: Take home

# Getting Started: Python

## Overview:

In this guide we will invite a user via an email address to an existing [Organization](https://stytch.com/docs/b2b/api/organization-object). This flow will create a new [Member](https://stytch.com/docs/b2b/api/member-object) using Stytch's API and a [Magic Link](https://stytch.com/docs/api/send-by-email), log this Member in, and store this Member's login credentials in the browser's session. This will simulate a common method for sending a user-friendly, passwordless, and secure invitation for a user to join and log into an Organization.

Check out these resources for more background information about Stytch's [data model](https://stytch.com/docs/b2b/guides/multi-tenancy) and [Magic Links](https://stytch.com/docs/b2b/guides/magic-links/overview) if you'd like more information about the techniques used in this guide.

## Prerequisites:

To run this quickstart, we will need:

* An Organization that has been created in Stytch's [Organizations dashboard](https://stytch.com/dashboard/organizations?env=test)
* An email address to which to send the Magic Link. You will need to be able to receive and access emails at this address.
* A development environment in which to implement the flow. Here we will use Python and Flask to host a local server which integrates with Stytch and guides new users through the flow.

## Goals:

By the end of this quickstart, you will have learned how to:

* Set up a basic B2B Organization in Stytch
* Set up and run a Python / Flask application to integrate with Stytch's API
* Send an email inviting the user to an organization using a Magic Link
* Use Stytch's [Discovery Authentication flow](https://stytch.com/docs/b2b/guides/what-is-stytch-b2b-auth#discovery-authentication) to implement a two-stage process of logging in a user to an Organization.
* Have a basic working app to iterate upon with your own business logic.

## Implementation:

#### Install Stytch SDK and configure your API Keys

✅ Create a Stytch B2B Project in your [Stytch Dashboard](https://stytch.com/dashboard). At this stage it is sufficient to make your test organization permissive by supplying the required "name" and "slug" fields and using the defaults for the other configuration fields. In production, Stytch strongly recommends modifying your [organization's settings](https://stytch.com/docs/b2b/guides/multi-tenancy#organization-settings) to configure security to your set of expected authorization flows, but that's an exercise for another time.


✅ Install our Python SDK in your Flask environment:

```bash
pip install stytch
```

✅ Collect your Stytch Project's API keys to use in our guide.

These are located in your project details [configuration dashboard](https://stytch.com/dashboard/project-settings?env=test). We recommend using the Test configuration for your credentials (selected in the Dashboard screen's header at the top of the page). Once you have these, make them available to your development environment. (As a reminder, these should be considered secret and we highly encourage you not to share or hard-code them):

```bash

STYTCH_PROJECT_ID="YOUR_STYTCH_PROJECT_ID"
STYTCH_SECRET="YOUR_STYTCH_PROJECT_SECRET"

```

✅ Set up a basic app using the framework of your choice and initialize the Stytch client with the environment variables you set in the previous step:
```


from flask import Flask, request, redirect, session, jsonify
from stytch import B2BClient
from stytch.core.response_base import StytchError
import os 

app = Flask(__name__)
# Flask requests a secret key for encrypting session data.
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

✅ Let's start with a simple dashboard that allows us to see the state of whether we are logged in with some simple HTML. THis will help us keep track of our app's state.

For now, this will simply show we're not logged in. After a successful authentication flow, this route will try to fetch a stored token from our Flask session data, authenticate it with Stytch, and print whether the user is authenticated in an organization:

```python
@app.route('/dashboard')
def dashboard():
    """
    Generate a simple dashboard that tells us our logged-in state with some helpful links
    """
    stytch_session = session.get('stytch_session_token')
    if not stytch_session:
        # We're not logged in because we unset or never set a session at all. We should run the whole log in flow.
        return f"""
            <p>No active session. Please <a href="/signup">submit an email address</a> to receive a magic link.</p>
        """

    try:
        # Try to authenticate with the token we fetched from the session
        resp = stytch_client.sessions.authenticate(session_token=stytch_session)
    except StytchError as e:
        # If there is an error (such as server-expired authentication or session error), clear the session.
        # This will have the effect of needing to fully re-log-in again.
        logout()
        return jsonify(dict(e.details))

    # If we reach here we have successfully logged in based on data stored in our session.

    # Remember to reset the cookie session on authenticate, as this will issue a new token.
    session['stytch_session_token'] = resp.session_token
    return f"""
        <p><em>{resp.member.email_address}</em> is currently logged into {resp.organization.organization_name}.<p>
        <p><a href="/signup">Submit another email</a> to log in.</p>
        """
```

✅ While we're at it, let's implement a `logout` function by adding a simple route to delete the session token. Visiting this logout endpoint will discard the logged-in session state:

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
2. On receipt of this email, the user clicks the log in button, indicating their intent to log in. Their browser briefly visits Stytch to proceed with the server side of the flow.
3. Stytch responds with a redirect to our app with some data. Our app takes a token from the url parameters and begins a token exchange process with Stytch.
4. Using the Stytch discovery flow, we process the log in request to create an intermediate session for the user, fetching a list of Organizations for which the user can log in.
5. Based on app business logic or user input, we select one of these organizations. We exchange the selected organization and the intermediate session token for a full session.

The user is now logged in to the given Organization.

Let's proceed with implementing this flow.

✅ We use a very basic no-frills form to capture the email address:

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

✅ Upon submission of this form, the browser sends the form data via POST to the `/request_magic_link` endpoint in our app. Let's implement the function to receive this form data and start the flow with Stytch:

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

Some short time later, when the user clicks the link, Stytch will continue the flow and return to our app for the next steps.

✅ Here our app will exchange the token to create the intermediate session, which informs us which Organizations are available for the user. For now, we simply choose the first one and perfom another exchange request with the intermediate token and our selected organization to create our session:

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
      # user to select which organization to log in to.
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

If these steps are successful, we have completed the log in process. Going to our dashboard route should now show our status as logged in.


## Next steps:

Keep in mind that this example app uses some shortcuts, is built for a test environment, and only programs defensively for a few basic errors. For more information how to extend this example, review the rest of Stytch's documents and follow best practices for configuring and maintaining the security of your application.

Some possible next steps with this app could be:

* Configure the Organization settings to tighten security (for instance, by whitelisting only certain email domains for the Organization).
* When a user has access to multiple Organizations, present a webpage with options for user to choose which organization to log into.
* Adjust your redirect URL to point to a web server that clients can access over the Internet (instead of localhost).
* Use Stytch's Discovery flow and intermediate session to dynamically create new Organizations on demand.

