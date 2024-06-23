class WebService {

  constructor() {
    let ws_protocol = "ws://"
    let ws_port = "80"
    if (window.location.protocol == "https:") {
      ws_protocol = "wss://"
      if (window.location.port == "") {
        ws_port = "443"
      } else {
        ws_port = window.location.port
      }
    } else {
      if (window.location.port == "") {
        ws_port = "80"
      } else {
        ws_port = window.location.port
      }
    }
    this.SIGNALING_SERVER = ws_protocol + window.location.hostname + ":" + ws_port + "/ws"
    //this.SIGNALING_SERVER = ws_protocol + window.location.hostname + ":8000/ws"
    this.signaling_socket = null   /* our socket.io connection to our webserver */
    this.modules = {} /* contains the registered modules */
    //alias for sending JSON encoded messages
    this.emit = (type, config) => {
      //attach the other peer username to our messages 
      let message = { 'type': type, 'config': config }
      if (this.signaling_socket && this.signaling_socket.readyState == 1) {
        this.signaling_socket.send(JSON.stringify(message))
      }
    }

    const getState = () => {
      if (document.visibilityState === 'hidden') {
        return 'hidden';
      }
      if (document.hasFocus()) {
        return 'active';
      }
      return 'passive';
    };

    // Stores the initial state using the `getState()` function (defined above).
    let state = getState();

    // Accepts a next state and, if there's been a state change, logs the
    // change to the console. It also updates the `state` value defined above.
    const logStateChange = (nextState) => {
      const prevState = state;
      if (nextState !== prevState) {
        console.log(`State change: ${prevState} >>> ${nextState}`);
        state = nextState;
        if (state == 'frozen') {
          this.disconnect();
        }
        if (state == 'resume') {
          this.connect();
        }
      }
    };

    // These lifecycle events can all use the same listener to observe state
    // changes (they call the `getState()` function to determine the next state).
    ['pageshow', 'focus', 'blur', 'visibilitychange', 'resume'].forEach((type) => {
      window.addEventListener(type, () => logStateChange(getState()), { capture: true });
    });

    // The next two listeners, on the other hand, can determine the next
    // state from the event itself.
    window.addEventListener('freeze', () => {
      // In the freeze event, the next state is always frozen.
      logStateChange('frozen');
    }, { capture: true });

    window.addEventListener('pagehide', (event) => {
      if (event.persisted) {
        // If the event's persisted property is `true` the page is about
        // to enter the Back-Forward Cache, which is also in the frozen state.
        logStateChange('frozen');
      } else {
        // If the event's persisted property is not `true` the page is
        // about to be unloaded.
        logStateChange('terminated');
      }
    }, { capture: true });



    console.log("Construct WebService", this.modules)

  }

  register(prefix, wsMsghandler, wsOnOpen, wsOnClose) {
    this.modules[prefix] = { 'msg': wsMsghandler, 'open': wsOnOpen, 'close': wsOnClose }
    console.log("Register prefix", prefix, this.modules)
  }

  connect() {
    let wshandler = this
    console.log("Connecting to signaling server")
    this.signaling_socket = new WebSocket(this.SIGNALING_SERVER)
    this.signaling_socket.onopen = () => {
      console.log("Connected to the signaling server")
      for (let prefix in this.modules) {
        if (this.modules[prefix].open) {
          this.modules[prefix].open()
        }
      }
      this.emit('_join', { "name": this.username })
    }

    this.signaling_socket.onclose = (e) => {
      console.log("Disconnected from signaling server")
      for (let prefix in this.modules) {
        if (this.modules[prefix].close) {
          this.modules[prefix].close()
        }
      }
      console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
      setTimeout(function () {
        wshandler.connect();
      }, 1000);
    }

    //when we got a message from a signaling server 
    this.signaling_socket.onmessage = (msg) => {
      var data = JSON.parse(msg.data)
      var success = false
      for (let prefix in this.modules) {
        if (data.type.startsWith(prefix)) {
          this.modules[prefix].msg(data.type, data.config)
          success = true
          break
        }
      }
      if (!success) {
        console.log("Error: Unknown ws message type ", data.type)
      }
    }

    this.signaling_socket.onerror = function (err) {
      console.error('Socket encountered error: ', err.message, 'Closing socket');
      this.signaling_socket = null
    }

  }

  disconnect() {
    if (this.signaling_socket) {
      this.signaling_socket.close()
      this.signaling_socket = null
    }
  }

  init(username, pw, remember) {
    this.username = username
    this.pw = pw
    this.remember = remember
    this.connect()
  }




}




const messenger = new WebService()
messenger.init("myuser", "mypw", { "somesettings": "anything" })