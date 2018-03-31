import ast # Abstract syntax tree used to build dictionary for transition rules
import re # RegEx used to check if string is apart of alphabet
import copy # Used to perform deep copy of nested dictionaries

def dfa_simulator(filename, inputStringFile, machineNumber):

	with open(filename) as fa:
		#lines = f.readlines()
		lines = fa.read().splitlines() # removes /r and /n 

	# Raw lines from file, can access lines individually
	#print lines

	### String manipulation functions ###

	# Insert bracket after key
	def insert_bracket(string):
		for i, char in enumerate(string):
		    if not char.isdigit():
		        break
		return string[:i+1] + '{' + string[i+1:]

	# Insert quotes for the first transition rule following a new state
	def insert_quote_first(string):
		# Split string at {
		tempBefore = string.split('{',1)[0]
		tempAfter = string.split('{', 1)[1]
	       
		# Insert quote after key
		for i, char in enumerate(tempAfter):
		    if not char.isdigit() or not char.isalpha() or '`' in char: # Numbers, letters, epsilon
		        break
		tempAfter = tempAfter[:i+1] + "'" + tempAfter[i+1:]

		# Insert quote before key
		for i, char in enumerate(tempAfter):
		    if char.isdigit() or char.isalpha or '`' in char: # Numbers, letters, epsilon
		        break
		tempAfter = tempAfter[:i] + "'" + tempAfter[i:]
		
		# Combine string back
		string = tempBefore + '{' +  tempAfter
		return string

	# Inserte quotes for added rules to a state
	def insert_quote_follow(string):
		# Insert quote after key
		for i, char in enumerate(string):
		    if not char.isdigit() or not char.isalpha() or '`' in char: # Numbers, letters, epsilon
		        break
		string = string[:i+1] + "'" + string[i+1:]

		# Insert quote before key
		for i, char in enumerate(string):
		    if char.isdigit() or char.isalpha() or '`' in char: # Numbers, letters, epsilon
		        break
		string = string[:i] + "'" + string[i:]
		return string

	def remove_state(string):
		string = string.split(',',1)[1] # Take split string after 1st comma
		return string

	tempLines = lines # Copy lines to temp variable
	acceptStates = tempLines[0] # Get acceptance state(s) from first line
	tempLines.pop(0) # Pop accepting state(s) from list of transistion rules

	# Prepare data for conversion to dictonary
	prevRule = -1
	newRule = '{'
	addEmpty = False

	# Iterate over every transition rule and put string into dictionary format
	for rule in tempLines: 
	   
	    # Empty string
	    if rule == '':
		prevRule = ''
		addEmpty = True # Bool flag used to help determine whether ot not to add empty string rule to 0 state

	    # First rule: Omit space for first rule 
	    elif rule[0] != prevRule and rule == tempLines[0]:
		rule = rule.replace(',', ':') # Replace , with :
		newRule += rule
		newRule = insert_bracket(rule)
		newRule = insert_quote_first(newRule)
		newRule = '{' + newRule 
	    
	    # New state: End curly bracket and add , delimeter for subsequent rules 
	    elif rule[0] != prevRule and rule != tempLines[0]:
		rule = rule.replace(',', ':') # Replace , with :
		rule = insert_bracket(rule) 
		rule = insert_quote_first(rule)
	    
		newRule += '}, ' # End previous transition rule
		newRule += rule # Add new transition rule 

	    # Add extra rules to states: Combine rules into dictionary
	    elif rule[0] == prevRule:
		#addRule = rule[2:] # Slice off first two chars
		addRule = remove_state(rule)
		addRule = addRule.replace(',', ':')
		addRule = insert_quote_follow(addRule)
		
		newRule += ',' # Added comma delimeter to seperate rules
		newRule += addRule # Add rule to transition rules 

	    if rule != '':
		prevRule = rule[0] # Store current rule as the previous for next iteration
	    #print newRule # Show construction of dictionary for each transition rule

	# Close the string with curly braces
	newRule += '}}'

	# Convert string to dictonary
	transitionRules = ast.literal_eval(newRule)
    
	# Copy transition rules for NFA checking
	transitionRulesCopy = copy.deepcopy(transitionRules)

	# Add empty string to 0 state if necessary
	if addEmpty == True:
	    transitionRules[0][''] = 0

	# Print type of transitionRules -> (dictionary) and print the dictionary of transition rules
	#print type(transitionRules)
	#print transitionRules

	# Number of states
	numStates = len(transitionRules.keys())
	print "Number of states: ", numStates

	# Alphabet of FA
	alphabetSet = set() # Distinct unorderd list (no duplicates)
	for i, j in transitionRules.items(): # Add values of nested dictionary
	    for q, r in j.items():
		alphabetSet.add(q)
	alphabetList = list(alphabetSet) # Convert set to list
	alphabetList.sort() # Sort the list in ASCII order
	alphabet = ''.join(alphabetList) # Convert the list to a string 
	print "Alphabet: ", alphabet

	# Accept states
	print "Accept state(s): ", acceptStates
	acceptStates = eval(acceptStates)

	# Check for NFA
        isNFA = False
	newRuleString = newRule.replace(" ", "")
	newTransitionRuleString = str(transitionRulesCopy).replace(" ", "")
	# Print statements to show difference in string before and after being applied to a dictionary, if they are unequal, duplicate rules were removed	
	#print newRuleString
	#print len(newRuleString)
	#print newTransitionRuleString
	#print len(newTransitionRuleString)
	if len(newRuleString) != len(newTransitionRuleString):
	    isNFA = True
	    print "DUPLICATE KEYS DIFFERENT RULES: NFA"

	# Check if machine is NFA or DFA or INVALID
	machineClass = ''
	if '`' in alphabet or isNFA == True: # If epsilon transition in rules or multiple transtions for same symbol
	    print "EPSILON TRANSITION: NFA"
	    machineClass = 'NFA'
	else:
	    machineClass = 'DFA'
	print "VALID: ", machineClass

	# Run Finite Automaton
	def run_fa(transitions, initialState, acceptStates, inputString, alphabet):
	    stringToCheck = "^[" + alphabet + "]*$" # Setup RegEx for alphabet
	    verify = re.match(stringToCheck, inputString) # Check against input string
	    
	    # Check if string is apart of alphabet
	    if verify is None:
		return False
	    
	    # If string apart of alphabet, check for acceptance
	    else:
		state = initialState # Set initial state
	       
	       # Iterate through input char by char 
		for char in inputString:
		    
                    # Check if rule exists for state 
	            if not(state in transitions.keys()):
	                return False

		    # Check if there is a transition rule for the current input symbol given the state
		    if not(char in transitions[state].keys()):# or not(set(transitions[state].values()) == set(transitions.keys())): # Second half handles transitions to states that don't exist
		        return False
		    else:
		        state = transitions[state][char]
		
		return state in acceptStates

	# Run machine against every string in the input file
	if machineClass == 'DFA':
		if machineNumber < 10:
		    txtFile = open('Output_Strings/m0' + str(machineNumber) + '.txt', "w")
		elif machineNumber >= 10:
		    txtFile = open('Output_Strings/m' + str(machineNumber) + '.txt', "w")
		
		with open(inputStringFile) as stringFile:
			lines = stringFile.read().splitlines() # removes /r and /n 

		acceptCount = 0
		totalCount = len(lines)

		for i in range(len(lines)):
		    acceptString = run_fa(transitionRules, 0, acceptStates, lines[i], alphabet)
		    if acceptString == True:
			txtFile.write(lines[i] + '\n')
			acceptCount += 1
		print 'Accepted Strings: ' + str(acceptCount) + ' / ' + str(totalCount)
		stringFile.close()

	# Log FA information to logfile
	if machineNumber < 10:
	    logFile = open('Logs/m0' + str(machineNumber) + '.log', "w")
	elif machineNumber >= 10:
	    logFile = open('Logs/m' + str(machineNumber) + '.log', "w")

	logFile.write('Valid: ' + machineClass + '\n')
	logFile.write('States: ' + str(numStates) + '\n')
	logFile.write('Alphabet: ' + alphabet + '\n')
	if machineClass == 'DFA':
	    logFile.write('Accepted Strings: ' + str(acceptCount) + ' / ' + str(totalCount))
	elif machineClass == 'NFA':
	    logFile.write('Accepted Strings: 0 / 0')
	

	## TESTING ##
	#print accepts(transitionRules, 0, acceptStates, 'baa', alphabet) #mo2.fa works with (empty string)

	#print accepts(transitionRules, 0, {17,9}, '001') #m007.fa works with {n,n,n} : TRUE
	#print accepts(transitionRules, 0, {17,9}, '01') #TRUE
	#print accepts(transitionRules, 0, {17,9}, '0') #FALSE
	#print accepts(transitionRules, 0, {17,9}, '0010')#m007.fa works with NFA also

	#print accepts(transitionRules, 0, {}, 'abcdef') #m009.fa works with {} accepting
	#print accepts(transitionRules, 0, {1}, 'aaa')
	#print accepts(transitionRules, 0, {1}, 'aa')
	####

	### NEED ###
	# rules input:
	# X. handle empty line rule for input
	# 
	# accepts:
	# X: accepts returns false if symbol not in alphabet
	# X: accepts returns false if it cant find a transition rule
	# 
	# rule extraction: 
	# X. get alphabet for transitionRules
	# X. get accepting states for transitionRules (tempLines[0])
	# X. get total number of states
	#
	# nfa:
	# X. check for nfa (epsilon trans, mult rules same state)
	# 
	# wrapper:
	# X. encapsulate everything here into a class which takes a file name as param
	# X. in main, iterate through folder for every file 
	# X. run each string in accepts for each machine
	# X. output information files 
	############

#End dfa_simulator


filenameLeft = 'Machines/m'
filenameRight = '.fa'
numMachines = 31

stringFile = 'Machines/input.txt'

for machine in range(numMachines):
    print "FA: " + str(machine)
     
    # Iterate through all machines (fa)     
    if machine < 10:  
        dfa_simulator(filenameLeft + '0' + str(machine) + filenameRight, stringFile, machine) 
    elif machine >= 10:
        dfa_simulator(filenameLeft + str(machine) + filenameRight, stringFile, machine)
  
    print ""

