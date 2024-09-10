import random

### Define Globals ###
RAM_SIZE = 32
ROM_SIZE = 64
ALU_AMOUNT = 4
OPERAND_SIZE = 16
VALID_INSTRUCTIONS = [".","BRA","BRM","BRE","BRL","RAV","RAA","STV","STA","LVA","LVB","LRA","LRB","LAA","LAB",".","ADD","SUB","AND","OR.","XOR","RNR",".",".","RIA","RIV","SIA","SIB","SIR","BRI","CSM","HLT"]
VALID_CONTROLS = ["w","s","a","d","1","2","3","4"]

### Define Objects ###

class RAM:
    def __init__(self):
        self.Reset()

    def WriteValue(self,Value):
        self.Contents[self.CurrentAddress] = Value

    def ReadValue(self):
        return self.Contents[self.CurrentAddress]

    def SetCurrentAddress(self,Value):
        self.CurrentAddress = Value

    def Reset(self):
        self.Contents = []
        self.CurrentAddress = 0
        
        for i in range(1,RAM_SIZE):
            self.Contents.append(0)

    def ResetScreen(self):
        for i in range(0, 16):
            self.Contents[i] = 0

class ROM:
    def __init__(self,Program):
        self.Reset(Program)

    def ReadOpcode(self,LineNum):
        return self.Contents[LineNum][0]

    def ReadOperand(self,LineNum):
        return self.Contents[LineNum][1]

    def ReadALUselection(self,LineNum):
        return self.Contents[LineNum][2]

    def Reset(self,Program):
        self.Contents = Program

class ProgramCounter:
    def __init__(self):
        self.Reset()

    def Update(self):
        if self.Branch:
            self.CurrentAddress = self.JumpAddress
            self.Branch = False
        else:
            self.CurrentAddress += 1
            if self.CurrentAddress >= ROM_SIZE:
                self.CurrentAddress = 0

    def Jump(self,jumpAddress):
        self.JumpAddress = jumpAddress
        self.Branch = True

    def ReadValue(self):
        return self.CurrentAddress

    def Reset(self):
        self.CurrentAddress = 0
        self.JumpAddress = 0
        self.Branch = False

class ALU:
    def __init__(self):
        self.Reset()

    def SetRegisterA(self,Value):
        self.RegisterA = Value

    def SetRegisterB(self,Value):
        self.RegisterB = Value

    def Add(self):
        Value = self.RegisterA + self.RegisterB
        Value = CastToBitAmount(Value,OPERAND_SIZE)
        self.Accumulator = Value

    def Subtract(self):
        Value = self.RegisterA - self.RegisterB
        Value = CastToBitAmount(Value,OPERAND_SIZE)
        self.Accumulator = Value

    def And(self):
        A = ConvertToBinary(self.RegisterA, OPERAND_SIZE)
        B = ConvertToBinary(self.RegisterB, OPERAND_SIZE)
        self.Accumulator = ConvertToDenary(AndValues(A,B))

    def Or(self):
        A = ConvertToBinary(self.RegisterA, OPERAND_SIZE)
        B = ConvertToBinary(self.RegisterB, OPERAND_SIZE)
        self.Accumulator = ConvertToDenary(OrValues(A,B))

    def Xor(self):
        A = ConvertToBinary(self.RegisterA, OPERAND_SIZE)
        B = ConvertToBinary(self.RegisterB, OPERAND_SIZE)
        self.Accumulator = ConvertToDenary(XorValues(A,B))

    def Reset(self):
        self.RegisterA = 0
        self.RegisterB = 0
        self.Accumulator = 0

    def IsEqual(self):
        return self.RegisterA == self.RegisterB

    def IsMore(self):
        return self.RegisterA > self.RegisterB

    def IsLess(self):
        return self.RegisterA < self.RegisterB

    def ReadValue(self):
        return self.Accumulator

class InputModule:
    def __init__(self):
        self.Reset()

    def SetCurrentAddress(self,Value):
        self.CurrentAddress = Value

    def WriteValue(self,Value):
        self.Contents[self.CurrentAddress] = Value

    def ReadValue(self):
        if self.ReadAddress != -1:
            Value = self.Contents[self.ReadAddress]
            self.ReadAddress = -1
            return Value
        else:
            return 0

    def GetReadAddress(self):
        return self.ReadAddress

    def SetReadAddress(self,Input):
        i = 0
        for item in VALID_CONTROLS:
            if item == Input:
                self.ReadAddress = i
                break
            i += 1
        

    def Reset(self):
        self.Contents = [65532,4,65535,1,2,3,4,5]
        self.CurrentAddress = 0
        self.ReadAddress = -1
        
### Define Functions ###

def DisplayProgramOutput(RAMinput,PCinput):
        print("[ OUTPUT:",RAMinput.Contents[16],"]")

        ScreenLine = ""
        for y in range (0,4):
            for line in range(0,4):
                for x in range(0,4):
                    for pixel in range(0,4):
                        Value = ConvertToBinary(RAMinput.Contents[y * 4 + x],16)
                        LineValue = Value[line * 4 : line * 4 + 4]
                        ScreenLine += " " + LineValue[pixel]
                print(ScreenLine)
                ScreenLine = ""
        
        print("[ PC:",PCinput.ReadValue(),"]")

