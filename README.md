<!DOCTYPE html>
<html>
<body>

<h1>Gmail to Discord Notification Tool</h1>

<p>This tool listens for incoming emails in a specified Gmail account and sends notifications to a Discord channel when new emails are received. It's designed to be used with the Heroku platform and can be scheduled to check for new emails at regular intervals.</p>

<h2>Features</h2>
<ul>
  <li>Automatically listens for incoming Gmail messages and posts to Discord.</li>
  <li>Tracks processed messages to avoid duplicate notifications.</li>
  <li>Parses email timestamps correctly, including handling time zones and "(UTC)" format issues.</li>
  <li>Designed to work with Heroku's free tier, scheduled to run every 10 minutes.</li>
</ul>

<h2>Prerequisites</h2>
<ul>
  <li>Google Cloud account with Gmail API enabled.</li>
  <li>Heroku account with a Python environment.</li>
  <li>A Discord Webhook URL to post the notifications to.</li>
</ul>

<h2>Setup Instructions</h2>

<ol>
  <li><strong>Clone the repository:</strong></li>
  <pre><code>git clone https://github.com/yourusername/gmail-to-discord</code></pre>

  <li><strong>Set up Google Cloud:</strong></li>
  <ul>
    <li>Create a Google Cloud project and enable the Gmail API.</li>
    <li>Download your credentials as <code>credentials.json</code> and place it in the project directory.</li>
    <li>Run the authorization flow to generate the <code>token.json</code> file.</li>
  </ul>

  <li><strong>Set up Heroku:</strong></li>
  <ul>
    <li>Create a new Heroku app:</li>
    <pre><code>heroku create</code></pre>
    <li>Deploy the app to Heroku:</li>
    <pre><code>git push heroku master</code></pre>
    <li>Add your Discord Webhook URL as a config variable in Heroku:</li>
    <pre><code>heroku config:set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url</code></pre>
  </ul>

  <li><strong>Run the app:</strong></li>
  <ul>
    <li>Schedule the script to run every 10 minutes using the Heroku Scheduler:</li>
    <pre><code>heroku addons:create scheduler:standard</code></pre>
    <li>Set up the job to run <code>python3 gmail_to_discord.py</code> every 10 minutes in the scheduler dashboard.</li>
  </ul>

  <li><strong>View Logs:</strong></li>
  <ul>
    <li>To view logs and troubleshoot:</li>
    <pre><code>heroku logs --tail --app your_app_name</code></pre>
  </ul>
</ol>

<h2>Important Notes</h2>
<ul>
  <li>Make sure your <code>processed_messages.txt</code> file is updated to avoid duplicate notifications.</li>
  <li>Ensure that your Google Cloud credentials and tokens are properly set up and stored securely.</li>
</ul>

<h2>License</h2>
<p>This project is open-source and available under the MIT License.</p>

</body>
</html>
