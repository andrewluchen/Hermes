import Tkinter, time, random, string, copy
from PIL import Image, ImageTk

#80Lines########################################################################

#GUI Class creates a Tk() Window object for the game
class GUI(Tkinter.Tk, object):
    
    def __init__(self):
        super(GUI, self).__init__()
        self.title("Hermes")
        self.iconbitmap("images/title.ico")
        self.winfo_toplevel().wm_state('zoomed')
        self.w, self.h = self.winfo_screenwidth(), self.winfo_screenheight()
        hpad, vpad = 100, 64
        self.h -= hpad
        self.w -= vpad
        self.geometry("%dx%d+0+0" % (self.w, self.h))
        self.menu = Tkinter.Menu(self)
        self.createMenu()
        self.config(menu=self.menu)
        self.keysPressed = []
        self.bind("<KeyPress>", self.keyPressed)
        self.bind("<KeyRelease>", self.keyReleased)
        
        self.init()
        self.openPath('Tutorial')
        self.mainloop()
    
    def init(self):
        self.toolFrame = LearnToolFrame(self, self.w, self.h)
        self.toolFrame.grid(row = 0, column = 0)
        self.functionFrame = FunctionFrame(self, self.w, self.h)
        self.functionFrame.grid(row = 0, column = 1)
        self.graphicFrame = GraphicFrame(self, self.w, self.h)
        self.graphicFrame.grid(row = 0, column = 2)
        self.maxstepssize = 20
        self.functionlimit = 100
        self.splitter = '#####'
    
    #creates menus in the window
    def createMenu(self):
        filemenu = Tkinter.Menu(self.menu, tearoff=0)
        filemenu.add_command(label="New", command=self.newFile)
        filemenu.add_command(label="Open", command=self.openFile)
        filemenu.add_command(label="Save", command=self.storeFile)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        self.menu.add_cascade(label="File", menu=filemenu)
        
        modeMenu = Tkinter.Menu(self.menu, tearoff=0)
        modeMenu.add_command(label="Sandbox Mode", command=self.sandbox)
        modeMenu.add_command(label="Learning Mode", command=self.learn)
        modeMenu.add_command(label="Editing Mode", command=self.teach)
        self.menu.add_cascade(label="Mode", menu=modeMenu)
        
        optionsMenu = Tkinter.Menu(self.menu, tearoff=0)
        optionsMenu.add_command(label="Zoom In  (Ctrl++)",
                             command=self.zoomin)
        optionsMenu.add_command(label="Zoom Out  (Ctrl+-)",
                             command=self.zoomout)
        optionsMenu.add_command(label="Change Step Size",
                             command=self.stepsize)
        optionsMenu.add_command(label="Change Function Limit",
                             command=self.functionlimit)
        optionsMenu.add_command(label="Toggle Slow/Fast Mode",
                             command=self.fastslow)
        self.menu.add_cascade(label="Options", menu=optionsMenu)
        
        helpmenu = Tkinter.Menu(self.menu, tearoff=0)
        helpmenu.add_command(label="About",
                             command=self.aboutProgram)
        helpmenu.add_command(label="Instructions",
                             command=self.showinstructions)
        self.menu.add_cascade(label="Help", menu=helpmenu)
    
    def newFile(self):
        master = Tkinter.Tk()
        Tkinter.Label(master, text="Board Size:").grid(row=0,
                                                column=0)
        form = Tkinter.Entry(master)
        form.grid(row=0, column=1)
        button = Tkinter.Button(master, text="Enter Size",
                    width=20,command=lambda f=form:\
                    self.newBoard(master, f))
        button.grid(row=2, column=1)
        master.mainloop()
    
    #creates a blank board
    def newBoard(self, master, form):
        size = form.get()
        master.quit()
        master.destroy()
        if(size.isdigit()):
            size = int(size)
            if(size < 2):
                size = 2
            elif(size > 100):
                size = 100
            self.graphicCanvas.boardSize = int(size)
            self.graphicCanvas.init()
            self.sandbox()
            self.functionCanvas.maxfunctions = 100
    
    #gets a game to be loaded on to the board
    def openFile(self):
        with open('save', 'r') as foo:
            savetext = foo.read()
            foo.flush()
        saves = savetext.split('\n')
        if(saves == ['']): return
        master = Tkinter.Tk()
        listbox = Tkinter.Listbox(master)
        listbox.pack()
        for item in saves:
            listbox.insert(Tkinter.END, item)
        button = Tkinter.Button(master, text="Load Puzzle",
                    command=lambda l=listbox: self.open(master, l))
        button.pack()
        master.mainloop()
    
    def open(self, master, listbox):
        load = listbox.get(Tkinter.ACTIVE)
        master.destroy()
        if(not load):return
        self.openPath(load)
    
    def openPath(self, path):
        self.learn()
        with open(path, 'r') as bar:
            data = bar.read()
            bar.flush()
        data = data.split(self.splitter)
        self.instructions = data[0]
        b = self.textToBoard(data[2])
        bs = len(b)
        c = self.graphicCanvas
        c.boardSize = bs
        c.board = b
        c.initfacing = self.textToPosition(data[3])
        c.initcount = int(data[4])
        c.reconstructBoard()
        c.redrawAll()
        self.popupInstructions()
        self.changefunctionlimit(int(data[1]))
        
    
    def textToPosition(self, text):
        text = text[1:-1]
        i = 0
        if(text[0] == '-'):
            x = int(text[1]) * -1
            i = 1
        else:
            x = int(text[0])
        if(text[5+i] == '-'):
            y = int(text[6+i]) * -1
        else:
            y = int(text[5+i])
        return (float(x), float(y))
    
    #popups instructions
    def popupInstructions(self):
        if(self.instructions):
            master = Tkinter.Tk()
            Tkinter.Label(master, text=self.instructions).pack()
            b = Tkinter.Button(master, text="OK",
                               command=master.destroy)
            b.pack(pady=5)
    
    #takes a text representation of a board, returns a baord
    def textToBoard(self, text):
        text = text[1:-1]
        board = []
        lefts, rights = 0, 0
        i, j = -1, -1
        while(text):
            if(text[0] == '['):
                if(lefts == rights):
                    i += 1
                    board.append([])
                if(lefts > rights):
                    j += 1
                    board[i].append([])
                lefts += 1
            elif(text[0] == ']'):
                rights += 1
                if(lefts == rights):
                    j = -1
            elif(text[0].isdigit()):
                result = self.extractFrontInt(text)
                board[i][j].append(result[0])
                text = " "+result[1]
            text = text[1:]
        return board
    
    #helper function, text --> (int, text w/o ints)
    def extractFrontInt(self, text):
        alpha = ''
        while(text):
            if(text[0].isdigit()):
                alpha += text[0]
                text = text[1:]
            else:
                return (int(alpha), text)
    
    #takes a game and adds it to the save list
    def storeFile(self):
        self.learn()
        master = Tkinter.Tk()
        form = Tkinter.Entry(master)
        form.pack()
        form.focus_set()
        button = Tkinter.Button(master, text="Enter Puzzle Name",
                    width=20,command=lambda f=form: self.store(master, f))
        button.pack()
        master.mainloop()
    
    def store(self, master, form):
        save = form.get()
        master.destroy()
        
        save = save[0:20]
        if(save == ''):
            save = self.generateRandom()
        with open(save, 'w') as foo:
            text = self.boardToText(save)
            foo.write(text)
            foo.flush()
        with open('save', 'a') as bar:
            bar.write(save+'\n')
            bar.flush()
    
    def boardToText(self, name):
        c = self.graphicCanvas
        f = self.functionCanvas
        text = name + self.splitter
        text += str(f.maxfunctions) + self.splitter
        text += str(c.board) + self.splitter
        for i in xrange(len(c.robots)):
            text += str(c.robots[i].facing) + self.splitter
            text += str(c.robots[i].count) + self.splitter
        return text
    
    #creates a random 10 length string
    def generateRandom(self):
        s = ''
        for i in xrange(10):
            s += random.choice(string.ascii_letters)
        return s
    
    #sets the game into sandbox mode
    def sandbox(self):
        self.functionFrame.grid_forget()
        self.functionFrame = FunctionFrame(self, self.w, self.h)
        self.functionFrame.grid(row = 0, column = 1)
        self.toolCanvas.editmode = False
        self.graphicCanvas.playmode = False
        self.toolCanvas.redrawAll()
        self.graphicCanvas.redrawAll()
    
    #sets the game into playing mode
    def learn(self):
        self.functionFrame.grid_forget()
        self.functionFrame = FunctionFrame(self, self.w, self.h)
        self.functionFrame.grid(row = 0, column = 1)
        self.toolCanvas.editmode = False
        self.graphicCanvas.playmode = True
        self.toolCanvas.redrawAll()
        self.graphicCanvas.redrawAll()
    
    #set the game into editor mode
    def teach(self):
        self.functionFrame.grid_forget()
        self.functionFrame = TeachToolFrame(self, self.w, self.h)
        self.functionFrame.grid(row = 0, column = 1)
        self.toolCanvas.editmode = True
        self.graphicCanvas.playmode = False
        self.toolCanvas.redrawAll()
        self.graphicCanvas.redrawAll()
    
    #keypressed listener
    def keyPressed(self, event):
        if(event.keysym not in self.keysPressed):
            self.keysPressed.append(event.keysym)
        if("Control_L" in self.keysPressed or
           "Control_R" in self.keysPressed):
            if("plus" in self.keysPressed): self.zoomin()
            if("minus" in self.keysPressed): self.zoomout()
    
    #key released listener
    def keyReleased(self, event):
        if (event.keysym in self.keysPressed):
            self.keysPressed.remove(event.keysym)
    
    #zooms in on graphics
    def zoomin(self):
        c = self.graphicCanvas
        if(c.playmode or c.space > c.minzoom): return
        c.space *= 2
        c.maxscroll *= 2
        self.graphicFrame.xscrollbar.grid_forget()
        self.graphicFrame.yscrollbar.grid_forget()
        self.graphicFrame.makeScrollbars()
        self.resizeObjects()
        c.redrawAll()
    
    #zooms out on graphics
    def zoomout(self):
        c = self.graphicCanvas
        if(c.playmode or c.space < c.maxzoom): return
        c.space /= 2
        c.maxscroll /= 2
        self.graphicFrame.xscrollbar.grid_forget()
        self.graphicFrame.yscrollbar.grid_forget()
        self.graphicFrame.makeScrollbars()
        self.resizeObjects()
        c.redrawAll()
    
    #resizes the objects
    def resizeObjects(self):
        c = self.graphicCanvas
        objs = c.objects
        for obj in objs:
            obj.resizeImage()
    
    #changes stepsize
    def stepsize(self):
        master = Tkinter.Tk()
        form = Tkinter.Entry(master)
        form.pack()
        form.focus_set()
        button = Tkinter.Button(master, text="Enter Step Size",
                    width=20,
                    command=lambda f=form:
                    self.changestepsize(master, f))
        button.pack()
        master.mainloop()
    
    def changestepsize(self, master, form):
        stepsize = form.get()
        master.destroy()
        
        if(stepsize.isdigit()):
            stepsize = int(stepsize)
            if(stepsize >= 0 and stepsize <= self.maxstepssize):
                self.graphicCanvas.steps = stepsize
    
    #changes function limit
    def functionlimit(self):
        if(self.toolCanvas.editmode): return
        master = Tkinter.Tk()
        form = Tkinter.Entry(master)
        form.pack()
        form.focus_set()
        button = Tkinter.Button(master, text="Enter Function Limit",
                    width=20,
                    command=lambda f=form:
                    self.functionlimitform(master, f))
        button.pack()
        master.mainloop()
    
    def functionlimitform(self, master, form):
        fl = form.get()
        master.destroy()
        
        if(fl.isdigit()):
            self.changefunctionlimit(int(fl))
            
    def changefunctionlimit(self, fl):
        if(fl >= 0 and fl <= self.functionlimit):
            if(fl <= len(self.functionCanvas.widgetfunctions)):
                self.functionCanvas.widgetfunctions = \
                    self.functionCanvas.widgetfunctions[0:fl]
            else:
                dif = fl - len(self.functionCanvas.widgetfunctions)
                self.functionCanvas.widgetfunctions += \
                    [None]*dif
            self.functionCanvas.maxfunctions = fl
            self.functionCanvas.redrawAll()
    
    #change fast/slow mode
    def fastslow(self):
        self.graphicCanvas.fast = not self.graphicCanvas.fast
        self.graphicCanvas.redrawAll()
    
    #about window
    def aboutProgram(self):
        about = Tkinter.Tk()
        text = """"Welcome to HERMES.
        HERMES is a puzzle-making application for educators to create
        games for children and students.
        \n
        In the game, you move a robot on a grid by giving him orders.
        Click on an order from the inventory to add it to the functions.
        Drag and drop objects onto the grid to your liking.
        Rearrange your functions until you think you have the solution.
        Then run your orders!
        \n
        You can also create your own puzzles in the edit mode.
        Drag objects onto the grid. Save your work and test it out
        in sandbox mode.
        """
        Tkinter.Label(about, text=text).pack()
    
    def showinstructions(self):
        self.popupInstructions()

