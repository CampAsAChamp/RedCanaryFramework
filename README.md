# RedCanaryFramework
Red Canary Homework Assignment

A framework that will generate endpoint activity. We will be able to test an EDR agent and ensure it generates the appropriate telemetry

---

**One you’ve completed the project, please write a short one page document describing what you’ve created and how it works**

I have created a framework that is able to run an executable/command at a given path. Create & Delete a file, given a path. Establish a network connection and transmit data. And log activity of all of this to a JSON file.

It works through Python[3.9], and I have tested it on Windows[21H2] and Mac[12.1]. I have taken advantage of many of the built in modules in Python, such as the JSON, OS, Socket, and Subprocess modules along with others. At the end of each of the main functions in the framework there is call to log, which will log some of the various information about the function we just did.


