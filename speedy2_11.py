#!/usr/bin/env python3.8
# NAME: speedy
# VERSION: 2.11
# LICENSE: SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only
# DESCRIPTION:
#This program has a single goal: to make repetive uploading to the Nordic
#   nRF52840 dongle as effortless as possible in order to program large numbers of dongles.
#It is intended to work automatically i.e. the user plugs in a dongle, as soon as
#the program detects the dongle it will program it. It is possible for the user to be
#plugging in another dongle to another USB socket whilst the first is in the process of upload.
#The first dongle it finds it will upload to.
#The consequence is that only one user at any one time on any one computer or else they
#will clash on the dongles
#This has only been tested on Ubuntu Linux and is unlikely to function on windows.
#generate the piz file with:
#nrfutil pkg generate --debug-mode --sd-req 0 --hw-version 52 --application combined_pca10059.hex app_dfu_package.piz
# despite no soft device you cannot do without sd-req - but zero works for now. debug mode is essential also.
#nrfutil pkg generate --debug-mode --sd-req 0 --hw-version 52 --application combined_pca10059.hex dfu.zip
#nrfutil pkg generate --debug-mode --hw-version 52 --application combined_pca10059.hex dfu.zip
# test-connection garage-pc -count 28000 -delay 4
#The program imports a speedy.json file from DEF_main_directory in order to load parameters.
# DEPENDENCIES:
#   The gui uses unchanged external product PySimpleGUI
#   It requires a piece of hardware, an nRF52840 usb dongle from Nordic (or a copy thereof).
#   The nRF5840 is programmed using nrfutils version 6.1
#  AUTHORS:
#    Ray Foulkes
# DESIGN:
#  The program is based on events, either as a result of users pushing screen buttons or
#  on time ticks. The state machine ticks at roughly half second intervals.
#  The standard output and standard error use files. The standard out file is parsed as necessary.
# ENVIRONMENT:
#
#  Written in Python 3.
#    Notes on nrfutil
#      After version 6.1 of nrfutil, Nordic decided to add more functionality, change the way that commands
#      are used and move what was open source to closed. Since this occurred post our testing but prior to
#      deployment, we were inclined not to re-test all our software but stick with nrfutil v6.1
#      unfortunately the python packaging for that had requirements of a version of python less than 3.9
#      Such a version was not available in the linux repositories. Thus we took the risk of backwards compatibility
#      of python versions (in the past - no guarantees!). Version 6.1 downloaded from github needs setup.py changing
#      to permit higher versions of Python than 3.5 to be used.
#      The zip file is expanded into a directory, the configuration files setup.py and requirements.txt
#      are patched with the setup.patch and requirements.patch text files.
#      Once the patches are installed cd to the directory and install with pip install .
#
#geof@Lenovo:/usr/local/lib$ ls -als                                                                                                   
#total 67448                                                                                                                           
#    4 drwxr-xr-x  6 root root      4096 Apr 21 10:38 .                                                                                
#    4 drwxr-xr-x 10 root root      4096 Feb  3  2020 ..                                                                               
#    4 drwxr-xr-x  4 root root      4096 Dec  2  2021 Devices                                                                          
#  140 -rw-r--r--  1 root root    143287 Apr  5  2021 JLinkDevices.xml                                                                 
#    0 lrwxrwxrwx  1 root root        23 Dec  7  2021 libjlinkarm.so.6 -> libjlinkpic32.so.6.98.5                                      
#    0 lrwxrwxrwx  1 root root        38 Dec  2  2021 libjlinkpic32.so -> /usr/local/lib/libjlinkpic32.so.6.98.5                       
#19840 -rw-r--r--  1 root root  20314080 Apr  5  2021 libjlinkpic32.so.6.98.5                                                          
#47440 -rwxr-xr-x  1 root root  48574968 Nov 28  2020 libLlvmDisassembler.so                                                           
#    0 lrwxrwxrwx  1 root root        22 Dec  7  2021 libLlvmDisassembler.so.4 -> libLlvmDisassembler.so                               
#    4 lrwxrwxrwx  1 root root        60 Dec  2  2021 libmchpusb-1.0.so -> /opt/microchip/mplabcomm/3.47.00/lib/libmchpusb-1.0.so.0.0.0
#    4 drwxr-xr-x  3 root root      4096 Dec  8  2022 python3.10                                                                       
#    4 drwxr-xr-x  3 root root      4096 Apr 21 10:38 python3.11                                                                       
#    4 drwxrwsr-x  4 root staff     4096 Sep 23 12:21 python3.8                                                                        
#
#   geof@Lenovo:/usr/local/lib/python3.8$ ls -als                 
#   total 744                                                     
#     4 drwxrwsr-x 4 root staff   4096 Sep 23 12:21 .             
#     4 drwxr-xr-x 6 root root    4096 Apr 21 10:38 ..            
#     4 drwxrwsr-x 4 root staff   4096 Mar 29  2021 dist-packages              <<<<<<<<<<<<<<<<<<<<<<<< Added to thgis
#     4 drwxr-sr-x 2 root staff   4096 Sep 23 12:21 lib-dynload                <<<<<<<<<<<<<<<<<<<<<added to this
#   728 -rw------- 1 root staff 742530 Sep 23 12:20 lib-dynload.7z             <<<<<<<<<Just a packed version of lib-dynload
#
#eof@Lenovo:/usr/local/lib/python3.8/dist-packages$ ls -als              
#total 16                                                                
#4 drwxrwsr-x 4 root staff 4096 Mar 29  2021 .                           
#4 drwxrwsr-x 4 root staff 4096 Sep 23 12:21 ..                          
#4 drwxr-sr-x 3 root staff 4096 Mar 29  2021 PySimpleGUI                       <<<<<<<<<<<<<Added this (via pip originally)
#4 drwxr-sr-x 2 root staff 4096 Mar 29  2021 PySimpleGUI-4.38.0.dist-info
#
#
#
#
#
#
NORDIC_VENDOR_ID = 0x1915
DONGLE_MODEL_NO = 0x521f


