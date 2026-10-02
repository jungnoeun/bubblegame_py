import pygame
import sys

# Pygame 초기화
pygame.init()

# 화면 크기
WIDTH = 800
HEIGHT = 600

# 게임 화면 생성
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# 게임 제목
pygame.display.set_caption("Bubble Bobble")

# FPS 설정
clock = pygame.time.Clock()

# 플레이어 설정
player = pygame.Rect(100, 500, 40, 50) 
player_speed = 5

# 점프 관련
velocity_y = 0
gravity = 0.5
jump_power = -12
on_ground = True

player_direction = 1

# 발판
platforms = [ pygame.Rect(0, 550, 800, 50),
            pygame.Rect(0, 450, 200, 20),
            pygame.Rect(400, 380, 200, 20),
            pygame.Rect(200, 300, 200, 20),
            pygame.Rect(500, 220, 200, 20)
            ]

# 적
enemy = pygame.Rect(500, 330, 40, 50) 
enemy_speed = 2 
enemy_velocity_y = 0 

# 적이 바라보는 방향 (1 = 오른쪽 / -1 = 왼쪽)
enemy_direction = 1 

# 적이 살아있는지
enemy_alive = True

# 적이 거품에 갇혔는지
enemy_trapped = False

# 거품
bubbles = []

bubble_speed = 7
bubble_max_distance = 250
bubble_rise_speed = 2

# 점수
score = 0

# 게임 상태
game_over = False

# 게임 실행
running = True