#The Tool Class is describes the actions of all possible tools/actions
class Tool(object):
    
    DEFAULT = 0
    
    #PLAYER Objects
    
    #no paramters, f value
    MOVE_FORWARD = 100
    MOVE_BACKWARD = 101
    TURN_LEFT = 102
    TURN_RIGHT = 103
    TURN_AROUND = 104
    DRAW_HERE = 105
    TOKEN_HERE = 106
    TOKEN_PICKUP = 107
    PUSH = 108
    
    #string parameter, f value
    SAY = 109
    
    #no parameters, number value
    ADD_ONE = 110
    SUB_ONE = 111
    
    #no parameter, boolean value
    STANDING_ON = 112
    WALL_IN_FRONT = 113
    
    #number parameters, f value
    DO_NUMBER_TIMES = 114
    
    #boolean parameter + f-value parameter, f value
    IF_THEN = 115
    IFNOT_THEN = 116
    WHILE_DO = 117
    UNTIL_DO = 118
    
    #function header, accepts f-values
    NEW_FUNCTION = 119
    
    #string parameter, f value
    OLD_FUNCTION = 120
    
    RED = {MOVE_FORWARD,
           MOVE_BACKWARD,
           TURN_LEFT,
           TURN_RIGHT,
           TURN_AROUND,
           DRAW_HERE,
           TOKEN_HERE,
           TOKEN_PICKUP,
           PUSH,
           SAY,
           ADD_ONE,
           SUB_ONE,
           OLD_FUNCTION}
    
    YELLOW = {STANDING_ON,
              WALL_IN_FRONT}
    
    BLUE = {IF_THEN,
            IFNOT_THEN,
            WHILE_DO,
            UNTIL_DO}
    
    ORANGE = {DO_NUMBER_TIMES}
    
    PURPLE = {NEW_FUNCTION}
    
    #TEACHER Objects
    ROCK = 182
    WALL = 183
    INV_WALL = 184
    TOKEN = 185
    INV_TOKEN = 186
    PAINT = 187
    UP_TURNER = 188
    DOWN_TURNER = 189
    LEFT_TURNER = 190
    RIGHT_TURNER = 191
    UP_PUSHER = 192
    DOWN_PUSHER = 193
    LEFT_PUSHER = 194
    RIGHT_PUSHER = 195
    ADDER = 196
    SUBTRACTER = 197
    TRANSPORTER = 198
    GOAL = 199
    ROBOT = 200
    BLUEBRUSH = 201
    REDBRUSH = 202
    GREENBRUSH = 203
    
    LEARNTOOLS = [MOVE_FORWARD,
                  MOVE_BACKWARD,
                  TURN_LEFT,
                  TURN_RIGHT,
                  TURN_AROUND,
                  DRAW_HERE,
                  TOKEN_HERE,
                  TOKEN_PICKUP,
                  PUSH,
                  #SAY,
                  ADD_ONE,
                  SUB_ONE,
                  STANDING_ON,
                  WALL_IN_FRONT,
                  DO_NUMBER_TIMES,
                  IF_THEN,
                  IFNOT_THEN,
                  WHILE_DO,
                  UNTIL_DO,
                  NEW_FUNCTION,
                  OLD_FUNCTION]
    TEACHTOOLS = [ROCK,
                  WALL,
                  INV_WALL,
                  TOKEN,
                  INV_TOKEN,
                  PAINT,
                  UP_TURNER,
                  DOWN_TURNER,
                  LEFT_TURNER,
                  RIGHT_TURNER,
                  UP_PUSHER,
                  DOWN_PUSHER,
                  LEFT_PUSHER,
                  RIGHT_PUSHER,
                  ADDER,
                  SUBTRACTER,
                  TRANSPORTER,
                  GOAL,
                  ROBOT,
                  BLUEBRUSH,
                  REDBRUSH,
                  GREENBRUSH]
    
    TEXTS = {MOVE_FORWARD: "move forwards",
             MOVE_BACKWARD: "move backwards",
             TURN_LEFT: "turn left",
             TURN_RIGHT: "turn right",
             TURN_AROUND: "turn around",
             DRAW_HERE: "paint here", 
             TOKEN_HERE: "place token",
             TOKEN_PICKUP: "pickup token",
             PUSH: "push rock",
             SAY: "say",
             ADD_ONE: "add one",
             SUB_ONE: "subtract one",
             STANDING_ON: "on token?",
             WALL_IN_FRONT: "in front of wall?",
             DO_NUMBER_TIMES: "do number of times",
             IF_THEN: "if then",
             IFNOT_THEN: "if not then",
             WHILE_DO: "do while",
             UNTIL_DO: "until do",
             NEW_FUNCTION: "create an order",
             OLD_FUNCTION: "do my order",
             ROCK: "rock",
             WALL: "wall",
             INV_WALL: "invisible wall",
             TOKEN: "token",
             INV_TOKEN: "invisible token",
             PAINT: "paint",
             UP_TURNER: "turn up",
             DOWN_TURNER: "turn down",
             LEFT_TURNER: "turn left",
             RIGHT_TURNER: "turn right",
             UP_PUSHER: "push up",
             DOWN_PUSHER: "push down",
             LEFT_PUSHER: "push left",
             RIGHT_PUSHER: "push right",
             ADDER: "adder",
             SUBTRACTER: "subtracter",
             TRANSPORTER: "transporter",
             GOAL: "goal",
             ROBOT: "robot",
             BLUEBRUSH: "blue colorer",
             REDBRUSH: "red colorer",
             GREENBRUSH: "green colorer"}
    
    BLUE_TEXT = {IF_THEN: ["If",
                           "Robot is",
                           "Then do"],
                IFNOT_THEN: ["If",
                           "Robot is not",
                           "Then do"],
                WHILE_DO: ["While",
                           "Robot is",
                           "Then do"],
                UNTIL_DO: ["While",
                           "Robot is not",
                           "Then do"]}
    
    HELP_MOVE_FORWARD = \
"""==Previous Order==
"Move Forward" will move the robot forward by one step.
==Next Order=="""

    HELP_MOVE_BACKWARD = \
"""==Previous Order==
"Move Backward" will move the robot backward by one step.
==Next Order=="""

    HELP_TURN_LEFT = \
"""==Previous Order==
"Turn Left" will turn the robot 90 degrees counterclockwise.
==Next Order=="""

    HELP_TURN_RIGHT = \
"""==Previous Order==
"Turn Right" will turn the robot 90 degrees clockwise.
==Next Order=="""

    HELP_TURN_AROUND = \
"""==Previous Order==
"Turn Around" will turn the robot 180 degrees.
==Next Order=="""

    HELP_DRAW_HERE = \
"""==Previous Order==
"Paint Here" will color the current cell the robot is standing on.
==Next Order=="""

    HELP_TOKEN_HERE = \
"""==Previous Order==
"Place Token" will place a token on the current cell.
==Next Order=="""

    HELP_TOKEN_PICKUP = \
"""==Previous Order==
"Pickup Token" will remove a token on the current cell.
==Next Order=="""
    
    HELP_PUSH = \
"""==Previous Order==
"Push Rock" will move push the rock directly in front of the robot.
==Next Order=="""

    HELP_SAY = \
"""==Previous Order==
"Say" will say.
==Next Order=="""

    HELP_ADD_ONE = \
"""==Previous Order==
"Add One" will add one to the current robot count.
==Next Order=="""

    HELP_SUB_ONE = \
"""==Previous Order==
"Subtract One" will subtract one from the current robot count.
==Next Order=="""

    HELP_STANDING_ON = \
"""==Previous Order==
Last: BLUE ORDER
"On Token?" will be true if there is a token on the current cell.
Next: RED ORDER
==Next Order=="""

    HELP_WALL_IN_FRONT = \