fail_list = [] #Used to record failures of module imports only.
some_failure = False
#This encapsulates imports to avoid presenting user with exception info.
# It is equivalent to import x as y
def import_module(x): 
    try:
        moditself =  importlib.import_module(x)
        #note moditself does not exist in case of exception.
    except ImportError as error:
        fail_list.append(error.name)
        return None
    else:
        return moditself
try:
    import importlib  #if this fails, it will be caught by the except clause below and no other module loading will be attempted.
    logging = import_module('logging')
    sys= import_module('sys')
    io = import_module('io')
    subprocess = import_module('subprocess')
    shlex = import_module('shlex')
    glob= import_module('glob')
    sg= import_module('PySimpleGUI')
    textwrap= import_module('textwrap')
    os= import_module('os')
    getpass= import_module('getpass')
    runningon= import_module('platform')
    grp= import_module('grp')
    operator= import_module('operator')
    serial= import_module('serial')
    time=import_module('time')
    pathlib=import_module('pathlib')
    seriallist_ports = import_module('serial.tools.list_ports')
    json=import_module('json')
except ModuleNotFoundError as moduleErr:
    fail_list.append(moduleErr.name)
except ImportError as impErr:
    fail_list.append(impErr.name)

last_resort_log=logging.getLogger() #This puts out info on the console

if fail_list:
# then abandon here with fatal error plus the modules which failed to load. (config error)
    last_resort_log.critical('Fatal error. The following Python modules failed to load')
    for err in fail_list:
        last_resort_log.critical(err)
    last_resort_log.critical('Try pip followed by the name on the command line to install each')
    exit(1)
    
def sprint(*args, **kwargs):
    sio = io.StringIO()
    print(*args, **kwargs, file=sio)
    return sio.getvalue()



chosen_zip_file = None
not_uploading = True #NOT in the process of uploading the dongle.
auto_upload = False #boolean controlled by the Auto button.
port_to_program = None
window = None
#

global current_user
current_user = getpass.getuser()
#Directories and files
#All the info for this program is kept in the users home directory under the directory named "DEF_main_directory"
#The logfile called "DEF_short_program_name+'_logfile'" is kept in this main directory.
#
#
DEF_version = '2.11'

DEF_short_program_name = 'speedy_dongle' #No spaces please. Used for filenames
DEF_main_directory = '/speedy'
DEF_log_file_name = '/'+DEF_short_program_name+'_logfile'
DEF_zip_file_dir = '/uploads'
DEF_upload_zip_ext = 'piz'
DEF_JSON_filename = '/speedy.json'
DEF_result_file = '/results.txt' #to avoid problems of lots of outputs in spawned process
DEF_error_file = '/errors.txt' #to avoid problems of lots of outputs in spawned process
user_home_dir = os.path.expanduser('~') #keeping stuff in the users home directory.
main_directory_path = user_home_dir+DEF_main_directory
user_log_file = main_directory_path+DEF_log_file_name #log file in main directory
result_file_path = main_directory_path+DEF_result_file

