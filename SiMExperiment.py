import json
import random
from psychopy import visual, core, event, gui
import os

# =========== Recording Libraries ============= #
import keyboard
import argparse
import queue
import sys

import sounddevice as sd
import soundfile as sf
import numpy  # Make sure NumPy is loaded before it is used in the callback
assert numpy  # avoid "imported but unused" message (W0611)
# =========== End Recording Libraries ============= #

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())


# Get user input
def showTextBox(questions):
    textBox = gui.Dlg(title='Type your response here')
    l = len(questions)
    count = 0
    answers = [""]*l
    while(count < l):
        textBox.addField(questions[count], "")
        count += 1
    textBox.show()
    count = 0
    if textBox.OK:
        while (count < l):
            answers[count] = textBox.data[count]
            count += 1
        return answers
    else:
        return answers


settingJSON = open('Settings_exp.json')
settings = json.load(settingJSON)

# Collect Text response from participant
answers = showTextBox(settings["questions"])

# Get the number of channels
channels = settings["channels"]

# Create user directory
if(settings["recordingDir"] == None):
    path = os.getcwd()
else:
    path = settings["recordingDir"]

saveLocation = path + "/" + answers[0]
os.mkdir(saveLocation)

# ================= Sentence Pre-processing ================= #
sentences_json = open(settings["filename"])
all_sentences = json.load(sentences_json)

sent_lis = []
if (settings["specifics"]):
    consider = settings["consider"]
    innerList = []
    for (key, value) in consider.items():
        for sen in value:
            innerList.append(all_sentences[key][sen])
        sent_lis.append(innerList)
        innerList = []

else:
    list_sen = []
    if (settings["random_superList"]):
        list_sen = list(all_sentences.values())

    else:
        list_sen = []
        for keys in settings["superList"]:
            list_sen.append(all_sentences[keys])

    count_limit = settings["numLists"]
    count = 0
    lisLen = []
    for inner in list_sen:
        lisLen.append(len(inner))
        sent_lis.append([])

    while (count < count_limit):
        random_index = random.randint(0, len(list_sen) - 1)  # Choose which list to show randomly
        if (lisLen[random_index] > 0):  # Check if any more lists are available in the list type
            randomListIdx = random.randint(0, lisLen[random_index] - 1)
            sent_lis[random_index].append(list_sen[random_index].pop(randomListIdx))
            lisLen[random_index] -= 1
            count += 1

for innerList in sent_lis:
    if (settings["randomize_sentences"]):
        for data in innerList:
            random.shuffle(data)
    random.shuffle(innerList)

random.shuffle(sent_lis)

flat_list = []
for innerList in sent_lis:
    for sent in innerList:
        flat_list += sent
# ================= Finish Sentence Pre-processing ================= #

trackIdx = 0
maxIdx = len(flat_list)

win = visual.Window(color="white", fullscr=False)

visual.ImageStim(win, image='./ub.png', size=(250, 31.7), pos=(0, 100), units="pix").draw()
msg0 = visual.TextStim(win, text="SiM Experiment", pos=(0, 0), color='#666666', height = 50, units='pix')
msg0.draw()
msg01 = visual.TextStim(win, text="\n\nPress any key to Continue.\nPress 'q' to quit.", pos=(0, -100), color='#000000', height=30,
                               units='pix')
msg01.draw()
win.flip()
imgKey = event.waitKeys()

if("q" in imgKey):
    trackIdx = maxIdx

# Start showing sentence stimuli.
while (trackIdx < maxIdx):
    parser = argparse.ArgumentParser(add_help=False)
    q = queue.Queue()

    # Filename structure:
    # <experiment sentence display index>_SiM_<participant ID>_<speech conditions>_<Sentence type> - <list number> - <sentence number> .wav
    filename = saveLocation+"/"+str(trackIdx)+"_SiM_"+answers[0]+"_"+answers[4]+"_"+flat_list[trackIdx]["ID"]+"-"+flat_list[trackIdx]["list_number"]+"-"+flat_list[trackIdx]["sen_number"] + ".wav"
    if(os.path.exists(filename)):
        os.remove(filename)
    msg = visual.TextStim(win, text="Sentence " + str(trackIdx + 1) + " of " + str(maxIdx), color='#000000', pos=(0, 100), height=30, units='pix')
    msg.draw()
    msg1 = visual.TextStim(win, text=flat_list[trackIdx]["sentence\n"], pos=(0, 0), color='#FF005C')
    msg1.draw()
    msg2 = visual.TextStim(win, text="Press 'Space' to start recording.", pos=(0, -100), color='#000000', height=30, units='pix')
    msg2.draw()
    win.flip()
    key1 = event.waitKeys()

    if('space' in key1):
        msg = visual.TextStim(win, text="Sentence " + str(trackIdx + 1) + " of " + str(maxIdx), color='#000000',
                              pos=(0, 100), height=30, units='pix')
        msg.draw()
        msg1 = visual.TextStim(win, text=flat_list[trackIdx]["sentence\n"], pos=(0, 0), color='#08cb0e')
        msg1.draw()
        msg2 = visual.TextStim(win, text="\n\nPress 'Space' to Stop Recording.", pos=(0, -100), color='#000000', height=30,
                               units='pix')
        msg2.draw()
        visual.ImageStim(win, image='./mike.png', pos=(0, -200), units='pix', size=60).draw()
        win.flip()

        # =========== Audio Recording ============= #
        with sf.SoundFile(filename, mode='x', samplerate=44100,
                          channels=channels, subtype=None) as file:
            with sd.InputStream(samplerate=44100, device=None,
                                channels=channels, callback=callback):
                while True:
                    file.write(q.get())
                    if keyboard.is_pressed("space"):
                        print('\nRecording finished: ' + repr(filename))
                        q.queue.clear()
                        break

        msg = visual.TextStim(win, text="Sentence " + str(trackIdx + 1) + " of " + str(maxIdx), color='#000000',
                              pos=(0, 100), height=30, units='pix')
        msg.draw()
        msg1 = visual.TextStim(win, text=flat_list[trackIdx]["sentence\n"], pos=(0, 0), color='#FF005C')
        msg1.draw()
        msg2 = visual.TextStim(win, text="\n\nPress 'Space' to Continue.\nPress 'r' to re-record", pos=(0, -100), color='#000000', height=30,
                               units='pix')
        msg2.draw()
        win.flip()
        keys = event.waitKeys()
        if ('space' in keys):
            print("Clicked Space to proceed after recording")
            trackIdx += 1
            continue
        elif('r' in keys):
            continue

        elif ('q' in keys):
            win.close()

    elif('q' in key1):
        win.close()