while running:

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:

            # SPACE = 거품 발사
            if event.key == pygame.K_SPACE and not game_over:

                bubble = {
                    "rect": pygame.Rect(player.centerx, player.centery, 20, 20),
                    "direction": player_direction,
                    "distance": 0,
                    "rising": False,
                    "trapped": False
                }

                bubbles.append(bubble)

            # X = 갇힌 적이 있는 거품 터뜨리기
            if event.key == pygame.K_x and not game_over:
                for bubble in bubbles:
                    if bubble["trapped"]:
                        bubble["trapped"] = False
                        enemy_alive = False
                        enemy_trapped = False

                        score += 100

                        # 해당 거품 제거
                        bubbles.remove(bubble)

                        break

    # 게임 오버가 아니라면 게임 진행
    if not game_over:
        # 키보드 입력
        keys = pygame.key.get_pressed()

        # 플레이어 좌우 이동
        if keys[pygame.K_LEFT]:
            player.x -= player_speed
            player_direction = -1

        if keys[pygame.K_RIGHT]:
            player.x += player_speed
            player_direction = 1

        # 화면 밖으로 나가지 않도록 제한
        if player.left < 0:
            player.left = 0

        if player.right > WIDTH:
            player.right = WIDTH
    

        # 점프
        if keys[pygame.K_UP] and on_ground:
            velocity_y = jump_power
            on_ground = False
    
        # 중력
        previous_bottom = player.bottom
        velocity_y += gravity
        player.y += int(velocity_y)
        on_ground = False # 바닥 충돌

        # 플레이어 발판 충돌
        for platform in platforms:
            # 플레이어가 아래로 떨어지고 있는 경우
            if velocity_y >= 0:
                horizontal_collision = (player.right > platform.left and player.left < platform.right)
                vertical_collision = (previous_bottom <= platform.top and player.bottom >= platform.top)

                if horizontal_collision and vertical_collision:
                    player.bottom = platform.top
                    velocity_y = 0
                    on_ground = True

        # 적 이동
        # 적이 살아있고 갇히지 않았을 때만 움직임
        if enemy_alive and not enemy_trapped:
            enemy.x += enemy_speed * enemy_direction

            # 적의 좌우 범위 제한
            # 벽에 닿으면 방향 변경
            if enemy.left <= 0:
                enemy.left = 0
                enemy_direction = 1

            if enemy.right >= WIDTH:
                enemy.right = WIDTH
                enemy_direction = -1

            # 적 중력
            enemy_previous_bottom = enemy.bottom
            enemy_velocity_y += gravity
            enemy.y += int(enemy_velocity_y)
            enemy_on_ground = False

        # 적 발판 충돌
            for platform in platforms:
                if enemy_velocity_y >= 0:
                    horizontal_collision = (enemy.right > platform.left and enemy.left < platform.right)

                    vertical_collision = (enemy_previous_bottom <= platform.top and enemy.bottom >= platform.top)

                    if horizontal_collision and vertical_collision:
                        enemy.bottom = platform.top
                        enemy_velocity_y = 0
                        enemy_on_ground = True


        # 플레이어와 적 충돌
        if enemy_alive and not enemy_trapped:
            if player.colliderect(enemy):
                game_over = True

        # 거품 이동
        for bubble in bubbles:

            rect = bubble["rect"]

            # 일반 거품
            if not bubble["trapped"]:
                # 아직 옆으로 이동하는 중
                if not bubble["rising"]:
                    rect.x += bubble_speed * bubble["direction"]
                    bubble["distance"] += bubble_speed

                    # 일정 거리 이동하면 위로 올라감
                    if bubble["distance"] >= bubble_max_distance:
                        bubble["rising"] = True


                # 위로 올라가는 중
                else:
                    rect.y -= bubble_rise_speed


            # 거품과 적 충돌
            if (enemy_alive
                and not enemy_trapped
                and not bubble["trapped"]
            ):

                if rect.colliderect(enemy):
                    # 적을 거품에 가둠
                    enemy_trapped = True
                    bubble["trapped"] = True

                    # 적을 거품 중앙으로 이동
                    enemy.center = rect.center    


        # 갇힌 적을 거품과 함께 이동
        for bubble in bubbles:
            if bubble["trapped"]:
                enemy.center = bubble["rect"].center


        # 화면 밖으로 나간 거품 제거
        bubbles = [
            bubble
            for bubble in bubbles
            if (
                bubble["rect"].right > 0
                and bubble["rect"].left < WIDTH
                and bubble["rect"].bottom > 0
                and bubble["rect"].top < HEIGHT
            )
        ]

    # 화면 배경
    screen.fill((30, 30, 50))

    # 발판
    for platform in platforms: 
        pygame.draw.rect( screen, (100, 180, 100), platform )

    # 플레이어
    pygame.draw.rect( screen, (255, 255, 0), player )
    pygame.draw.rect( screen, (255, 0, 0), player, 2 )

    # 적
    if enemy_alive:

        # 일반 적
        if not enemy_trapped:
            pygame.draw.rect(screen, (255, 50, 50), enemy )

        # 거품에 갇힌 적
        else:
            pygame.draw.rect(screen, (255, 50, 50), enemy )


    # 거품
    for bubble in bubbles:

        # 갇힌 거품은 조금 크게 표시
        if bubble["trapped"]:
            pygame.draw.circle(screen, (150, 220, 255), bubble["rect"].center, 20 )
            pygame.draw.circle(screen, (255, 255, 255), bubble["rect"].center, 20, 2 )

        else:
            pygame.draw.circle( screen,(150, 220, 255), bubble["rect"].center,  10)
            pygame.draw.circle( screen, (255, 255, 255), bubble["rect"].center, 10, 2 )

    # 점수
    font = pygame.font.SysFont(None, 36)

    score_text = font.render(
        f"SCORE: {score}",
        True,
        (255, 255, 255)
    )

    screen.blit(score_text,(20, 20))

    # 게임 오버
    if game_over:
        font = pygame.font.SysFont(None, 70)
        text = font.render("GAME OVER",True,(255, 255, 255) )
        text_rect = text.get_rect( center=(WIDTH // 2, HEIGHT // 2) )
        screen.blit(text, text_rect)


    # 화면 업데이트
    pygame.display.flip()

    #FPS
    clock.tick(60)



pygame.quit()
sys.exit()