error_file_path = main_directory_path+DEF_error_file
JSON_file_path = main_directory_path + DEF_JSON_filename
upload_path = main_directory_path+DEF_zip_file_dir

# Next load the parameters from the JSON file.
with open(JSON_file_path) as f:
  json_data = json.load(f)
  
right_col_width_chars = json_data['speedy_config']['right_column']['width_in_chars']
left_col_width_chars = json_data['speedy_config']['left_column']['width_in_chars']
announce_prog = json_data['speedy_config']['header']['program_announce'] + ' ' + DEF_version
announce_file = json_data['speedy_config']['left_column']['file_select_button']['announce_file']
announce_no_file = json_data['speedy_config']['left_column']['file_select_button']['announce_no_file']

Python_version = 'Python:'+sg.sys.version
System_info = 'System:'+runningon.platform()
Uname = 'System:'+sprint(runningon.uname())
PySimpleGui_source = 'PySimpleGui source:'+sprint(sg)
PySimpleGui_version = 'PySimpleGui version:'+sg.ver
TCL_version ='TCL version:'+sg.tclversion_detailed
exit_requested = False #set to true if the user presses the exit key.
#program exit is deferred until any uploading is finished to avoid screwing a dongle.
try:
    speedy_logger = open(user_log_file,'+a')
except Exception:
    last_resort_log.exception('Fatal error - cannot open '+user_log_file)
speedy_logger.write('\n\n\n\nNew session at '+time.strftime("%d/%m/%Y %H:%M")+' of '+announce_prog)
speedy_logger.write('\nUser '+current_user+' is logged on')
speedy_logger.write('\nSystem:'+runningon.platform())
speedy_logger.write('\nPython:'+sg.sys.version)
speedy_logger.write('\nPySimpleGui version:'+sg.ver)
speedy_logger.write('\nPySimpleGui source:'+sprint(sg))
speedy_logger.write('\nTCL version:'+sg.tclversion_detailed)

#Class messagey deals with PySimplegui things that have a static text field announcing something.
#Each instance manages a single window containing the message.
#Messages can time out or not. Time out is not very accurate.
#To achieve timeout, the method 'check' must be called in the infinite loop of PySimpleGui from a timeout event.
#If the message times out it is replaced by the default message
#The time-out can be cancelled during 'check' and the message replaced by the default message immediately
#A message can be declared critical so it cannot be cancelled but will time out as normal
# When initialising the class give the window key string, an initial message and a timeout_real_seconds count which is the number
# of seconds before the message times out and gets replaced with default message.
# instance.message(mess,timeout,important) installs the string mess in the window, boolean timeout = True means
#   that the message will remain for at least the number of seconds declared at instantiation and
#   boolean important = True means that it cannot be cancelled (it must be replaced to remove it).
#call check(cancel) Checks for timeout but if boolean cancel = True the message will be replaced by default
#  unless the message has been declared critical.
class messagey:
    def __update_window(self,msg): #local function to update the messagecontent & the window.
        self.messagecontent = msg
        window[self.key].update(msg) 
    def __init__(self, window_key, startingmessage,timeout_real_seconds):
        self.default = '' #The "empty" message
        self.key = window_key #The key of the window showing the message
        self.real_seconds = timeout_real_seconds
        self.timing = False
        self.timeout_at = 0.0
        self.critical = False
        self.__update_window(startingmessage)
    def message(self,newmessage,timeout,important):
        if newmessage != self.messagecontent: self.__update_window(newmessage)
        self.critical = important
        self.timing = timeout
        if self.timing:
            self.timeout_at = self.real_seconds+time.monotonic()
    def check(self,cancel):
        if self.timing and ((cancel and not self.critical) or time.monotonic() > self.timeout_at):
            self.timing = False
            self.__update_window(self.default) # erase message



def log_event(str):
    window['-REPORT-'].print(time.strftime("%d/%m/%Y %H:%M")+str)
    speedy_logger.write('\n'+time.strftime("%d/%m/%Y %H:%M")+str)

