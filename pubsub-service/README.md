# Publish / Subscribe Micro-Service

- Handles messaging from one or more Home Hubs

## Setup and running the project locally

- After you pull the project down (at the top powernet level), cd into this dir
```
cd pubsub-service
```

- Then run the following setup commands:
```
npm install
export PUBSUB_TOPIC=home-hub-message
export PUBSUB_SUBSCRIPTION=home-hub-sub-update
```

- Lastly, run the node server:
```
npm start
```

- Now you can launch a browser and hit localhost:8080 to see the app running
