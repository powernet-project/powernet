// [START app]
'use strict';

const express = require('express');
const bodyParser = require('body-parser');

// By default, the client will authenticate using the service account file
// specified by the GOOGLE_APPLICATION_CREDENTIALS environment variable and use
// the project specified by the GCLOUD_PROJECT environment variable. See
// https://googlecloudplatform.github.io/gcloud-node/#/docs/google-cloud/latest/guides/authentication
// These environment variables are set automatically on Google App Engine
const PubSub = require('@google-cloud/pubsub');

// Instantiate a pubsub client
const pubsub = PubSub();

const app = express();
app.set('view engine', 'pug');

const formBodyParser = bodyParser.urlencoded({ extended: false });
const jsonBodyParser = bodyParser.json();

// List of all messages received by this instance
const messages = [];

// The following environment variables are set by app.yaml when running on GAE,
// but will need to be manually set when running locally.
const PUBSUB_VERIFICATION_TOKEN = process.env.PUBSUB_VERIFICATION_TOKEN;

const topic = pubsub.topic(process.env.PUBSUB_TOPIC);

// [START index]
app.get('/', (req, res) => {
  res.render('index', { messages: messages });
});

app.post('/', formBodyParser, (req, res, next) => {
  if (!req.body.payload) {
    res.status(400).send('Missing payload');
    return;
  }

  topic.publish({
    data: req.body.payload
  }, (err) => {
    if (err) {
      next(err);
      return;
    }
    res.status(200).send('Message sent');
  });
});
// [END index]

// [START push]
app.post('/pubsub/push', jsonBodyParser, (req, res) => {
  if (req.query.token !== PUBSUB_VERIFICATION_TOKEN) {
    res.status(400).send();
    return;
  }

  // The message is a unicode string encoded in base64.
  const message = new Buffer(req.body.message.data, 'base64').toString('utf-8');

  messages.push(message);

  res.status(200).send();
});
// [END push]

// Start the server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`App listening on port ${PORT}`);
  console.log('Press Ctrl+C to quit.');
});
// [END app]