def start_upload(str):
    global not_uploading,results,errors,process,statewindow
#    statewindow.check(True) #True forces cancel if not critical
    not_uploading = False
    log_event(str+' '+port_to_program.serial_number)
    window['-FILE-'].update(disabled = True)
    statewindow.message('Uploading,\ndo not unplug dongle',True,False)
    ##spawn process.
    results = open(result_file_path, "w")
    errors  = open(error_file_path,"w")
    #nrfutil dfu usb-serial -pkg dfu.zip -p /dev/com60 -b 115200
    #nrfutil pkg display /home/ray/speedy/uploads/app_dfu_package.piz
    #command = 'ls -als'
    #command = 'nrfutil pkg display '+chosen_zip_file #check the file contents
    command = 'nrfutil dfu usb-serial -pkg '+chosen_zip_file+' -p '+port_to_program.device+' -b 115200'
    #log_event('command='+command)
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=results, stderr=errors)
    except:
        speedy_logger.write("\nERROR {} while running {}".format(sys.exc_info()[1], command))
        exit('unable to spawn subprocess')



def test_finish_upload(str):
    global not_uploading,results,errors,process
    success = True
    finished = process.poll() is not None
    if finished: #then the process has finished.
        not_uploading = True
        rc = process.poll()
        results.close()
        errors.close()
        result_size = pathlib.Path(result_file_path).stat().st_size
        error_size = pathlib.Path(error_file_path).stat().st_size
        success = not(error_size != 0)
        if success: #then all is well.
            statewindow.message('Finished uploading\nunplug now',True,False)
            msg=' Successful upload to '
        else:
            #perhaps parse and report error here.
            msg=' Failed upload to '
            statewindow.message('Failed uploading\nunplug now',True,True)
        log_event(msg+str)
        if not auto_upload:
            window['-FILE-'].update(disabled = False)
    return finished,success #first is that it is finished, second that it was a success (or not)
#Here do initial checking for file to upload to determine whether user has to choose.
#check installation file structure

if not os.path.exists(main_directory_path):
    some_failure = True
    speedy_logger.write('\nMain directory missing: should be:'+main_directory_path)
if not os.path.exists(upload_path):
    some_failure = True
    speedy_logger.write('\nUpload directory missing: should be:'+upload_path)

#files_path = [os.path.abspath(x) for x in os.listdir()]
upload_files = glob.glob(upload_path+'/*.'+DEF_upload_zip_ext)
if not upload_files:
    some_failure = True
    speedy_logger.write('\nNo upload (.'+DEF_upload_zip_ext+') files present in: '+upload_path)
    
    

if some_failure:
    last_resort_log.critical('Fatal error - file problem, see '+user_log_file)
    exit(0)
if len(upload_files) == 1:
    #there is only one choice so use it.
    chosen_zip_file = upload_files[0]
    browse_button_text = announce_file.replace('***',os.path.basename(chosen_zip_file)) #replace *** with file name.
    browse_button_color = 'white on green'
else: 
    browse_button_text = announce_no_file
    browse_button_color = 'white on grey'

left_column_font = tuple(json_data['speedy_config']['left_column']['font'])
right_column_font = tuple(json_data['speedy_config']['right_column']['font'])
right_column_header_text = json_data['speedy_config']['right_column']['header_text']
# Column layout 
layout = [sg.vtop(
         [sg.Col([
                  [sg.FileBrowse(file_types=((announce_no_file, '*.'+DEF_upload_zip_ext),),button_text = browse_button_text,
                     initial_folder = upload_path,tooltip = 'If there is only one file, it will be shown here.\n otherwise you need to choose.\
\nFiles can only be selected when not uploading and not in Auto', enable_events = True,
                     size=(left_col_width_chars,4),font=left_column_font,button_color=browse_button_color,key = '-FILE-',disabled=False, auto_size_button=True)],
                  [sg.Button('searching for\ndongle',size=(left_col_width_chars,4),font=left_column_font,button_color='white on orange',key = '-ACTION-',disabled=True,
                  tooltip = 'When green push to program the dongle.\nDo not unplug dongle until told')],
                  [sg.Button('Auto is off',          size=(left_col_width_chars,5),font=left_column_font,button_color='white on red', key = '-AUTO-',
                  tooltip = 'If AUTO is on then any dongle found\n will be immediately programmed.\nIf you have more than one USB in use,\
\nthe first one found with a dongle\nwill be programmed, followed by the others')],
                  [sg.Text('         ',             size=(left_col_width_chars+1,3),font=left_column_font,key='-STATE-')],
                  [sg.Button('Exit', key='-E-',tooltip = 'Exit the program, ALWAYS exit this way', font = left_column_font,  size=(left_col_width_chars,2))]
                 ]
                ) #from layout helper funcs. Vtop align tops of [elements]
         ,sg.Col([
                  [sg.Multiline(right_column_header_text,justification='center', size =(right_col_width_chars,2),write_only = True, background_color = 'light blue', font = right_column_font)],
                  [sg.Multiline('Nordic Dongle Programmer version '+DEF_version+'\n',autoscroll = True,size = (right_col_width_chars, 
                     json_data['speedy_config']['right_column']['number_of_lines']),font = right_column_font,
                  key='-REPORT-',auto_refresh = True,write_only = True,tooltip = 'Report on activity. No user input here.')],
                  ],expand_x = True)]
         )
         ]

