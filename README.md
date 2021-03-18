# PyElant
## Python Easy Language Translator

PyElant is a simple python tool for performing translations and storing it on the clipboard.
Input can be received via microphone, command line or the clipboard itself. 
This programs runs in the background so you can easily translate on the go and paste it in multiple programs such as text editors, browsers or programming tools easily without changing your current window.

## Installation Instructions
You can install this package either via pip or via repository download. 

```sh
pip3 install pyelant
```

### Third party requirements

To run this program on _Debian_ distros you need to install the following dependencies:

```sh
sudo apt install sudo apt-get install xsel   # To have proper access to the clipboard
sudo apt install portaudio19-dev python-pyaudio   # Only if you want to use the microphone input
```
For the [Speech Recognition](https://github.com/Uberi/speech_recognition) library, please visit their repository for more details.
For other python packages required to run this program read `requirements.txt`.

## Usage

There are three ways of using pyelant:
1. Voice input via microphone
2. Input text via clipboard
3. Input text via command line

### 1. Via microphone
First, initiate the program using the command line and let it run on the background:
```sh
python3 -m pyelant 
```
Then press `CTRL + ALT + M` to start listening. Say something and wait for the program to execute the translation.
Once it's done, it will automatically place it in your clipboard, so you can easily paste it wherever you want.

### 2. Via clipboard
First, initiate the program using the command line and let it run on the background:
```sh
python3 -m pyelant 
```
Then press `CTRL + ALT + E` to translate the text that is already in your clipboard. 
Once it's done, it will automatically place it in your clipboard, so you can easily paste it wherever you want.

### 3. Via command line
First, run the program with the `-t` or `--text` argument
```sh
python3 -m pyelant -t "This sentence will be translated to Japanese."
```
And it will automatically store the translation in your clipboard.

## Choosing languages
python3 -m PyElant comes by default with English as the input language and Japanese as the output language.
Currently the program can only accept a single pair of languages per execution, meaning that you need to close the program to change languages.
To translate other languages use the `-i` or `--input_language` and `-o` or `--output_language` as follows:
```sh
python3 -m pyelant -i pt -o en   # To run in the background and translate from Portuguese to English
python3 -m pyelant -i fr -o kr   # To run in the backrground and translate from French to Korean
python3 -m pyelant -i En -o it -t "This sentence will be translated from English to Italian."
```
## Other options
To disable the system notification use `-dn` or `--disable_notification`.

## License
MIT License as described in `LICENSE.txt`.