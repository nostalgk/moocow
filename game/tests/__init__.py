import evennia.server.evennia_launcher as launcher

launcher.TEST_MODE = True
launcher.GAMEDIR = "."

launcher.init_game_directory(launcher.GAMEDIR)
