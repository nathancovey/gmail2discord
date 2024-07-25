<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<h1>Gmail to Discord Notification Tool</h1>
<p>This open-source tool sends a message in Discord when your Gmail gets an email from a specified email address. Don't pay for Zapier because this is free. It's designed to help teams stay informed about important updates directly within their communication channels.</p>

<h2>Features</h2>
<ul>
<li><strong>Scheduled Notifications</strong>: Sends a message to a specified Discord channel for each email received from a specified email address. Triggers every 10 minutes.</li>
<li><strong>Free Tools</strong>: Utilizes free tiers of Google Cloud and Heroku, ensuring no cost under normal usage.</li>
<li><strong>Customizable</strong>: Easily modify the script to fit your needs.</li>
<li><strong>Open Source</strong>: Free to use, modify, and distribute.</li>
</ul>

<h2>Getting Started</h2>
<h3>Prerequisites</h3>
<ul>
<li><strong>Python 3.x</strong></li>
<li><strong>Google Cloud Account</strong>: To use the Gmail API</li>
<li><strong>Discord Account</strong>: To set up a webhook</li>
<li><strong>Heroku Account</strong>: For deployment and scheduling</li>
</ul>
<h3>Installation</h3>
<ol>
<li><strong>Clone the Repository</strong>
<pre><code>git clone https://github.com/yourusername/gmail-to-discord.git
cd gmail-to-discord</code></pre>
</li>
<li><strong>Set Up Google Cloud Credentials</strong>
<ul>
<li>Follow the <a href="https://developers.google.com/gmail/api/quickstart/python">Gmail API Quickstart</a> to create a project, enable the Gmail API, and download <code>credentials.json</code>.</li>
<li>Encode <code>credentials.json</code> to base64 and store it in an environment variable <code>GOOGLE_CREDENTIALS</code>.</li>
</ul>
</li>
<li><strong>Set Up Discord Webhook</strong>
<ul>
<li>Create a webhook in your Discord channel and copy the URL.</li>
</ul>
</li>
<li><strong>Install Dependencies</strong>
<pre><code>pip install -r requirements.txt</code></pre>
</li>
<li><strong>Set Up Environment Variables</strong>
<ul>
<li>Add your environment variables for Google credentials, Discord webhook URL, and token JSON:</li>
</ul>
<pre><code>export GOOGLE_CREDENTIALS=your_base64_encoded_credentials
export TOKEN_JSON=your_base64_encoded_token
export DISCORD_WEBHOOK_URL=your_discord_webhook_url</code></pre>
</li>
</ol>

<h3>Usage</h3>
<p>Run the script to start receiving notifications:</p>
<pre><code>python3 gmail_to_discord.py</code></pre>

<h3>Deployment on Heroku</h3>
<ol>
<li><strong>Create a Procfile</strong>
<ul>
<li>Create a file named <code>Procfile</code> with the following content:</li>
</ul>
<pre><code>worker: python3 gmail_to_discord.py</code></pre>
</li>
<li><strong>Deploy to Heroku</strong>
<pre><code>heroku create
heroku config:set GOOGLE_CREDENTIALS=your_base64_encoded_credentials
heroku config:set TOKEN_JSON=your_base64_encoded_token
heroku config:set DISCORD_WEBHOOK_URL=your_discord_webhook_url
git push heroku master
heroku ps:scale worker=1</code></pre>
</li>
<li><strong>Set Up Heroku Scheduler</strong>
<ul>
<li>Add the Heroku Scheduler add-on:</li>
</ul>
<pre><code>heroku addons:create scheduler:standard --app your-heroku-app-name</code></pre>
<ul>
<li>Open the Heroku Scheduler dashboard:</li>
</ul>
<pre><code>heroku addons:open scheduler --app your-heroku-app-name</code></pre>
<ul>
<li>Add a new job to run the script every 10 minutes:</li>
</ul>
<pre><code>python3 gmail_to_discord.py</code></pre>
</li>
</ol>

<h3>Manually Triggering the Script</h3>
<p>To manually trigger the script and check if it's working, use the following command:</p>
<pre><code>heroku run python3 gmail_to_discord.py --app your-heroku-app-name</code></pre>
<p>Replace <code>your-heroku-app-name</code> with the name of your Heroku app.</p>

<h3>Check Logs</h3>
<p>To check the logs and see the output of the script, use:</p>
<pre><code>heroku logs --tail --app your-heroku-app-name</code></pre>

<h3>License</h3>
<p>This project is licensed under the MIT License - see the <a href="LICENSE">LICENSE</a> file for details.</p>
</body>
</html>
