#!/usr/bin/env python3

"""
Python Easy Language Translator PyElant is a python tool for easily performing
translations and storing it on the clipboard.
Input can be received via microphone, command line or the clipboard itself.

 @brief   PyElant
 @author  Paulo Marcos
 @date    2021-03-19
 Copyright (c) 2021 paulomarcos@me.com
"""

# pylint: disable-msg=C0103
import sys
import speech_recognition as sr
from googletrans import Translator
from pynput import keyboard
import pyperclip
import notify2


class PyElant:
    """ PyElant class """

    def __init__(self, input_language, output_language, text, disable_notification, verbose):
        self.input_language = input_language
        self.output_language = output_language
        self.text = text
        self.disable_notification = disable_notification
        self.verbose = verbose

        kk = keyboard.Key
        self.combination_clipboard = {kk.alt, kk.ctrl, keyboard.KeyCode.from_char('e')}
        self.combination_microphone = {kk.alt, kk.ctrl, keyboard.KeyCode.from_char('m')}
        self.current = set()
        self.listener = None

        if self.input_language is None:
            self.input_language = "en"
        if self.output_language is None:
            self.output_language = "ja"

        if self.text is not None:
            PyElant.translate_text(self.text)
            sys.exit(0)

        PyElant.background_translator(self)

    def background_translator(self):
        """ Runs in the background and waits for key press """
        with keyboard.Listener(on_press=lambda event: PyElant.on_press(self, event),
                               on_release=lambda event: PyElant.on_release(self, event)) as self.listener:
            self.listener.join()
    
    def clipboard_translator(self):
        """ Translates from the clipboard back to itself """
        self.text = pyperclip.paste()
        PyElant.translate_text(self)

    def start_listening(self):
        """ Start listening for microphone input """
        # obtain audio from the microphone
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            PyElant.printv(self.verbose, "Say something")
            audio = recognizer.listen(source)

        # recognize speech using Google Speech Recognition
        try:
            self.text = recognizer.recognize_google(audio, language=self.input_language)
            PyElant.translate_text(self)
        except sr.UnknownValueError:
            PyElant.printv(self.verbose, "Speech Recognition could not understand audio")
        except sr.RequestError as error:
            PyElant.printv(self.verbose, "Could not request results from Speech Recognition service; {0}".format(error))

    def on_press(self, key):
        """ Detects key press and performs either translation via microphone or clipboard """
        if key in self.combination_clipboard:
            self.current.add(key)
            if all(k in self.current for k in self.combination_clipboard):
                PyElant.clipboard_translator(self)
        if key in self.combination_microphone:
            self.current.add(key)
            if all(k in self.current for k in self.combination_microphone):
                PyElant.start_listening(self)
        if key == keyboard.Key.esc:
            self.listener.stop()

    def on_release(self, key):
        """ Detects key release to reset key buffer """
        try:
            self.current.remove(key)
        except KeyError:
            pass

    def translate_text(self):
        """ Translates text from a specified input language to the specified output language """
        try:
            TRANSLATOR = Translator()
            result = TRANSLATOR.translate(self.text,
                                          src=self.input_language,
                                          dest=self.output_language)
            PyElant.printv(self.verbose, "Input: {}".format(self.text))
            PyElant.printv(self.verbose, "Output: {}".format(result.text))
            pyperclip.copy(result.text)
        except ValueError as error:
            PyElant.printv(self.verbose, "Error found.")
            sys.exit(error)
        if not self.disable_notification:
            notify2.init('pyelant')
            notify = notify2.Notification(self.text,
                                          result.text + " was copied to the clipboard",
                                          "notification-message-im"   # Icon name
                                         )
            notify.show()
        
    @staticmethod
    def printv(verbose, text):
        """ Print message if verbose is on """
        if verbose:
            print(text)
