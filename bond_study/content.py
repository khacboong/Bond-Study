from __future__ import annotations
import textwrap


levels = ["Foundations", "Core Skills", "Applied Python"]
lessons_per_page = [16, 16, 6]


def make_step(desc, code=""):
    description = textwrap.dedent(desc).strip()
    code_text = textwrap.dedent(code).strip()

    if code_text:
        # Put a short explanation directly in the editor so learners can
        # understand the purpose of an example before reading every line.
        if description.lower().startswith("answer idea"):
            comment_text = "Worked example for the task above."
        else:
            comment_text = " ".join(description.splitlines()).strip()

        comment_lines = textwrap.wrap(
            comment_text,
            width=88,
            initial_indent="# ",
            subsequent_indent="# ",
        )
        code_text = "\n".join(comment_lines + [code_text])

    return {"desc": description, "code": code_text}


def make_lesson(title, *steps):
    return {"title": title, "steps": list(steps)}


lessons = [
    make_lesson(
        'Greetings and Output',
        make_step(
            """Python can show text with print(). You can print words, numbers, and variables. Start with a message and check that it appears exactly as you expect.""",
            """print("Hello, Bond learners!")"""
        ),
        make_step(
            """Variables let you store values before printing them. This makes your programs easier to change and reuse.""",
            """greeting = "Welcome"
name = input("Name: ")
print(greeting, name)"""
        ),
        make_step(
            """Try it! Ask for two school subjects and print one friendly sentence that mentions both of them."""
        ),
        make_step(
            """Answer idea:""",
            """subject1 = input("First subject: ")
subject2 = input("Second subject: ")
print("I think", subject1, "and", subject2, "are interesting.")"""
        )
    ),
    make_lesson(
        'Whole Numbers and Operators',
        make_step(
            """Integers are whole numbers. Use int() when input should become a number before calculation.""",
            """a = int(input("First whole number: "))
b = int(input("Second whole number: "))
print("Total:", a + b)"""
        ),
        make_step(
            """Operators help you calculate. + adds, - subtracts, * multiplies, / divides and // makes whole-number division.""",
            """x = 17
y = 5
print(x + y)
print(x - y)
print(x * y)
print(x // y)"""
        ),
        make_step(
            """Try it! Ask for three whole numbers. Print the sum and then print half of that sum."""
        ),
        make_step(
            """Answer idea:""",
            """n1 = int(input("n1: "))
n2 = int(input("n2: "))
n3 = int(input("n3: "))
total = n1 + n2 + n3
print("Total:", total)
print("Half:", total / 2)"""
        )
    ),
    make_lesson(
        'Decimal Calculations',
        make_step(
            """Use float() when values may include decimal places. This is useful for money, length, speed, and time.""",
            """distance = float(input("Distance km: "))
time = float(input("Time hours: "))
print("Average speed:", distance / time)"""
        ),
        make_step(
            """You can combine decimal inputs to make a new result. Store intermediate values when the calculation has more than one step.""",
            """travel = float(input("Travel minutes: "))
rest = float(input("Rest minutes: "))
total_minutes = travel + rest
print("Total minutes:", total_minutes)"""
        ),
        make_step(
            """Try it! Build a floor-area calculator with decimal length and width."""
        ),
        make_step(
            """Answer idea:""",
            """length = float(input("Length: "))
width = float(input("Width: "))
area = length * width
print("Area:", area)"""
        )
    ),
    make_lesson(
        'Simple Decisions',
        make_step(
            """if and else let your program choose between two paths. The code inside a true condition runs, otherwise the else branch runs.""",
            """choice = input("Study or rest? ").lower()
if choice == "study":
    print("Open your notes.")
else:
    print("Take a short break.")"""
        ),
        make_step(
            """You can personalize a decision by collecting another input first and using it in both outcomes.""",
            """name = input("Name: ")
choice = input("Walk or read? ").lower()
if choice == "walk":
    print(name, "can go for a walk.")
else:
    print(name, "can read at home.")"""
        ),
        make_step(
            """Try it! Ask if someone wants tea. Show one message for yes and a different message for every other answer."""
        ),
        make_step(
            """Answer idea:""",
            """drink = input("Do you want tea? ").lower()
if drink == "yes":
    print("Tea is ready.")
else:
    print("Choose another drink.")"""
        )
    ),
    make_lesson(
        'Score Bands with Elif',
        make_step(
            """elif is useful when you have several ranges to test. Python checks the conditions from top to bottom.""",
            """score = int(input("Score 0-10: "))
if score >= 9:
    print("Excellent")
elif score >= 5:
    print("Good")
elif score >= 3:
    print("Keep going")
else:
    print("Try again")"""
        ),
        make_step(
            """Choose boundaries carefully so each input fits one clear group.""",
            """temperature = int(input("Temperature: "))
if temperature >= 30:
    print("Hot")
elif temperature >= 20:
    print("Warm")
else:
    print("Cool")"""
        ),
        make_step(
            """Try it! Classify a number as positive, negative, or zero."""
        ),
        make_step(
            """Answer idea:""",
            """number = int(input("Number: "))
if number > 0:
    print("Positive")
elif number < 0:
    print("Negative")
else:
    print("Zero")"""
        )
    ),
    make_lesson(
        'Logical Conditions',
        make_step(
            """and means every condition must be true. or means at least one condition must be true.""",
            """age = int(input("Age: "))
has_ticket = input("Ticket? ").lower() == "yes"
has_adult = input("Adult with you? ").lower() == "yes"
if age >= 14 and (has_ticket or has_adult):
    print("Entry allowed")
else:
    print("Please check the rules")"""
        ),
        make_step(
            """Booleans are just True and False. A comparison like score >= 8 creates a boolean value.""",
            """member = input("Member? ").lower() == "yes"
valid_pass = input("Valid pass? ").lower() == "yes"
print(member and valid_pass)"""
        ),
        make_step(
            """Try it! Print True when an age is between 13 and 19 inclusive."""
        ),
        make_step(
            """Answer idea:""",
            """age = int(input("Age: "))
print(13 <= age <= 19)"""
        )
    ),
    make_lesson(
        'Nested Decisions',
        make_step(
            """A nested decision is an if statement inside another if statement. Use this when the second question only matters after the first answer.""",
            """raining = input("Is it raining? ").lower()
if raining == "yes":
    windy = input("Is it windy? ").lower()
    if windy == "yes":
        print("Wear a waterproof coat.")
    else:
        print("Take an umbrella.")
else:
    print("No rain gear needed.")"""
        ),
        make_step(
            """Nested logic can also appear in the dry-weather branch when you want a different follow-up question.""",
            """raining = input("Rain? ").lower()
if raining == "yes":
    print("Check the forecast.")
else:
    sunny = input("Sunny? ").lower()
    if sunny == "yes":
        print("Wear a hat.")
    else:
        print("A light jacket is fine.")"""
        ),
        make_step(
            """Try it! Ask whether homework is finished. If yes, ask whether revision is done too. Show a message for each route."""
        ),
        make_step(
            """Answer idea:""",
            """homework = input("Homework finished? ").lower()
if homework == "yes":
    revision = input("Revision finished? ").lower()
    if revision == "yes":
        print("You are ready for tomorrow.")
    else:
        print("Do your revision next.")
else:
    print("Finish homework first.")"""
        )
    ),
    make_lesson(
        'Counted Loops',
        make_step(
            """for with range() repeats a block a fixed number of times. This is useful for times tables, repeated messages, and numbered tasks.""",
            """number = int(input("Which table? "))
for count in range(1, 11):
    print(number, "x", count, "=", number * count)"""
        ),
        make_step(
            """range(start, stop) includes the start number and stops before the end number.""",
            """for round_number in range(3, 8):
    print("Round", round_number)"""
        ),
        make_step(
            """Try it! Ask for a short message and print it three times with line numbers."""
        ),
        make_step(
            """Answer idea:""",
            """message = input("Message: ")
for line in range(1, 4):
    print(line, message)"""
        )
    ),
    make_lesson(
        'Condition Loops',
        make_step(
            """while repeats as long as its condition stays true. This is good when you do not know exactly how many repeats you need.""",
            """target = 7
attempts = 0
guess = 0
while guess != target and attempts < 5:
    guess = int(input("Guess 1-10: "))
    attempts += 1
print("Finished in", attempts, "tries.")"""
        ),
        make_step(
            """A while loop often uses a variable that changes each cycle so the loop can eventually end.""",
            """countdown = 3
while countdown > 0:
    print(countdown)
    countdown -= 1
print("Go!")"""
        ),
        make_step(
            """Try it! Keep asking for numbers until the user enters 0."""
        ),
        make_step(
            """Answer idea:""",
            """number = None
while number != 0:
    number = int(input("Number (0 to stop): "))
    if number != 0:
        print("You typed", number)"""
        )
    ),
    make_lesson(
        'Choosing the Right Loop',
        make_step(
            """Use for when the repeat count is known. Use while when the loop should continue until a condition changes.""",
            """for warmup in range(1, 6):
    print("Warm-up round", warmup)
answer = ""
while answer != "done":
    answer = input("Type done to finish: ").lower()
print("Session complete.")"""
        ),
        make_step(
            """A while loop can also count attempts so you can report how many entries were made.""",
            """attempts = 0
answer = ""
while answer != "done":
    answer = input("Command: ").lower()
    attempts += 1
print("Entries:", attempts)"""
        ),
        make_step(
            """Try it! Use a for loop to show four rounds, then a while loop that waits for the word exit."""
        ),
        make_step(
            """Answer idea:""",
            """for round_number in range(1, 5):
    print("Round", round_number)
command = ""
while command != "exit":
    command = input("Type exit to stop: ").lower()
print("Closed")"""
        )
    ),
    make_lesson(
        'Arcade Awards Project',
        make_step(
            """This project combines input, totals, loops, and decisions. Start by assigning an award from a final score.""",
            """name = input("Player name: ")
score = int(input("Score 0-30: "))
if score >= 24:
    award = "Gold"
elif score >= 15:
    award = "Silver"
else:
    award = "Bronze"
print(name, "earned", award)"""
        ),
        make_step(
            """You can build the score instead of typing it directly by looping through several rounds and adding points each time.""",
            """name = input("Player name: ")
total = 0
for round_number in range(1, 4):
    points = int(input(f"Round {round_number} score: "))
    total += points
print(name, "scored", total)"""
        ),
        make_step(
            """Try it! Extend the project so it shows both the total score and the award."""
        ),
        make_step(
            """Answer idea:""",
            """name = input("Player name: ")
total = 0
for round_number in range(1, 4):
    total += int(input(f"Round {round_number}: "))
if total >= 24:
    award = "Gold"
elif total >= 15:
    award = "Silver"
else:
    award = "Bronze"
print(name, "finished with", total, "points and earned", award)"""
        )
    ),
    make_lesson(
        'Cleaning and Formatting Text',
        make_step(
            """strip() removes spaces at the start and end of text. title() can improve the display of names.""",
            """name = input("First name: ")
name = name.strip().title()
print("Welcome,", name)"""
        ),
        make_step(
            """You can clean more than one text field before joining them.""",
            """first = input("First name: ").strip().title()
last = input("Surname: ").strip().title()
print("Name badge:", first, last)"""
        ),
        make_step(
            """Try it! Ask for a place you want to visit. Clean the text and print a sentence about that destination."""
        ),
        make_step(
            """Answer idea:""",
            """place = input("Destination: ").strip().title()
print("One day I want to visit", place)"""
        )
    ),
    make_lesson(
        'String Positions',
        make_step(
            """Strings store characters in order. Index 0 is the first character, and slices can extract a section of the text.""",
            """word = input("Word: ")
print("First:", word[0])
print("Preview:", word[0:4])"""
        ),
        make_step(
            """Indexes keep the original characters exactly as typed, including capitals.""",
            """first_word = input("Word one: ")
second_word = input("Word two: ")
badge = first_word[0] + second_word[0]
print("Badge:", badge)"""
        ),
        make_step(
            """Try it! Ask for a word and print the first letter, last letter, and middle three letters if possible."""
        ),
        make_step(
            """Answer idea:""",
            """word = input("Word: ")
word = word.strip()
if not word:
    print("Please enter at least one letter.")
else:
    print("First:", word[0])
    print("Last:", word[-1])
    if len(word) >= 3:
        middle_start = (len(word) - 3) // 2
        print("Middle three:", word[middle_start:middle_start + 3])
    else:
        print("Middle three: not enough letters.")"""
        )
    ),
    make_lesson(
        'Changing Text Case',
        make_step(
            """lower() and upper() help you compare and display text consistently.""",
            """team = input("Team name: ")
code = input("Team code: ")
print(team.upper())
print(code.lower())"""
        ),
        make_step(
            """A common pattern is to lower the user response before checking it.""",
            """response = input("Accepted? ").lower()
if response == "yes":
    print("Accepted")
else:
    print("Not accepted")"""
        ),
        make_step(
            """Try it! Ask for a sentence and print it once in lower-case and once in upper-case."""
        ),
        make_step(
            """Answer idea:""",
            """sentence = input("Sentence: ")
print(sentence.lower())
print(sentence.upper())"""
        )
    ),
    make_lesson(
        'Joining Text',
        make_step(
            """You can combine smaller strings to build usernames, tags, and labels.""",
            """first_name = input("First name: ")
last_name = input("Last name: ")
username = first_name.lower() + "_" + last_name.lower()
print("Username:", username)"""
        ),
        make_step(
            """A join can mix transformed parts, such as a lower-case name and an upper-case department code.""",
            """last_name = input("Last name: ")
department = input("Department: ")
label = last_name.lower() + "-" + department.upper()
print(label)"""
        ),
        make_step(
            """Try it! Make an event tag from a venue, activity, and two-letter group code."""
        ),
        make_step(
            """Answer idea:""",
            """venue = input("Venue: ").lower()
activity = input("Activity: ").lower()
group = input("Group code: ").upper()
tag = venue + "-" + activity + "-" + group
print("Tag:", tag)"""
        )
    ),
    make_lesson(
        'Check Your Progress: Foundations',
        make_step(
            """This checkpoint reviews the main ideas from the first page: output, variables, numbers, decisions, and loops. Try each task without looking back first."""
        ),
        make_step(
            """Challenge 1
Ask for a name and two whole numbers. Print a greeting and then print their total."""
        ),
        make_step(
            """Challenge 2
Ask for a score from 0 to 100. Print High if it is 80 or more, Medium if it is 50 to 79, and Low otherwise."""
        ),
        make_step(
            """Challenge 3
Use a loop to print the 5 times table from 1 to 10."""
        ),
        make_step(
            """Answer idea:""",
            """name = input("Name: ")
a = int(input("First number: "))
b = int(input("Second number: "))
print("Hello", name)
print("Total:", a + b)

score = int(input("Score: "))
if score >= 80:
    print("High")
elif score >= 50:
    print("Medium")
else:
    print("Low")

for i in range(1, 11):
    print("5 x", i, "=", 5 * i)"""
        )
    ),
    make_lesson(
        'Text Length and Layout',
        make_step(
            """len() tells you how many characters are in a string. Newline characters can help you show text on separate lines.""",
            """message = input("Short message: ")
print("Notice:\\n" + message)
print("Characters:", len(message))"""
        ),
        make_step(
            """You can count the size of more than one text value in the same program.""",
            """title = input("Title: ")
subtitle = input("Subtitle: ")
print(title)
print(subtitle)
print("Title length:", len(title))
print("Subtitle length:", len(subtitle))"""
        ),
        make_step(
            """Try it! Create a two-line poster with a heading and one instruction, then report the total characters in both parts."""
        ),
        make_step(
            """Answer idea:""",
            """heading = input("Heading: ")
instruction = input("Instruction: ")
print(heading + "\\n" + instruction)
print("Total characters:", len(heading) + len(instruction))"""
        )
    ),
    make_lesson(
        'List Basics',
        make_step(
            """Lists store many values in one variable. append() adds a new item to the end.""",
            """packing_list = ["water", "map", "snack"]
item = input("Add one more item: ")
packing_list.append(item)
print(packing_list)"""
        ),
        make_step(
            """You can collect several new items and keep them in order.""",
            """items = ["ticket", "phone"]
items.append(input("Extra item 1: "))
items.append(input("Extra item 2: "))
print(items)"""
        ),
        make_step(
            """Try it! Start a movie-night checklist with two items, then add one more and print the final list."""
        ),
        make_step(
            """Answer idea:""",
            """checklist = ["popcorn", "blanket"]
checklist.append(input("Add one item: "))
print("Checklist:", checklist)"""
        )
    ),
    make_lesson(
        'Random Whole Numbers',
        make_step(
            """random.randint(a, b) gives a whole number between a and b inclusive.""",
            """import random
roll = random.randint(1, 12)
print("Roll:", roll)"""
        ),
        make_step(
            """You can generate more than one random number and then combine them.""",
            """import random
first = random.randint(1, 6)
second = random.randint(1, 6)
print("Rolls:", first, second)
print("Total:", first + second)"""
        ),
        make_step(
            """Try it! Ask for a minimum and maximum, then generate one random target between them."""
        ),
        make_step(
            """Answer idea:""",
            """import random
low = int(input("Minimum: "))
high = int(input("Maximum: "))
print("Target:", random.randint(low, high))"""
        )
    ),
    make_lesson(
        'Random Steps and Choices',
        make_step(
            """random.randrange() can skip in steps, and random.choice() picks from a list.""",
            """import random
move = random.randrange(5, 31, 5)
colour = random.choice(["red", "blue", "gold", "green"])
print("Move:", move)
print("Colour:", colour)"""
        ),
        make_step(
            """Independent random choices can produce different results even when they use the same options.""",
            """import random
colours = ["red", "blue", "gold", "green"]
print(random.choice(colours))
print(random.choice(colours))"""
        ),
        make_step(
            """Try it! Build a random training prompt with one even step and one activity choice."""
        ),
        make_step(
            """Answer idea:""",
            """import random
steps = random.randrange(2, 13, 2)
activity = random.choice(["jump", "skip", "stretch"])
print("Do", steps, activity + "s")"""
        )
    ),
    make_lesson(
        'Reliable Menus',
        make_step(
            """A looped menu keeps running until the user chooses to leave. This makes programs feel more interactive.""",
            """running = True
while running:
    choice = input("1: status, 2: leave: ").lower()
    if choice == "1":
        print("Status ready.")
    elif choice == "2":
        running = False
    else:
        print("Choose 1 or 2.")
print("Menu closed.")"""
        ),
        make_step(
            """Invalid input should not crash the menu. Instead, respond clearly and continue the loop.""",
            """while True:
    choice = input("a: hello, b: quit: ").lower()
    if choice == "a":
        print("Hello!")
    elif choice == "b":
        break
    else:
        print("Unknown option")"""
        ),
        make_step(
            """Try it! Make a menu with one route that prints the day plan and another route that exits."""
        ),
        make_step(
            """Answer idea:""",
            """running = True
while running:
    choice = input("1: plan, 2: exit: ")
    if choice == "1":
        print("Plan: code, test, revise")
    elif choice == "2":
        running = False
    else:
        print("Pick 1 or 2")"""
        )
    ),
    make_lesson(
        'Character Codes',
        make_step(
            """ord() changes a character into its code number, and chr() changes a code back into a character.""",
            """letter = input("One letter: ")
code = ord(letter)
print("Code:", code)
print("Next:", chr(code + 1))"""
        ),
        make_step(
            """Shifting codes can create a tiny encoder.""",
            """letter = input("Lower-case letter: ")
shift = int(input("Shift 1-3: "))
print(chr(ord(letter) + shift))"""
        ),
        make_step(
            """Try it! Ask for three letters and print the next letter for each one without a loop."""
        ),
        make_step(
            """Answer idea:""",
            """a = input("Letter 1: ")
b = input("Letter 2: ")
c = input("Letter 3: ")
print(chr(ord(a) + 1))
print(chr(ord(b) + 1))
print(chr(ord(c) + 1))"""
        )
    ),
    make_lesson(
        'Updating List Positions',
        make_step(
            """List indexes let you read or replace a value at a chosen position.""",
            """supplies = ["pencil", "book", "tape"]
position = int(input("Position 0-2: "))
print("Old item:", supplies[position])
replacement = input("Replacement: ")
supplies[position] = replacement
print("Updated:", supplies)"""
        ),
        make_step(
            """You can read another position after updating the first one.""",
            """items = ["folder", "ruler", "pen"]
items[1] = "marker"
print(items[1])
print(items)"""
        ),
        make_step(
            """Try it! Make a list of three snacks, replace one using a position, and print the full list."""
        ),
        make_step(
            """Answer idea:""",
            """snacks = ["apple", "chips", "yogurt"]
pos = int(input("Which snack to replace? "))
snacks[pos] = input("New snack: ")
print(snacks)"""
        )
    ),
    make_lesson(
        'Insert and Remove Items',
        make_step(
            """insert() adds at a specific position, and remove() deletes the first matching value.""",
            """kit = ["water", "torch", "rope"]
kit.insert(1, "map")
kit.remove("rope")
print(kit)"""
        ),
        make_step(
            """These tools are useful when order matters, such as lineups, task queues, or travel kits.""",
            """names = ["Ava", "Ben", "Cara"]
names.insert(2, "Dara")
names.remove("Ben")
print(names)"""
        ),
        make_step(
            """Try it! Start with four names, insert a reserve at one position, remove another name, and print the result."""
        ),
        make_step(
            """Answer idea:""",
            """names = ["Mia", "Noah", "Omar", "Pia"]
position = int(input("Insert position 0-4: "))
reserve = input("Reserve name: ").strip().title()
remove_name = input("Name to remove (Mia, Noah, Omar, or Pia): ").strip().title()
names.insert(position, reserve)
if remove_name in names:
    names.remove(remove_name)
else:
    print("That name was not in the list.")
print(names)"""
        )
    ),
    make_lesson(
        'Delete by Position',
        make_step(
            """del list[index] removes an item by its position. Save the removed item first if you still want to show it.""",
            """tasks = ["email", "design", "test", "publish"]
position = int(input("Completed position: "))
completed = tasks[position]
del tasks[position]
print("Completed:", completed)
print("Remaining:", tasks)"""
        ),
        make_step(
            """After deleting one item, the list becomes shorter and indexes shift left.""",
            """items = ["red", "blue", "green"]
del items[1]
print(items)"""
        ),
        make_step(
            """Try it! Delete two tasks one after another and print what remains."""
        ),
        make_step(
            """Answer idea:""",
            """tasks = ["draft", "check", "edit", "send"]
first = int(input("First position: "))
del tasks[first]
second = int(input("Second position after the first delete: "))
del tasks[second]
print(tasks)"""
        )
    ),
    make_lesson(
        'Looping Through Lists',
        make_step(
            """A for loop can visit each item in a list one by one.""",
            """survey = ["tea", "water", "juice", "milk"]
for drink in survey:
    print("Choice:", drink)
print("Total drinks:", len(survey))"""
        ),
        make_step(
            """len(list_name) gives the number of items in the list.""",
            """colours = ["red", "blue", "green"]
for colour in colours:
    print(colour)
print("Count:", len(colours))"""
        ),
        make_step(
            """Try it! Make a list of three hobbies, print each hobby on its own line, and then print the total."""
        ),
        make_step(
            """Answer idea:""",
            """hobbies = ["drawing", "coding", "cycling"]
for hobby in hobbies:
    print("Hobby:", hobby)
print("Total:", len(hobbies))"""
        )
    ),
    make_lesson(
        'Building Lists with Loops',
        make_step(
            """You can start with an empty list and build it using repeated input.""",
            """notes = []
for count in range(5):
    note = input(f"Note {count + 1}: ")
    notes.append(note)
for note in notes:
    print(note)"""
        ),
        make_step(
            """A while loop can keep collecting until a stop word appears. Do not append the stop word itself.""",
            """notes = []
while True:
    note = input("Enter a note or stop: ")
    if note.lower() == "stop":
        break
    notes.append(note)
print(notes)"""
        ),
        make_step(
            """Try it! Collect shopping items until the user types done, then print the final list."""
        ),
        make_step(
            """Answer idea:""",
            """shopping = []
while True:
    item = input("Item or done: ")
    if item.lower() == "done":
        break
    shopping.append(item)
print(shopping)"""
        )
    ),
    make_lesson(
        'Prize Draw Project',
        make_step(
            """This mini project combines cleaning names, storing them in a list, and using randomness to pick a winner.""",
            """import random
entrants = []
for _ in range(3):
    name = input("Name: ").strip().title()
    entrants.append(name)
winner = random.choice(entrants)
bonus = random.randint(1, 10)
print("Winner:", winner)
print("Bonus tokens:", bonus)"""
        ),
        make_step(
            """Normalizing names means making them look consistent before storing them.""",
            """name = input("Name: ").strip().title()
print(name)"""
        ),
        make_step(
            """Try it! Upgrade the draw so it also prints the full entrants list before choosing a winner."""
        ),
        make_step(
            """Answer idea:""",
            """import random
entrants = []
for _ in range(3):
    entrants.append(input("Name: ").strip().title())
print("Entrants:", entrants)
print("Winner:", random.choice(entrants))"""
        )
    ),
    make_lesson(
        'Reading 2D Lists',
        make_step(
            """A 2D list is a list of rows. Each row can store related values, such as a club name and a member count.""",
            """clubs = [["Art", 12], ["Chess", 18], ["Code", 15]]
row = int(input("Club row 0-2: "))
print("Record:", clubs[row])
print("Club:", clubs[row][0])
print("Members:", clubs[row][1])"""
        ),
        make_step(
            """You can loop through every row to show a full table without printing the square brackets.""",
            """clubs = [["Art", 12], ["Chess", 18], ["Code", 15]]
for club in clubs:
    print(club[0], club[1])"""
        ),
        make_step(
            """Try it! Create a timetable with subject and room rows, then print one selected row."""
        ),
        make_step(
            """Answer idea:""",
            """timetable = [["Math", "A1"], ["Science", "B2"], ["History", "C3"]]
row = int(input("Row 0-2: "))
print(timetable[row][0], timetable[row][1])"""
        )
    ),
    make_lesson(
        'Updating 2D Cells',
        make_step(
            """You can change one value inside one row by using two indexes: row first, then column.""",
            """clubs = [["Art", 12], ["Chess", 18], ["Code", 15]]
row = int(input("Row 0-2: "))
new_members = int(input("New members: "))
clubs[row][1] = new_members
print(clubs[row])
print(clubs)"""
        ),
        make_step(
            """The same pattern works for text fields too.""",
            """record = ["Code", 15]
record[0] = "Coding"
record[1] = 17
print(record)"""
        ),
        make_step(
            """Try it! Let the user pick a row and update both the name and the number."""
        ),
        make_step(
            """Answer idea:""",
            """clubs = [["Art", 12], ["Chess", 18], ["Code", 15]]
row = int(input("Row 0-2: "))
clubs[row][0] = input("New name: ")
clubs[row][1] = int(input("New members: "))
print(clubs[row])"""
        )
    ),
    make_lesson(
        'Changing 2D Rows',
        make_step(
            """append(), insert(), and del also work with whole rows in a 2D list.""",
            """clubs = [["Art", 12], ["Chess", 18]]
clubs.append(["Code", 15])
clubs.insert(0, ["Drama", 11])
del clubs[1]
for club in clubs:
    print(club[0], club[1])"""
        ),
        make_step(
            """Build a new row first when the row needs several values.""",
            """new_club = ["Music", 9]
clubs = [["Art", 12]]
clubs.append(new_club)
print(clubs)"""
        ),
        make_step(
            """Try it! Add one new row, remove one chosen row, and print the remaining rows."""
        ),
        make_step(
            """Answer idea:""",
            """clubs = [["Art", 12], ["Chess", 18]]
name = input("New club: ")
members = int(input("Members: "))
clubs.append([name, members])
remove_row = int(input("Delete row 0-2: "))
del clubs[remove_row]
print(clubs)"""
        )
    ),
    make_lesson(
        'Check Your Progress: Core Skills',
        make_step(
            """This checkpoint reviews text handling, lists, random values, menus, and list processing. Work through the tasks and then compare your ideas with the sample answer."""
        ),
        make_step(
            """Challenge 1
Ask for first name and last name, then build a username using lower-case letters joined with an underscore."""
        ),
        make_step(
            """Challenge 2
Start with a list of three foods, add one more food from input, and print each food on its own line."""
        ),
        make_step(
            """Challenge 3
Use random.choice() to pick one reward from a list, then print it inside a looped menu that stops when the user types 2."""
        ),
        make_step(
            """Answer idea:""",
            """import random

first = input("First name: ")
last = input("Last name: ")
username = first.lower() + "_" + last.lower()
print("Username:", username)

foods = ["pizza", "pho", "sushi"]
foods.append(input("Add a food: "))
for food in foods:
    print(food)

rewards = ["sticker", "bookmark", "bonus point"]
running = True
while running:
    choice = input("1: reward, 2: exit: ")
    if choice == "1":
        print("Reward:", random.choice(rewards))
    elif choice == "2":
        running = False
    else:
        print("Pick 1 or 2")"""
        )
    ),
    make_lesson(
        'Searching 2D Lists',
        make_step(
            """To search a 2D list, loop through the rows and compare the field you care about.""",
            """clubs = [["art", 12], ["chess", 18], ["code", 15]]
target = input("Club to find: ").lower()
found = False
for club in clubs:
    if club[0] == target:
        print("Members:", club[1])
        found = True
if found == False:
    print("Club not found.")"""
        ),
        make_step(
            """A found flag helps you decide what to print after the loop finishes.""",
            """items = [["pen", 4], ["book", 2]]
found = False
for item in items:
    if item[0] == "pen":
        found = True
print(found)"""
        ),
        make_step(
            """Try it! Search a 2D list of subjects and rooms, then print the room or a not-found message."""
        ),
        make_step(
            """Answer idea:""",
            """rooms = [["math", "A1"], ["science", "B2"], ["art", "C4"]]
target = input("Subject: ").lower()
for record in rooms:
    if record[0] == target:
        print("Room:", record[1])
        break
else:
    print("Not found")"""
        )
    ),
    make_lesson(
        'Functions Basics',
        make_step(
            """A function groups instructions under a name so you can run them whenever you need.""",
            """def show_greeting():
    print("Hello, coder!")

show_greeting()
print("Welcome to Python.")"""
        ),
        make_step(
            """Calling the same function again reuses the same code without rewriting it.""",
            """def cheer():
    print("Keep learning!")

cheer()
cheer()"""
        ),
        make_step(
            """Try it! Write a function named show_rule() that prints one classroom rule, then call it twice."""
        ),
        make_step(
            """Answer idea:""",
            """def show_rule():
    print("Save your work often.")

show_rule()
show_rule()"""
        )
    ),
    make_lesson(
        'Functions with Results',
        make_step(
            """Some functions return a value so the main program can store it, print it, or use it in another calculation.""",
            """def add_score(first, second):
    total = first + second
    return total

score = add_score(7, 5)
print("Score:", score)"""
        ),
        make_step(
            """A good rule is that a function should calculate and return, while the main program decides how to display the result.""",
            """def total_cost(price, delivery):
    return price + delivery

print(total_cost(12.5, 3.0))"""
        ),
        make_step(
            """Try it! Create a function that returns the area of a rectangle."""
        ),
        make_step(
            """Answer idea:""",
            """def rectangle_area(length, width):
    return length * width

print(rectangle_area(4.5, 2))"""
        )
    ),
    make_lesson(
        'Several Functions Together',
        make_step(
            """A larger program often uses several functions, each with one job.""",
            """def show_menu():
    print("1: double")
    print("2: triple")
    print("3: half")

def double(number):
    return number * 2

def triple(number):
    return number * 3

def half(number):
    return number / 2"""
        ),
        make_step(
            """The main program can call a different function depending on the chosen option.""",
            """def show_menu():
    print("1: double")
    print("2: triple")
    print("3: half")

def double(number):
    return number * 2

def triple(number):
    return number * 3

def half(number):
    return number / 2

show_menu()
choice = input("Choice: ")
value = int(input("Number: "))
if choice == "1":
    print(double(value))
elif choice == "2":
    print(triple(value))
elif choice == "3":
    print(half(value))
else:
    print("Invalid choice")"""
        ),
        make_step(
            """Try it! Build area and perimeter functions for a rectangle and choose one from a menu."""
        ),
        make_step(
            """Answer idea:""",
            """def area(length, width):
    return length * width

def perimeter(length, width):
    return 2 * (length + width)

choice = input("a for area, p for perimeter: ")
l = float(input("Length: "))
w = float(input("Width: "))
if choice == "a":
    print("Area:", area(l, w))
else:
    print("Perimeter:", perimeter(l, w))"""
        )
    ),
    make_lesson(
        'Functions with 2D Data',
        make_step(
            """Functions can accept a 2D list as an argument and work through its rows.""",
            """def show_names(records):
    for record in records:
        print(record[0])

def find_members(records, target):
    for record in records:
        if record[0] == target:
            return record[1]
    return -1"""
        ),
        make_step(
            """A second helper can total one column by looping through every row.""",
            """def total_members(records):
    total = 0
    for record in records:
        total += record[1]
    return total

clubs = [["art", 12], ["chess", 18], ["code", 15]]
print(total_members(clubs))"""
        ),
        make_step(
            """Try it! Make functions to display names, search by name, and return the highest score from [name, score] rows."""
        ),
        make_step(
            """Answer idea:""",
            """def highest_score(records):
    best = records[0][1]
    for record in records:
        if record[1] > best:
            best = record[1]
    return best

results = [["ava", 9], ["ben", 7], ["cara", 10]]
print(highest_score(results))"""
        )
    ),
    make_lesson(
        'Club Manager Project',
        make_step(
            """This final project combines 2D lists and functions into one small manager program.""",
            """def show_records(records):
    for record in records:
        print(record)

def find_members(records, target):
    for record in records:
        if record[0] == target:
            return record[1]
    return -1"""
        ),
        make_step(
            """Store each record as [club name, member count, room]. Keep club names in lower-case if you want easy searching.""",
            """def show_records(records):
    for record in records:
        print(record)

def find_members(records, target):
    for record in records:
        if record[0] == target:
            return record[1]
    return -1

clubs = [["art", 12, "A1"], ["chess", 18, "B2"], ["code", 15, "C3"]]
show_records(clubs)
name = input("Club: ").lower()
members = find_members(clubs, name)
if members == -1:
    print("Club not found")
else:
    print("Members:", members)"""
        ),
        make_step(
            """Try it! Extend the project so it also prints the total number of members across all clubs."""
        ),
        make_step(
            """Answer idea:""",
            """def total_members(records):
    total = 0
    for record in records:
        total += record[1]
    return total

clubs = [["art", 12, "A1"], ["chess", 18, "B2"], ["code", 15, "C3"]]
print("Total members:", total_members(clubs))"""
        )
    )
]

