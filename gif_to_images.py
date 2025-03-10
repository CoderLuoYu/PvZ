import pygame
import image_loader

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Plant vs Zombie")

image = pygame.image.load(r"C:\PythonProject\pythonProject1\植物大战僵尸\element\Others\Card\Blover.jpg").convert_alpha()
image_loader = image_loader.ImageLoader()
new_image = image_loader.create_cooldown_effect(image, 40)
while True:
    screen.blit(new_image, (0, 0))
    # pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.display.update()