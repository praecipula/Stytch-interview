#! /usr/bin/env python

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

@app.route('/signup')
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

@app.route('/request_magic_link', methods=['POST'])
def request_magic_link():
    """
    Start the magic link flow.
    This method is the target of the POST request sent by submitting the form on the `/signup` page.
    """
    email = request.form['email']
    try:
        response = stytch_client.magic_links.email.discovery.send(
                email_address=email
                )
        if response.is_success:
            return f"""
            <h1>Success!</h1>
            <p>You should soon receive an email request to log in at {email}</p>
            """
    except StytchError as e:
        return jsonify(dict(e.details))

@app.route('/authenticate')
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
    # for this user. The intermediate session token is valid for the half-session (User is known, but not Organization)
    # that we have so far.
    ist = response.intermediate_session_token
    discovered_orgs = response.discovered_organizations
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
    session['stytch_session_token'] = response.session_token
    return f"""
    <h1>Success!</h1>
    <p>You are logged in as {response.member.email_address}</p>
    <a href='/dashboard'>Go to dashboard</a>
    """


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
        response = stytch_client.sessions.authenticate(session_token=stytch_session)
    except StytchError as e:
        # If there is an error (such as server-expired authentication or session error), clear the session.
        # This will have the effect of needing to fully re-log-in again.
        logout()
        return jsonify(dict(e.details))

    # If we reach here we have successfully logged in based on data stored in our session.

    # Remember to reset the cookie session on authenticate, as this will issue a new token.
    session['stytch_session_token'] = response.session_token
    return f"""
        <p><em>{response.member.email_address}</em> is currently logged into {response.organization.organization_name}.<p>
        <p><a href="/signup">Submit another email</a> to log in.</p>
        """

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

if __name__ == '__main__':
    app.run(debug=True)
