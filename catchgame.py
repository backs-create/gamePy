import pygame
import random
import os

HIGH_SCORE_FILE = "highscore.txt"

# 初期化
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Game")
clock = pygame.time.Clock()

# フォント・色
font = pygame.font.SysFont(None, 48)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 効果音
catch_sounds = {
    1: pygame.mixer.Sound("catch1.wav"),
    2: pygame.mixer.Sound("catch2.wav"),
    3: pygame.mixer.Sound("catch3.wav"),
}
miss_sound = pygame.mixer.Sound("miss.wav")
gameover_sound = pygame.mixer.Sound("gameover.wav")
combo_sound = pygame.mixer.Sound("combo.wav")
bonus_start_sound = pygame.mixer.Sound("bonus_start.wav")

# BGM
pygame.mixer.music.load("title_bgm.mp3")
pygame.mixer.music.play(-1)

# 画像
player_img = pygame.image.load("player.png")
player_img = pygame.transform.scale(player_img, (100, 40))
player_width, player_height = player_img.get_width(), player_img.get_height()
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - 60
player_speed = 12

item_images = {
    1: pygame.transform.scale(pygame.image.load("item1.png"), (40, 40)),
    2: pygame.transform.scale(pygame.image.load("item2.png"), (40, 40)),
    3: pygame.transform.scale(pygame.image.load("item3.png"), (40, 40)),
}
item_width, item_height = 40, 40
base_speed = 5
max_speed = 10

heart_image = pygame.image.load("heart.png")
heart_image = pygame.transform.scale(heart_image, (40, 40))

tree_image = pygame.image.load("tree.png")
tree_height = 300
tree_image = pygame.transform.scale(tree_image, (WIDTH, tree_height))

background_image = pygame.image.load("background.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# アイテム種類
item_types = [
    {"score": 1, "weight": 60},
    {"score": 2, "weight": 30},
    {"score": 3, "weight": 10},
]

# ボーナスタイム設定
BONUS_DURATION = 5000  # 5秒
bonus_time_active = False
bonus_time_start = 0
bonus_items = []

bonus_score = 0         # ボーナスタイム中の加算用
bonus_end_display = None  # 演出情報

# ハイスコア読み込み関数
def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except:
                return 0
    return 0

# ハイスコア保存関数
def save_high_score(score):
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(score))

def draw_text_with_outline(text, font, screen, x, y, text_color, outline_color=(255,255,255), outline_width=1):
    outline_surf = font.render(text, True, outline_color)
    text_surf = font.render(text, True, text_color)
    # 縁取りは上下左右だけでなく斜めも加えるとより綺麗
    for dx in [-outline_width, 0, outline_width]:
        for dy in [-outline_width, 0, outline_width]:
            if dx != 0 or dy != 0:
                screen.blit(outline_surf, (x + dx, y + dy))
    screen.blit(text_surf, (x, y))

def get_random_item_type():
    choices = []
    for item in item_types:
        choices += [item] * item["weight"]
    return random.choice(choices)

def draw_fancy_text(text, font, screen, x, y, base_color, outline_color, shadow_color, scale=1.0, alpha=255):
    # フォントサイズをスケールで調整
    scaled_font = pygame.font.SysFont(None, int(font.get_height() * scale), bold=True)

    # 影を描く（少し右下にずらす）
    shadow_surf = scaled_font.render(text, True, shadow_color)
    shadow_surf.set_alpha(alpha)
    screen.blit(shadow_surf, (x + 4, y + 4))

    # 縁取り（上下左右4方向）
    outline_surf = scaled_font.render(text, True, outline_color)
    outline_surf.set_alpha(alpha)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                screen.blit(outline_surf, (x + dx, y + dy))

    # 本体文字
    text_surf = scaled_font.render(text, True, base_color)
    text_surf.set_alpha(alpha)
    screen.blit(text_surf, (x, y))

