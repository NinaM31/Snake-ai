from GameGUI import GameGUI

game = GameGUI()

while game.running:
    game.curr_menu.display_menu()
    game.game_loop()