"""==Previous Order==
Last: BLUE ORDER
"In Front of Wall?" will be true if there is wall in front of the robot.
Next: RED ORDER
==Next Order=="""

    HELP_IF_THEN = \
"""==Previous Order==
"If Then" will do the red order if the yellow order is true
Next: YELLOW ORDER
Next: RED ORDER
==Next Order=="""

    HELP_IFNOT_THEN = \
"""==Previous Order==
"If Not Then" will do the red order if the yellow order is NOT true
After: YELLOW ORDER
After: RED ORDER
==Next Order=="""

    HELP_WHILE_DO = \
"""==Previous Order==
"Continue Doing Will" will continue doing the red order
as long as the the yellow order is true
Next: YELLOW ORDER
Next: RED ORDER
==Next Order=="""

    HELP_UNTIL_DO = \
"""==Previous Order==
"Until Do" will continue doing the red order
as long as the the yellow order is not true
Next: YELLOW ORDER
Next: RED ORDER
==Next Order=="""

    HELP_NEW_FUNCTION = \
"""==END OF PREVIOUS ORDERS==
"New Function" will create a new order based
on everything below until another function is defined
==Next Order=="""

    HELP_OLD_FUNCTION = \
"""==Previous Order==
"Defined Order" will execute an already existing order
==Next Order=="""

    
    HELP = {MOVE_FORWARD: HELP_MOVE_FORWARD,
            MOVE_BACKWARD: HELP_MOVE_BACKWARD,
            TURN_LEFT: HELP_TURN_LEFT,
            TURN_RIGHT: HELP_TURN_RIGHT,
            TURN_AROUND: HELP_TURN_AROUND,
            DRAW_HERE: HELP_DRAW_HERE, 
            TOKEN_HERE: HELP_TOKEN_HERE,
            TOKEN_PICKUP: HELP_TOKEN_PICKUP,
            PUSH: HELP_MOVE_FORWARD,
            SAY: "say",
            ADD_ONE: HELP_ADD_ONE,
            SUB_ONE: HELP_SUB_ONE,
            STANDING_ON: HELP_STANDING_ON,
            WALL_IN_FRONT: HELP_WALL_IN_FRONT,
            DO_NUMBER_TIMES: "do number of times",
            IF_THEN: HELP_IF_THEN,
            IFNOT_THEN: HELP_IFNOT_THEN,
            WHILE_DO: HELP_WHILE_DO,
            UNTIL_DO: HELP_UNTIL_DO,
            NEW_FUNCTION: HELP_NEW_FUNCTION,
            OLD_FUNCTION: HELP_OLD_FUNCTION,
            ROCK: "rock",
            WALL: "wall",
            INV_WALL: "invisible wall",
            TOKEN: "token",
            INV_TOKEN: "invisible token",
            PAINT: "paint",
            UP_TURNER: "turn up",
            DOWN_TURNER: "turn down",
            LEFT_TURNER: "turn left",
            RIGHT_TURNER: "turn right",
            UP_PUSHER: "push up",
            DOWN_PUSHER: "push down",
            LEFT_PUSHER: "push left",
            RIGHT_PUSHER: "push right",
            ADDER: "adder",
            SUBTRACTER: "subtracter",
            TRANSPORTER: "transporter",
            GOAL: "goal",
            ROBOT: "robot"}
    
    INACCESSIBLE = (WALL, INV_WALL, ROCK, ROBOT)
    
    def __init__(self, toolType=0, visibility=True):
        self.type = toolType
        self.visibility = visibility
    
    def moveforward(self, robot, orders, index):
        robot.move()
        return (1, None)
    
    def movebackward(self, robot, orders, index):
        x, y = -robot.facing[0], -robot.facing[1]
        robot.move((x,y))
        return (1, None)
    
    def turnleft(self, robot, orders, index):
        robot.turnLeft()
        return (1, None)
    
    def turnright(self, robot, orders, index):
        robot.turnRight()
        return (1, None)
    
    def turnaround(self, robot, orders, index):
        robot.turnLeft()
        robot.turnLeft()
        return (1, None)
    
    def drawhere(self, robot, orders, index):
        robot.paintHere()
        return (1, None)
    
    def tokenhere(self, robot, orders, index):
        robot.placeToken()
        return (1, None)
    
    def tokenpickup(self, robot, orders, index):
        robot.pickUpToken()
        return (1, None)
    
    def push(self, robot, orders, index):
        robot.push()
        return (1, None)
    
    def say(self, robot, orders, index):
        return (1, None)
    
    def addone(self, robot, orders, index):
        robot.changeCount(1)
        return (1, None)
    
    def subone(self, robot, orders, index):
        robot.changeCount(-1)
        return (1, None)
    
    def standingon(self, robot, orders, index):
        bool = robot.standingOnToken()
        return (1, bool)
    
    def wallinfront(self, robot, orders, index):
        bool = robot.wallInFront()
        return (1, bool)
    
    def donumbertimes(self, robot, orders, index):
        if(robot.count <= 0):
            return (2, None)
        if(robot.repeat <= 0):
            robot.repeat = robot.count
        widget = orders[index+1]
        tool = widget.tool
        foo = Tool.METHODS[tool.type]
        foo(tool, robot, orders, index+1)
        robot.repeat -= 1
        if(robot.repeat <= 0):
            return (2, None)
        return (0, None)
    
    def ifthen(self, robot, orders, index):
        widget = orders[index+1]
        tool = widget.tool
        foo = Tool.METHODS[tool.type]
        result = foo(tool, robot, orders, index+1)
        if(result[1]):
            widget = orders[index+2]
            tool = widget.tool
            foo = Tool.METHODS[tool.type]
            foo(tool, robot, orders, index+2)
        return (3, None)
    
    def ifnotthen(self, robot, orders, index):
        widget = orders[index+1]
        tool = widget.tool
        foo = Tool.METHODS[tool.type]
        result = foo(tool, robot, orders, index+1)
        if(not result[1]):
            widget = orders[index+2]
            tool = widget.tool
            foo = Tool.METHODS[tool.type]
            foo(tool, robot, orders, index+2)
        return (3, None)
    
    def dowhile(self, robot, orders, index):
        widget = orders[index+1]
        tool = widget.tool
        foo = Tool.METHODS[tool.type]
        result = foo(tool, robot, orders, index+1)
        if(result[1]):
            widget = orders[index+2]
            tool = widget.tool
            foo = Tool.METHODS[tool.type]
            foo(tool, robot, orders, index+2)
            return (0, None)
        else:
            return (3, None)
    
    def untildo(self, robot, orders, index):
        widget = orders[index+1]
        tool = widget.tool
        foo = Tool.METHODS[tool.type]
        result = foo(tool, robot, orders, index+1)
        if(not result[1]):
            widget = orders[index+2]
            tool = widget.tool
            foo = Tool.METHODS[tool.type]
            foo(tool, robot, orders, index+2)
            return (0, None)
        else:
            return (3, None)
    
    def neworder(self, robot, orders, index):
        neworder = orders[index]
        i = index + neworder.step
        last = self.findLastOrder(orders)
        if(i < last and neworder.overflow < neworder.maxoverflow):
            if(orders[i]):
                if(orders[i].tool.type == Tool.NEW_FUNCTION):
                    neworder.step = 1
                    neworder.overflow = 0
                    return (1, True)
                if(orders[i].name == neworder.name):
                    self.error("Be careful and check your logic "+\
                        "or you'll be trapped doing the same orders")
                    neworder.step = 1
                    neworder.overflow = 0
                    return (1, True)
                widget = orders[i]
                tool = widget.tool
                foo = Tool.METHODS[tool.type]
                result = foo(tool, robot, orders, i)
            neworder.step += result[0]
            neworder.overflow += 1
            return (1, False)
        else:
            if(neworder.overflow >= neworder.maxoverflow):
                self.error("Be careful and check your logic "+\
                    "or you'll be trapped doing the same orders")
            neworder.step = 1
            neworder.overflow = 0
            return (1, True)
    
    def order(self, robot, orders, index):
        name = orders[index].name
        for i in xrange(len(orders)):
            if(orders[i] and orders[i].name == name and
               orders[i].tool.type == Tool.NEW_FUNCTION):
                widget = orders[i]
                tool = widget.tool
                foo = Tool.METHODS[tool.type]
                result = foo(tool, robot, orders, i)
                break
        if(result[1]):
            return (1, None)
        else:
            return (0, None)
    
    def findLastOrder(self, orders):
        i = 0
        for j in xrange(len(orders)):
            if(orders[j]):
                    i = j + 1
        return i
    
    def getColor(self):
        if(self.type in self.RED):
            return '#ff4040'
        elif(self.type in self.YELLOW):
            return 'yellow'
        elif(self.type in self.BLUE):
            return 'light blue'
        elif(self.type in self.PURPLE):
            return 'purple'
        elif(self.type in self.ORANGE):
            return 'orange'
        else:
            return 'white'
    
    def error(self, msg):
        master = Tkinter.Tk()
        Tkinter.Label(master, text=msg).pack()
        b = Tkinter.Button(master, text="OK",
                           command=master.destroy)
        b.pack(pady=5)
    
    METHODS = {MOVE_FORWARD: moveforward,
               MOVE_BACKWARD: movebackward,
               TURN_LEFT: turnleft,
               TURN_RIGHT: turnright,
               TURN_AROUND: turnaround,
               DRAW_HERE: drawhere,
               TOKEN_HERE: tokenhere,
               TOKEN_PICKUP: tokenpickup,
               PUSH: push,
               SAY: say,
               ADD_ONE: addone,
               SUB_ONE: subone,
               STANDING_ON: standingon,
               WALL_IN_FRONT: wallinfront,
               DO_NUMBER_TIMES: donumbertimes,
               IF_THEN: ifthen,
               IFNOT_THEN: ifnotthen,
               WHILE_DO: dowhile,
               UNTIL_DO: untildo,
               NEW_FUNCTION: neworder,
               OLD_FUNCTION: order}

#LearnToolFrame is a frame for the LearnToolCanvas to exist
class LearnToolFrame(Tkinter.Frame, object):

    def __init__(self, root, width, height):
        super(LearnToolFrame, self).__init__(root)
        root.toolCanvas = LearnToolCanvas(self, width, height)
        self.scrollbar = Tkinter.Scrollbar(self)
        self.scrollbar.pack(side=Tkinter.RIGHT,fill=Tkinter.Y)
        self.scrollbar.config(command=root.toolCanvas.yview)
        root.toolCanvas.config(yscrollcommand=self.scrollbar.set)

