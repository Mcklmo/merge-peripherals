import pygame
import sys

import websocket
import rel
import json

# Constants
WIDTH = 800
HEIGHT = 600
BRICK_SIZE = 50
BRICK_COLOR = (255, 0, 0)
BRICK_COLOR_PRESSED = (255, 255, 0)
BG_COLOR = (255, 255, 255)

IP = "192.168.1.125:8081"

INPUT_MAPPING = {
    "x": "joystick__x",
    "y": "joystick__y",
    "pressed": "joystick__pressed",
    "speed": "tacx_trainer__speed" 
    
}



# Initialize Pygame
pygame.init()
pygame.font.init()


# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Input from WS")

# Initial position of the brick
BRICK_POSSITION = {
    "x": WIDTH // 2,
    "y": HEIGHT // 2
}

def on_message(ws, message):
    print(f"Recived message: {message}")
    
    data_as_json = json.loads(message)
    
    x = 1 if 0 <= data_as_json[INPUT_MAPPING["x"]] < 45 else (0 if 45 < data_as_json[INPUT_MAPPING["x"]] < 55 else -1)
    y = -1 if 0 <= data_as_json[INPUT_MAPPING["y"]] < 45 else (0 if 45 < data_as_json[INPUT_MAPPING["y"]] < 55 else 1)
    
    speed = data_as_json[INPUT_MAPPING["speed"]]*3
    pressed = data_as_json[INPUT_MAPPING["pressed"]]
    
    
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Move the brick
    BRICK_POSSITION["x"] -= x*speed
    BRICK_POSSITION["y"] -= y*speed


    # Ensure the brick stays within the window
    BRICK_POSSITION["x"] = max(0, min(WIDTH - BRICK_SIZE, BRICK_POSSITION["x"]))
    BRICK_POSSITION["y"] = max(0, min(HEIGHT - BRICK_SIZE, BRICK_POSSITION["y"]))

    # Fill the background color
    screen.fill(BG_COLOR)

    # Draw the brick
    pygame.draw.rect(screen, BRICK_COLOR if not pressed else BRICK_COLOR_PRESSED, (BRICK_POSSITION["x"], BRICK_POSSITION["y"], BRICK_SIZE, BRICK_SIZE))
    
    text = pygame.font.SysFont('Comic Sans MS', 13).render(f"Speed: {round(speed,2)}, X: {round(BRICK_POSSITION['x'], 2)}, Y: {round(BRICK_POSSITION['y'],2)}, Pressed: {pressed}", True, (0, 0, 0))
    text_rect = text.get_rect(center=(160, 20))
    screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    #pygame.time.Clock().tick(60)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

websocket.enableTrace(True)
ws = websocket.WebSocketApp(f"ws://{IP}",
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)


ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
rel.signal(2, rel.abort)  # Keyboard Interrupt
rel.dispatch()


