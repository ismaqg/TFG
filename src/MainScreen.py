from abc import ABC, abstractmethod

from tkinter import messagebox

import constants
import DBcontroller  # needs to be imported before activePerson
from Person import ActivePerson  # to make abstract classes
import Screen_manager
import Language_controller
import Counters
import Printer_controller
from Keyboard import Numerical_keyboard




# The idea of ​​this class is that it will contain the frame of the main screen, but 3 classes will inherit from it, which must
# have access to that frame. Those 3 classes that inherit are singleton and when they are instantiated for the first and only time
# they will call the create_main_frame function of their parent.
# That method is a class method, which means that the class atributes (i.e. the frame) will have the same conent for anyone using them. So only
# the first time that create_main_frame is invoked, the frame will be created, and the next times that create_main_frame is invoked, will be ignored
# Children of this class will have access to that frame


class MainScreen(ABC): # abstract

    # class atributes. Protected.
    _main_screen_frame = None
    _ms_header_frame = None
    _ms_body_frame = None

    @classmethod
    def create_main_frames(cls):
        if (cls._main_screen_frame != None):  # check if main screen frame has already been created
            return
        cls._main_screen_frame = Screen_manager.init_screen_frame()
        cls._ms_header_frame = Screen_manager.header_frame(cls._main_screen_frame)
        cls._ms_body_frame = Screen_manager.body_frame(cls._main_screen_frame)

    @classmethod
    def _admin_and_operator_header_frame_rowcolumn_configure(cls):
        cls._ms_header_frame.columnconfigure(0, weight = 4)
        cls._ms_header_frame.columnconfigure(1, weight = 1)
        cls._ms_header_frame.columnconfigure(2, weight = 1)
        cls._ms_header_frame.rowconfigure(0, weight = 1) # it's necessary to give a weight (even though there is only one row in ms_header_frame) for sticky=NSEW of the inside widgets to work correctly

    @classmethod
    def _admin_and_operator_body_frame_rowcolumn_configure(cls):
        cls._ms_body_frame.rowconfigure(0, weight = 1)
        cls._ms_body_frame.rowconfigure(1, weight = 4)
        cls._ms_body_frame.rowconfigure(2, weight = 4)
        cls._ms_body_frame.columnconfigure(0, weight = 1)
        cls._ms_body_frame.columnconfigure(1, weight = 1)
        cls._ms_body_frame.columnconfigure(2, weight = 1)
        cls._ms_body_frame.columnconfigure(3, weight = 1)
        cls._ms_body_frame.columnconfigure(4, weight = 1)
        cls._ms_body_frame.columnconfigure(5, weight = 1)

    @classmethod
    def _user_header_frame_rowcolumn_configure(cls):
        cls._ms_header_frame.columnconfigure(0, weight = 4)
        cls._ms_header_frame.columnconfigure(1, weight = 1)
        cls._ms_header_frame.columnconfigure(2, weight = 1)
        cls._ms_header_frame.rowconfigure(0, weight = 1) # it's necessary to give a weight (even though there is only one row in ms_header_frame) for sticky=NSEW of the inside widgets to work correctly

    @classmethod
    def _user_body_frame_rowcolumn_configure(cls):
        cls._ms_body_frame.rowconfigure(0, weight = 1)
        cls._ms_body_frame.rowconfigure(1, weight = 0)
        cls._ms_body_frame.rowconfigure(2, weight = 0)
        cls._ms_body_frame.columnconfigure(0, weight = 3)
        cls._ms_body_frame.columnconfigure(1, weight = 3)
        cls._ms_body_frame.columnconfigure(2, weight = 0)
        cls._ms_body_frame.columnconfigure(3, weight = 0)
        cls._ms_body_frame.columnconfigure(4, weight = 0)
        cls._ms_body_frame.columnconfigure(5, weight = 0)


    # El operador indica cuantos kits hay después del refill por teclado (habiendo un valor máximo: el máximo aceptado por la máquina)
    def _refill_kits(numerical_keyboard):
        if numerical_keyboard.is_keyboard_alive():  # otherwise the function to check the number of refilled kits is not reprogrammed
            if not numerical_keyboard.is_number_introduced():
                # program to check the keyboard input after another 0.5 seconds:
                Screen_manager.get_root().after(500, lambda:MainScreen._refill_kits(numerical_keyboard))
            else:
                number_introduced = numerical_keyboard.get_number_introduced()
                if (number_introduced > constants.AVAILABLE_KITS_AFTER_REFILL):
                    messagebox.showwarning(Language_controller.get_message("número inválido"), str(constants.AVAILABLE_KITS_AFTER_REFILL) + Language_controller.get_message("se actualizará con el valor máximo"))
                    number_introduced = constants.AVAILABLE_KITS_AFTER_REFILL
                # set kits in the csv:
                Counters.set_available_kits(number_introduced)
                # change displayed info about kits:
                if ActivePerson.getCurrent().get_status() == "ADMIN":
                    from MainScreen_admin import MainScreen_admin
                    MainScreen_admin.getInstance().remaining_kits_info.config( text = Language_controller.get_message("avisador kits restantes") + str(Counters.get_available_kits()) + Language_controller.get_message("de") + str(constants.AVAILABLE_KITS_AFTER_REFILL), fg = Counters.get_available_kits_fg_color(), bg = Counters.get_available_kits_bg_color())
                    DBcontroller.add_new_event(ActivePerson.getCurrent().get_CIP(), "ADMINISTRATOR REPLENISHED KITS")
                else:
                    from MainScreen_operator import MainScreen_operator
                    MainScreen_operator.getInstance().remaining_kits_info.config( text = Language_controller.get_message("avisador kits restantes") + str(Counters.get_available_kits()) + Language_controller.get_message("de") + str(constants.AVAILABLE_KITS_AFTER_REFILL), fg = Counters.get_available_kits_fg_color(), bg = Counters.get_available_kits_bg_color())
                    DBcontroller.add_new_event(ActivePerson.getCurrent().get_CIP(), "OPERATOR REPLENISHED KITS")
                messagebox.showinfo( Language_controller.get_message("kits repuestos (cabecera)"), Language_controller.get_message("reposicion/recogida finalizada (cuerpo)"))


    # NOTE: In this function it is important to first print the label and then do the management with the DDBB for the following reason: Both actions could fail due to external problems (problems with the remote DB or problems with the printer). If the label is printed first and then the operation with the DDBB fails,
    # there would be no problem: The operator would find out about the failure because the program would abort and later he could try again to print and use the new printed label instead of the previous one (and in the DDBB would be shown the ID of the new printed label). On the other hand, if we first did the management
    # with the DDBBs and then printed and the printing failed, we would have the DDBBs changed but we would never obtain the label with the identification number shown in the DDBBs, so it would be a huge problem.
    @staticmethod
    def _collect_samples():
        Printer_controller.print_label(constants.MACHINE_ID + str(Counters.get_container_number()))
        messagebox.showinfo(Language_controller.get_message("efectuar recogida muestras (cabecera)"), Language_controller.get_message("efectuar recogida muestras (cuerpo)"))

        # at this point, we know that the operator/admin has stuck the printed label on the container and has picked it up, because he has pressed OK in the message on the previous line. 
        DBcontroller.insert_local_DB_sample_submissions_into_remote_DB_and_delete_local_DB_sample_submissions()
        if ActivePerson.isThereActivePerson():
            DBcontroller.add_new_event( ActivePerson.getCurrent().get_CIP(), "SAMPLES COLLECTION. Container ID: " + constants.MACHINE_ID + str(Counters.get_container_number()))
        else: # case: container full when turning on the machine
            DBcontroller.add_new_event("-", "SAMPLES COLLECTION. Container ID: " + constants.MACHINE_ID + str(Counters.get_container_number()))
        
        Counters.increment_containter_number() # this line is needed after the insertion of information in the remote DB because in that insertion is used the container number prior to the 'container_number++'
        Counters.set_stored_samples(0)
        # now, unless this function has been accessed through a 'TurningON', it returns to the admin/operation functions, where other operations are done, such as changing the value and color that represents the stored samples, or the record of the collection samples action in the info_uso database
        


    @staticmethod
    def _quit_program():  # only accessible from operator and admin
        shutdown = messagebox.askokcancel(Language_controller.get_message("apagar"), Language_controller.get_message("el programa se cerrará y la máquina se apagará"))
        if shutdown == True:
            DBcontroller.add_new_event( ActivePerson.getCurrent().get_CIP(), "PROGRAM SHUTDOWN" )
            Screen_manager.get_root().destroy()


    @abstractmethod
    def logOut_button(self):
        pass

    @abstractmethod
    def erase_mainScreen_contents(self):
        pass

    @abstractmethod
    def go_to_main_screen(self):
        pass


    