def reset_game():
    global item_x, item_y, item_score, item_info,item
    global score, combo_count, combo_display, combo_text_timer
    global miss_count, game_over, item_speed, game_started
    global floating_scores, bonus_time_active, bonus_time_start
    global bonus_items,saved_high_score
    global bonus_score, bonus_end_display

    saved_high_score = False
    item_info = get_random_item_type()
    item ={
         "type": item_info,
        "x": random.randint(0, WIDTH - item_width),
        "y": 0,
        "rotation_angle": 0,
        "rotation_speed": random.uniform(-5, 5)  # -5〜5度ずつ回転
    }
    item_score = item_info["score"]
    item_x = random.randint(0, WIDTH - item_width)
    item_y = 0
    item_speed = base_speed
    score = 0
    combo_count = 0
    combo_display = ""
    combo_text_timer = 0
    miss_count = 0
    game_over = False
    game_started = False
    floating_scores = []

    bonus_time_active = False
    bonus_time_start = 0
    bonus_items = []

    bonus_score = 0         # ボーナスタイム中の加算用
    bonus_end_display = None  # 演出情報

    bonus_banner_start = 0  # ボーナスタイム演出開始時刻

high_score = load_high_score()

reset_game()

running = True
while running:
    screen.blit(background_image, (0, 0))
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not game_started:
                game_started = True
                pygame.mixer.music.stop()
                pygame.mixer.music.load("game_bgm.mp3")
                pygame.mixer.music.play(-1)
            elif game_over:
                pygame.mixer.music.stop()
                pygame.mixer.music.load("title_bgm.mp3")
                pygame.mixer.music.play(-1)
                reset_game()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_x += player_speed
    player_x = max(0, min(WIDTH - player_width, player_x))

    if not game_started:
        elapsed = (pygame.time.get_ticks() // 10) % 100
        scale = 2
        alpha = int(255 * (0.5 * ((elapsed / 50) % 2)))  # ゆっくり点滅
        draw_fancy_text("Catch Game", font, screen, WIDTH//2 - 150, HEIGHT//2 - 80,
                        base_color=(255, 215, 0),      # ゴールド色
                        outline_color=(255, 255, 255), # 白縁取り
                        shadow_color=(128, 64, 0),     # 茶色影
                        scale=scale)
        
        draw_fancy_text("Click to Start", font, screen, WIDTH//2 - 80, HEIGHT//2 + 10,
                        base_color=(255, 255, 255),
                        outline_color=(0, 0, 0),
                        shadow_color=(50, 50, 50),
                        alpha=alpha)
        
        draw_fancy_text(f"High Score: {high_score}", font, screen, 10, 10,
                        base_color=(255, 255, 255),
                        outline_color=(0, 0, 0),
                        shadow_color=(50, 50, 50),)
    elif not game_over:
        screen.blit(player_img, (player_x, player_y))
        

        if bonus_time_active:
            if current_time - bonus_time_start > BONUS_DURATION:
                bonus_time_active = False
                bonus_items.clear()
                if bonus_score > 0:
                    bonus_multiplier = 10 * (combo_count//30)
                    bonus_add = bonus_score * bonus_multiplier
                    score += bonus_add

                    bonus_end_display = {
                        "value": bonus_add,
                        "start_time": current_time
                    }
                    bonus_score = 0
            else:
                new_bonus_items = []
                for bi in bonus_items:
                    bi["y"] += item_speed * 1.5
                    bi["rotation_angle"] = (bi["rotation_angle"] + bi["rotation_speed"]) % 360
                    rotated_bonus_img = pygame.transform.rotate(item_images[bi["type"]["score"]], bi["rotation_angle"])
                    rotated_bonus_rect = rotated_bonus_img.get_rect(center=(bi["x"] + item_width // 2, bi["y"] + item_height // 2))
                    screen.blit(rotated_bonus_img, rotated_bonus_rect.topleft)
                    if (bi["y"] + item_height >= player_y and
                        player_x < bi["x"] + item_width and
                        player_x + player_width > bi["x"]):
                        score += bi["type"]["score"]
                        bonus_score += bi["type"]["score"]
                        floating_scores.append({
                            "text": f"+{bi['type']['score']}",
                            "x": bi["x"],
                            "y": bi["y"],
                            "start_time": current_time
                        })
                        if bi["type"]["score"] in catch_sounds:
                            catch_sounds[bi["type"]["score"]].play()
                    elif bi["y"] < HEIGHT:
                        new_bonus_items.append(bi)
                bonus_items = new_bonus_items

                if random.random() < 0.1:
                    bonus_items.append({
                        "type": get_random_item_type(),
                        "x": random.randint(0, WIDTH - item_width),
                        "y": random.randint(-100, 0),
                        "rotation_angle": 0,
                        "rotation_speed": random.uniform(-5, 5)
                    })

        else:
            item_speed = min(base_speed + score // 20, max_speed)
            item["y"] += item_speed
            item["rotation_angle"] = (item["rotation_angle"] + item["rotation_speed"]) % 360

            rotated_image = pygame.transform.rotate(item_images[item["type"]["score"]], item["rotation_angle"])
            rotated_rect = rotated_image.get_rect(center=(item["x"] + item_width // 2, item["y"] + item_height // 2))
            screen.blit(rotated_image, rotated_rect.topleft)

            if (item["y"] + item_height >= player_y and
                player_x < item["x"] + item_width and
                player_x + player_width > item["x"]):

                combo_count += 1

                if combo_count % 5 == 0:
                    bonus = combo_count
                    score += bonus
                    combo_display = f"Combo x{combo_count}! +{bonus}"
                    combo_text_timer = current_time
                    combo_sound.play()

                if combo_count % 30 == 0:
                    bonus_time_active = True
                    bonus_time_start = current_time
                    bonus_banner_start = current_time
                    bonus_start_sound.play()
                    bonus_items.clear()
                    for _ in range(30):
                        item_type = get_random_item_type()
                        bonus_items.append({
                            "type": item_type,
                            "x": random.randint(0, WIDTH - item_width),
                            "y": random.randint(-200, -40),
                            "rotation_angle": 0,
                            "rotation_speed": random.uniform(-5, 5)
                        })

                score += item_score
                floating_scores.append({
                    "text": f"+{item_score}",
                    "x": item["x"],
                    "y": item["y"],
                    "start_time": current_time
                })
                if item_score in catch_sounds:
                    catch_sounds[item_score].play()

                item_info = get_random_item_type()
                item_score = item_info["score"]
                item = {
                    "type": item_info,
                    "x": random.randint(0, WIDTH - item_width),
                    "y": 0,
                    "rotation_angle": 0,
                    "rotation_speed": random.uniform(-5, 5)
                }

            elif item["y"] > HEIGHT:
                miss_count += 1
                combo_count = 0
                miss_sound.play()
                if miss_count >= 3:
                    game_over = True
                    gameover_sound.play()
                else:
                    item_info = get_random_item_type()
                    item = {
                        "type": item_info,
                        "x": random.randint(0, WIDTH - item_width),
                        "y": 0,
                        "rotation_angle": 0,
                        "rotation_speed": random.uniform(-5, 5)
                    }

        screen.blit(tree_image, (0, 0))

        # UI
        draw_text_with_outline(f"Score: {score}", font, screen, 10, 10, (0, 0, 0))
        draw_text_with_outline(f"Combo: {combo_count}", font, screen, 10, 50, (0, 0, 0))

        # 大きなコンボ演出（中央、アニメ付き）
        if combo_display and current_time - combo_text_timer < 1000:
            elapsed = current_time - combo_text_timer
            alpha = max(255 - (elapsed // 4), 0)  # フェードアウト
            scale = 1.0 + (elapsed / 1000) * 0.5  # 拡大アニメ

            combo_font = pygame.font.SysFont(None, int(96 * scale))  # 拡大フォントサイズ

            # 色変化（赤〜オレンジ〜黄色あたり）
            red = min(255, 255)
            green = min(255, int(128 + (elapsed / 1000) * 127))
            blue = 0
            combo_color = (red, green, blue)

            combo_text = combo_font.render(combo_display, True, combo_color)
            combo_text.set_alpha(alpha)
            screen.blit(combo_text, (
                WIDTH // 2 - combo_text.get_width() // 2,
                HEIGHT // 2 - 100
            ))
        # BONUS TIME演出：点滅付き、黄色にオレンジ影、右から左へ流れる
        if bonus_time_active and 0 <= current_time - bonus_banner_start < 3000:
            banner_elapsed = current_time - bonus_banner_start
            banner_font = pygame.font.SysFont(None, 120, bold=True)
            text = "BONUS TIME!!!"

            # 点滅させる（0.2秒ごとにON/OFF）
            if (banner_elapsed // 200) % 2 == 0:
                banner_text = banner_font.render(text, True, (255, 255, 0))      # 黄色本体
                shadow_text = banner_font.render(text, True, (255, 140, 0))      # オレンジ影

                banner_width = banner_text.get_width()
                x_pos = WIDTH - (WIDTH + banner_width) * (banner_elapsed / 3000)
                y_pos = HEIGHT // 3

                # 影 → 本体の順で描画（影は少し下・右へずらす）
                screen.blit(shadow_text, (x_pos + 4, y_pos + 4))
                screen.blit(banner_text, (x_pos, y_pos))
    
        for i in range(3 - miss_count):
            screen.blit(heart_image, (WIDTH - (i + 1) * 50 - 10, 10))

        for fs in floating_scores[:]:
            elapsed = current_time - fs["start_time"]
            if elapsed > 1000:
                floating_scores.remove(fs)
                continue
            float_y = fs["y"] - elapsed // 20
            alpha = max(255 - elapsed // 4, 0)
            score_surf = font.render(fs["text"], True, (0, 0, 0))
            score_surf.set_alpha(alpha)
            screen.blit(score_surf, (fs["x"], float_y))

        if bonus_end_display:
            elapsed = current_time - bonus_end_display["start_time"]
            if elapsed < 2000:
                alpha = max(0, 255 - elapsed // 8)
                scale = 1.5 + (elapsed / 1000)
                bonus_font = pygame.font.SysFont(None, int(72 * scale), bold=True)
                text = f"BONUS +{bonus_end_display['value']}!"
                surf = bonus_font.render(text, True, (255, 255, 0))
                surf.set_alpha(alpha)
                screen.blit(surf, (
                    WIDTH // 2 - surf.get_width() // 2,
                    HEIGHT // 2 - 50
                ))
            else:
                bonus_end_display = None
    
    else:
        pygame.mixer.music.stop()
        if game_over and not saved_high_score:
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            saved_high_score = True
        elapsed = (pygame.time.get_ticks() // 10) % 1000
        scale = 2.0
        alpha = int(255 * (0.5 * ((elapsed / 30) % 2)))
        draw_fancy_text("Game Over", font, screen, WIDTH//2 - 120, HEIGHT//2 - 80,
                        base_color=(255, 69, 0),       # 赤オレンジ色
                        outline_color=(255, 255, 255),
                        shadow_color=(128, 0, 0),
                        scale=scale, alpha=alpha)

        draw_fancy_text("Click to Restart", font, screen, WIDTH//2 - 80, HEIGHT//2 + 10,
                        base_color=(255, 255, 255),
                        outline_color=(0, 0, 0),
                        shadow_color=(50, 50, 50))
        
        draw_fancy_text(f"High Score: {high_score}", font, screen, 10, 10,
                        base_color=(255, 255, 255),
                        outline_color=(0, 0, 0),
                        shadow_color=(50, 50, 50),)
        draw_fancy_text(f"Your Score: {score}", font, screen, WIDTH//2 -70, HEIGHT - 150,
                        base_color=(255, 255, 255),
                        outline_color=(0, 0, 0),
                        shadow_color=(50, 50, 50),)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
