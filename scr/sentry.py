from typing import Callable, Tuple, Any
import time
import threading
import traceback
import inspect
import asyncio

UPDATE_FEQ = 5

class EModuleWrapper:
    def __init__(self, name: str, start_method: Callable, start_attrs: Tuple[Any], callback: Callable, **defaults) -> None:
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
            success = asyncio.run(self.start_method(*self.start_attrs)) if inspect.iscoroutinefunction(self.start_method) else self.start_method(*self.start_attrs)
            if not success: raise Exception
            print(f"Successfully attached to module {self.name}")

            threading.Thread(target=self.update, daemon=True).start()
            self.is_running = True
            
        except Exception:
            print(f"FATAL: Unable to start {self.name}\n{traceback.format_exc()}")

    def update(self):
        """
        Continuously updates data from the callback method.
        """
        while True:
            try:
                res = asyncio.run(self.callback()) if inspect.iscoroutinefunction(self.callback) else self.callback()

                if type(res) != dict:
                    print(f"FATAL: Return value of module {self.name} is not a dict!\nShutting down.")
                    self.is_running = False
                    return

                for key, value in res.items():
                    if key in self.data:
                        self.data[key] = value

                time.sleep(1/UPDATE_FEQ)

            except Exception as err:
                print(f"Error calling callback for module {self.name}\n{err}")


class Sentry:
    def __init__(self) -> None:
        """
        Initializes an instance of Sentry.
        """
        self.modules = []
        self.frequency = 0
        self.ws_client = None
    
    def ws_spin_up_server(self):
        print("Started ws server..")



    def ws_send_payload(self, payload):
        pass




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

            print(payload_data)
            
            # send data
            self.ws_send_payload(payload_data)
            time.sleep(self.frequency)

    def register_module(self, name: str, start_method: Callable, start_attrs: Tuple[Any], callback: Callable, **defaults):
        """
        Registers a new module with the specified parameters.

        Parameters:
        - name (str): Name of the external module.
        - start_method (Callable): Method to initialize the external service - Must be non-blocking, and return True on success.
        - start_attrs (Tuple[Any]): Attributes to pass to the start_method.
        - callback (Callable): Callback method for updating data.
        - **defaults: The default values in the format to expect from the callback.
        """
        self.modules.append(
            EModuleWrapper(
                name=name,
                start_method=start_method,
                start_attrs=start_attrs,
                callback=callback,
                **defaults
            )
        )
