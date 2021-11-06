import PySimpleGUI as sg
import os
from media import Media
from pytube.exceptions import RegexMatchError

def set_buttons(window, status):
    window['Download'].update(disabled=status)
    window['Cancel'].update(disabled=status)
    window['Browse'].update(disabled=status)

def clear_inputs(window):
    window['-URL-'].update('')
    window['-A-'].update(True)
    window['-RES-'].update(disabled=True, values=[])

def status_notifier(msg):
    sg.popup_notify(msg, display_duration_in_ms=3000, fade_in_duration=400, location=window.current_location(more_accurate = False))

sg.theme("Reds")

left_col = [
    [sg.Text('Video URL: ')],
    [sg.Text('Quality: ')],
    [sg.Text('Output Folder: ')]
]

right_col = [
    [
        sg.In(size=(40, 1), key='-URL-'), 
        sg.Radio("Audio", group_id="format", default=True, key="-A-"), 
        sg.Radio("Video", group_id="format", key="-V-", enable_events=True)
    ],
    [
        sg.Combo([], key='-RES-', disabled=True, size=(40, 1))
    ],
    [
        sg.In(size=(40, 1), key="-FOLDER-", default_text="C:/Users/petar/Music/Youtube"), 
        sg.FolderBrowse(initial_folder="C:/Users/petar")
    ]
]

layout = [
    [
        sg.Col(left_col),
        sg.Col(right_col),
    ],
    [
        [
            sg.Button("Download", expand_x=True),
            sg.Button("Cancel", expand_x=True)
        ]
    ]
]

window = sg.Window("Youtube Downloader", layout)

while True:
    event, values = window.read()
    if event == "Cancel" or event == sg.WIN_CLOSED:
        break

    if event == "Download":
        set_buttons(window, True)

        if values["-URL-"] == '':
            sg.popup_ok("Please specify a URL")
        else:
            if values["-A-"]:
                media = Media(values["-URL-"], values["-FOLDER-"])

                try:
                    status_notifier('Downloading Audio...')
                    filename = media.download_audio()
                except RegexMatchError:
                    sg.popup_error("Error downloading media. Please check the URL.")
                else:
                    status_notifier('Converting Audio...')
                    media.convert_to_audio(filename)

                    try:
                        status_notifier('Moving to selected Folder...')
                        media.move_to_folder()
                    except FileExistsError:
                        filename = filename.replace('.mp4', '.mp3')
                        os.remove(filename)
                        sg.popup_error("File already exists.")
                    else:
                        status_notifier('Done.')
            
            elif values["-V-"]:
                media = Media(values["-URL-"], values["-FOLDER-"])
                if values['-RES-'] == '':
                    sg.popup_ok('Please select a resolution from the dropdown.')
                    clear_inputs(window)
                else:
                    try: 
                        status_notifier('Downloading Video...')
                        media.download_video(values['-RES-'])
                    except:
                        sg.popup_error('Unable to download video.')
                    else:
                        try:
                            status_notifier('Moving to selected Folder...')
                            media.move_to_folder()
                        except FileExistsError:
                            os.remove(filename)
                            sg.popup_error("File already exists.")
                        else:
                            status_notifier('Done.')
        
        set_buttons(window, False)
        clear_inputs(window)

    elif event == "-V-":
        if values["-URL-"] == '':
            sg.popup_ok("Please specify a URL")
        else:
            try:
                sg.popup_notify('Getting available resolutions...', display_duration_in_ms=3000, fade_in_duration=400, location=window.current_location(more_accurate = False))
                res = Media(values["-URL-"], values["-FOLDER-"]).get_resolutions()
            except:
                sg.popup_error("No resolutions found. Please check your URL.")
            else:
                window['-RES-'].update(values=res, disabled=False)

    elif event == '-A-':
        window['-RES-'].update(values=res, disabled=True)

    print(event, values)

window.close()