
screen_width = 800
screen_height = 600
background_image = 'images/background.jpg'

frame_rate = 90

row_count = 6
brick_width = 60
brick_height = 20
brick_color =(155, 48, 255)
offset_y = brick_height + 10

ball_speed = 3
ball_radius = 8
ball_color =(255, 255, 0)

paddle_width = 80
paddle_height = 20
paddle_color = (240, 248, 255)
paddle_speed = 6

status_offset_y = 5

text_color = (255, 255, 0)
initial_lives = 3
lives_right_offset = 85
lives_offset = screen_width - lives_right_offset
score_offset = 5

font_name = 'Arial'
font_size = 20

effect_duration = 20

sounds_effects = dict(
    brick_hit='sound_effects/brick_hit.wav',
    effect_done='sound_effects/effect_done.wav',
    paddle_hit='sound_effects/paddle_hit.wav',
    level_complete='sound_effects/level_complete.wav',
)

message_duration = 2

button_text_color = (255, 255, 255)

menu_offset_x = 20
menu_offset_y = 300
menu_button_w = 80
menu_button_h = 50