def ConvertToBinary(Number,BitAmount):
    Value = ""
    Number = int(Number)
    Number = Number % 2**BitAmount

    for i in range(BitAmount - 1, -1, -1):
        if Number - (2**i) >= 0:
            Value = Value + "#"
            Number -= (2**i)
        else:
            Value = Value + "."
    
    return Value

def ConvertToDenary(Number):
    Value = 0
    PlaceValue = len(Number)
    
    for i in range(PlaceValue - 1, -1, -1):
        if Number[PlaceValue - i - 1] == "#":
            Value += (2**i)
        
    return Value

def AndValues(NumberA,NumberB):
    Output=""
    for i in range(0,len(NumberA)):
        if NumberA[i] == "#" and NumberB[i] == "#":
            Output += "#"
        else:
            Output += "."
    return Output

def OrValues(NumberA,NumberB):
    Output=""
    for i in range(0,len(NumberA)):
        if NumberA[i] == "#" or NumberB[i] == "#":
            Output += "#"
        else:
            Output += "."
    return Output

def XorValues(NumberA,NumberB):
    Output = ""
    for i in range(0,len(NumberA)):
        if NumberA[i] != NumberB[i]:
            Output += "#"
        else:
            Output += "."
    return Output

def CastToBitAmount(Number,BitAmount):
    NewNum = ConvertToBinary(Number, OPERAND_SIZE)
    NewNum = NewNum[len(NewNum) - BitAmount : len(NewNum)]
    return ConvertToDenary(NewNum)
        

def GetInstructionID(Instruction):
    ID = 0
    for item in VALID_INSTRUCTIONS:
        if item == Instruction:
            return ID
        ID += 1
    return -1

def GenerateRandom():
    Output = ""
    for i in range(0,OPERAND_SIZE):
        Output += random.choice([".","#"])

    return Output

def AssembleProgram(Program):
    print("Here is your program, paint the # as white onto the appropriate positions on the cartridge\n")
    print("Top Side:")

    LineNum = 0
    for line in Program:
        if LineNum == 32:
            print("Bottom Side:")

        # Convert Instruction to Binary #
        Opcode = line[0]
        Opcode = ConvertToBinary(GetInstructionID(Opcode),5)

        # Convert Value to Binary #
        Operand = line[1]
        if Operand[0] not in [".","#"]:
            Operand = ConvertToBinary(Operand, OPERAND_SIZE)
        elif Operand == ".":
            Operand = "." * OPERAND_SIZE 

        # Convert ALU Selection to Binary #
        ALUselection = line[2]
        if ALUselection == ".":
            ALUselection = ".."
        else:
            ALUselection = ConvertToBinary(ALUselection,2)

        print(str(LineNum) + ":",Opcode,"\t",Operand,"\t",ALUselection)
        LineNum += 1

def RunProgram(Program):
    programCounter = ProgramCounter()
    ram = RAM()
    rom = ROM(Program)
    inputModule = InputModule()
    
    ALUs = []
    for i in range(0,ALU_AMOUNT):
        ALUs.append(ALU())

    CurrentOpcode = "."
    CurrentOperand = "."
    CurrentALU = "."
    
    UserInput = ""
    run = True
    while run:
        print("\n" * 20)

        if programCounter.ReadValue() >= len(Program):
            print("!! Program Terminated Program Counter Out Of Range !!")
            run = False
            break

        CurrentOpcode = rom.ReadOpcode(programCounter.ReadValue())
        CurrentOperand = rom.ReadOperand(programCounter.ReadValue())
        CurrentALU = rom.ReadALUselection(programCounter.ReadValue())
        print(CurrentOpcode,CurrentOperand,CurrentALU)
        if CurrentOperand[0] in ["#","."]:
            CurrentOperand = ConvertToDenary(CurrentOperand)

        programCounter, ram, ALUs, inputModule = ExecuteInstruction(CurrentOpcode,CurrentOperand,CurrentALU,programCounter,ram,ALUs,inputModule)
        
        DisplayProgramOutput(ram,programCounter)

        if CurrentOpcode == "HLT":
            print("Program Finished!")
            run = False
            break

        programCounter.Update()

        print("Hit ENTER Or type \"Quit\" to leave")
        UserInput = input("Use wasd for Dpad and 1234 for Select, Start A and B\n>")
        
        if UserInput in ["Quit","quit"]:
            print("Exiting Program...")
            run = False
            break
        elif UserInput in VALID_CONTROLS:
            if (inputModule.GetReadAddress() == -1):
                inputModule.SetReadAddress(UserInput)
            