# Display the window and get values
window = sg.Window(announce_prog, layout = layout, resizable = True, margins=(0,0), element_padding=(0,0),finalize=True)
(old_width,old_height) = window.size
awaiting_dongle_plugin = True
statewindow = messagey('-STATE-','',5.5) #set up the message window with blank entry and 5.5 seconds timeout.
window['-REPORT-'].print(Python_version)
window['-REPORT-'].print(System_info)
#window['-REPORT-'].print(Uname+'\n')
window['-REPORT-'].print(PySimpleGui_version)
#window['-REPORT-'].print(PySimpleGui_source)
window['-REPORT-'].print(TCL_version)
log_event('User '+current_user+' is logged on\n')
def choose_first_dongle(list_of_ports):
    global awaiting_dongle_plugin
    success = True
    if list_of_ports :  #there is at least one dongle plugged in.
        port = list_of_ports[0] #so just pick first one.
        awaiting_dongle_plugin = False             
#        speedy_logger.write('\nhwid='+port.hwid)                  
#        speedy_logger.write('\ndescription='+port.description)    
#        speedy_logger.write('\nvid='+hex(port.vid))               
#        speedy_logger.write('\npid='+hex(port.pid))               
#        speedy_logger.write('\nmanufacturer='+port.manufacturer)  
#        speedy_logger.write('\nproduct='+port.product)
        try:
            myserial = serial.Serial(port.device) #attempt to open up the serial line to see if it is possible.
        except:
            success = False
        if success:
            myserial.close() #successfully opened so close again to leave free for uploader.
            window['-ACTION-'].update(text='dongle serial' +port.serial_number+'\nwill be programmed'
               if auto_upload else "Push here to upload\n to dongle serial "+port.serial_number, button_color='white on red' if auto_upload else 'white on green',
               disabled=True if auto_upload or not chosen_zip_file else False)
        else: # unable to access the serial line for the Dongle.
            window['-ACTION-'].update(text='dongle serial' +port.serial_number+'\nfound but you have no\n access to '+port.device,disabled=True,button_color='white on red')
            my_groups = [g.gr_name for g in grp.getgrall() if current_user in g.gr_mem]
            mygroupstr = ", ".join(my_groups)
            statewindow.message('get permissions changed\nsee log for info>>>>>',True,True)
            log_event('User '+current_user+' Unable to access '+port.device)
            log_event(current_user+' is in groups '+mygroupstr)
            log_event(current_user+' needs to be in dialout to access port')
            log_event('Add user to group dialout using "sudo usermod -a -G dialout '+current_user+'"')
            log_event('you will have to log out and back in again to make it active\n\n\n')
    else: 
        port = None
    return port
