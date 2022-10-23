import os
import pygame
import time


class Char:  # This class is used to represent each character.
    def __init__(self, img, name, selected=False):
        self.img = img  # The image of the character
        self.selected = selected  # Whether or not the user has marked the character as dead.
        self.collide = 0  # Set to 0 at first, later and used to check if the user clicked the image.
        self.name = name  # File name of the character

    def __repr__(self):
        return f"Char: {self.name}, collide: {self.collide}, selected: {self.selected}, img: {self.img}"


class Application(object):
    settings = {}
    images = {}
    current_game_folder = ""  # What folder the program will use images from
    game_names = []  # All the subfolders
    settings_file_name = "settings.txt"
    screen = None

    window_width = 400
    window_height = 830
    picture_size = 50
    resized_images = {}

    collision_list = []
    selected_characters = []
    character_matrix = [[]]
    char_dict = {}

    image_changed = True

    # Used to check if these keys are being held by the user.
    control_held = False
    shift_held = False

    def __init__(self):
        self.__initialize_images()

        # Start out by initializing our default settings
        self.init_default_settings()
        # afterwards override the settings from the file
        self.load_settings()
        self.initialize_game_list()
        self.current_game_folder = self.game_names[self.settings["current_game"]]
        self.rebuild_character_matrix(self.current_game_folder)
        self.__build_main_display()

    def loop(self):
        time_to_sleep = .01
        done = False
        while not done:
            click_position = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Checks what the user clicked.
                        self.handle_mouse_click(click_position)
            time.sleep(time_to_sleep)

    def __build_main_display(self):
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        screen.fill("black")

        pygame.display.set_caption("FE Death Counter")
        font = pygame.font.SysFont("Times New Roman", 30, False, False)
        pygame.font.SysFont("Times New Roman", 20, False, False)

        self.rendered_image = pygame.Surface((self.settings["display_x"], self.settings["display_y"])) \
            .convert_alpha()
        self.rendered_image.fill(
            (self.settings["bg_red"], self.settings["bg_green"], self.settings["bg_blue"], self.settings["bg_alpha"]))

        # Text
        size_text = font.render("Char Size: " + str(self.settings["main_size"]), True, "white")
        game_text = font.render(f"Game: {self.settings['current_game']}", True, "white")
        image_text = font.render("Output Size", True, "white")
        image_size_text = font.render(f'{self.settings["display_x"]} x {self.settings["display_y"]})', True, "white")
        color_text = font.render("BG Color:", True, "white")
        red_text = font.render(str(self.settings["bg_red"]), True, "red")
        green_text = font.render(str(self.settings["bg_green"]), True, "green")
        blue_text = font.render(str(self.settings["bg_blue"]), True, "blue")
        opacity_text = font.render(str(self.settings["bg_alpha"]), True, "white")

        # Displaying text and images
        screen.blit(size_text, (0, 700))
        screen.blit(game_text, (0, 650))
        screen.blit(image_text, (215, 700))
        screen.blit(image_size_text, (220, 730))
        screen.blit(color_text, (0, 770))
        screen.blit(red_text, (130, 770))
        screen.blit(green_text, (185, 770))
        screen.blit(blue_text, (240, 770))
        screen.blit(opacity_text, (295, 770))

        self.plusClick = screen.blit(self.images["plus"], (100, 740))
        self.minusClick = screen.blit(self.images["minus"], (50, 740))
        self.previous_game_arrow = screen.blit(self.images["left"], (200, 660))
        self.next_game_arrow = screen.blit(self.images["right"], (250, 660))

        self.output_x_minus = screen.blit(self.images["small_minus"], (220, 760))
        self.output_x_plus = screen.blit(self.images["small_plus"], (240, 760))

        self.output_y_minus = screen.blit(self.images["small_minus"], (300, 760))
        self.output_y_plus = screen.blit(self.images["small_plus"], (320, 760))

        self.red_minus = screen.blit(self.images["small_minus"], (130, 800))
        self.red_plus = screen.blit(self.images["small_plus"], (160, 800))

        self.green_minus = screen.blit(self.images["small_minus"], (185, 800))
        self.green_plus = screen.blit(self.images["small_plus"], (210, 800))

        self.blue_minus = screen.blit(self.images["small_minus"], (240, 800))
        self.blue_plus = screen.blit(self.images["small_plus"], (270, 800))

        self.opacity_minus = screen.blit(self.images["small_minus"], (295, 800))
        self.opacity_plus = screen.blit(self.images["small_plus"], (325, 800))
        self.show_characters_in_window(screen)
        self.render_image()
        self.screen = screen
        pygame.display.flip()

    def show_characters_in_window(self, screen):
        if screen is None:
            return
        size = self.picture_size
        self.collision_list = []
        # Goes through the list of characters and displays them as they are organized in the 2D array..
        for j, row in enumerate(self.character_matrix):
            for i, char in enumerate(row):
                char.collide = screen.blit(pygame.transform.scale(char.img, (size, size)),
                                           [self.picture_size * i, j * self.picture_size])
                self.collision_list.append(char)
                if char.selected:  # Displays an "x" over any character who has been marked as dead.
                    screen.blit(self.images["rip"], [self.picture_size * i, j * self.picture_size])

    def render_image(self):
        main_size = self.settings["main_size"]
        i, j = 0, 0
        max_per_row = self.settings["display_x"] // main_size
        for c in self.selected_characters:
            char = self.char_dict[c]
            if char.name in self.resized_images:
                resized_image = self.resized_images[char.name]
            else:
                resized_image = pygame.transform.scale(char.img, (main_size, main_size))
                self.resized_images[char.name] = resized_image

            self.rendered_image.blit(resized_image, [i * main_size, j * main_size])
            i += 1
            if i >= max_per_row:
                i = 0
                j += 1

        if self.image_changed:
            self.image_changed = False  # prevents the image from saving again until another change is made
            while True:
                try:
                    pygame.image.save(self.rendered_image, "output.png")
                    break
                except pygame.error:
                    continue

    def handle_mouse_click(self, clicked_pos):
        # https://stackoverflow.com/questions/9961563/how-can-i-make-a-sprite-move-when-key-is-held-down
        keys = pygame.key.get_pressed()
        self.control_held = keys[pygame.K_LCTRL]
        self.shift_held = keys[pygame.K_LSHIFT]

        # Plus/Minus Clicks
        event_handled = False
        if self.plusClick.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("main_size", True, 1, 1000)
        elif self.minusClick.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("main_size", False, 1, 1000)
        elif self.output_x_plus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("display_x", True, 1, 2500)
        elif self.output_x_minus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("display_x", False, 1, 2500)
        elif self.output_y_plus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("display_y", True, 1, 2500)
        elif self.output_y_minus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("display_y", False, 1, 2500)
        elif self.red_plus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("bg_red", True, 0, 255)
        elif self.red_minus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("bg_red", False, 0, 255)
        elif self.green_plus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("bg_green", True, 0, 255)
        elif self.green_minus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("bg_green", False, 0, 255)
        elif self.blue_plus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("bg_blue", True, 0, 255)
        elif self.blue_minus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("bg_blue", False, 0, 255)
        elif self.opacity_plus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("bg_alpha", True, 0, 255)
        elif self.opacity_minus.collidepoint(clicked_pos):
            event_handled &= self.handle_plus_minus("bg_alpha", False, 0, 255)

        if not event_handled:
            event_handled &= self.handle_game_change(self.settings["current_game"], clicked_pos)

        if not event_handled:
            self.handle_portrait_clicked(clicked_pos)

        self.__build_main_display()

    def handle_portrait_clicked(self, my_pos):
        for i in self.collision_list:  # Checks if the user has clicked on a character.
            if i.collide.collidepoint(my_pos) and not i.selected:  # Marks the character as dead if it isn't already
                i.selected = True
                self.selected_characters.append(i.name)
            elif i.collide.collidepoint(my_pos) and i.selected:  # Unmarks the character from being dead
                i.selected = False
                self.selected_characters.remove(i.name)
                self.resized_images.pop(i.name)
        self.image_changed = True

        # Rewrites the list of dead characters with the updated information.
        with open(self.current_game_folder + '/dead.txt', 'w+') as f:
            for line in self.selected_characters:
                f.write(line)
                f.write('\n')

    def initialize_game_list(self):
        # Taken from https://stackoverflow.com/questions/141291/how-to-list-only-top-level-directories-in-python
        root, dir_names, filenames = next(os.walk('.'))
        if len(dir_names) > 0:
            self.game_names = dir_names.copy()

    def __initialize_images(self):
        self.images["plus"] = pygame.image.load("plus.png")
        self.images["minus"] = pygame.image.load("minus.png")
        self.images["left"] = pygame.image.load("left.png")
        self.images["right"] = pygame.image.load("right.png")
        self.images["off"] = pygame.image.load("off.png")
        # self.images["on"] = pygame.image.load("on.png")

        icon = pygame.image.load('icon.ico')
        pygame.display.set_icon(icon)

        self.images["small_plus"] = pygame.transform.scale(self.images["plus"], (15, 15))  # for changing BG color
        self.images["small_minus"] = pygame.transform.scale(self.images["minus"], (15, 15))

        # self.images["small_on"] = pygame.transform.scale(self.images["on"], (15, 15))  # for toggling PNG saving
        self.images["small_off"] = pygame.transform.scale(self.images["off"], (15, 15))
        self.images["rip"] = pygame.transform.scale(pygame.image.load("x.png"), (self.picture_size, self.picture_size))

    def init_default_settings(self):
        self.settings["main_size"] = 100
        self.settings["current_game"] = 0
        self.settings["bg_red"] = 161
        self.settings["bg_green"] = 199
        self.settings["bg_blue"] = 150
        self.settings["bg_alpha"] = 255
        self.settings["display_x"] = 400
        self.settings["display_y"] = 400

    def load_settings(self):  # Loads the settings from the settings file.
        with open(self.settings_file_name, "r") as settingsFile:
            try:
                self.settings["main_size"] = int(settingsFile.readline().split(":")[1].strip(" ").strip("\n"))
                self.settings["current_game"] = int(settingsFile.readline().split(":")[1].strip(" ").strip("\n"))
                self.settings["bg_red"] = int(settingsFile.readline().split(":")[1].strip(" ").strip("\n"))
                self.settings["bg_green"] = int(settingsFile.readline().split(":")[1].strip(" ").strip("\n"))
                self.settings["bg_blue"] = int(settingsFile.readline().split(":")[1].strip(" ").strip("\n"))
                self.settings["bg_alpha"] = int(settingsFile.readline().split(":")[1].strip(" ").strip("\n"))
                self.settings["display_x"] = int(settingsFile.readline().split(":")[1].strip(" ").strip("\n"))
                self.settings["display_y"] = int(settingsFile.readline().split(":")[1].strip(" ").strip("\n"))
            except IndexError:
                self.write_settings()

    # Used when the program needs to update the settings file.
    def write_settings(self):
        with open("settings.txt", "w") as f:
            f.write(f"size: {self.settings['main_size']}\n")
            f.write(f"game: {self.settings['current_game']}\n")
            f.write(f"bgred: {self.settings['bg_red']}\n")
            f.write(f"bggreen: {self.settings['bg_green']}\n")
            f.write(f"bgblue: {self.settings['bg_blue']}\n")
            f.write(f"opacity: {self.settings['bg_alpha']}\n")
            f.write(f"imgx: {self.settings['display_x']}\n")
            f.write(f"imgy: {self.settings['display_y']}\n")

    def handle_game_change(self, game_index, my_pos):
        if self.previous_game_arrow.collidepoint(my_pos):  # Goes to the previous directory in the folder.
            game_index -= 1
            if game_index < 0:  # If the index is too low, and if so loops back to the end of the list.
                game_index = len(self.game_names) - 1

        elif self.next_game_arrow.collidepoint(my_pos):  # Goes to the next directory in the folder.
            game_index += 1
            if game_index > len(self.game_names) - 1:
                # Checks if the index is at the end of the list, and if so loops to the beginning of the list.
                game_index = 0
        else:
            return False
        self.settings["current_game"] = game_index
        new_game = self.game_names[game_index]  # Changes the directory that the program is taking the characters from

        # Recreates the lists the program uses to now have the characters from the specified game.
        self.current_game_folder = new_game
        self.rebuild_character_matrix(new_game)
        self.write_settings()
        return True

    def rebuild_character_matrix(self, new_game):
        self.selected_characters = []
        self.resized_images = {}
        self.character_matrix = [[]]
        max_images_in_row = self.window_width / self.picture_size
        folder_content = os.listdir(new_game)

        char_dict = dict()

        for file in folder_content:  # Add all characters for the current game to a dictionary
            if file.endswith(".png") or file.endswith(".jpg"):
                image = pygame.image.load(f'{new_game}/{file}')
                char_dict[file] = Char(image, file)

        with open(f'{new_game}/dead.txt', "r") as deaths:  # Mark the characters that are in the death file as dead
            for char in deaths:
                char = char.strip("\n")
                if char == "":
                    continue

                char_dict[char].selected = True
                self.selected_characters.append(char_dict[char].name)

        z = 0  # Represents the row number in the character_matrix array.
        for iterator, (k, char) in enumerate(char_dict.items()):  # Convert the dict into a 2d array
            if iterator % max_images_in_row == 0 and iterator != 0:
                z += 1
                self.character_matrix.append([])
            self.character_matrix[z].append(char)

        self.char_dict = char_dict
        self.show_characters_in_window(self.screen)

    # Used for the plus and minus icons.
    def handle_plus_minus(self, setting, add, lower_bound, upper_bound):
        x = int(self.settings[setting])
        change = 1
        if self.control_held and self.shift_held:
            change = 100
        elif self.control_held:
            change = 10
        elif self.shift_held:
            change = 50

        x = x + change if add else x - change

        if x < lower_bound:
            x = lower_bound
        elif x > upper_bound:
            x = upper_bound

        self.settings[setting] = x
        self.write_settings()
        return True


def main():
    pygame.init()
    a = Application()
    a.loop()
    pygame.quit()


if __name__ == "__main__":
    main()
