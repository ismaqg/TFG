from tkinter import *
from tkinter import messagebox

from MainScreen import MainScreen
from Person import ActivePerson
from ClaimKit_screen import ClaimKit_screen
from SubmitSample_screen import SubmitSample_screen
import constants
import DBcontroller
import Screen_manager
import Language_controller

class MainScreen_user(MainScreen):  # singleton 

    __instance = None

    @staticmethod
    def getInstance():
        if MainScreen_user.__instance == None:
            MainScreen_user()
        return MainScreen_user.__instance

    def __init__(self):
        if MainScreen_user.__instance != None:
            Screen_manager.get_root().destroy()
            raise Exception("MainScreen_operator class is singleton")
        else:
            MainScreen.create_main_frames()

            # NO .grid, because the main_screen_frame is shared with other classes. The .grid is done in "go_to_main_screen"

            self.__title = Label(MainScreen._ms_header_frame, text = Language_controller.get_message("título usuario") + "UNKNOWN CIP", bg = constants.CATSALUT_COLOR, font = (constants.CATSALUT_TEXT_FONT, constants.SCREEN_TITLE_TEXT_SIZE, 'bold'))  # The "unknown cip" is changed when the programe goes to this screen
            self.__info_b = Button(MainScreen._ms_header_frame, text = Language_controller.get_message("¿qué hago?"), font = (constants.CATSALUT_TEXT_FONT, constants.BUTTON_TEXT_SIZE, 'bold'), borderwidth=5, command = self.__show_usage_info)
            self.__logout_b = Button(MainScreen._ms_header_frame, text = Language_controller.get_message("texto botón cerrar sesión para usuario"), borderwidth=5, font = (constants.CATSALUT_TEXT_FONT, constants.BUTTON_TEXT_SIZE, 'bold'), fg="red", command = self.logOut_button) 
            
            self.__claim_kit_b = Button(MainScreen._ms_body_frame, text = Language_controller.get_message("obtener un kit"), font = (constants.CATSALUT_TEXT_FONT, constants.BUTTON_TEXT_SIZE, 'bold'), borderwidth=5, command = ClaimKit_screen.getInstance().go_to_claimKit_screen)
            self.__submit_sample_b = Button(MainScreen._ms_body_frame, text = Language_controller.get_message("entregar una muestra"), font = (constants.CATSALUT_TEXT_FONT, constants.BUTTON_TEXT_SIZE, 'bold'), borderwidth=5, command = SubmitSample_screen.getInstance().go_to_submitSample_screen)
            
            MainScreen_user.__instance = self


    def __show_usage_info(self):
        messagebox.showinfo(Language_controller.get_message("respuesta al ¿qué hago? (cabecera)"), Language_controller.get_message("respuesta al ¿qué hago? (cuerpo)"))

    # changes the texts to the current language. This function is called by Language_controller when a new language is setted
    def change_language(self):
        self.__logout_b["text"] = Language_controller.get_message("texto botón cerrar sesión para usuario")
        self.__claim_kit_b["text"] = Language_controller.get_message("obtener un kit")
        self.__submit_sample_b["text"] = Language_controller.get_message("entregar una muestra")
        self.__info_b["text"] = Language_controller.get_message("¿qué hago?")
        # title text is changed every time that the program goes to main screen

    # override abstract parent method
    def go_to_main_screen(self):
        # column and row configure (because the configuration of the frames is not the same as the user main screen):
        MainScreen._user_header_frame_rowcolumn_configure()
        MainScreen._user_body_frame_rowcolumn_configure()

        # change the text because maybe we have a new user
        self.__title["text"] = Language_controller.get_message("título usuario") + ActivePerson.getCurrent().get_CIP()

        # .grids are here and not in constructor because MainScreen_admin, MainScreen_operator and MainScreen_user share the same frame (the main screen frame where this widgets are displayed)
        self.__title.grid(row = 0, column = 0, sticky = 'NSEW')
        self.__info_b.grid(row = 0, column = 1, sticky = 'NSEW', padx = (10, 5), pady = 10)
        self.__logout_b.grid(row = 0, column = 2, sticky = 'NSEW', padx = (5, 10), pady = 10)

        if not DBcontroller.user_has_kit() or ActivePerson.getCurrent().get_has_submitted_in_this_session():  # actually checking if the user has delivered a sample in that session is redundant because when he/she delivers a sample the session closes inmediately
            self.__submit_sample_b["state"] = DISABLED
        else: 
            self.__submit_sample_b["state"] = NORMAL
        
        if ActivePerson.getCurrent().get_has_claimed_kit_in_this_session():
            self.__claim_kit_b["state"] = DISABLED
        else:
            self.__claim_kit_b["state"] = NORMAL

        self.__claim_kit_b.grid(row = 0, column = 0, sticky = 'NSEW', padx = (10, 5), pady = 10)
        self.__submit_sample_b.grid(row = 0, column = 1, sticky = 'NSEW', padx = (5, 10), pady = 10)
        

        MainScreen._main_screen_frame.tkraise()

    # override abstract parent method
    def erase_mainScreen_contents(self):
        self.__title.grid_forget()
        self.__logout_b.grid_forget()

        self.__claim_kit_b.grid_forget()
        self.__submit_sample_b.grid_forget()
        self.__info_b.grid_forget()

    # override abstract parent method
    def logOut_button(self):
        logout = messagebox.askyesno(Language_controller.get_message("mensaje cierre sesión (cabecera)"), Language_controller.get_message("mensaje cierre sesión (cuerpo)"))
        if logout == True:
            self.erase_mainScreen_contents()
            ActivePerson.getCurrent().logOut()
        