#LearnToolCanvas is where the possible tools are listed
class LearnToolCanvas(Tkinter.Canvas, object):
    
    def __init__(self, root, width, height):
        ratio = 0.2
        self.width = width*ratio
        self.height = height
        self.maxscroll = 2000
        super(LearnToolCanvas, self).__init__(root,
                    bg='white',
                    width=self.width, height=self.height,
                    scrollregion=(0, 0, self.maxscroll, self.maxscroll))
        self.pack(side='left')
        self.init()
    
    def init(self):
        self.editmode = False
        
        self.itemToTool = dict()
        self.tools = []
        self.createTools()
        self.titleid = None
        self.redrawAll()
        
        self.tag_bind('selectable', '<Button-1>', self.mouseClick)
        self.tag_bind('selectable', '<Enter>', self.enter)
        self.tag_bind('selectable', '<Leave>', self.leave)
        
        self.popup = None
    
    #Handler for mouse events
    def mouseClick(self, event):
        scale = self.maxscroll
        scroll = self.master.scrollbar.get()[0]
        truex, truey = event.x, event.y + scroll*scale
        item = self.find_closest(truex, truey)[0]
        tool = self.itemToTool[item]
        if(self.editmode):
            if(tool.visibility):
                self.itemconfigure(item, fill='white')
            else:
                self.itemconfigure(item, fill='grey')
            tool.visibility = not tool.visibility
        else:
            canvas = self.master.master.functionCanvas
            canvas.addTool(self.itemToTool[item])
        self.drawTools()
    
    #create popup
    def enter(self, event):
        if(self.popup): return
        scale = self.maxscroll
        scroll = self.master.scrollbar.get()[0]
        truex, truey = event.x, event.y + scroll*scale
        self.popup = Tkinter.Toplevel(self)
        self.popup.overrideredirect(True)
        self.popup.geometry("%+d%+d" %
                            (event.x, event.y))
        item = self.find_closest(truex, truey)[0]
        tool = self.itemToTool[item]
        text = Tool.HELP[tool.type]
        label = Tkinter.Label(self.popup, text=text,
                              justify=Tkinter.LEFT)
        label.pack()
    
    #delete popup
    def leave(self, event):
        if(self.popup):
            self.popup.destroy()
            self.popup = None
    
    #Instantiates all the tools
    def createTools(self):
        for tool in Tool.LEARNTOOLS:
            newTool = Tool(tool)
            newTool.visibility = True
            self.tools.append(newTool)
    
    def redrawAll(self):
        self.delete(Tkinter.ALL)
        self.createTitle()
        self.drawTools()
    
    #Draws all the tools
    def drawTools(self):
        x, y = self.width/2, 120
        height, width = 20, 80
        padding = 60
        for tool in self.tools:
            if(tool.visibility or self.editmode):
                if(not tool.visibility and self.editmode):
                    color = 'grey'
                else:
                    color = tool.getColor()
                itemid = self.create_rectangle(x-width, y-height,
                                               x+width, y+height,
                                               fill=color,
                                               tags='selectable')
                self.itemToTool[itemid] = tool
                y += padding
        y = 120
        for tool in self.tools:
            if(tool.visibility or self.editmode):
                text = Tool.TEXTS[tool.type]
                itemid = self.create_text(x, y, text=text,
                                          tags='selectable',
                                          font='bold')
                self.itemToTool[itemid] = tool
                y += padding
        
    #creates title instruction for players
    def createTitle(self):
        if(self.titleid):
            self.delete(self.titleid)
        x, y = self.width/2, 40
        if(self.editmode):
            text = "In editmode, you can enable\n" +\
                    "or disable tools\n" +\
                    "Click to grey out/disable"
        else:
            text = "These are your tools,\n" +\
                    "Click to add to the order list"
        self.titleid = self.create_text(x, y, text=text,
                                        font='bold',
                                        justify=Tkinter.CENTER)
    

#TeachToolFrame is a frame for the TeachToolCanvas to exist
class TeachToolFrame(Tkinter.Frame, object):

    def __init__(self, root, width, height):
        super(TeachToolFrame, self).__init__(root)
        root.functionCanvas = TeachToolCanvas(self, width, height)
        self.scrollbar = Tkinter.Scrollbar(self)
        self.scrollbar.pack(side=Tkinter.RIGHT,fill=Tkinter.Y)
        self.scrollbar.config(command=root.functionCanvas.yview)
        root.functionCanvas.config(yscrollcommand=self.scrollbar.set)

#TeachToolCanvas is where the teaching tools are listed
class TeachToolCanvas(Tkinter.Canvas, object):
    
    def __init__(self, root, width, height):
        ratio = 0.2
        self.width = width*ratio
        self.height = height
        self.maxscroll = 4000
        super(TeachToolCanvas, self).__init__(root,
                    bg='white',
                    width=self.width, height=self.height,
                    scrollregion=(0, 0, self.maxscroll, self.maxscroll))
        self.pack(side='left')
        self.init()
    
    def init(self):
        self.selectedItem = None
        self.selectedTool = None
        self.tools = [None]
        self.createTools()
        self.drawTools()
        
        self.tag_bind('selectable', '<Button-1>', self.mouseClick)
    
    #Handler for mouse events
    def mouseClick(self, event):
        scale = self.maxscroll
        scroll = self.master.scrollbar.get()[0]
        truex, truey = event.x, event.y + scroll*scale
        item = self.find_closest(truex, truey)[0]
        self.itemconfigure(self.selectedItem, fill='white')
        self.selectedItem = item
        if(item >= len(self.tools)):
            self.selectedTool = None
        else:
            self.selectedTool = self.tools[item]
        self.itemconfigure(item, fill='grey')

    #Instantiates all the tools
    def createTools(self):
        for tool in Tool.TEACHTOOLS:
            self.tools.append(Tool(tool))
    
    #Draws all the tools
    def drawTools(self):
        x, y = self.width/2, 160
        height, width = 20, 60
        padding = 60
        for tool in self.tools:
            if(tool):
                self.create_rectangle(x-width, y-height,
                                      x+width, y+height,
                                      fill='white',
                                      tags='selectable')
                y += padding
        y = 160
        for tool in self.tools:
            if(tool):
                text = Tool.TEXTS[tool.type]
                self.create_text(x, y, text=text)
                y += padding
        self.drawDragBox()
    
    #Draws the drag-drop option
    def drawDragBox(self):
        x, y = self.width/2, 100
        height, width = 20, 60
        itemid = self.create_rectangle(x-width, y-height,
                                       x+width, y+height,
                                       fill='grey',
                                       tags='selectable')
        self.selectedItem = itemid
        self.create_text(x, y, text="drag-drop mode")
        self.create_text(x, y-60, text="Click a grid object "+\
                         "to add it to the board\n\n"+\
                         "Right click a grid object\n"+\
                         "to remove it from the board",
                         justify=Tkinter.CENTER)

#Widget Class defines widgets that go on the FunctionFrame
class Widget(object):
    
    
    RAWRED = Image.open("images/widgetred.png")
    RAWBLUE = Image.open("images/widgetblue.png")
    RAWYELLOW = Image.open("images/widgetyellow.png")
    RAWORANGE = Image.open("images/widgetorange.png")
    RAWPURPLE = Image.open("images/widgetpurple.png")
    
    def __init__(self, position, tool, name=None):
        (self.x, self.y) = position
        self.tool = tool
        self.contentsid = []
        self.value = dict()
        self.name = name
        self.setIMG()
        self.xoff = 10
        self.step = 1
        self.overflow = 0
        self.maxoverflow = 100
        if(not self.name):
            if(self.tool.type == Tool.OLD_FUNCTION or
               self.tool.type == Tool.NEW_FUNCTION):
                self.askName()
            else:
                self.name = Tool.TEXTS[self.tool.type]
    
    #asks for a name of this widget
    def askName(self):
        master = Tkinter.Tk()
        form = Tkinter.Entry(master)
        form.pack()
        form.focus_set()
        button = Tkinter.Button(master,
                text="What is the name\nof this order?",
                width=20,command=lambda f=form:\
                    self.setName(master, f))
        button.pack()
        master.mainloop()
    
    #returns the name based on the form
    def setName(self, master, form):
        name = form.get()
        name = name[0:10]
        master.destroy()
        master.quit()
        if(not name):
            name = "undefined"
        self.name = name
    
    # sets the images for the widgets for the canvas
    def setIMG(self):
        if(self.tool.type in Tool.RED):
            self.color = 'red'
            self.image = ImageTk.PhotoImage(self.RAWRED)
        elif(self.tool.type in Tool.BLUE):
            self.color = 'blue'
            self.image = ImageTk.PhotoImage(self.RAWBLUE)
        elif(self.tool.type in Tool.YELLOW):
            self.color = 'yellow'
            self.image = ImageTk.PhotoImage(self.RAWYELLOW)
        elif(self.tool.type in Tool.ORANGE):
            self.color = 'orange'
            self.image = ImageTk.PhotoImage(self.RAWORANGE)
        elif(self.tool.type in Tool.PURPLE):
            self.color = 'purple'
            self.image = ImageTk.PhotoImage(self.RAWPURPLE)
    
    #allows for movement of the widget across the canvas
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
    
    #draws the image
    def drawImage(self, canvas, dimensions):
        x1 = self.x
        y1 = self.y
        canvas.create_image(x1-self.xoff, y1, anchor=Tkinter.NW,
                            image=self.image, tags="movable")
        return True
    
    #create the text on the widget
    def createText(self, canvas, dimensions):
        x1 = self.x
        y1 = self.y
        x2 = x1 + dimensions[0]
        y2 = y1 + dimensions[1]
        ws = canvas.widgetsize[1]
        if(self.color == 'blue'):
            texts = Tool.BLUE_TEXT[self.tool.type]
            canvas.create_text((x1+x2)/2,
                               (y1+y2)/2,
                               text=texts[0],
                               font='bold')
            canvas.create_text((x1+x2)/2,
                               (y1+y2)/2+1*ws,
                               text=texts[1],
                               font='bold')
            canvas.create_text((x1+x2)/2,
                               (y1+y2)/2+3*ws,
                               text=texts[2],
                               font='bold')
        else:
            canvas.create_text((x1+x2)/2, (y1+y2)/2,
                               text=self.name,
                               font='bold')
    
    #draws a widget to the canvas
    def draw(self, canvas, dimensions):
        x1 = self.x
        y1 = self.y
        x2 = x1 + dimensions[0]
        y2 = y1 + dimensions[1]
        color = self.tool.getColor()
        if(not self.drawImage(canvas, dimensions)):
            canvas.create_rectangle(x1, y1, x2, y2,
                                    fill=color, tags="movable")
        self.createText(canvas, dimensions)

