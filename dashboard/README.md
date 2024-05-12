# WAS - The Web Application Skeleton

(work in progress - if there is interest, this short docu might be extended )

During some other projects (Zuul, Schnipsl) it became obvious that these projects all had a common core containing basically a webserver and a plugin manager. As that skeleton can be well used again for other projects, it was extracted from Schnipsl and here now released as minimal package as a base for other projects.

Basically it provides:
* A tiny webserver providing static content and a websocket connection
* a python base class to add own functionial plugins into it
* the docker file to run the final app in a docker environment


## The plugin principle
The way how the plugins work and communicate are quite simple. When a plugin runs the first time, the plugin-manager notices this and add's an entry into its config, which can be found in volumes/backup/PluginManager. In this config, a plugin must be set to active after the first run. When then the program is restarted, the plugin will be started too.

Then the plugin runs as separate thread and can basically do whatever is needed.


### Plugin communication
The communication is quite simple, as the whole interaction with the whole interaction with the outer world just happens on two ways:

#### Events
Each plugin can send or receive events. All events contains a type (defined in defaults.py) and data. Eeach plugin has to handle each event, there is no further distribution logic behind. Sending events is non blocking, like fire and forget

#### Queries
Each plugin can send or receive queries. All queries contains a type (defined in defaults.py) and data. Eeach plugin has to handle each query, there is no further distribution logic behind. In opposite to events this is a blocking call, which returns after all plugins have added their result sets. This is used today in the Schnipsl application, where a movie is searched through several media sources.



* change all filenames which contains canspy_dashboard against your application mame
* by search and replace, change all appearences of canspy_dashboard in all files against your application mame
* add as much plugins as you need. Take the sample spl_canspy_dashboard in plugins/canspy_dashboard as starting point. Please note that a plugin must be named starting with spl_ to allow the plugin manager to find them. You can create as much plugin subfolders as wanted
* if needed, do not forget to add/adjust the installdocker scipts inside each plugin folder to install additional software /packages in case the plugin need them.
* create your own websites. Take static/index.html as starting point, especially for the websocket communication

## The Javascript Client
In the sample file the WebService object is started. This object provide two methods to send and receive messages

### Register
Each javascript object which wants to receive messages and/or notifications need to call the register method to annouce it's callback function for messages and websocket connect/disconnect notification. The parameter prefix helps the WebService Object to identify the receiver object. If a message type starts with a known prefix, the message is forwarded to the matching objects callback function

### emit
This function sends a given message type and content to the server.

## Docker
the `docker-compose build` command will build the container and run it interactive