# Overview

The application that is needed is a time tracking application.  It is a derivative of the canonical single page starter application [TodoMVC](http://addyosmani.github.com/todomvc/).  I hope that because of the simularity, you will be able take the concepts from the tutorials on TODO apps and expand that to work with this application.

## The web service

I have written a simple web service to use with your front-end. To start the web service run the following in a terminal:

    python timetracker.py
    

### Resources

The webservice is composed of the following RESTful resources that your Backbone.js application will need to integrate with.  The keys and JSON structure are not defined in the web service.  Your client-side application is free to define the structure and the JSON and what the key will be.

#### GET /projects

Retrieve a list of projects

#### GET /projects/{project-key}

Retrieve a single project

#### PUT /projects/{project-key}

Store a project's JSON document at this URI

#### DELETE /projects/{project-key}

Delete a project

#### GET /projects/{project-key}/tasks

Retrieve a list of tasks for a project

#### GET /projects/{project-key}/tasks/{task-key}

Get a single task's data

#### PUT /projects/{project-key}/tasks/{task-key}

Store a task's JSON document at this URI

#### DELETE /project/{project-key}/tasks/{task-key}

Delete a task


### Static resources

Place all your HTML, CSS, and Javascript in the webroot/ directory.  They will be served from the root of the site.

For instance `webroot/app.js` will be served at `http://localhost:8000/app.js`.


## Project Requirements

* As a user, I would like to have a page that lists all my projects
* As a user, I would like to have a page for a single project that lists its tasks and total elapsed time
* As a user, I would like to be able to add, edit and delete projects
* As a user, I expect a project to have a title
* As a user, I would like to be able to add, edit and delete tasks for a project
* As a user, I expect a project's task to have a title and an elapsed time

All UX and design for this project is up to you as long as these requirements are satisified.