def ExecuteInstruction(Opcode,Operand,ALUselected,programCounter,ram,ALUs,inputModule):
    if Opcode == "BRA":
        programCounter.Jump(int(Operand))
    elif Opcode == "BRM":
        if ALUs[int(ALUselected)].IsMore():
            programCounter.Jump(int(Operand))
    elif Opcode == "BRE":
        if ALUs[int(ALUselected)].IsEqual():
            programCounter.Jump(int(Operand))
    elif Opcode == "BRL":
        if ALUs[int(ALUselected)].IsLess():
            programCounter.Jump(int(Operand))
    elif Opcode == "RAV":
        ram.SetCurrentAddress(CastToBitAmount(Operand,5))
    elif Opcode == "RAA":
        NewAddress = ALUs[int(ALUselected)].ReadValue()
        ram.SetCurrentAddress(CastToBitAmount(NewAddress,5))
    elif Opcode == "STV":
        ram.WriteValue(Operand)
    elif Opcode == "STA":
        NewValue = ALUs[int(ALUselected)].ReadValue()
        ram.WriteValue(CastToBitAmount(NewValue,OPERAND_SIZE))
    elif Opcode == "LVA":
        ALUs[int(ALUselected)].SetRegisterA(int(Operand))
    elif Opcode == "LVB":
        ALUs[int(ALUselected)].SetRegisterB(int(Operand))
    elif Opcode == "LRA":
        ALUs[int(ALUselected)].SetRegisterA(ram.ReadValue())
    elif Opcode == "LRB":
        ALUs[int(ALUselected)].SetRegisterB(ram.ReadValue())
    elif Opcode == "LAA":
        ALUs[int(ALUselected)].SetRegisterA(ALUs[int(ALUselected)].ReadValue())
    elif Opcode == "LAB":
        ALUs[int(ALUselected)].SetRegisterB(ALUs[int(ALUselected)].ReadValue())
    elif Opcode == "ADD":
        ALUs[int(ALUselected)].Add()
    elif Opcode == "SUB":
        ALUs[int(ALUselected)].Subtract()
    elif Opcode == "AND":
        ALUs[int(ALUselected)].And()
    elif Opcode == "OR.":
        ALUs[int(ALUselected)].Or()
    elif Opcode == "XOR":
        ALUs[int(ALUselected)].Xor()
    elif Opcode == "RNR":
        RandNum = GenerateRandom()
        RandNum = AndValues(RandNum,ConvertToBinary(Operand,OPERAND_SIZE))
        ram.WriteValue(ConvertToDenary(RandNum))
    elif Opcode == "RIA":
        inputModule.SetCurrentAddress(CastToBitAmount(Operand,3))
    elif Opcode == "RIV":
        inputModule.WriteValue(int(Operand))
    elif Opcode == "SIA":
        ALUs[int(ALUselected)].SetRegisterA(inputModule.ReadValue())
    elif Opcode == "SIB":
        ALUs[int(ALUselected)].SetRegisterB(inputModule.ReadValue())
    elif Opcode == "SIR":
        ram.WriteValue(inputModule.ReadValue())
    elif Opcode == "BRI":
        if inputModule.GetReadAddress() != -1:
            programCounter.Jump(int(Operand))
    elif Opcode == "CSM":
        ram.ResetScreen()
    
    return programCounter, ram, ALUs, inputModule

### Main Program ###
print("Reading File...")
File = open("INPUT CODE HERE.txt","r")
FileLines = File.readlines()
File.close()

if len(FileLines) > ROM_SIZE:
    print("!! ERROR: Program must be at max 64 lines !!")
else:
    ### Syntax Check ###
    print("Checking Program...")

    Program = []
    EncounteredError = False
    
    for line in FileLines:
        line=line.strip("\n")
        ProgramLine = line.split(" ")

        if len(ProgramLine) == 3:
            if ProgramLine[2] not in [".","0","1","2","3"]:
                print("!! ERROR: Invalid ALU selection !!")
                print(">> ",line)
                EncounteredError = True
                break
                
            elif ProgramLine[0] not in VALID_INSTRUCTIONS:
                print("!! ERROR: Invalid Instruction !!")
                print(">> ",line)
                EncounteredError = True
                break
            
            else:
                Program.append(ProgramLine)
        else:
            print("!! ERROR: Each line must contain an opcode, operand and ALU selection !!")
            print(">> ", line)
            print("NOTE: If a line doesn't require a value put a 0 or .")
            EncounteredError = True
            break

    if not EncounteredError:
        ### Main Loop ###
        print("No Errors Encountered")
        UserInput=""
        
        while UserInput not in ["quit","Quit"]:
            print("\n=======================")
            print("Type \"Quit\" to exit\nType \"Output\" to assemble program to machine code\nType \"Run\" to test program")
            print("=======================\n")
            UserInput = input(">")

            if UserInput in ["output","Output"]:
                AssembleProgram(Program)
                input("\nHit ENTER to continue...")

            elif UserInput in ["run","Run"]:
                RunProgram(Program)
                input("\nHit ENTER to continue...")

    print("Exiting Program...")