#FunctionFrame is a frame for the FunctionCanvas to exist
class FunctionFrame(Tkinter.Frame, object):

    def __init__(self, root, width, height):
        super(FunctionFrame, self).__init__(root)
        root.functionCanvas = FunctionCanvas(self, width, height)
        self.scrollbar = Tkinter.Scrollbar(self)
        self.scrollbar.pack(side=Tkinter.RIGHT,fill=Tkinter.Y)
        self.scrollbar.config(command=root.functionCanvas.yview)
        root.functionCanvas.config(yscrollcommand=self.scrollbar.set)

#FunctionCanvas is the canvas where the functions
class FunctionCanvas(Tkinter.Canvas, object):
    
    RAW_RUN = Image.open("images/gobutton.png")
    RAW_POINTER = Image.open("images/pointer.png")
    
    
    def __init__(self, root, width, height):
        ratio = 0.2
        self.width = width*ratio
        self.height = height
        self.maxscroll = 4000
        super(FunctionCanvas, self).__init__(root,
                    bg='white', width=self.width, height=self.height,
                    scrollregion=(0, 0, self.maxscroll, self.maxscroll))
        self.pack(side="left")
        self.init()
    
    def init(self):
        self.selected = {"widget":None, "x":None, "y":None}
        self.widgetsize = (160, 40)
        self.widgets = []
        self.maxfunctions = 100
        self.widgetfunctions = [None]*self.maxfunctions
        self.responsive = True
        self.offsettop = 0
        self.count = 0
        self.overflow = 300
        
        self.enableRun()
        self.createSnapRegion()
        self.enableMouse()
        
        self.redrawAll()
    
    #Initiates mouse events
    def enableMouse(self):
        self.tag_bind("run", "<Button-1>", self.runFunctions)
        self.bind('<Button-3>', self.mouseClick)
        self.bind("<ButtonPress-1>", self.mousePress)
        self.bind("<B1-Motion>", self.mouseMove)
        self.bind("<ButtonRelease-1>", self.mouseRelease)

    #Redraws all
    def redrawAll(self):
        self.delete(Tkinter.ALL)
        self.enableRun()
        self.drawSnapRegion()
        for w in self.widgets:
            w.draw(self, self.widgetsize)
    
    #Takes a widget and draws it to the screen
    def drawWidget(self, widget):
        tool = widget.tool
        x1 = widget.x
        y1 = widget.y
        x2 = x1 + self.widgetsize[0]
        y2 = y1 + self.widgetsize[1]
        self.create_rectangle(x1, y1, x2, y2,
                              fill="grey", tags="movable")
        self.create_text((x1+x2)/2, (y1+y2)/2,
                         text=Tool.TEXTS[tool.type])
    
    #Draws the snap region
    def drawSnapRegion(self):
        x, y = self.snapRegion[0], self.snapRegion[1]
        widx, widy = self.widgetsize
        for i in xrange(2*self.maxfunctions):
            if(i % 2 == 0):
                self.create_rectangle(x, y + i*widy,
                                      x + widx, y + (i+1)*widy,
                                      outline="red", dash=1)
        self.create_text((2*x + widx)/2, (2*y + widy)/2,
                         text="To get started, click an order,"+
                            "\non the left and drag it here")
        self.create_text((2*x + widx)/2, (2*y + 5*widy)/2,
                         text="Right click an order\nto delete it")
    
    #Defines a region for widgets to snap to
    def createSnapRegion(self):
        startx, starty = self.width/2-80, 80
        widx, widy = self.widgetsize
        self.snapRegion = (startx, starty,
                           startx + widx,
                           starty + 2*self.maxfunctions*widy)
    
    #Creates a run button to run widget tools
    #and pointer image tracker
    def enableRun(self):
        margin = 20
        self.runimage = ImageTk.PhotoImage(self.RAW_RUN)
        self.pointerimage = ImageTk.PhotoImage(self.RAW_POINTER)
        self.pointerid = None
        self.create_image(self.width/2, 2*margin,
                         image=self.runimage, tags="run")
    
    #Runs the functions in the snapregion
    def runFunctions(self, event):
        if(not self.responsive): return
        self.count = 0
        self.responsive = False
        canvas = self.master.master.graphicCanvas
        canvas.robots[0].runlist = self.widgetfunctions
        done = False
        while(not done):
            done = self.runOnce()
        for obj in canvas.objects:
            obj.reset()
        self.responsive = True
        if(canvas.playmode):
            canvas.resetBoard()
    
    #Iterates one run call
    def runOnce(self):
        canvas = self.master.master.graphicCanvas
        done = False
        self.drawPointer()
        for obj in canvas.objects:
            if(isinstance(obj, Robot)):
                (action, finish) = obj.action()
                if(not done):
                    done = finish
                if(action):
                    canvas.redrawAll()
                    canvas.update()
        self.count += 1
        if(self.count > self.overflow):
            self.error("Be careful and check your logic "+\
                    "or you'll be trapped doing the same orders")
            done = True
        return done
    
    #draws pointer tracker
    def drawPointer(self):
        if(self.pointerid):
            self.delete(self.pointerid)
        canvas = self.master.master.graphicCanvas
        robot = canvas.robots[0]
        index = robot.index
        ws = self.widgetsize[1]
        x, y = self.width/2-120, (160+ws)/2
        self.pointerid = self.create_image(x,
                            y+ws*2*index,
                            image=self.pointerimage)
    
    #Takes a coordinate and finds a widget
    def findWidget(self, x, y):
        widgetlist = copy.copy(self.widgets)
        widgetlist.reverse()
        for widget in widgetlist:
            if(x > widget.x and
               x < widget.x + self.widgetsize[0] and
               y > widget.y and
               y < widget.y + self.widgetsize[1]):
                return widget
    
    #Takes a widget and removes the widget from the board
    def removeWidgetFromBoard(self, widget):
        self.widgets.remove(widget)
    
    #Handler for Mouse events
    def mouseClick(self, event):
        if(not self.responsive): return
        scale = self.maxscroll
        scroll = self.master.scrollbar.get()[0]
        truex, truey = event.x, event.y + scroll*scale
        widget = self.findWidget(truex, truey)
        if(widget):
            if(widget in self.widgetfunctions):
                i = self.widgetfunctions.index(widget)
                self.widgetfunctions[i] = None
            self.removeWidgetFromBoard(widget)
        self.redrawAll()
    
    #Handler for Mouse events
    def mousePress(self, event):
        if(not self.responsive): return
        scale = self.maxscroll
        scroll = self.master.scrollbar.get()[0]
        truex, truey = event.x, event.y + scroll*scale
        widget = self.findWidget(truex, truey)
        if(widget):
            self.selected["widget"] = widget
            self.selected["x"] = truex
            self.selected["y"] = truey
            if(widget in self.widgetfunctions):
                i = self.widgetfunctions.index(widget)
                self.widgetfunctions[i] = None
        self.redrawAll()
    
    #Handler for Mouse events
    def mouseMove(self, event):
        if(not self.selected["widget"]): return
        scale = self.maxscroll
        scroll = self.master.scrollbar.get()[0]
        truex, truey = event.x, event.y + scroll*scale
        dx = truex - self.selected["x"]
        dy = truey - self.selected["y"]
        widget = self.selected["widget"]
        widget.move(dx, dy)
        self.selected["x"] = truex
        self.selected["y"] = truey
        self.redrawAll()
    
    #Handler for Mouse events
    def mouseRelease(self, event):
        if(not self.selected["widget"]): return
        widget = self.selected["widget"]
        scale = self.maxscroll
        scroll = self.master.scrollbar.get()[0]
        truex, truey = event.x, event.y + scroll*scale
        truex, truey = int(truex), int(truey)
        if(not self.onCanvas(event.x, event.y)):
            self.removeWidgetFromBoard(widget)
            return
        elif(self.inSnapRegion(truex, truey)):
            self.snap(truex, truey)
        self.selected["widget"] = None
        self.selected["x"] = None
        self.selected["y"] = None
        self.redrawAll()
    
    #Takes a coordinate and checks
    #if it is in the snapregion
    def inSnapRegion(self, x, y):
        x1, y1, x2, y2 = self.snapRegion
        return (x >= x1 and x <= x2 and
           y >= y1 and y <= y2)
    
    #Takes a coordinate and snaps
    #current widget to coordinate NW
    def snap(self, x, y):
        widget = self.selected["widget"]
        offy = y - self.snapRegion[1]
        row = offy/self.widgetsize[1]
        if(row >= 2*len(self.widgetfunctions) or
           row % 2 != 0 or self.widgetfunctions[row/2]):
            return
        index = row/2
        if(self.legalSnap(widget, index)):
            self.widgetfunctions[index] = widget
            widget.x = self.snapRegion[0]
            widget.y = self.snapRegion[1] + row*self.widgetsize[1]
        else:
            self.replaceWidget(widget)
        self.redrawAll()
    
    #checks if the snap is legal
    def legalSnap(self, widget, index):
        wf = self.widgetfunctions
        if(widget.tool.type not in Tool.RED):
            if(index - 1 >= 0 and wf[index-1] and
               wf[index-1].tool.type in Tool.ORANGE):
                self.error("Only Red Allowed Here")
                return False
            if(index - 2 >= 0 and wf[index-2] and
               wf[index-2].tool.type in Tool.BLUE):
                self.error("Only Red Allowed Here")
                return False
        if(widget.tool.type not in Tool.YELLOW):
            if(index - 1 >= 0 and wf[index-1] and
               wf[index-1].tool.type in Tool.BLUE):
                self.error("Only Yellow Allowed Here")
                return False
        if(widget.tool.type in Tool.BLUE):
            if(index + 2 >= len(wf) or
               wf[index+1] or wf[index+2]):
                self.error("Make sure next 2 cells are empty")
                return False
        if(widget.tool.type in Tool.ORANGE):
            if(index + 2 >= len(wf) or wf[index+1]):
                self.error("Make sure next 1 cell is empty")
                return False
        if(widget.tool.type in Tool.YELLOW):
            if(index - 1 < 0 or not wf[index-1] or
               not (wf[index-1].tool.type in Tool.BLUE)):
                self.error("No Yellow Allowed Here")
                return False
        return True
    
    #displays error
    def error(self, msg):
        master = Tkinter.Tk()
        Tkinter.Label(master, text=msg).pack()
        b = Tkinter.Button(master, text="OK",
                           command=master.destroy)
        b.pack(pady=5)
    
    #replaces the widget to start
    def replaceWidget(self, widget):
        self.removeWidgetFromBoard(widget)
        self.addTool(widget.tool, name=widget.name)
    
    #Takes a coordinate and checks if on canvas
    def onCanvas(self, x, y):
        if(x < 0 or x > self.width):
            return False
        if(y < 0 or y > self.height):
            return False
        return True
    
    #takes a tool and adds it to the widgets
    def addTool(self, tool, x=20, y=60, name=None):
        y = y + 30*self.offsettop
        scale = self.maxscroll
        scroll = self.master.scrollbar.get()[0]
        truex, truey = x, y + scroll*scale
        widget = Widget((truex,truey), tool, name)
        self.widgets.append(widget)
        self.redrawAll()
        self.offsettop += 1
        if(self.offsettop >= 10):
            self.offsettop = 0
    
    #attaches a widget id to the function call
    def attachTool(self, itemid):
        self.widgetfunctions.append(itemid)

