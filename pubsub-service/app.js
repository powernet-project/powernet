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
const formBodyParser = bodyParser.urlencoded({ extended: false });
const jsonBodyParser = bodyParser.json();
const messages = []; // List of all messages received by this instance

// The following environment variables are set by app.yaml when running on GAE,
// but will need to be manually set when running locally.
const PUBSUB_VERIFICATION_TOKEN = process.env.PUBSUB_VERIFICATION_TOKEN;
const topic = pubsub.topic(process.env.PUBSUB_TOPIC);
const subscription = pubsub.subscription(process.env.PUBSUB_SUBSCRIPTION);

// assign the view engine we're going to use
app.set('view engine', 'pug');

// setup the index route  
app.get('/', (req, res) => {
	res.render('index');
});

app.post('/', formBodyParser, (req, res, next) => {
	if (!req.body.payload) {
    	res.status(400).send('Missing payload');
    	return;
  	}

	topic.publish({data: req.body.payload}, (err) => {
		if (err) {
			next(err);
			return;
		}
		res.status(200).send('Message sent');
	});
});

// pull sub message setup
app.get('/messages', (req, res) => {
	messages.push("Hellloooo, I'm alive")

	subscription.pull({returnImmediately: false}).then((results) => {
		const data = results[0];
		data.forEach((message) => {
			messages.push(`* %d %j %j`, message.id, message.data, message.attributes);
		});	
		console.log(data);
		return subscription.ack(messages.map((message) => message.ackId));
	});	

	res.render('messages', { messages: messages });
});

// push sub message setup
app.post('/pubsub/push', jsonBodyParser, (req, res) => {
//   if (req.query.token !== PUBSUB_VERIFICATION_TOKEN) {
//     res.status(400).send();
//     return;
//   }

  // The message is a unicode string encoded in base64.
  const message = new Buffer(req.body.message.data, 'base64').toString('utf-8');

  messages.push(message);

  res.status(200).send();
});


// Start the server
const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  	console.log(`App listening on port ${PORT}`);
  	console.log('Press Ctrl+C to quit.');
});