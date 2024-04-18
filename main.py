from scr.sentry import Sentry
from modules.TacxTrainer.main import run as TacxStart, get as TacxGet

sentry = Sentry()



# Register your modules here!
sentry.register_module(
    "Tacx Trainer",
    TacxStart, 
    ("EAAA3D1F-6760-4D77-961E-8DDAC1CC9AED", 5),
    TacxGet,
    speed=0
)

# sentry.register_module(
#     "Tacx Trainer",
#     TacxStart,
#     ("EAAA3D1F-6760-4D77-961E-8DDAC1CC9AED", ),
#     TacxGet,
#     speed=0
# )


sentry.start_server()