<p align="center">
  <img style="width: 120px; margin: 0 auto 40px; display: block; border-radius: 14px;" src="https://i.imgur.com/Gu7EcLR.jpeg" alt="Logo" referrerpolicy="no-referrer"/>
</p>

# LogArbor – Log Aggregation Tool

LogArbor is a modern and lightweight log aggregation and monitoring platform designed for developers who want real-time insight into their logs without complexity.

---

# ⚙️ Setup

Follow these steps to get started with LogArbor

---

## Setup Video

<p align="center">
  <iframe width="560" height="315" src="https://drive.google.com/file/d/1l2BZK7xnJYiZc5v9ySvZO-Q_Mucq29kj/view?usp=sharing" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</p>

## 📋 1️⃣ Create an account

1. Go to https://logarbor.com/auth/register
2. Create an account or just sign in with github.

## 📋 2️⃣ Create a service

1. Log in to your account.
2. Go to "Services".
3. Click "New Service" button.
4. Fill out information about your service like name and alert level, etc.
5. Go to the created service and copy the service id.

## 📋 3️⃣ Get your access token

1. Go to "Settings".
2. Under the "API Keys", copy the "Primary API Key".

## 📋 4️⃣ Secure your keys

1. Create an .env file.
2. Place your api key and service id in the file.

## 📋 5️⃣ Send logs

1. Install LogArbor Client.
```bash
pip install log-arbor
```
2. Send logs.
```python
from log_arbor.utils import log
import os

def event_that_needs_logged():

  # Some operations...

  # Allowed log levels: [debug, info, warning, error, critical]
  log(os.getenv("YOUR_SERVICE_ID"), "info", "some message over here", os.getenv("YOUR_ACCESS_TOKEN"))
```

## 📋 6️⃣ View/Search/Detect your logs

1. Go to the "Dashboard" there you will see your log count graph along with other graphs.
<p align="center">
  <img src="https://i.imgur.com/0U80gmK.png" alt="" width="500"/>
</p>
<p align="center">
  <img src="https://i.imgur.com/tS1aub5.png" alt="" width="500"/>
</p>
<p align="center">
  <img src="https://i.imgur.com/5bW7sJh.png" alt="" width="500"/>
</p>
2. Go to "Logs" and see and search your logs. If you don't see your logs, probably something went wrong, so check your inbox for an alert.
<p align="center">
  <img src="https://i.imgur.com/0xN1Rnd.png" alt="" width="500"/>
</p>
3. Alerts are usually triggered if your log's level is worse than your service's alert level. For example: In your application you have an error handler which sends a log with log() function, that log will contain "error" as a level because it is an error handler. Your service that the log is sending to has an alert level of "warning" which means that if the log that is going to this service has a level of "warning" or beyond there will be an alert triggered. In other cases an alert is going to be triggered because something went wrong with the log function, it could be the wrong access token or invalid service id. Note that if log function fails the alert is going to be sent to your inbox only unlike the log alert, which is going to be sent to your inbox and the Alerts page.

---

## 🚀 Live Tool

🔗 **Access LogArbor:**  
https://logarbor.com

---
 
### System Architecture Preview

<p align="center">
  <img src="https://i.imgur.com/15l8VMu.png" alt="System Architecture Diagram" width="800"/>
</p>


## Lisence

Copyright © 2026 Platon Tikhnenko. All rights reserved.

This project is proprietary. The source code is made public for the sole purpose 
of portfolio review by potential employers. It may not be copied, redistributed, 
or used for any other purpose without explicit written permission.


