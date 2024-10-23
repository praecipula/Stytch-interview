#! /usr/bin/env python

from flask import Flask, request, redirect, session, jsonify
from stytch import B2BClient
from stytch.core.response_base import StytchError
import os 

app = Flask(__name__)
# Flask requests a secret key for session signing.
# As this is not production code, we'll use a random value.
app.secret_key="1234567890abcdef"

stytch_client = B2BClient(
        project_id=os.environ['STYTCH_PROJECT_ID'],
        secret=os.environ['STYTCH_SECRET'],
        environment="test"
        )

@app.route('/signup', methods=['GET'])
def sign_up():
    """
    Render a simple form for the user to start the signup/login flow in their browser
    """

    return """
    <form action="/request_magic_link" method="post">
        <label for="email">Please enter an email address to send a magic link to: </label>
        <input type="email" id="email" name="email"/>
        <input type="submit" value="Send magic link"/>
    </form>
    """

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
    # so you know which authenticate() method to use
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
    if len(discovered_orgs):
      # email belongs to >= 1 organization, simply log into the first one for this example
        try:
            response = stytch_client.discovery.intermediate_sessions.exchange(
                    intermediate_session_token=ist,
                    organization_id=discovered_orgs[0].organization.organization_id,
                    )
        except StytchError as e:
            return e.details
    else:
      return f"""<h1>Action needed:</h1>
        <p><em>Stytch was unable to locate any valid organizations for this user to join.</em></p>
        <p>Please double check the <a href="https://stytch.com/dashboard/organizations?env=test">Organizations</a> configuration for your account.</p>
        """

# Store the returned session in cookies
    session['stytch_session_token'] = resp.session_token
    return f"""
    <h1>Success!</h1>
    <p>You are logged in as {resp.member.email_address}></p>
    <a href='/dashboard'>Go to dashboard</a>
    """

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

@app.route('/logout')
def logout():
    """
    Log out the user.
    Simply pop the session token from the session so we'll have to reauthenticate.
    """
    session.pop("stytch_session_token", None)
    return """<p>Logged out.</p>
        <p><a href="/signup">Submit another email</a> to log in.</p>
        """

if __name__ == '__main__':
    app.run(debug=True)
