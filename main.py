import time
from datetime import datetime
from os.path import exists

import init
from init import *


# Anytime there is a promt other than the actual game
# the backround looks like the game but blackened
def background_game():
    # draw standard images
    for img, pos in images:
        WIN.blit(img, pos)
    # draw a zero-ed timer
    timer = font.render('00:00:00', True, WHITE)
    WIN.blit(timer, (480, 0))
    # draw a black rectangle with the opacity turned down
    s = pygame.Surface((1000, 750))
    s.set_alpha(220)
    s.fill((0, 0, 0))
    WIN.blit(s, (0, 0))


# The screen that promots the user to input their name
def name_screen():
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 55)
    text_pos = (WIDTH // 2 - 230, HEIGHT // 2 - 180)
    # colors of box when active and inactive
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    # needs separate event loop
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            # write users input on textbox
            if event.type == pygame.KEYDOWN:
                if active:
                    # cant enter blank name
                    if event.key == pygame.K_RETURN and text == '':
                        text = text[:-1]
                    # if text is not blank and enter, end function
                    elif event.key == pygame.K_RETURN and text != '':
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    # name cant have spaces, messes up scoreboard file
                    elif event.key == pygame.K_SPACE:
                        pass
                    else:
                        text += event.unicode

        background_game()

        # Render the current text.
        txt_surface = font.render(text, True, color)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        # Blit the text.
        WIN.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        # Blit the input_box rect.
        pygame.draw.rect(WIN, color, input_box, 2)

        manual_text = small_font.render('(Click on the box, write your name and press enter)', True, WHITE)
        WIN.blit(intro_text, text_pos)
        WIN.blit(manual_text, (110, 250))

        pygame.display.update()
        clock.tick(FPS)


# After player enters name, we go into the 'press space to begin prompt'
# As well as directions on how to play
# We just draw the screen before game
# Space input is handled in main game loop
def draw_begin_game():
    text_pos = (WIDTH // 2 - 260, HEIGHT // 2 + 100)
    manual_text = med_font.render('Use Up, Down, Left, Right arrow keys to move the car', True, WHITE)
    background_game()
    WIN.blit(space_to_play, text_pos)
    WIN.blit(manual_text, (20, 200))


# Save score inside a plain txt file
# USER MUST NOT EDIT THAT FILE
# EVERYTHING IS HANDLED HERE
def save_score(name, score):
    # if file does not exist just write name, score, datetime
    if not exists('scoreboard.txt'):
        f = open("scoreboard.txt", "w")
        f.write(name + ' ' + score + ' ' + datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + '\n')
        f.close()
    # if file exists and is not corrupt, write new score
    # then read file, sort based on time and write while file again
    else:
        try:
            scores = []
            f = open('scoreboard.txt', 'a')
            f.write(name + ' ' + score + ' ' + datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + '\n')
            f.close()
            f = open('scoreboard.txt', 'r')
            lines = f.readlines()
            for line in lines:
                n = line[0:line.find(' ')]
                line = line[line.find(' ') + 1:]
                s = line[0:line.find(' ')]
                d = line[line.find(' ') + 1:-1]
                scores.append((n, datetime.strptime(s, '%M:%S:%f'), d))
            f.close()
            scores.sort(key=lambda x: x[1])
            f = open('scoreboard.txt', 'w')
            for score in scores:
                f.write(str(score[0]) + ' ' + score[1].strftime('%M:%S:%f')[:-4] + ' ' + str(score[2]) + '\n')
            f.close()
        # if file is corrupt, create new one with just new score
        except Exception:
            print('File is corrupted, created new one')
            f = open("scoreboard.txt", "w")
            f.write(name + ' ' + score + ' ' + datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + '\n')
            f.close()


# main game loop
def game():
    done = False
    begin_game = False
    start_of_timer = datetime.now()
    timer = 0
    lap = 0
    cooldown_timer = 0
    temp_time = time.time()
    top3 = get_top_3()
    car = Car(3.5, 4, x=90, y=230)
    while not done:
        # if we are still at 'press space..' screen
        if not begin_game:
            draw_begin_game()
        if begin_game:
            # the timer is used to count how much time the user
            # took to complete course
            timer = datetime.now() - start_of_timer
            # get all keys being pressed
            keys = pygame.key.get_pressed()
            # cars velocity is determined by where exactly in the screen it is
            car.max_vel = draw_game(car, keys)
            # hud is timer, top3, current lap
            draw_hud(timer, top3, lap)

            # get car's center (position it is drawn is topleft)
            car_center = (car.pos_X + car.img.get_width() // 2, car.pos_Y + car.img.get_height() // 2)
            # temp time is used to determine that user took some time to pass the finish line for the second time
            # it is used to prevent cheating
            if time.time() - temp_time > 1:
                temp_time = time.time()
                # cooldown timer is a timer that goes down by one second
                # it is set to 7 seconds, that meaning, the user must wait 7 seconds
                # before passing the finish line every time they pass the finish line
                if cooldown_timer > 0:
                    cooldown_timer -= 1
            # If car's x pos is on the finish line and y pos is just under, while car moving up, register a lap passed
            # cooldown timer is now 7
            if FINISH_POS[0] <= car_center[0] <= FINISH_POS[0] + FINISH.get_width() and FINISH_POS[
                1] + FINISH.get_height() / 2 <= car_center[1] <= FINISH_POS[1] + FINISH.get_height() / 2 + 4 and keys[
                pygame.K_UP] and cooldown_timer == 0:
                lap += 1
                cooldown_timer = 7
            # update car's pos based on user input
            if keys[pygame.K_UP] and car_center[1] - car.max_vel > 0:
                car.pos_Y -= car.max_vel
            if keys[pygame.K_DOWN] and car_center[1] + car.max_vel < HEIGHT:
                car.pos_Y += car.max_vel
            if keys[pygame.K_LEFT] and car_center[0] - car.max_vel > 0:
                car.pos_X -= car.max_vel
            if keys[pygame.K_RIGHT] and car_center[0] + car.max_vel < WIDTH:
                car.pos_X += car.max_vel

            # end game when user completes 2 whole laps
            if lap == 3:
                timer = str(timer)[2:-4]
                timer = timer.replace('.', ':')
                return timer

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    begin_game = True
                ### FOR DEBUG ###
                # can press 0 to terminate game
                if event.key == pygame.K_0 and begin_game:
                    done = True
                    timer = str(timer)[2:-4]
                    timer = timer.replace('.', ':')
                    return timer
                ### FOR DEBUG ###

        clock.tick(FPS)
        pygame.display.update()


# draw all standard images
# also get pixel color under car
# if color is the street's color, velocity is normal
# otherwise speed is reduced
# Depending on what keys are being pressed, car is drawn at different angle
def draw_game(car, keys):
    for img, pos in images:
        WIN.blit(img, pos)
    color_under_car = WIN.get_at(
        (int(car.pos_X + car.img.get_width() // 2), int(car.pos_Y + car.img.get_height() // 2)))
    WIN.blit(FINISH, FINISH_POS)
    if keys[pygame.K_LEFT] and keys[pygame.K_UP]:
        car.draw(WIN, 45)
        init.last_angle = 45
    elif keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
        car.draw(WIN, 315)
        init.last_angle = 315
    elif keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
        car.draw(WIN, 135)
        init.last_angle = 135
    elif keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
        car.draw(WIN, 225)
        init.last_angle = 225
    elif keys[pygame.K_UP]:
        car.draw(WIN, 0)
        init.last_angle = 0
    elif keys[pygame.K_DOWN]:
        car.draw(WIN, 180)
        init.last_angle = 180
    elif keys[pygame.K_RIGHT]:
        car.draw(WIN, 270)
        init.last_angle = 270
    elif keys[pygame.K_LEFT]:
        car.draw(WIN, 90)
        init.last_angle = 90
    else:
        car.draw(WIN, init.last_angle)
    if color_under_car == (111, 112, 116, 255):
        return 3.5
    else:
        return 0.6


# returns a list of the top 3 names and scores from scoreboard file
def get_top_3():
    try:
        f = open('scoreboard.txt', 'r')
        lines = f.readlines()
        cnt = 0
        res = []
        for line in lines:
            if cnt < 3:
                n = line[0:line.find(' ')]
                line = line[line.find(' ') + 1:]
                s = line[0:line.find(' ')]
                d = line[line.find(' ') + 1:-1]
                res.append(n)
                res.append(s)
                res.append(d)
                cnt += 1
            else:
                break
        f.close()
        return res
    except FileNotFoundError:
        return []


# draws timer, lap
# tries to draw top3
# if there are less people in the scoreboard, this way of retrieving the top3 throws exception
# So we just draw all that don't throw exceptions
def draw_hud(timer, top3, lap):
    timer = font.render(str(timer)[2:-4], True, WHITE)
    lap_count = font.render(f'Lap: {lap}/2', True, WHITE)
    WIN.blit(timer, (490, 0))
    WIN.blit(lap_count, (490, 60))

    try:
        name1 = small_font.render(top3[0], True, WHITE)
        time1 = small_font.render(top3[1], True, WHITE)
        date1 = small_font.render(top3[2], True, WHITE)
        WIN.blit(name1, (40, 15))
        WIN.blit(time1, (180, 15))
        WIN.blit(date1, (280, 15))
    except IndexError:
        pass

    try:
        name2 = small_font.render(top3[3], True, WHITE)
        time2 = small_font.render(top3[4], True, WHITE)
        date2 = small_font.render(top3[5], True, WHITE)
        WIN.blit(name2, (40, 50))
        WIN.blit(time2, (180, 50))
        WIN.blit(date2, (280, 50))
    except IndexError:
        pass

    try:
        name3 = small_font.render(top3[6], True, WHITE)
        time3 = small_font.render(top3[7], True, WHITE)
        date3 = small_font.render(top3[8], True, WHITE)
        WIN.blit(name3, (40, 85))
        WIN.blit(time3, (180, 85))
        WIN.blit(date3, (280, 85))
    except IndexError:
        pass


# After playing the game, player is presented with a play again screen,
# displaying their score
def play_again(timer):
    done = False
    quit_text = font.render('Quit', True, WHITE)
    play_again_text = font.render('Play again', True, WHITE)
    timer_text = font.render('Your time: ' + timer, True, WHITE)
    while not done:
        clock.tick(FPS)
        background_game()
        # 2 buttons (play again, quit)
        mouse = pygame.mouse.get_pos()

        WIN.blit(timer_text, (100, 200))

        # Play again button
        if 40 <= mouse[0] <= 310 and 270 <= mouse[1] <= 370:
            pygame.draw.rect(WIN, color_light, [40, 270, 270, 100])
        else:
            pygame.draw.rect(WIN, color_dark, [40, 270, 270, 100])
        WIN.blit(play_again_text, (45, 295))

        # Quit button
        if 390 <= mouse[0] <= 660 and 270 <= mouse[1] <= 370:
            pygame.draw.rect(WIN, color_light, [390, 270, 270, 100])
        else:
            pygame.draw.rect(WIN, color_dark, [390, 270, 270, 100])
        WIN.blit(quit_text, (470, 295))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 350 <= mouse[0] <= 650 and 270 <= mouse[1] <= 370:
                    return False
                if 40 <= mouse[0] <= 310 and 270 <= mouse[1] <= 370:
                    return True


# main driver function
# begin by getting name
# get time by playing game
# save score
# play_again() returns the player's choice
def start():
    name = name_screen()
    timer = game()
    save_score(name, timer)
    return play_again(timer)


# this function runs all the times that start() gives true
# meaning player wants to play again
# if player wants to quit, just present a screen 'thank you for playing'
# and game is terminated
def main():
    while start():
        print('New game started!')

    start_time = time.time()

    text_pos = (WIDTH // 2 - 245, HEIGHT // 2 - 100)
    while True:
        clock.tick(FPS)
        background_game()
        WIN.blit(outro_text, text_pos)
        pygame.display.update()

        if time.time() - start_time > 0.7:
            pygame.quit()
            quit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


if __name__ == '__main__':
    main()