#GraphicFrame is a frame for the GraphicCanvas to exist
class GraphicFrame(Tkinter.Frame, object):

    def __init__(self, root, width, height):
        super(GraphicFrame, self).__init__(root)
        root.graphicCanvas = GraphicCanvas(self, width, height)
        self.canvas = root.graphicCanvas
        root.graphicCanvas.grid(row=0, column=0)
        self.makeScrollbars()
    
    #makes scrollbars for the canvas
    def makeScrollbars(self):
        self.yscrollbar = Tkinter.Scrollbar(self, orient=Tkinter.VERTICAL)
        self.yscrollbar.pack(side=Tkinter.RIGHT,fill=Tkinter.Y)
        self.yscrollbar.config(command=self.master.graphicCanvas.yview)
        self.yscrollbar.grid(row=0, column=1, sticky=Tkinter.N+Tkinter.S)
        self.xscrollbar = Tkinter.Scrollbar(self, orient=Tkinter.HORIZONTAL)
        self.xscrollbar.pack(side=Tkinter.BOTTOM,fill=Tkinter.X)
        self.xscrollbar.config(command=self.master.graphicCanvas.xview)
        self.xscrollbar.grid(row=1, column=0, sticky=Tkinter.E+Tkinter.W)
        self.canvas.config(scrollregion=(0, 0,
                        self.canvas.maxscroll, self.canvas.maxscroll))
        self.canvas.config(xscrollcommand=self.xscrollbar.set,
                           yscrollcommand=self.yscrollbar.set)

#GraphicCanvas is the visual represntation of the board
class GraphicCanvas(Tkinter.Canvas, object):

    def __init__(self, root, width, height, boardSize=10):
        ratio = 0.6
        self.width = width*ratio
        self.height = height
        self.boardSize = boardSize
        self.screenfit = 20
        self.space = max(1.0*self.width/self.screenfit,
                          1.0*self.height/self.screenfit)
        self.maxscroll = int(self.space*(boardSize+1))
        self.maxzoom = 20
        self.minzoom = 400
        super(GraphicCanvas, self).__init__(root,
                    bg='white',
                    width=self.width, height=self.height,
                    scrollregion=(0, 0, self.maxscroll, self.maxscroll))
        self.pack(side="left")
        self.init()
    
    def init(self):
        self.playmode = False
        self.objects = []
        self.createBoard()
        self.initboard = copy.deepcopy(self.board)
        self.initboard[0][0].append(Tool.ROBOT)
        self.initcount = 0
        self.initfacing = Robot.RIGHT
        self.robots = [Robot(Tool.ROBOT, self)]
        self.steps = 20
        self.selected = None
        self.fast = False
        self.instructions = ""
        
        self.bind('<Button-1>', self.mouseClick)
        self.bind('<Button-3>', self.mouseClickRight)
        self.bind("<B1-Motion>", self.mouseMove)
        self.bind("<ButtonRelease-1>", self.mouseRelease)
    
        self.redrawAll()
    
    #Instantiates the board
    def createBoard(self):
        self.board = []
        for i in xrange(self.boardSize):
            self.board.append([])
            for j in xrange(self.boardSize):
                self.board[i].append([])
                self.board[i][j] = []
    
    #Recreates the board from the current stored board
    def reconstructBoard(self):
        b = self.board
        self.initboard = copy.deepcopy(b)
        self.objects = []
        self.robots = []
        def construct( b, i, j, k, tool):
            b[i][j][k] = GridObject.construct(tool, i, j, self)
        for i in xrange(len(b)):
            for j in xrange(len(b[i])):
                length = len(b[i][j])
                for k in xrange(length):
                    construct(b, i, j, k, b[i][j][k])
                    if(b[i][j][k].type == Tool.ROBOT):
                        self.robots.append(b[i][j][k])
                    b[i][j][k] = b[i][j][k-1]
                    b[i][j].pop()
        self.robots[0].count = self.initcount
        self.robots[0].facing = self.initfacing
    
    #resets board to last save
    def resetBoard(self):
        self.board = self.initboard
        self.reconstructBoard()
        self.redrawAll()
    
    #Redraws All
    def redrawAll(self):
        self.delete(Tkinter.ALL)
        self.drawGrid()
        for obj in self.objects:
            obj.draw()
        for robot in self.robots:
            robot.draw()
    
    #Draws grid
    def drawGrid(self):
        for i in xrange(self.boardSize + 1):
            self.create_line(i*self.space, 0,
                             i*self.space, self.boardSize*self.space,
                             fill="grey")
            self.create_line(0, i*self.space,
                             self.boardSize*self.space, i*self.space,
                             fill="grey")
    
    #Draws a cell
    def drawCell(self, row, col, item):
        if(item == 0): return
    
    #Handler for Mouse Events
    def mouseClick(self, event):
        if(not self.master.master.toolCanvas.editmode): return
        coordinate = self.findPosition(event.x, event.y)
        if(not self.onBoard(coordinate[0], coordinate[1])): return
        tool = self.master.master.functionCanvas.selectedTool
        if(tool and self.isAccessible(coordinate)):
            toolType = tool.type
            GridObject.construct(toolType, coordinate[0], coordinate[1], self)
            self.redrawAll()
        if(self.get((coordinate[0], coordinate[1]))):
            self.selected = coordinate

    #Handler for Mouse Events
    def mouseClickRight(self, event):
        if(not self.master.master.toolCanvas.editmode): return
        coordinate = self.findPosition(event.x, event.y)
        if(not self.onBoard(coordinate[0], coordinate[1])): return
        obj = self.get((coordinate[0], coordinate[1]))
        if(obj and obj[-1] != self.robots[0]):
            self.pop(coordinate)
            self.redrawAll()

    #Handler for Mouse Events
    def mouseMove(self, event):
        newCoord = self.findPosition(event.x, event.y)
        if(self.selected and self.onBoard(newCoord[0], newCoord[1]) and
           self.isAccessible(newCoord)):
            obj = self.pop(self.selected)
            self.selected = self.findPosition(event.x, event.y)
            obj.position = self.selected
            self.place(self.selected, obj)
            self.redrawAll()
    
    #Handler for Mouse Events
    def mouseRelease(self, event):
        self.selected = None
    
    #Takes a coordinate and returns a grid position
    def findPosition(self, x, y):
        scale = self.maxscroll
        xscroll = self.master.xscrollbar.get()[0]
        yscroll = self.master.yscrollbar.get()[0]
        truex = x + xscroll*scale
        truey = y + yscroll*scale
        return int(truey/self.space), int(truex/self.space)
    
    #Takes a grid coordinate and returns True if on board
    def onBoard(self, row, col):
        if(row < 0 or row >= self.boardSize):
            return False
        elif(col < 0 or col >= self.boardSize):
            return False
        return True
    
    #Takes a grid position and returns a list of the objects
    def get(self, position):
        r, c = position
        arr = self.board[int(r)][int(c)]
        return arr
    
    #Takes a position and object and places the object
    def place(self, position, gridobject):
        r, c = position
        if(gridobject.type == Tool.ROBOT):
            self.objects.insert(0, gridobject)
        else:
            self.objects.append(gridobject)
        self.board[int(r)][int(c)].append(gridobject)
    
    #Takes an object and removes it from the grid
    def remove(self, gridobject):
        r, c = gridobject.position
        self.objects.remove(gridobject)
        arr = self.board[int(r)][int(c)]
        arr.remove(gridobject)
    
    #Takes a position and removes the top object
    def pop(self, position):
        r, c = position
        arr = self.board[int(r)][int(c)]
        popped = arr[len(arr)-1]
        self.objects.remove(popped)
        arr.remove(popped)
        return popped
    
    #Takes a position and states whether objects can enter
    def isAccessible(self, position):
        r = int(round(position[0]))
        c = int(round(position[1]))
        if(not self.onBoard(r, c)): return False
        arr = self.get(position)
        for obj in arr:
            if(obj.type in Tool.INACCESSIBLE):
                return False
        return True