# Actual vector artwork for the lesson map. Keeping these as SVG strings
# avoids font/emoji differences between macOS, Windows, and Linux.
LESSON_ICON_SVGS = {
    "terminal": """<svg viewBox=\"0 0 24 24\"><rect x=\"3\" y=\"4\" width=\"18\" height=\"16\" rx=\"2\"/><path d=\"m7 9 3 3-3 3M12 15h5\"/></svg>""",
    "calculator": """<svg viewBox=\"0 0 24 24\"><rect x=\"5\" y=\"2.5\" width=\"14\" height=\"19\" rx=\"2\"/><path d=\"M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M16 15h0M8 18h2M12 18h6\"/></svg>""",
    "ruler": """<svg viewBox=\"0 0 24 24\"><path d=\"m4 18 14-14 3 3L7 21H4zM9 13l2 2M12 10l2 2M15 7l2 2\"/></svg>""",
    "branch": """<svg viewBox=\"0 0 24 24\"><circle cx=\"6\" cy=\"5\" r=\"2\"/><circle cx=\"18\" cy=\"19\" r=\"2\"/><circle cx=\"18\" cy=\"5\" r=\"2\"/><path d=\"M8 5h5a5 5 0 0 1 5 5v7M8 5h5a5 5 0 0 0 5-5\"/></svg>""",
    "logic": """<svg viewBox=\"0 0 24 24\"><circle cx=\"9\" cy=\"12\" r=\"5\"/><circle cx=\"15\" cy=\"12\" r=\"5\"/><path d=\"M12 8v8M8 12h8\"/></svg>""",
    "loop": """<svg viewBox=\"0 0 24 24\"><path d=\"M18 7V3l3 3-3 3M6 17v4l-3-3 3-3\"/><path d=\"M18 6a7 7 0 0 0-12 3M6 18a7 7 0 0 0 12-3\"/></svg>""",
    "trophy": """<svg viewBox=\"0 0 24 24\"><path d=\"M8 4h8v4a4 4 0 0 1-8 0zM8 6H4v2a4 4 0 0 0 4 4M16 6h4v2a4 4 0 0 1-4 4M12 12v5M8 21h8M9 17h6\"/></svg>""",
    "text": """<svg viewBox=\"0 0 24 24\"><path d=\"M5 20 10 4h4l5 16M7 14h10M5 4h14\"/></svg>""",
    "brackets": """<svg viewBox=\"0 0 24 24\"><path d=\"M8 4H5v16h3M16 4h3v16h-3M10 9l2 3-2 3M14 9l-2 3 2 3\"/></svg>""",
    "link": """<svg viewBox=\"0 0 24 24\"><path d=\"m9 15-2 2a4 4 0 0 1-6-3 4 4 0 0 1 1-3l4-4a4 4 0 0 1 6 0M15 9l2-2a4 4 0 0 1 6 3 4 4 0 0 1-1 3l-4 4a4 4 0 0 1-6 0M8 12h8\"/></svg>""",
    "check": """<svg viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"8.5\"/><path d=\"m8 12 2.5 2.5L16 9\"/></svg>""",
    "list": """<svg viewBox=\"0 0 24 24\"><path d=\"M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01\"/></svg>""",
    "dice": """<svg viewBox=\"0 0 24 24\"><rect x=\"4\" y=\"4\" width=\"16\" height=\"16\" rx=\"3\"/><circle cx=\"8\" cy=\"8\" r=\".8\" fill=\"#171A2A\" stroke=\"none\"/><circle cx=\"16\" cy=\"16\" r=\".8\" fill=\"#171A2A\" stroke=\"none\"/><circle cx=\"12\" cy=\"12\" r=\".8\" fill=\"#171A2A\" stroke=\"none\"/></svg>""",
    "menu": """<svg viewBox=\"0 0 24 24\"><path d=\"M4 6h16M4 12h16M4 18h16\"/></svg>""",
    "grid": """<svg viewBox=\"0 0 24 24\"><rect x=\"4\" y=\"4\" width=\"7\" height=\"7\"/><rect x=\"13\" y=\"4\" width=\"7\" height=\"7\"/><rect x=\"4\" y=\"13\" width=\"7\" height=\"7\"/><rect x=\"13\" y=\"13\" width=\"7\" height=\"7\"/></svg>""",
    "plus": """<svg viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"8.5\"/><path d=\"M12 8v8M8 12h8\"/></svg>""",
    "trash": """<svg viewBox=\"0 0 24 24\"><path d=\"M5 7h14M9 7V4h6v3M7 7l1 13h8l1-13M10 11v5M14 11v5\"/></svg>""",
    "pencil": """<svg viewBox=\"0 0 24 24\"><path d=\"m5 16-1 4 4-1L19 8l-3-3zM14 7l3 3M5 20h14\"/></svg>""",
    "search": """<svg viewBox=\"0 0 24 24\"><circle cx=\"10.5\" cy=\"10.5\" r=\"6.5\"/><path d=\"m16 16 5 5\"/></svg>""",
    "function": """<svg viewBox=\"0 0 24 24\"><path d=\"M7 5c-2 0-3 2-3 7s1 7 3 7M17 5c2 0 3 2 3 7s-1 7-3 7M9 8h6M9 16h6\"/></svg>""",
    "return": """<svg viewBox=\"0 0 24 24\"><path d=\"M5 6h14v12H5zM8 12h8M8 12l3-3M8 12l3 3\"/></svg>""",
}

LESSON_ICON_KEYS = [
    "terminal", "calculator", "ruler", "branch", "branch", "logic", "branch",
    "loop", "loop", "loop", "trophy", "text", "brackets", "text", "link", "check",
    "ruler", "list", "dice", "dice", "menu", "brackets", "grid", "plus", "trash",
    "loop", "list", "trophy", "grid", "pencil", "grid", "check", "search",
    "function", "return", "function", "grid", "grid",
]


def lesson_icon_key(index):
    return LESSON_ICON_KEYS[index % len(LESSON_ICON_KEYS)]
