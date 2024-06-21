from typing import Callable, Tuple, Any
import time
import threading
import traceback
import inspect
import asyncio
import logging
from websocket_server import WebsocketServer
import sys
import json

UPDATE_FEQ = 5


class EModuleWrapper:
    def __init__(
        self,
        name: str,
        start_method: Callable,
        start_attrs: Tuple[Any],
        callback: Callable,
        **defaults,
    ) -> None:
        """
        Initializes an instance of EModuleWrapper.

        Parameters:
        - name (str): Name of the external module.
        - start_method (Callable): Method to initialize the external service - Must be non-blocking, and return True on success.
        - start_attrs (Tuple[Any]): Attributes to pass to the start_method.
        - callback (Callable): Callback method for updating data.
        - **defaults: The default values in the format to expect from the callback.
        """
        self.name = name
        self.start_method = start_method
        self.start_attrs = start_attrs
        self.callback = callback
        self.is_running = False
        self.data = defaults
        self.should_stop = False
    
    @property
    def name_safe(self):
        return self.name.lower().replace(" ", "_")


    def __call__(self) -> Any:
        """
        Simpel getter to get the state of the module.
        """
        return self.data

    def start(self):
        """
        Starts the module, initializes the external service, and begins updating data.
        """
        try:
            success = (
                asyncio.run(self.start_method(*self.start_attrs))
                if inspect.iscoroutinefunction(self.start_method)
                else self.start_method(*self.start_attrs)
            )
            if not success:
                raise Exception
            print(f"Successfully attached to module {self.name}")

            threading.Thread(target=self.update, daemon=True).start()
            self.is_running = True

        except Exception:
            print(f"FATAL: Unable to start {self.name}\n{traceback.format_exc()}")

    def update(self):
        """
        Continuously updates data from the callback method.
        """
        while not self.should_stop:
            try:
                res = (
                    asyncio.run(self.callback())
                    if inspect.iscoroutinefunction(self.callback)
                    else self.callback()
                )

                if type(res) != dict:
                    print(
                        f"FATAL: Return value of module {self.name} is not a dict!\nShutting down."
                    )
                    self.is_running = False
                    return

                for key, value in res.items():
                    if key in self.data:
                        self.data[key] = value

                time.sleep(1 / UPDATE_FEQ)

            except Exception as err:
                print(f"Error calling callback for module {self.name}\n{err}")


class Sentry:
    def __init__(self) -> None:
        """
        Initializes an instance of Sentry.
        """
        self.benchmark = []
        self.modules = []
        self.frequency = 0
        self.ws_server = None
        self.should_stop = False
    
    def ws_spin_up_server(self):
        def new_client_alert(client, server):
            print(f"New connection from: {client}")
            
        try:
            self.ws_server = WebsocketServer(host='0.0.0.0', port=8081, loglevel=logging.INFO)
            self.ws_server.set_fn_new_client(new_client_alert)
            threading.Thread(target=self.ws_server.run_forever, daemon=True).start()
        except Exception:
            print("Unable to start WS server..")
            sys.exit(-1)
            
        print("Started ws server..")



    def ws_send_payload(self, payload:dict):
        self.ws_server.send_message_to_all(json.dumps(payload))
        # print(f"Send {payload}")




    def start_server(self, frequency=5):
        """
        Starts the server and all registered modules, continuously prints their data.
        """

        self.ws_spin_up_server()

        self.frequency = 1/frequency
        for module in self.modules:
            module.start()

        while True:
            # concatenete data
            payload_data = {module.name_safe+"__"+key:value for module in self.modules for key, value in module().items()}
            
            # send data
            self.ws_send_payload(payload_data)
            time.sleep(self.frequency)
            
            self.benchmark.append({"type": "reading", "time": time.perf_counter(), "modules": len(self.modules), "package_size": sys.getsizeof(payload_data), "target_freq": self.frequency})
    
    def stop(self):
        for m in self.modules:
            m.should_stop = True
            
            

    def register_module(
        self,
        name: str,
        start_method: Callable,
        start_attrs: Tuple[str, int],
        callback: Callable,
        **defaults,
    ):
        """
        Registers a new module which input will be incorporated into the output stream of the system.

        Parameters:
        - name (str): Name of the module.
        - start_method (Callable): Method to initialize the external service - Must be non-blocking, and return True on success.
        - start_attrs (Tuple[Any]): Attributes expected from start_method.
        - callback (Callable): Callback method that provides the module's output data.
            Output data format is a dictionary, which keys are required to match the keys expected by the input for the video game that uses our system.
        - **defaults: The default values in the format to expect from the callback, with matching keys.
        """
        self.modules.append(
            EModuleWrapper(
                name=name,
                start_method=start_method,
                start_attrs=start_attrs,
                callback=callback,
                **defaults,
            )
        )