#GridObject class for objects that can be added to the board
class GridObject(object):
    
    NO_ACTION = (False, False)
    COMPLETE_ACTION = (True, False)
    
    def __init__(self, toolType, canvas,
                 position=(0.0,0.0), color=None):
        self.type = toolType
        self.canvas = canvas
        self.position = float(position[0]), float(position[1])
        self.color = color
        self.resizeImage()
        if(self.onBoard(self.position[0], self.position[1])):
            self.canvas.place(position, self)
    
    @staticmethod
    def construct(tool, row, col, canvas):
        if(tool == Tool.ROBOT):
            return Robot(tool, canvas, position=(row, col))
        if(tool == Tool.TOKEN):
            return Token(tool, canvas, position=(row, col))
        if(tool == Tool.INV_TOKEN):
            return InvisibleToken(tool, canvas, position=(row, col))
        if(tool == Tool.PAINT):
            return Paint(tool, canvas, position=(row, col))
        if(tool == Tool.ROCK):
            return Rock(tool, canvas, position=(row, col))
        if(tool == Tool.WALL):
            return Wall(tool, canvas, position=(row, col))
        if(tool == Tool.INV_WALL):
            return InvisibleWall(tool, canvas, position=(row, col))
        if(tool == Tool.UP_TURNER):
            return UpTurner(tool, canvas, position=(row, col))
        if(tool == Tool.DOWN_TURNER):
            return DownTurner(tool, canvas, position=(row, col))
        if(tool == Tool.LEFT_TURNER):
            return LeftTurner(tool, canvas, position=(row, col))
        if(tool == Tool.RIGHT_TURNER):
            return RightTurner(tool, canvas, position=(row, col))
        if(tool == Tool.UP_PUSHER):
            return UpPusher(tool, canvas, position=(row, col))
        if(tool == Tool.DOWN_PUSHER):
            return DownPusher(tool, canvas, position=(row, col))
        if(tool == Tool.LEFT_PUSHER):
            return LeftPusher(tool, canvas, position=(row, col))
        if(tool == Tool.RIGHT_PUSHER):
            return RightPusher(tool, canvas, position=(row, col))
        if(tool == Tool.ADDER):
            return Adder(tool, canvas, position=(row, col))
        if(tool == Tool.SUBTRACTER):
            return Subtracter(tool, canvas, position=(row, col))
        if(tool == Tool.GOAL):
            return Goal(tool, canvas, position=(row, col))
        if(tool == Tool.TRANSPORTER):
            return Teleporter(tool, canvas, position=(row, col))
        if(tool == Tool.BLUEBRUSH):
            return BlueBrush(tool, canvas, position=(row, col))
        if(tool == Tool.REDBRUSH):
            return RedBrush(tool, canvas, position=(row, col))
        if(tool == Tool.GREENBRUSH):
            return GreenBrush(tool, canvas, position=(row, col))
    
    #Takes a grid coordinate and returns True if on board
    def onBoard(self, row, col):
        return self.canvas.onBoard(row, col)
    
    #placeholder, must be overridden
    def inView(self):
        r = int(round(self.position[0]))
        c = int(round(self.position[1]))
        return self.canvas.onBoard(r, c)
    
    #placeholder, must be overridden
    def draw(self):
        pass
    
    #draws with image
    def drawImage(self):
        r, c = self.position
        w = h = self.canvas.space
        image = self.IMAGE
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(((c+0.5)*w, (r+0.5)*h),
                                image=self.photo)
        return True
    
    #resizes the image, override
    def resizeImage(self):
        pass
    
    #placeholder, must be overridden
    def action(self):
        return self.NO_ACTION
    
    #resets index
    def reset(self):
        self.index = 0
    
    #string represntation (for saves)
    def __repr__(self):
        return str(self.type)

class Robot(GridObject):
    
    UP = (-1.0, 0.0)
    DOWN = (1.0, 0.0)
    LEFT = (0.0, -1.0)
    RIGHT = (0.0, 1.0)
    
    RAW_IMG = {UP: [Image.open("images/robot_up.png"),
                    Image.open("images/robot_up2.png"),
                    Image.open("images/robot_up3.png")],
               DOWN: [Image.open("images/robot_down.png"),
                      Image.open("images/robot_down2.png"),
                      Image.open("images/robot_down3.png")],
               LEFT: [Image.open("images/robot_left.png"),
                      Image.open("images/robot_left2.png"),
                      Image.open("images/robot_left3.png")],
               RIGHT: [Image.open("images/robot_right.png"),
                      Image.open("images/robot_right2.png"),
                      Image.open("images/robot_right3.png")]}
    
    def __init__(self, toolType, canvas,
                 position=(0.0,0.0), facing=RIGHT):
        self.IMG = dict()
        super(Robot, self).__init__(toolType, canvas,
                                    position, color='blue')
        self.facing = facing
        self.count = 0
        self.repeat = 0
        self.runlist = []
        self.index = 0
        self.ids = [None, None, None]
        
    
    def drawImage(self):
        r, c = self.position
        w = h = self.canvas.space
        image = self.IMG[self.facing][self.colorNum()]
        self.photo = ImageTk.PhotoImage(image)
        self.ids[0] = self.canvas.create_image(((c+0.5)*w,
                                                (r+0.5)*h),
                                            image=self.photo)
        m = 0.25
        self.ids[1] = self.canvas.create_oval(c*w, r*h,
                                              (c+m)*w, (r+m)*h,
                                            fill='white')
        self.ids[2] = self.canvas.create_text(((c*w+(c+m)*w)/2,
                                               (r*h+(r+m)*h)/2),
                                            text=str(self.count))
        return True
    
    def draw(self):
        for item in self.ids:
            if(item):
                self.canvas.delete(item)
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        m = 2
        w = h = self.canvas.space
        self.ids[0] = self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)
        self.ids[1] = self.canvas.create_text((c+0.5)*w+m, (r+0.5)*h+m,
                                text=str(self.count))
        self.ids[2] = self.drawHead()
    
    def drawHead(self):
        r, c = self.position
        w = h = self.canvas.space
        m = 20
        n = 15
        return self.canvas.create_oval(
                            c*w+m + n*self.facing[1],
                            r*h+m + n*self.facing[0],
                            (c+1)*w-m + n*self.facing[1],
                            (r+1)*h-m + n*self.facing[0],
                            fill='white')
    
    def colorNum(self):
        if(self.color=='blue'):
            return 0
        elif(self.color=='red'):
            return 1
        elif(self.color=='green'):
            return 2
    
    def resizeImage(self):
        w = h = self.canvas.space
        for face in self.RAW_IMG:
            size = len(self.RAW_IMG[face])
            self.IMG[face] = [None] * size
            for i in xrange(size):
                self.IMG[face][i] = self.RAW_IMG[face][i].resize(
                                            (int(w), int(h)),
                                            Image.ANTIALIAS)
    
    #Takes an action according to the list and
    #returns True for action complete, boolean for finished all orders
    def action(self):
        if(self.index >= len(self.runlist)):return
        if(self.runlist[self.index]):
            widget = self.runlist[self.index]
            tool = widget.tool
            foo = Tool.METHODS[tool.type]
            increment = foo(tool, self, self.runlist, self.index)[0]
        else:
            increment = 1
        self.index += increment
        last = self.findLastAction()
        if(self.index >= last):
            return (True, True)
        else:
            return (True, False)
    
    #finds the index of the last item on functionlist
    def findLastAction(self):
        i = 0
        for j in xrange(len(self.runlist)):
            if(self.runlist[j]):
                if(self.runlist[j].tool.type == Tool.NEW_FUNCTION):
                    return i
                else:
                    i = j + 1
        return i
    
    #Delays
    def delay(self):
        delay = 0.001
        time.sleep(delay)
    
    #Takes an int and changes the count
    def changeCount(self, dx):
        self.count += dx
    
    #Returns the coordinate directly in front
    def side(self, face=None, dist=1):
        if(not face):
            face = self.facing
        r = round(self.position[0] + dist*face[0])
        c = round(self.position[1] + dist*face[1])
        return (r, c)
    
    #Moves forward
    def move(self, direction=None):
        if(not direction):
            direction = self.facing
        position = self.side(direction)
        if(not self.canvas.onBoard(position[0],
                                   position[1]) or
           not self.canvas.isAccessible(position)): return
        if(self.onBoard(self.position[0], self.position[1])):
            self.canvas.remove(self)
        dr, dc = direction
        stepr = 1.0*dr/self.canvas.steps
        stepc = 1.0*dc/self.canvas.steps
        for i in xrange(self.canvas.steps):
            self.position = (self.position[0]+stepr,
                             self.position[1]+stepc)
            self.draw()
            self.canvas.update()
            self.delay()
        self.position = round(self.position[0]), round(self.position[1])
        if(self.onBoard(self.position[0], self.position[1])):      
            self.canvas.place(self.position, self)
        self.activateSquare()
    
    #activates any interactive object
    def activateSquare(self):
        arr = self.canvas.get(self.position)
        for obj in arr:
            if(obj.type != Tool.ROBOT):
                obj.action()
    
    #Turns left
    def turnLeft(self):
        if (self.facing == Robot.UP):
            self.facing = Robot.LEFT
        elif (self.facing == Robot.LEFT):
            self.facing = Robot.DOWN
        elif (self.facing == Robot.DOWN):
            self.facing = Robot.RIGHT
        elif (self.facing == Robot.RIGHT):
            self.facing = Robot.UP
        self.delay()
    
    #Turns right
    def turnRight(self):
        if (self.facing == Robot.UP):
            self.facing = Robot.RIGHT
        elif (self.facing == Robot.RIGHT):
            self.facing = Robot.DOWN
        elif (self.facing == Robot.DOWN):
            self.facing = Robot.LEFT
        elif (self.facing == Robot.LEFT):
            self.facing = Robot.UP
        self.delay()
    
    #Add paint object to current position
    def paintHere(self):
        position = round(self.position[0]), round(self.position[1])
        paint = Paint(Tool.PAINT, self.canvas, position,
                      color=self.color)
    
    #Adds token object to current position
    def placeToken(self):
        position = round(self.position[0]), round(self.position[1])
        token = Token(Tool.TOKEN, self.canvas, position)
    
    #Removes token object to current position
    def pickUpToken(self):
        arr = self.canvas.get(self.position)
        for obj in arr:
            if(isinstance(obj, Token)):
                self.canvas.remove(obj)
                return obj
    
    #Pushes rock in direction
    def push(self):
        start = self.side()
        end = self.side(dist=2)
        if(not self.canvas.onBoard(start[0],
                                   start[1])):return
        arr = self.canvas.get(start)
        for obj in arr:
            if(obj.type == Tool.ROCK):
                if(not self.canvas.onBoard(end[0],
                                           end[1])):return
                if(self.canvas.isAccessible(end)):
                    self.canvas.remove(obj)
                    obj.position = end
                    self.canvas.place(obj.position, obj)
                return
    
    def standingOnToken(self):
        arr = self.canvas.get(self.position)
        for obj in arr:
            if(isinstance(obj, Token)):
                return True
        return False
    
    def wallInFront(self):
        front = self.side()
        if(not self.canvas.onBoard(front[0], front[1])):
            return False
        arr = self.canvas.get(front)
        for obj in arr:
            if(isinstance(obj, Wall)):
                return True
        return False

#Paint object
class Paint(GridObject):
    
    def __init__(self, toolType, canvas, position, color="blue"):
        super(Paint, self).__init__(toolType, canvas, position, color)
    
    def draw(self):
        if(not self.inView()): return
        r, c = self.position
        w = h = self.canvas.space
        self.canvas.create_rectangle(c*w, r*h,
                                    (c+1)*w, (r+1)*h,
                                    fill=self.color)

#Token object
class Token(GridObject):
    
    RAW_IMAGE = Image.open("images/token.png")
    
    def __init__(self, toolType, canvas, position, color="yellow"):
        super(Token, self).__init__(toolType, canvas, position, color)
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)

    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

