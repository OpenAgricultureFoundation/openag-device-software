import pygame
import pygame.camera
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.camera.init()

# Get camera names
camera_names = pygame.camera.list_cameras()
if camera_names == None:
    camera_names = []
print("Camera names: {}".format(camera_names))

# Get cameras
cameras = []
for camera_name in camera_names:
    cameras.append(pygame.camera.Camera(camera_name, (640, 480)))

# Get images
images = []
for camera in cameras:
    camera.start()
    images.append(camera.get_image())

# Save images
for index, image in enumerate(images):
    pygame.image.save(image, "image{}.png".format(index))