while True:
    if exit_requested and not_uploading: #then tidy up and leave
        break
    else:
        if exit_requested:     window['-E-'].update(text='Still uploading, please wait')
    missed_event = True
    event, values = window.read(timeout = 500,timeout_key = "-TIMEOUT-",close = False)
    if event == '-ACTION-' and not_uploading :
        if not auto_upload : ##should not be an action event anyway if auto is set.
            window['-ACTION-'].update('uploading to dongle\n'+port_to_program.serial_number,disabled=True,button_color='white on black')
            start_upload(' Started manual upload to ') #start uploading process here.
        missed_event = False
    if event == '-AUTO-':
        #do not permit auto to be turned on if there is no file chosen.
        if chosen_zip_file == None and not auto_upload :
            statewindow.message('auto is disabled\nfile must be chosen\nfirst',True,False)
            log_event(' Auto upload refused - no file yet chosen')
        else:
            auto_upload = not auto_upload
            if auto_upload :
                log_event(' Auto upload turned on')
                window['-ACTION-'].update(disabled=True)
                window['-FILE-'].update(disabled = True)
            else:
                log_event(' Auto upload turned off')
                if not_uploading:
                    window['-FILE-'].update(disabled = False,button_color = 'white on green')
                if not_uploading and not awaiting_dongle_plugin:
                    window['-ACTION-'].update(disabled=False)
            window['-AUTO-'].update(text='AUTO is ON\n all inserted dongles\nwill be programmed'
               if auto_upload else 'AUTO is OFF\npush button above\nto programme', button_color='white on green' if auto_upload else 'white on red')
        missed_event = False
        
        
    if event == '-FILE-':
        temp_file = values['-FILE-']
        if temp_file: #then there is a file string
            if temp_file != chosen_zip_file: #then it is different
                log_event('Changed upload file to '+temp_file)
                chosen_zip_file = temp_file
                window['-FILE-'].update(announce_file.replace('***',os.path.basename(chosen_zip_file)), button_color = 'white on green')
                if port_to_program:
                    window['-ACTION-'].update(disabled=False)
        missed_event = False
    if event == "-TIMEOUT-":
        statewindow.check(not awaiting_dongle_plugin and not_uploading) #cancel if not awaiting dongle plugin and not uploading.
        if not_uploading:
            if auto_upload and port_to_program:
                start_upload(' Started auto upload to ')
                window['-ACTION-'].update('uploading to dongle\n'+port_to_program.serial_number,disabled=True,button_color='white on black')
        else:
            if test_finish_upload(' '+port_to_program.serial_number)[0]: #Just finished uploading, change state to searching for dongle
                awaiting_dongle_plugin = True
                port_to_program = None #because it is just finished
                window['-ACTION-'].update('searching for\ndongle',button_color='white on orange',disabled=True)
        missed_event = False
        #mNow re-check the port_to_program contains the same dongle.
        #once chosen, unless removed, we do not want to switch. So, always scan comports
        #if we DON'T find the one we already have (serial number) then reset the search.
        if seriallist_ports.comports and not_uploading:
             #Make a list containing all comports which look like they contain a dongle.
             # i.e. the supplier is Nordic and the device has the right pid.
             ports_with_dongles = [x if x.vid == NORDIC_VENDOR_ID and x.pid == DONGLE_MODEL_NO else None for x in list(seriallist_ports.comports())]
             if awaiting_dongle_plugin:
                 if ports_with_dongles: #if awaiting, and the list is not empty, then just choose first.
                     port_to_program = choose_first_dongle(ports_with_dongles)
                     log_event(' Found dongle No. '+port_to_program.serial_number+' on '+port_to_program.device)
             else: #there is already a dongle set
                 chosen = [x if x.serial_number == port_to_program.serial_number else None for x in ports_with_dongles]
                 if not chosen: #The chosen list is empty so the chosen device is no longer accessible
                    if ports_with_dongles :  #there is at least one dongle plugged in.
                        port_to_program = choose_first_dongle(ports_with_dongles)
                        log_event('Changed dongle to: '+port_to_program.serial_number+' on '+port_to_program.device)
                    else: 
                        awaiting_dongle_plugin = True #if empty then nothing plugged in so await plugin.
                        port_to_program = None # and forget the port_to_program.
                        window['-ACTION-'].update('searching for\ndongle',button_color='white on orange',disabled=True)
                 #else do nothing, chosen device is still available.
    if event == "-E-" or event == sg.WIN_CLOSED or event == sg.WIN_CLOSED or event == 'Exit':
        exit_requested = True #only abandon if the upload is finished.
        missed_event = False
    if missed_event:
        print('\nMissed event=',event, values)
speedy_logger.write('\nExited gracefully at '+time.strftime("%d/%m/%Y %H:%M")+'\n\n\n')
speedy_logger.close()
window.close()

#print('~\working\\'+datetime.datetime.now().time.strftime("%y%m%d_%H%M%S")+'_'+str(uuid.uuid4().hex)+'.usbres')