#Invisible Token object
class InvisibleToken(Token):
    
    RAW_IMAGE = Image.open("images/token_inv.png")
    
    def __init__(self, toolType, canvas, position, color="token"):
        super(InvisibleToken, self).__init__(toolType,
                                    canvas, position, color)
    
    def drawImage(self):
        if(self.canvas.playmode): return True
        r, c = self.position
        m = 2
        w = h = self.canvas.space
        image = self.IMAGE
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(((c+0.5)*w, (r+0.5)*h),
                                image=self.photo)
        return True
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        self.color = "" if self.canvas.playmode else "token"
        if(not self.inView()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                outline="",
                                fill=self.color)

    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

#Rock object
class Rock(GridObject):
    
    def __init__(self, toolType, canvas, position, color="grey"):
        super(Rock, self).__init__(toolType, canvas, position, color)
    
    def draw(self):
        if(not self.inView()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)

#Wall object
class Wall(GridObject):
    
    RAW_IMAGE = Image.open("images/wall.png")
    
    def __init__(self, toolType, canvas, position, color="grey"):
        super(Wall, self).__init__(toolType, canvas, position, color)
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_rectangle(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)

    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

#InvisibleWall object
class InvisibleWall(Wall):
    
    RAW_IMAGE = Image.open("images/wall_inv.png")
    
    def __init__(self, toolType, canvas, position, color="grey"):
        super(InvisibleWall, self).__init__(toolType, canvas, position, color)
    
    def drawImage(self):
        if(self.canvas.playmode): return True
        r, c = self.position
        m = 2
        w = h = self.canvas.space
        image = self.IMAGE
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(((c+0.5)*w, (r+0.5)*h),
                                image=self.photo)
        return True
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        self.color = "" if self.canvas.playmode else "grey"
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_rectangle(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                outline="",
                                fill=self.color)

    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

#TeleporterIn
class Teleporter(GridObject):
    
    RAW_IMAGE = Image.open("images/teleporter1.png")
    
    #popup to help with initializing
    def popupinit(self):
        master = Tkinter.Tk()
        Tkinter.Label(master, text="Row:").grid(row=0,
                                                column=0)
        Tkinter.Label(master, text="Column:").grid(row=1,
                                                   column=0)
        form1 = Tkinter.Entry(master)
        form1.grid(row=0, column=1)
        form2 = Tkinter.Entry(master)
        form2.grid(row=1, column=1)
        button = Tkinter.Button(master, text="Enter Destination",
                    width=20,command=lambda f=form1, g=form2:\
                    self.closepop(master, f, g))
        button.grid(row=2, column=1)
        master.mainloop()
    
    #close the popup
    def closepop(self, master, form1, form2):
        row = form1.get()
        col = form2.get()
        master.quit()
        master.destroy()
        if(row.isdigit() and col.isdigit()):
            row, col = int(row), int(col)
            if(self.canvas.onBoard(row, col) and
               self.canvas.isAccessible((row, col))):
                self.destination = (row, col)
    
    def __init__(self, toolType, canvas, position,
                 color="orange"):
        super(Teleporter, self).__init__(toolType,
                        canvas, position, color)
        self.destination = None
        self.popupinit()
        if(not self.destination):
            self.destination = position
        self.link = TeleporterOut(self.type, canvas,
                                 position=self.destination)
    
    def drawImage(self):
        r, c = self.position
        w = h = self.canvas.space
        image = self.IMAGE
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(((c+0.5)*w,
                                  (r+0.5)*h),
                                 image=self.photo)
        return True
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)
        r, c = self.destination
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)
    
    def action(self):
        dest = self.destination
        if(not self.canvas.onBoard(dest[0],dest[1])):
            return self.COMPLETE_ACTION
        if(not self.canvas.isAccessible(dest)):
            return self.COMPLETE_ACTION
        arr = self.canvas.get(self.position)
        for obj in arr:
            if(obj.type == Tool.ROBOT):
                obj.canvas.remove(obj)
                obj.position = (round(self.destination[0]),
                                    round(self.destination[1]))
                obj.canvas.place(obj.position, obj)
        return self.COMPLETE_ACTION
    
    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)
    
#TeleporterOut
class TeleporterOut(GridObject):
    
    RAW_IMAGE = Image.open("images/teleporter2.png")
    
    def __init__(self, toolType, canvas, position,
                 color="blue"):
        toolType = 0
        super(TeleporterOut, self).__init__(toolType,
                        canvas, position, color)
    
    def drawImage(self):
        r, c = self.position
        w = h = self.canvas.space
        image = self.IMAGE
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(((c+0.5)*w,
                                  (r+0.5)*h),
                                 image=self.photo)
        return True
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)
    
    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

#Motioner abstract object
class Motioner(GridObject):
    
    def __init__(self, toolType, canvas, position,
                 direction=(0.0,0.0), distance=0, color="orange"):
        super(Motioner, self).__init__(toolType,
                        canvas, position, color)
        self.direction = direction
        self.distance = distance
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)
    
    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

    def action(self):
        r = round(self.position[0] +
                  self.distance*self.direction[0])
        c = round(self.position[1] +
                  self.distance*self.direction[1])
        dest = (r, c)
        if(not self.canvas.onBoard(dest[0],dest[1])):
            return self.COMPLETE_ACTION
        if(not self.canvas.isAccessible(dest) and
           self.distance != 0):
            return self.COMPLETE_ACTION
        arr = self.canvas.get(self.position)
        for obj in arr:
            if(obj.type == Tool.ROBOT):
                if(self.distance == 0):
                    obj.facing = self.direction
                else:
                    obj.move(self.direction)
        return self.COMPLETE_ACTION

class UpTurner(Motioner):
    
    def __init__(self, toolType, canvas, position, color="orange"):
        super(UpTurner, self).__init__(toolType,
                        canvas, position, (-1, 0), 0, color)
    
    RAW_IMAGE = Image.open("images/turner_up.png")

class DownTurner(Motioner):
    
    def __init__(self, toolType, canvas, position, color="orange"):
        super(DownTurner, self).__init__(toolType,
                        canvas, position, (1, 0), 0, color)
    
    RAW_IMAGE = Image.open("images/turner_down.png")

class LeftTurner(Motioner):
    
    def __init__(self, toolType, canvas, position, color="orange"):
        super(LeftTurner, self).__init__(toolType,
                        canvas, position, (0, -1), 0, color)

    RAW_IMAGE = Image.open("images/turner_left.png")

class RightTurner(Motioner):
    
    def __init__(self, toolType, canvas, position, color="orange"):
        super(RightTurner, self).__init__(toolType,
                        canvas, position, (0, 1), 0, color)

    RAW_IMAGE = Image.open("images/turner_right.png")

class UpPusher(Motioner):
    
    def __init__(self, toolType, canvas, position, color="orange"):
        super(UpPusher, self).__init__(toolType,
                        canvas, position, (-1, 0), 1, color)

    RAW_IMAGE = Image.open("images/pusher_up.png")

class DownPusher(Motioner):
    
    def __init__(self, toolType, canvas, position, color="orange"):
        super(DownPusher, self).__init__(toolType,
                        canvas, position, (1, 0), 1, color)

    RAW_IMAGE = Image.open("images/pusher_down.png")

class LeftPusher(Motioner):
    
    def __init__(self, toolType, canvas, position, color="orange"):
        super(LeftPusher, self).__init__(toolType,
                        canvas, position, (0, -1), 1, color)

    RAW_IMAGE = Image.open("images/pusher_left.png")

class RightPusher(Motioner):
    
    def __init__(self, toolType, canvas, position, color="orange"):
        super(RightPusher, self).__init__(toolType,
                        canvas, position, (0, 1), 1, color)

    RAW_IMAGE = Image.open("images/pusher_right.png")

#GridObject adds one
class Adder(GridObject):
    
    RAW_IMAGE = Image.open("images/plus.png")
    
    def __init__(self, toolType, canvas, position, color="white"):
        super(Adder, self).__init__(toolType,
                        canvas, position, color)
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)
    
    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

    def action(self):
        arr = self.canvas.get(self.position)
        for obj in arr:
            if(obj.type == Tool.ROBOT):
                obj.changeCount(1)
        return self.COMPLETE_ACTION

#GridObject adds one
class Subtracter(GridObject):
    
    RAW_IMAGE = Image.open("images/minus.png")
    
    def __init__(self, toolType, canvas, position, color="white"):
        super(Subtracter, self).__init__(toolType,
                        canvas, position, color)
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)
    
    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

    def action(self):
        arr = self.canvas.get(self.position)
        for obj in arr:
            if(obj.type == Tool.ROBOT):
                obj.changeCount(-1)
        return self.COMPLETE_ACTION

#GridObject colors
class Colorer(GridObject):
    
    def __init__(self, toolType, canvas, position, color="blue"):
        super(Colorer, self).__init__(toolType,
                        canvas, position, color)
    
    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)
    
    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

    def action(self):
        arr = self.canvas.get(self.position)
        for obj in arr:
            if(isinstance(obj, Robot)):
                obj.color = self.color
        return self.COMPLETE_ACTION

class BlueBrush(Colorer):
    
    def __init__(self, toolType, canvas, position, color="blue"):
        super(BlueBrush, self).__init__(toolType,
                        canvas, position, color)

    RAW_IMAGE = Image.open("images/brushblue.png")

class RedBrush(Colorer):
    
    def __init__(self, toolType, canvas, position, color="red"):
        super(RedBrush, self).__init__(toolType,
                        canvas, position, color)

    RAW_IMAGE = Image.open("images/brushred.png")

class GreenBrush(Colorer):
    
    def __init__(self, toolType, canvas, position, color="green"):
        super(GreenBrush, self).__init__(toolType,
                        canvas, position, color)

    RAW_IMAGE = Image.open("images/brushgreen.png")

#Goal Object
class Goal(GridObject):
    
    RAW_IMAGE = Image.open("images/goal.png")
    
    def __init__(self, toolType, canvas, position, color="red"):
        super(Goal, self).__init__(toolType, canvas, position, color)
    
    def resizeImage(self):
        m = 2
        w = h = self.canvas.space
        self.IMAGE = self.RAW_IMAGE.resize((int(w-m),
                                            int(h-m)),
                                           Image.ANTIALIAS)

    def draw(self):
        if(not self.inView()): return
        if(not self.canvas.fast and self.drawImage()): return
        r, c = self.position
        w = h = self.canvas.space
        m = 4
        self.canvas.create_oval(c*w+m, r*h+m,
                                (c+1)*w-m, (r+1)*h-m,
                                fill=self.color)

game = GUI()
