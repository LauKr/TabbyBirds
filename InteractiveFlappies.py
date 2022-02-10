import random

import pygame
import pygame_menu
import os
import configparser
import sqlite3
from datetime import date
pygame.font.init()
pygame.get_init()
configParser = configparser.RawConfigParser()
configFilePath = os.path.join(os.path.dirname(__file__), 'game.cfg')
configParser.read(configFilePath)


# Game-Speed and difficulty in a sense
VELOCITY = configParser.getint("difficulty", "VELOCITY")
PIPE_DISTANCE = configParser.getint("difficulty", "PIPE_DISTANCE")
PIPE_GAP = configParser.getint("difficulty", "PIPE_GAP")


WIN_WIDTH = configParser.getint("window", "WIN_WIDTH")
WIN_HEIGHT = configParser.getint("window", "WIN_HEIGHT")


BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

difficulty = 1
name = "Anonymous"


def end_game(win, score: int, user_name: str):
    def render_multi_line(text, x, y, fsize):
        lines = text.splitlines()
        for i, l in enumerate(lines):
            win.blit(STAT_FONT.render(l, 1, (255, 255, 255)), (x, y + fsize * i))

    got_highscore = write_leaderboard(score=score, write_name=user_name)
    win.blit(BG_IMG, (0, 0))
    if got_highscore:
        text = f"Game ended\nYou scored: {score}\nThat's good!\nPress Space"
    else:
        text = f"Game ended\nYou scored: {score}\nPress Space"
    render_multi_line(text, 100, 200, 50)
    pygame.display.update()
    clock = pygame.time.Clock()
    ending = True
    while ending:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ending = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ending = False
    pygame.quit()
    quit()


def begin_game(surface):
    global difficulty
    global name

    def set_difficulty(value, my_difficulty):
        global difficulty
        difficulty = my_difficulty

    def get_name(my_name):
        global name
        print("Player name is ", my_name)
        name = my_name

    def start_the_game():
        global difficulty
        global name
        with open("game_variables.transfer", 'w') as f:
            f.write("Difficulty:{}\n".format(difficulty))
            f.write("Name:{}\n".format(name))
        menu.close()

    def draw_bg():
        surface.blit(BG_IMG, (0, 0))

    def show_highscores():
        highscores = show_leaderboard()
        leaders = pygame_menu.Menu('Leaderboard', 400, 700, theme=pygame_menu.themes.THEME_DEFAULT,
                                   onclose=pygame_menu.events.BACK)
        leader_table = leaders.add.table()
        leader_table.default_cell_padding = 5
        for scores in highscores:
            leader_table.add_row(scores)
        leaders.add.button("Back", pygame_menu.events.BACK)
        leaders.mainloop(surface, bgfun=draw_bg)

    menu = pygame_menu.Menu('Welcome', 400, 400,
                            theme=pygame_menu.themes.THEME_BLUE, onclose=pygame_menu.events.BACK)

    menu.add.text_input('Name :', default=name, onchange=get_name)
    menu.add.selector('Difficulty :', [('Normal', 0), ('Hard', 2), ('Easy', 1)], onchange=set_difficulty, style='fancy')
    menu.add.button('Play', start_the_game)
    menu.add.button('Highscores', show_highscores)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(surface, bgfun=draw_bg)


def write_leaderboard(score: int, write_name: str):
    db_path = os.path.join(os.path.dirname(__file__), 'leaderboard.db')
    if not os.path.isfile(db_path):  # If database is missing, create new
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE scores (
            score INTEGER, 
            name TEXT, 
            date TEXT
            )""")
        conn.commit()
        cursor.close()
        conn.close()

    today = date.today().strftime('%d %B %Y')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scores ORDER BY score ASC")
    tops = cursor.fetchall()
    empty_places = len(tops) < 10
    is_leader = False
    i = 0
    for i, leader in enumerate(tops):
        if score > leader[0]:
            is_leader = True
        else:
            break
    if empty_places:  # If there are less than 10 entries, automatically add score
        is_leader = True
    if is_leader:
        # Remove last and insert here
        if not empty_places:
            cursor.execute("""DELETE FROM scores WHERE score = (SELECT MIN(score) FROM scores);""")
        cursor.execute("INSERT INTO scores VALUES (?, ?, ?)", (score, write_name, today))
        conn.commit()
    cursor.close()
    conn.close()
    return is_leader


def clear_leaderboard():
    print("Be careful!\nThis will delete ALL entries in the leaderboard.")
    really = input("Are you really sure this is what you want? (yN) ")
    if really == ("y" or "Y"):
        print("Initializing deletion...")
        db_path = os.path.join(os.path.dirname(__file__), 'leaderboard.db')
        if not os.path.isfile(db_path):  # If database is missing, create new
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE scores (
                score INTEGER, 
                name TEXT, 
                date TEXT
                )""")
            conn.commit()
            cursor.close()
            conn.close()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scores")
        conn.commit()
        cursor.close()
        conn.close()
        return 0
    else:
        print("Noting deleted")
        return 1


def show_leaderboard():
    db_path = os.path.join(os.path.dirname(__file__), 'leaderboard.db')
    if not os.path.isfile(db_path):  # If database is missing, create new
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE scores (
            score INTEGER, 
            name TEXT, 
            date TEXT
            )""")
        conn.commit()
        conn.close()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scores ORDER BY score DESC")
    tops = cursor.fetchall()
    conn.close()
    return tops


if __name__ == '__main__':
    clear_leaderboard()